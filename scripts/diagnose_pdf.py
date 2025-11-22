from src.news_extractor import PDFTextExtractor

pdf_path = "data/tages-news-2111.pdf"

extractor = PDFTextExtractor(pdf_path)
pages = extractor.extract_text()

for i, p in enumerate(pages):
    if p is None:
        print(f"Page {i+1}: <None>")
    else:
        text = p.strip()
        print(f"Page {i+1}: length={len(text)} | preview={repr(text[:200].replace('\n','\\n'))}")
