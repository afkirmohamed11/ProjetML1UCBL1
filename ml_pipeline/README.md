# ML Pipeline — Infrastructure

This repository contains a minimal, ready-to-use infrastructure for the ML Pipeline


## 1. Set Up the local infrastructure

### Create a virtual environment
```sh
python -m venv ml
```
### Activate the virtual environment
```sh
ml\Scripts\activate

```
### Install dependencies
```sh
pip install -r requirements.txt
```

### Create your own `.env` file from `.env.example`

- **macOS / Linux**
```sh
cp .env.example .env
```
- **windows**
```sh
copy .env.example .env
```