from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
import PyPDF2


@dataclass
class Article:
    title: str
    date: Optional[str]
    content: str


class PDFTextExtractor:
    def __init__(self, filepath: str):
        self.filepath = filepath

    def extract_text(self) -> List[str]:
        texts = []
        with open(self.filepath, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                texts.append(page.extract_text())
        return texts


class ArticleParser:
    def __init__(self, text_pages: List[str]):
        self.text_pages = text_pages

    def parse_articles(self) -> List[Article]:
        articles = []
        for text in self.text_pages:
            articles.extend(self._parse_page(text))
        return articles

    def _parse_page(self, text: str) -> List[Article]:
        # Example split - adjust splitting logic for your PDF format
        articles = []
        lines = text.split("\n")
        current_title, current_date, current_content = None, None, []

        for line in lines:
            if self._is_title(line):
                if current_title and current_content:
                    articles.append(
                        Article(
                            title=current_title,
                            date=current_date,
                            content="\n".join(current_content),
                        )
                    )
                current_title = line
                current_date = None
                current_content = []
            elif self._is_date(line):
                current_date = line
            else:
                current_content.append(line)
        if current_title and current_content:
            articles.append(
                Article(
                    title=current_title,
                    date=current_date,
                    content="\n".join(current_content),
                )
            )
        return articles

    def _is_title(self, line: str) -> bool:
        # Heuristic for title detection
        return line.isupper() and 5 < len(line) < 100

    def _is_date(self, line: str) -> bool:
        # Very simple date pattern detection, adapt as needed
        return any(
            month in line
            for month in [
                "Januar",
                "Februar",
                "März",
                "April",
                "Mai",
                "Juni",
                "Juli",
                "August",
                "September",
                "Oktober",
                "November",
                "Dezember",
            ]
        )


class NewsPDFExtractor:
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path

    def extract(self) -> Dict:
        text_extractor = PDFTextExtractor(self.pdf_path)
        pages = text_extractor.extract_text()
        parser = ArticleParser(pages)
        articles = parser.parse_articles()
        return {"articles": [asdict(article) for article in articles]}


# Usage
if __name__ == "__main__":
    extractor = NewsPDFExtractor("data/tages-news-2111.pdf")
    news_data = extractor.extract()
    print(news_data)
