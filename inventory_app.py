import os
import sqlite3
from contextlib import asynccontextmanager
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Query, Path, Response
from pydantic import BaseModel, Field

DB_PATH = os.getenv("INVENTORY_DB_PATH", "inventory.db")

@asynccontextmanager
async def lifespan(app: FastAPI):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS products (
                sku TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                price REAL NOT NULL,
                quantity INTEGER NOT NULL,
                category TEXT DEFAULT 'general',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
    yield

app = FastAPI(lifespan=lifespan, title="Inventory API", version="1.0.0")

class ProductCreate(BaseModel):
    sku: str = Field(..., pattern=r"^[A-Z0-9-]{3,20}$", description="Unique product SKU")
    name: str = Field(..., min_length=1, description="Product name")
    price: float = Field(..., gt=0, description="Price must be greater than 0")
    quantity: int = Field(..., ge=0, description="Quantity cannot be negative")
    category: str = Field(default="general", description="Product category")

class ProductUpdate(BaseModel):
    name: str = Field(..., min_length=1)
    price: float = Field(..., gt=0)
    quantity: int = Field(..., ge=0)
    category: str = Field(default="general")

class ProductOut(ProductCreate):
    pass

@app.post("/products", status_code=201, response_model=ProductOut)
def create_product(product: ProductCreate):
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        try:
            conn.execute(
                "INSERT INTO products (sku, name, price, quantity, category) VALUES (?, ?, ?, ?, ?)",
                (product.sku, product.name, product.price, product.quantity, product.category)
            )
        except sqlite3.IntegrityError:
            raise HTTPException(status_code=409, detail="SKU already exists")
    return product

@app.get("/products", response_model=List[ProductOut])
def list_products(
    category: Optional[str] = None,
    in_stock_only: bool = Query(default=False)
):
    query = "SELECT sku, name, price, quantity, category FROM products WHERE 1=1"
    params = []
    if category:
        query += " AND category = ?"
        params.append(category)
    if in_stock_only:
        query += " AND quantity > 0"
        
    query += " ORDER BY created_at DESC"
    
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

@app.get("/products/{sku}", response_model=ProductOut)
def get_product(sku: str = Path(...)):
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute("SELECT sku, name, price, quantity, category FROM products WHERE sku = ?", (sku,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Product not found")
        return dict(row)

@app.put("/products/{sku}", response_model=ProductOut)
def update_product(product: ProductUpdate, sku: str = Path(...)):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute("SELECT sku FROM products WHERE sku = ?", (sku,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Product not found")
            
        conn.execute(
            "UPDATE products SET name = ?, price = ?, quantity = ?, category = ? WHERE sku = ?",
            (product.name, product.price, product.quantity, product.category, sku)
        )
    return {**product.model_dump(), "sku": sku}

@app.delete("/products/{sku}", status_code=204)
def delete_product(sku: str = Path(...)):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute("SELECT sku FROM products WHERE sku = ?", (sku,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Product not found")
            
        conn.execute("DELETE FROM products WHERE sku = ?", (sku,))
    return Response(status_code=204)

@app.get("/health")
def health():
    return {"status": "ok"}
