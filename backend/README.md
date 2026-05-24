# TripNote Backend

FastAPI backend for temporary card generation. Uploaded images are read in memory and are not saved by this service.

## Install

```bash
cd backend
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

## Run in mock mode

```bash
MOCK_AI=1 .venv/bin/python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8787
```

## Run with a vision model

Set environment variables before starting:

```bash
export ARK_API_KEY="your-key"
export ARK_BASE_URL="https://ark.cn-beijing.volces.com/api/v3"
export UPSTREAM_MODE="responses"
.venv/bin/python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8787
```

`ARK_MODEL` is optional for the demo. If it is empty, or if a Key ID like
`ak-...` is pasted by mistake, the backend uses the default vision model
`doubao-seed-1-6-vision-250815`. To force a specific endpoint/model, set:

```bash
export ARK_MODEL="your-endpoint-or-model-id"
```

## API

```text
POST /api/cards/generate
multipart/form-data:
  image: file
  hint: optional string
```
