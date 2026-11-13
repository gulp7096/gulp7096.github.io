# Standard Operating Procedure (SOP) - Inventory API

This runbook outlines how to safely operate, maintain, and troubleshoot the Inventory API.

## 1. Operating the Server

**To start the API:**
Open your terminal in the project folder and run:
```bash
uvicorn src.app:app --host 127.0.0.1 --port 8000
```

The API will be live at http://127.0.0.1:8000.

**To stop the API:**
Press Ctrl + C in the terminal where the server is running.

## 2. Running the QA / Regression Suite

Any time you make a change to the code or spec, run the automated tests.
```bash
pytest tests/test_api.py -v
```

If a test fails, do not deploy. The code and openapi.yaml must pass 100% of tests.

## 3. Backing up the Database

The database is a single local file named inventory.db.
To back it up, simply copy it to a secure location:
```bash
cp inventory.db backups/inventory_backup_$(date +%F).db
```

## 4. Rollback Plan

If an update breaks the application, rolling back is completely safe. Because the database is a standard SQLite file, reversing the code logic will not corrupt the data.
Fix: Run git revert HEAD (or manually restore the last known good src/app.py file) and restart the server.

## 5. Troubleshooting Table

| Error / Issue | Cause | Fix |
|---|---|---|
| 409 Conflict | The system blocked an attempt to create a product with a sku that already exists. | Use a unique SKU, or use the PUT /products/{sku} endpoint to update the existing product instead. |
| 422 Unprocessable Entity | A validation rule was broken (e.g., negative price, negative quantity, or missing required field). | Check the payload against the openapi.yaml requirements. Fix the data and resubmit. |
| "Port already in use" | Another process (or a frozen version of the server) is already occupying port 8000. | Run lsof -i :8000 to find the process ID (PID), then run kill -9 <PID> and restart. |
| "Database is locked" | A previous database connection hung or a manual SQLite browser tool is actively locking the file. | Close any external SQLite viewers. If it persists, restart the API server. |
| Server won't start | Usually a syntax error in src/app.py or a missing Python dependency. | Check the terminal output for the exact line number of the crash, or run pip install -r requirements.txt. |
