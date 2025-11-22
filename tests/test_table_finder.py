import pandas as pd
import pytest
from src.news_extractor.table_finder import find_tables_containing


@pytest.fixture
def sample_news_data():
    return {
        "tables": [
            pd.DataFrame({"col1": ["Berlin", "Dortmund"], "col2": [20, 30]}),
            [["Berlin", "20"], ["Dortmund", "30"]],
            "This is a string table with Berlin and 20",
            pd.DataFrame({"col1": ["Munich", "Hamburg"], "col2": [40, 50]}),
            [["Munich", "40"], ["Hamburg", "50"]],
        ]
    }


def test_find_tables_containing_single_string(sample_news_data):
    matches = find_tables_containing(sample_news_data, ["Berlin"])
    assert len(matches) == 3
    assert matches[0][0] == 0
    assert matches[1][0] == 1
    assert matches[2][0] == 2


def test_find_tables_containing_multiple_strings(sample_news_data):
    matches = find_tables_containing(sample_news_data, ["Berlin", "20"])
    assert len(matches) == 3
    assert matches[0][0] == 0
    assert matches[1][0] == 1
    assert matches[2][0] == 2


def test_find_tables_containing_case_sensitive(sample_news_data):
    matches = find_tables_containing(sample_news_data, ["berlin"], case_sensitive=True)
    assert len(matches) == 0


def test_find_tables_containing_no_match(sample_news_data):
    matches = find_tables_containing(sample_news_data, ["Stuttgart"])
    assert len(matches) == 0


def test_find_tables_containing_empty_data():
    matches = find_tables_containing({}, ["Berlin"])
    assert len(matches) == 0

    matches = find_tables_containing({"tables": []}, ["Berlin"])
    assert len(matches) == 0


def test_find_tables_containing_empty_search_strings(sample_news_data):
    matches = find_tables_containing(sample_news_data, [])
    assert len(matches) == 0
