import fitz  # PyMuPDF


def load_pdf(filepath):
    doc = fitz.open(filepath)
    print(doc)
    pages = []

    for page_num, page in enumerate(doc):
        text = page.get_text()
        if text.strip():  # skip blank pages
            pages.append({
                "page": page_num + 1,
                "text": text
            })

    doc.close()
    return pages


if __name__ == "__main__":
    pages = load_pdf("The Public History of Westeros Brethorst.pdf")

    for p in pages:
        print(f"\n--- Page {p['page']} ---")
        print(p['text'][:300])  # print first 300 chars per page

    print(f"\nTotal pages loaded: {len(pages)}")
