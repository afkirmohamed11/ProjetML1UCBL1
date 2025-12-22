from typing import Any, Dict
from app.model import load_model


def _to_jsonable(value: Any) -> Any:
    try:
        import numpy as np
        if isinstance(value, (np.ndarray,)):
            return value.tolist()
    except Exception:
        pass
    try:
        # Handle pandas objects if present
        import pandas as pd
        if isinstance(value, (pd.Series, pd.Index)):
            return value.tolist()
    except Exception:
        pass
    return value


def get_model_info() -> Dict[str, Any]:
    m = load_model()
    info: Dict[str, Any] = {
        "type": type(m).__name__,
    }

    # Try sklearn-specific inspection without hard dependency
    try:
        from sklearn.pipeline import Pipeline
        from sklearn.compose import ColumnTransformer

        if isinstance(m, Pipeline):
            info["pipeline_steps"] = [name for name, _ in m.steps]
            final_est = m.steps[-1][1]
            info["final_estimator"] = type(final_est).__name__
            try:
                # Feature names after preprocessing
                preproc = m[:-1]
                if hasattr(preproc, "get_feature_names_out"):
                    info["feature_names_out"] = list(preproc.get_feature_names_out())
            except Exception:
                pass

        if hasattr(m, "get_params"):
            try:
                params = m.get_params()
                info["params"] = {k: _to_jsonable(v) for k, v in params.items()}
            except Exception:
                pass

        # Common estimator attributes
        for attr in [
            "classes_",
            "coef_",
            "intercept_",
            "feature_names_in_",
            "n_features_in_",
            "multi_class",
            "solver",
        ]:
            if hasattr(m, attr):
                try:
                    val = getattr(m, attr)
                    info[attr] = _to_jsonable(val)
                except Exception:
                    pass

        # If ColumnTransformer directly
        if isinstance(m, ColumnTransformer):
            try:
                info["feature_names_out"] = list(m.get_feature_names_out())
            except Exception:
                pass
    except Exception:
        # Non-sklearn object or inspection failure; return minimal info
        pass

    return info
