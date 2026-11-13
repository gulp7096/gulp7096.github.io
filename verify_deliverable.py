import os
import pandas as pd
import pytest

CSV_FILE = "hn_top30.csv"

@pytest.fixture(scope="module")
def df():
    assert os.path.exists(CSV_FILE), f"Deliverable missing: {CSV_FILE} was not generated."
    return pd.read_csv(CSV_FILE)

def test_file_has_exactly_30_rows(df):
    assert len(df) == 30, f"Acceptance criteria failed: Expected exactly 30 rows, found {len(df)}."

def test_no_nulls_in_critical_columns(df):
    assert df['rank'].isnull().sum() == 0, "Validation failed: 'rank' column contains nulls."
    assert df['title'].isnull().sum() == 0, "Validation failed: 'title' column contains nulls."
    assert df['title'].str.strip().eq("").sum() == 0, "Validation failed: 'title' column contains empty strings."

def test_submitter_is_populated_on_all_rows(df):
    # Ensure submitter column exists, has no nulls, and contains no empty strings
    assert 'submitter' in df.columns, "Validation failed: 'submitter' column is missing."
    assert df['submitter'].isnull().sum() == 0, "Validation failed: 'submitter' column contains nulls."
    assert df['submitter'].str.strip().ne("").all(), "Validation failed: One or more rows have an empty submitter."

def test_general_no_empty_values_except_domain(df):
    # Domain can legitimately be empty for Ask HN / Show HN text posts, but rank, title, points, submitter, and comment_count must be populated
    critical_cols = ['rank', 'title', 'points', 'submitter', 'comment_count']
    for col in critical_cols:
        if pd.api.types.is_string_dtype(df[col]):
            assert df[col].str.strip().ne("").all(), f"Validation failed: Column '{col}' contains blank values."
        else:
            assert df[col].notnull().all(), f"Validation failed: Column '{col}' contains null values."

def test_schema_types_are_correct(df):
    assert pd.api.types.is_integer_dtype(df['rank']), "'rank' failed integer type check."
    assert pd.api.types.is_integer_dtype(df['points']), "'points' failed integer type check."
    assert pd.api.types.is_integer_dtype(df['comment_count']), "'comment_count' failed integer type check."

def test_domain_is_string(df):
    # Missing domains in CSV are often parsed as NaN by pandas; we fill with "" to verify schema intent
    df['domain'] = df['domain'].fillna("")
    assert pd.api.types.is_string_dtype(df['domain']), "'domain' failed string type check."
