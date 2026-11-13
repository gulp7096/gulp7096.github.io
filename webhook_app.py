import os
import sqlite3
from contextlib import asynccontextmanager
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr, Field

DB_PATH = os.getenv("SYNC_DB_PATH", "sync-log.db")
CRM_URL = "https://jsonplaceholder.typicode.com/users"

@asynccontextmanager
async def lifespan(app: FastAPI):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                phone TEXT,
                message TEXT NOT NULL,
                source TEXT DEFAULT 'website',
                crm_id TEXT,
                status TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
    yield

app = FastAPI(lifespan=lifespan)

class ContactPayload(BaseModel):
    name: str = Field(..., min_length=1)
    email: EmailStr
    phone: str | None = None
    message: str = Field(..., min_length=1)
    source: str = "website"

@app.post("/webhooks/contact", status_code=201)
async def handle_contact(payload: ContactPayload):
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        
        # 1. Duplicate check
        cursor = conn.execute("SELECT id FROM contacts WHERE email = ? AND status = 'synced'", (payload.email,))
        row = cursor.fetchone()
        if row:
            return JSONResponse(
                status_code=200, 
                content={"status": "duplicate", "contact_id": row["id"]}
            )

        # 2. Forward to CRM
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(CRM_URL, json=payload.model_dump())
                resp.raise_for_status()
                crm_data = resp.json()
                crm_id = str(crm_data.get("id"))
                
            # 3. Log success
            cursor = conn.execute("""
                INSERT INTO contacts (name, email, phone, message, source, crm_id, status)
                VALUES (?, ?, ?, ?, ?, ?, 'synced')
            """, (payload.name, payload.email, payload.phone, payload.message, payload.source, crm_id))
            
            return {"status": "synced", "crm_id": crm_id, "contact_id": cursor.lastrowid}
            
        except httpx.HTTPError as e:
            # 4. Log downstream failure
            cursor = conn.execute("""
                INSERT INTO contacts (name, email, phone, message, source, status)
                VALUES (?, ?, ?, ?, ?, 'failed')
            """, (payload.name, payload.email, payload.phone, payload.message, payload.source))
            # CLANCY FIX: commit before raising — without this, the
            # HTTPException unwinds the `with` block and sqlite rolls
            # the failed row back, so the failure is never logged.
            conn.commit()

            raise HTTPException(
                status_code=502, 
                detail={"status": "failed", "detail": f"Downstream CRM error: {str(e)}"}
            )

@app.get("/sync-log")
def get_sync_log():
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute("SELECT * FROM contacts ORDER BY created_at DESC, id DESC LIMIT 50")
        return [dict(row) for row in cursor.fetchall()]

@app.get("/health")
def health():
    return {"status": "ok"}
