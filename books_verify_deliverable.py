import os
import pandas as pd
import pytest

CSV_FILE = "books.csv"

@pytest.fixture(scope="module")
def df():
    assert os.path.exists(CSV_FILE), f"Deliverable missing: {CSV_FILE} was not generated."
    return pd.read_csv(CSV_FILE)

def test_file_has_exactly_1000_rows(df):
    assert len(df) == 1000, f"Acceptance criteria failed: Expected exactly 1000 rows, found {len(df)}."

def test_has_required_columns(df):
    expected_cols = {'title', 'price', 'rating', 'availability', 'category', 'product_url'}
    assert set(df.columns) == expected_cols, f"Validation failed: Columns mismatch. Found {df.columns}"

def test_no_nulls_in_critical_columns(df):
    critical_cols = ['title', 'price', 'rating', 'category']
    for col in critical_cols:
        assert df[col].isnull().sum() == 0, f"Validation failed: '{col}' column contains nulls."
        if pd.api.types.is_string_dtype(df[col]):
            assert df[col].str.strip().eq("").sum() == 0, f"Validation failed: '{col}' column contains empty strings."

def test_price_is_float_and_positive(df):
    assert pd.api.types.is_float_dtype(df['price']), "Validation failed: 'price' is not a float."
    assert (df['price'] > 0).all(), "Validation failed: Found price values <= 0."

def test_rating_is_int_in_range(df):
    assert pd.api.types.is_integer_dtype(df['rating']), "Validation failed: 'rating' is not an integer."
    assert df['rating'].between(1, 5).all(), "Validation failed: 'rating' contains values outside 1-5."

def test_product_url_is_unique(df):
    assert df['product_url'].is_unique, "Validation failed: Duplicate product_urls found."

def test_category_is_populated_and_sums_to_total(df):
    assert df['category'].notnull().sum() == 1000, "Validation failed: Not all rows have a category."
    assert df['category'].str.strip().ne("").all(), "Validation failed: One or more rows have an empty category string."
