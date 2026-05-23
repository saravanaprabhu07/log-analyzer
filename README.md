# Intelligent Log Analyzer Dashboard

This React dashboard connects to the FastAPI backend at `http://localhost:8000/api/v1`.

## Setup

1. Install Node.js and npm.
2. From the `frontend` folder run:
   ```bash
   npm install
   npm start
   ```

## Backend

Start the Python backend from the project root:

```bash
python3 -m uvicorn main:app --reload
```

Then open:

- `http://localhost:8000/app/` for the dashboard served by FastAPI
- `http://localhost:8000/docs` for FastAPI documentation

## Notes

This frontend is implemented as browser-native React ESM modules, so it does not require `npm` to run. If you have `npm` installed later, the existing `package.json` still supports a standard Create React App workflow.
