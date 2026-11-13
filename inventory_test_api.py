import os
import yaml
import pytest
from fastapi.testclient import TestClient

os.environ["INVENTORY_DB_PATH"] = "test_inventory.db"
from src.app import app

@pytest.fixture(autouse=True)
def clean_db():
    if os.path.exists("test_inventory.db"):
        os.remove("test_inventory.db")
    with TestClient(app) as client:
        yield client
    if os.path.exists("test_inventory.db"):
        os.remove("test_inventory.db")

def test_create_product(clean_db):
    res = clean_db.post("/products", json={"sku": "PROD-1", "name": "Widget", "price": 19.99, "quantity": 100})
    assert res.status_code == 201
    data = res.json()
    assert data["sku"] == "PROD-1"
    assert data["name"] == "Widget"
    assert data["price"] == 19.99
    assert data["quantity"] == 100
    assert data["category"] == "general"

def test_duplicate_sku(clean_db):
    payload = {"sku": "PROD-1", "name": "Widget", "price": 19.99, "quantity": 10}
    clean_db.post("/products", json=payload)
    res = clean_db.post("/products", json=payload)
    assert res.status_code == 409

def test_validation_bad_sku_pattern(clean_db):
    res = clean_db.post("/products", json={"sku": "pr", "name": "Widget", "price": 10, "quantity": 1})
    assert res.status_code == 422

def test_validation_negative_price(clean_db):
    res = clean_db.post("/products", json={"sku": "PROD-1", "name": "Widget", "price": -5, "quantity": 1})
    assert res.status_code == 422

def test_validation_negative_quantity(clean_db):
    res = clean_db.post("/products", json={"sku": "PROD-1", "name": "Widget", "price": 10, "quantity": -1})
    assert res.status_code == 422

def test_get_product(clean_db):
    clean_db.post("/products", json={"sku": "PROD-2", "name": "Gadget", "price": 5.0, "quantity": 5})
    res = clean_db.get("/products/PROD-2")
    assert res.status_code == 200
    assert res.json()["name"] == "Gadget"

def test_get_unknown_product(clean_db):
    res = clean_db.get("/products/UNKNOWN")
    assert res.status_code == 404

def test_list_and_filters(clean_db):
    clean_db.post("/products", json={"sku": "PROD-A", "name": "A", "price": 10, "quantity": 10, "category": "toys"})
    clean_db.post("/products", json={"sku": "PROD-B", "name": "B", "price": 20, "quantity": 0, "category": "toys"})
    clean_db.post("/products", json={"sku": "PROD-C", "name": "C", "price": 30, "quantity": 5, "category": "tools"})

    # All products
    res = clean_db.get("/products")
    assert len(res.json()) == 3

    # Category filter
    res = clean_db.get("/products?category=toys")
    assert len(res.json()) == 2

    # In-stock + Category filter
    res = clean_db.get("/products?category=toys&in_stock_only=true")
    data = res.json()
    assert len(data) == 1
    assert data[0]["sku"] == "PROD-A"

def test_update_product(clean_db):
    clean_db.post("/products", json={"sku": "PROD-3", "name": "Old", "price": 10, "quantity": 1})
    res = clean_db.put("/products/PROD-3", json={"name": "New", "price": 15, "quantity": 2, "category": "updated"})
    assert res.status_code == 200
    data = res.json()
    assert data["name"] == "New"
    assert data["price"] == 15.0

def test_update_unknown_product(clean_db):
    res = clean_db.put("/products/NOPE", json={"name": "New", "price": 15, "quantity": 2})
    assert res.status_code == 404

def test_delete_product(clean_db):
    clean_db.post("/products", json={"sku": "PROD-4", "name": "Del", "price": 10, "quantity": 1})
    res_del = clean_db.delete("/products/PROD-4")
    assert res_del.status_code == 204
    
    res_get = clean_db.get("/products/PROD-4")
    assert res_get.status_code == 404

def test_delete_unknown_product(clean_db):
    res = clean_db.delete("/products/NOPE")
    assert res.status_code == 404

def test_health(clean_db):
    assert clean_db.get("/health").status_code == 200

def test_openapi_spec_conformance():
    """Verifies that the live FastAPI routes exactly match the hand-written openapi.yaml"""
    app_schema = app.openapi()
    
    with open("openapi.yaml", "r", encoding="utf-8") as f:
        yaml_schema = yaml.safe_load(f)

    # 1. Verify all paths and methods match
    app_paths = set(app_schema["paths"].keys())
    yaml_paths = set(yaml_schema["paths"].keys())
    assert app_paths == yaml_paths, "API Routes have drifted from the OpenAPI spec!"

    for path in app_paths:
        app_methods = set(app_schema["paths"][path].keys())
        yaml_methods = set(yaml_schema["paths"][path].keys())
        assert app_methods == yaml_methods, f"HTTP Methods for {path} have drifted!"

    # 2. Verify ProductCreate required fields match
    app_required = set(app_schema["components"]["schemas"]["ProductCreate"].get("required", []))
    yaml_required = set(yaml_schema["components"]["schemas"]["ProductCreate"].get("required", []))
    assert app_required == yaml_required, "Product schema validation has drifted!"
