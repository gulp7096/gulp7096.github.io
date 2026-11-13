# Webhook-to-CRM Sync Microservice

A lightweight FastAPI microservice designed to replace fragile Zapier/Make automations for incoming contact forms. It receives inbound webhooks, validates payloads, deduplicates repeated emails, pushes data to a downstream CRM, and writes local SQLite audit logs for complete visibility.

## What this Replaces
This fully replaces a multi-step Zapier Zap (Webhook Catch -> Filter -> CRM Create -> Notification). Unlike the Zap, this microservice:
- Imposes strict JSON schema validation, rejecting malformed leads immediately (422 Unprocessable Entity).
- Has an integrated SQLite sync log preventing duplicate email submissions from firing duplicate API requests to the CRM.
- Gracefully handles and permanently logs downstream network failures, ensuring no dropped leads disappear silently.
- Requires $0/month in subscription fees and eliminates pay-per-task billing.

## Endpoints
* **`POST /webhooks/contact`** - Validates the payload and executes the CRM sync. Expects `name`, `email`, and `message`. Returns `201` on success, `200` on deduplication, and `502` on upstream network failures.
* **`GET /sync-log`** - Returns the latest 50 CRM sync attempts directly from the internal SQLite audit table.
* **`GET /health`** - Basic server health check.

## Setup & Running

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the local automated test suite:**
   ```bash
   pytest tests/test_app.py -v
   ```

3. **Execute the end-to-end Live Demo:**
   Starts the app locally, sends a new request to trigger the live CRM mock endpoint, sends a duplicate to verify the deduplication block, and prints the audit logs.
   ```bash
   bash run_demo.sh
   ```
