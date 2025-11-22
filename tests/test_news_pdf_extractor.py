
import pytest
from unittest.mock import MagicMock, patch
from src.news_extractor import NewsPDFExtractor, Article


@patch("src.news_extractor.PDFTextExtractor")
def test_extract(mock_pdf_text_extractor):
    # Arrange
    mock_pdf_text_extractor.return_value.extract_text.return_value = [
        """
ARTICLE 1 TITLE
Januar 1, 2023
Content for article 1.
""",
        """
ARTICLE 2 TITLE
Januar 2, 2023
Content for article 2.
"""
    ]
    mock_pdf_text_extractor.return_value.extract_tables.return_value = [
        {"page": 1, "table_index": 0, "rows": [{"Header": "Value"}]}
    ]

    # Act
    extractor = NewsPDFExtractor("dummy.pdf")
    data = extractor.extract()

    # Assert
    assert len(data["articles"]) == 2
    assert len(data["tables"]) == 1
    assert data["articles"][0]["title"] == "ARTICLE 1 TITLE"
    assert data["tables"][0]["rows"][0]["Header"] == "Value"
