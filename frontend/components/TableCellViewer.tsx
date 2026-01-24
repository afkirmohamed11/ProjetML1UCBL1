import React from "react";

// Displays a PredictRequest + prediction result with grouped, styled UI
export type PredictRecord = {
  gender: string;
  senior_citizen: boolean;
  partner: boolean;
  dependents: boolean;
  tenure: number;
  phone_service: boolean;
  multiple_lines: string;
  internet_service: string;
  online_security: string;
  online_backup: string;
  device_protection: string;
  tech_support: string;
  streaming_tv: string;
  streaming_movies: string;
  contract: string;
  paperless_billing: boolean;
  payment_method: string;
  monthly_charges: number;
  total_charges: number;
  churned: boolean;
  status: string;
  notified: boolean;
  first_name: string;
  last_name: string;
  email: string;
  churn_probability: number;
  notified_date?: string;
  feedback_date?: string;
  feedback_answer?: string;
};

type FieldType = "text" | "boolean" | "months" | "money" | "number";

function currency(v: number) {
  try {
    return new Intl.NumberFormat(undefined, { style: "currency", currency: "USD", maximumFractionDigits: 2 }).format(
      v
    );
  } catch {
    return v.toFixed(2);
  }
}

function BooleanBadge({ value }: { value: boolean }) {
  return (
    <span
      className={
        "inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium " +
        (value
          ? "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-300"
          : "bg-rose-100 text-rose-700 dark:bg-rose-900/30 dark:text-rose-300")
      }
    >
      {value ? "Yes" : "No"}
    </span>
  );
}

function StatusBadge({ status }: { status: string }) {
  let colorClasses = "bg-gray-100 text-gray-700 dark:bg-gray-900/30 dark:text-gray-300";
  let label = status;

  switch (status) {
    case "notified":
      colorClasses = "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-300";
      label = "Notified";
      break;
    case "not_notified":
      colorClasses = "bg-rose-100 text-rose-700 dark:bg-rose-900/30 dark:text-rose-300";
      label = "Not Notified";
      break;
    case "responded_ok":
      colorClasses = "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-300";
      label = "Responded OK";
      break;
    case "responded_no":
      colorClasses = "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-300";
      label = "Responded No";
      break;
    default:
      label = "Unknown";
  }

  return (
    <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${colorClasses}`}>
      {label}
    </span>
  );
}

function ValueCell({ value, type }: { value: unknown; type: FieldType }) {
  if (type === "boolean") return <BooleanBadge value={Boolean(value)} />;
  if (type === "months") return <span>{Number(value)} months</span>;
  if (type === "money") return <span>{currency(Number(value))}</span>;
  if (type === "number") return <span>{Number(value).toLocaleString()}</span>;
  return <span className="capitalize">{String(value ?? "-")}</span>;
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="rounded-lg border bg-card text-card-foreground">
      <div className="border-b px-4 py-2 font-medium">{title}</div>
      <div className="p-4">{children}</div>
    </div>
  );
}

export default function TableCellViewer({ data }: { data: PredictRecord }) {
  console.log("Rendering TableCellViewer with data:", data);
  const percent = (() => {
    const v = Number(data.churn_probability);
    const p = v <= 1 ? v * 100 : v;
    return Math.max(0, Math.min(100, p));
  })();

  const barColor = percent < 33 ? "bg-emerald-500" : percent < 66 ? "bg-amber-500" : "bg-rose-500";

  return (
    <div className="space-y-4">
      <div className="rounded-xl border p-4">
        <div className="mb-3 flex items-center justify-between">
          <div className="text-sm text-muted-foreground">Churn Probability</div>
          <div className="text-sm font-medium">{percent.toFixed(2)}%</div>
        </div>
        <div className="h-2 w-full overflow-hidden rounded bg-muted">
          <div className={`h-full ${barColor}`} style={{ width: `${percent}%` }} />
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <Section title="Customer Info">
          <dl className="grid grid-cols-1 gap-2 sm:grid-cols-2">
            <Field label="First Name">
              <ValueCell value={data.first_name} type="text" />
            </Field>
            <Field label="Last Name">
              <ValueCell value={data.last_name} type="text" />
            </Field>
            <Field label="Senior Citizen">
              <ValueCell value={data.senior_citizen} type="boolean" />
            </Field>
            <Field label="Partner">
              <ValueCell value={data.partner} type="boolean" />
            </Field>
            <Field label="Gender">
              <ValueCell value={data.gender} type="text" />
            </Field>
          </dl>
        </Section>
        <Section title="Profile">
          <dl className="grid grid-cols-1 gap-2 sm:grid-cols-2">
            <Field label="Gender">
              <ValueCell value={data.gender} type="text" />
            </Field>
            <Field label="Senior Citizen">
              <ValueCell value={data.senior_citizen} type="boolean" />
            </Field>
            <Field label="Partner">
              <ValueCell value={data.partner} type="boolean" />
            </Field>
            <Field label="Dependents">
              <ValueCell value={data.dependents} type="boolean" />
            </Field>
            <Field label="Tenure">
              <ValueCell value={data.tenure} type="months" />
            </Field>
          </dl>
        </Section>

        <Section title="Contact">
          <dl className="grid grid-cols-1 gap-2 sm:grid-cols-2">
            <Field label="Phone Service">
              <ValueCell value={data.phone_service} type="boolean" />
            </Field>
            <Field label="Multiple Lines">
              <ValueCell value={data.multiple_lines} type="text" />
            </Field>
          </dl>
        </Section>

        <Section title="Internet & Add-ons">
          <dl className="grid grid-cols-1 gap-2 sm:grid-cols-2">
            <Field label="Internet Service">
              <ValueCell value={data.internet_service} type="text" />
            </Field>
            <Field label="Online Security">
              <ValueCell value={data.online_security} type="text" />
            </Field>
            <Field label="Online Backup">
              <ValueCell value={data.online_backup} type="text" />
            </Field>
            <Field label="Device Protection">
              <ValueCell value={data.device_protection} type="text" />
            </Field>
            <Field label="Tech Support">
              <ValueCell value={data.tech_support} type="text" />
            </Field>
            <Field label="Streaming TV">
              <ValueCell value={data.streaming_tv} type="text" />
            </Field>
            <Field label="Streaming Movies">
              <ValueCell value={data.streaming_movies} type="text" />
            </Field>
          </dl>
        </Section>

        <Section title="Billing">
          <dl className="grid grid-cols-1 gap-2 sm:grid-cols-2">
            <Field label="Contract">
              <ValueCell value={data.contract} type="text" />
            </Field>
            <Field label="Paperless Billing">
              <ValueCell value={data.paperless_billing} type="boolean" />
            </Field>
            <Field label="Payment Method">
              <ValueCell value={data.payment_method} type="text" />
            </Field>
          </dl>
        </Section>

        <Section title="Charges">
          <dl className="grid grid-cols-1 gap-2 sm:grid-cols-2">
            <Field label="Monthly Charges">
              <ValueCell value={data.monthly_charges} type="money" />
            </Field>
            <Field label="Total Charges">
              <ValueCell value={data.total_charges} type="money" />
            </Field>
          </dl>
        </Section>

        <Section title="Notification Status">
          <dl className="grid grid-cols-1 gap-2 sm:grid-cols-2">
            <Field label="Status">
              <StatusBadge status={data.status} />
            </Field>
            <Field label="Notified">
              {data.notified_date ? (
                <div className="flex flex-col items-end">
                  <span className="text-emerald-600 font-medium">Yes</span>
                  <span className="text-xs text-muted-foreground">
                    {new Date(data.notified_date).toLocaleDateString()}
                  </span>
                </div>
              ) : (
                <span className="text-muted-foreground">No</span>
              )}
            </Field>
            {data.notified_date && (
              <Field label="Feedback">
                {data.feedback_date && data.feedback_answer ? (
                  <div className="flex flex-col items-end">
                    <span className={
                      data.feedback_answer.toLowerCase() === "yes"
                        ? "text-emerald-600 font-medium"
                        : "text-amber-600 font-medium"
                    }>
                      {data.feedback_answer.toLowerCase() === "yes" ? "Responded OK" : "Responded No"}
                    </span>
                    <span className="text-xs text-muted-foreground">
                      {new Date(data.feedback_date).toLocaleDateString()}
                    </span>
                  </div>
                ) : (
                  <span className="text-muted-foreground">No response yet</span>
                )}
              </Field>
            )}
          </dl>
        </Section>
      </div>
    </div>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="flex items-start justify-between gap-4 rounded-md border p-3">
      <dt className="text-xs font-medium text-muted-foreground">{label}</dt>
      <dd className="text-sm font-medium">{children}</dd>
    </div>
  );
}
