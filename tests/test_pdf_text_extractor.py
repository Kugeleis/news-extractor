
import pytest
from unittest.mock import MagicMock, patch
from src.news_extractor import PDFTextExtractor


@patch("pdfplumber.open")
def test_extract_text(mock_pdfplumber_open):
    # Arrange
    mock_page = MagicMock()
    mock_page.extract_text.return_value = "This is a page."
    mock_pdfplumber_open.return_value.__enter__.return_value.pages = [mock_page, mock_page]

    # Act
    extractor = PDFTextExtractor("dummy.pdf")
    texts = extractor.extract_text()

    # Assert
    assert len(texts) == 2
    assert texts[0] == "This is a page."

@patch("pdfplumber.open")
def test_extract_tables(mock_pdfplumber_open):
    # Arrange
    mock_page = MagicMock()
    mock_page.extract_tables.return_value = [
        [["Header 1", "Header 2"], ["Data 1", "Data 2"]]
    ]
    mock_pdfplumber_open.return_value.__enter__.return_value.pages = [mock_page]

    # Act
    extractor = PDFTextExtractor("dummy.pdf")
    tables = extractor.extract_tables()

    # Assert
    assert len(tables) == 1
    assert tables[0]["page"] == 1
    assert len(tables[0]["rows"]) == 1
    assert tables[0]["rows"][0]["Header 1"] == "Data 1"

def test_normalize_table():
    extractor = PDFTextExtractor("dummy.pdf")
    table = [
        ["  Header 1  ", None, "Header 3"],
        ["Data 1", "Data 2", "Data 3"],
        ["Data 4", "Data 5"]
    ]
    norm_table = extractor._normalize_table(table)
    assert len(norm_table[0]) == 3
    assert len(norm_table[2]) == 3
    assert norm_table[0][0] == "Header 1"
    assert norm_table[0][1] == ""
    assert norm_table[2][2] == ""

def test_has_header():
    extractor = PDFTextExtractor("dummy.pdf")
    assert extractor._has_header(["Header 1", "Header 2"]) is True
    assert extractor._has_header(["", ""]) is False
    assert extractor._has_header([]) is False

def test_rows_from_table_with_header():
    extractor = PDFTextExtractor("dummy.pdf")
    table = [
        ["Header 1", "Header 2"],
        ["Data 1", "Data 2"],
        ["Data 3", "Data 4"]
    ]
    rows = extractor._rows_from_table(table)
    assert len(rows) == 2
    assert rows[0]["Header 1"] == "Data 1"
    assert rows[1]["Header 2"] == "Data 4"

def test_rows_from_table_no_header():
    extractor = PDFTextExtractor("dummy.pdf")
    table = [
        ["", ""],
        ["Data 1", "Data 2"],
        ["Data 3", "Data 4"]
    ]
    rows = extractor._rows_from_table(table)
    assert len(rows) == 3
    assert rows[1]["col_1"] == "Data 1"
    assert rows[2]["col_2"] == "Data 4"
