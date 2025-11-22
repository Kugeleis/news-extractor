from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
import PyPDF2
import re
import pdfplumber


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

    def extract_tables(self) -> List[Dict]:
        """Detect tables in the PDF and return them as a list of dicts.

        Each table dict contains: `page` (1-based), `table_index` (0-based on page),
        and `rows` which is a list of row-dictionaries (header->value if header found,
        otherwise `col_N` keys).
        Single-responsibility: this method orchestrates page iteration and delegates
        normalization/row conversion to helper methods for readability and testability.
        """
        tables_out: List[Dict] = []
        try:
            with pdfplumber.open(self.filepath) as pdf:
                for i, page in enumerate(pdf.pages):
                    page_tables = self._extract_tables_from_page(page)
                    for t_idx, table in enumerate(page_tables):
                        table_dict = self._table_to_dict(i, t_idx, table)
                        if table_dict:
                            tables_out.append(table_dict)
        except Exception:
            return tables_out

        return tables_out

    def _extract_tables_from_page(self, page) -> List[List[List[str]]]:
        """Return raw table data from a pdfplumber page.

        Kept as a separate method so it can be mocked or extended later.
        """
        try:
            raw = page.extract_tables() or []
        except Exception:
            raw = []
        return raw

    def _table_to_dict(self, page_index: int, table_index: int, table: List[List]) -> Optional[Dict]:
        """Convert a single raw table into the public dict format.

        Handles normalization and conversion to row dictionaries.
        """
        if not table:
            return None

        norm_table = self._normalize_table(table)
        rows = self._rows_from_table(norm_table)
        return {"page": page_index + 1, "table_index": table_index, "rows": rows}

    def _normalize_table(self, table: List[List]) -> List[List[str]]:
        """Normalize raw table cells into strings and pad rows to same length.

        - Strip text cells
        - Convert None -> empty string
        - Ensure each row has the same number of columns by padding with ""
        """
        # convert cells to strings and strip
        converted = [
            [cell.strip() if isinstance(cell, str) else ("" if cell is None else str(cell)) for cell in row]
            for row in table
        ]
        max_cols = max((len(r) for r in converted), default=0)
        for r in converted:
            if len(r) < max_cols:
                r.extend([""] * (max_cols - len(r)))
        return converted

    def _has_header(self, header_row: List[str]) -> bool:
        """Heuristic to decide whether a row is a header.

        Simple rule: if any non-empty string present, treat it as header.
        This can be replaced with more sophisticated checks later.
        """
        return any(bool(cell) for cell in header_row)

    def _rows_from_table(self, norm_table: List[List[str]]) -> List[Dict]:
        """Convert normalized table into list of row dicts.

        - If the first row looks like a header, use it for keys.
        - Otherwise, use generic col_N keys for all rows.
        """
        if not norm_table:
            return []

        max_cols = max(len(r) for r in norm_table)
        header = norm_table[0]
        rows: List[Dict] = []

        if self._has_header(header):
            keys = [h if h else f"col_{idx+1}" for idx, h in enumerate(header)]
            for data_row in norm_table[1:]:
                # ensure row length
                if len(data_row) < max_cols:
                    data_row = data_row + [""] * (max_cols - len(data_row))
                row_dict = { (keys[idx] if idx < len(keys) else f"col_{idx+1}"): data_row[idx] for idx in range(max_cols) }
                rows.append(row_dict)
        else:
            for data_row in norm_table:
                if len(data_row) < max_cols:
                    data_row = data_row + [""] * (max_cols - len(data_row))
                row_dict = {f"col_{j+1}": data_row[j] for j in range(max_cols)}
                rows.append(row_dict)

        return rows


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
        if not text:
            return []

        articles: List[Article] = []
        lines = text.split("\n")
        current_title, current_date, current_content = None, None, []

        for line in lines:
            if self._is_title(line):
                if current_title and current_content:
                    articles.append(
                        Article(
                            title=current_title,
                            date=current_date,
                            content="\n".join(current_content).strip(),
                        )
                    )
                current_title = line.strip()
                current_date = None
                current_content = []
            elif self._is_date(line):
                current_date = line.strip()
            else:
                current_content.append(line)

        if current_title and current_content:
            articles.append(
                Article(
                    title=current_title,
                    date=current_date,
                    content="\n".join(current_content).strip(),
                )
            )

        # If no articles found with heuristics above, try a fallback
        if articles:
            return articles

        # Fallback: split page into blocks separated by blank lines and use
        # first line as title and the rest as content. This catches layouts
        # where titles aren't uppercase or follow different formatting.
        blocks = [b.strip() for b in re.split(r"\n{2,}", text) if b.strip()]
        for block in blocks:
            parts = block.split("\n", 1)
            title = parts[0].strip()
            content = parts[1].strip() if len(parts) > 1 else ""
            articles.append(Article(title=title, date=None, content=content))
        return articles

    def _is_title(self, line: str) -> bool:
        # Heuristic for title detection
        if not line:
            return False
        line = line.strip()
        # Clear uppercase headlines
        if line.isupper() and 5 < len(line) < 100:
            return True

        # Title-case heuristic: most words start with uppercase and line length reasonable
        words = [w for w in line.split() if any(c.isalpha() for c in w)]
        if words and 1 < len(words) <= 12:
            cap_count = sum(1 for w in words if w[0].isupper())
            if cap_count / len(words) >= 0.6 and 5 < len(line) < 120:
                return True

        return False

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
        tables = text_extractor.extract_tables()
        parser = ArticleParser(pages)
        articles = parser.parse_articles()
        return {"articles": [asdict(article) for article in articles], "tables": tables}


# Usage
if __name__ == "__main__":
    extractor = NewsPDFExtractor("data/tages-news-2111.pdf")
    news_data = extractor.extract()
    print(news_data)
