
import pytest
from src.news_extractor import Article, ArticleParser


def test_is_title():
    parser = ArticleParser([])
    assert parser._is_title("THIS IS A TITLE") is True
    assert parser._is_title("This is a Title Case Title") is True
    assert parser._is_title("This is a regular sentence.") is False
    assert parser._is_title("") is False

def test_is_date():
    parser = ArticleParser([])
    assert parser._is_date("Published on Januar 1, 2023") is True
    assert parser._is_date("This line has no date.") is False
    assert parser._is_date("") is False

def test_parse_articles_single():
    text = """
THIS IS A TITLE
Januar 1, 2023
This is the content of the article.
"""
    parser = ArticleParser([text])
    articles = parser.parse_articles()
    assert len(articles) == 1
    assert articles[0].title == "THIS IS A TITLE"
    assert articles[0].date == "Januar 1, 2023"
    assert articles[0].content == "This is the content of the article."

def test_parse_articles_multiple():
    text = """
FIRST TITLE
Januar 1, 2023
Content of the first article.
SECOND TITLE
Januar 2, 2023
Content of the second article.
"""
    parser = ArticleParser([text])
    articles = parser.parse_articles()
    assert len(articles) == 2
    assert articles[0].title == "FIRST TITLE"
    assert articles[1].title == "SECOND TITLE"

def test_parse_articles_no_date():
    text = """
A TITLE WITHOUT A DATE
Content of the article.
"""
    parser = ArticleParser([text])
    articles = parser.parse_articles()
    assert len(articles) == 1
    assert articles[0].title == "A TITLE WITHOUT A DATE"
    assert articles[0].date is None
    assert articles[0].content == "Content of the article."

def test_parse_articles_fallback():
    text = """
This is a title by fallback
This is the content.

Another title
More content.
"""
    parser = ArticleParser([text])
    articles = parser.parse_articles()
    assert len(articles) == 2
    assert articles[0].title == "This is a title by fallback"
    assert articles[1].title == "Another title"

def test_parse_articles_empty_input():
    parser = ArticleParser([""])
    articles = parser.parse_articles()
    assert len(articles) == 0

    parser = ArticleParser([])
    articles = parser.parse_articles()
    assert len(articles) == 0
