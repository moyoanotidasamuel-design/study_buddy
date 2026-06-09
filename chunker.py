from loader import load_pdf

def chunk_pages(pages, chunk_size=500, overlap=50):
    chunks = []

    for page in pages:
        text = page["text"].strip()
        words = text.split()

        start = 0
        while start < len(words):
            end = start + chunk_size
            chunk_text = " ".join(words[start:end])

            chunks.append({
                "text": chunk_text,
                "page": page["page"],
                "chunk_index": len(chunks)
            })

            start += chunk_size - overlap  # overlap keeps context between chunks

    return chunks


if __name__ == "__main__":
    pages = load_pdf("The Public History of Westeros Brethorst.pdf")
    chunks = chunk_pages(pages)

    print(f"Total chunks created: {len(chunks)}")
    print(f"\n--- Sample chunk ---")
    print(f"Page: {chunks[0]['page']}")
    print(f"Text: {chunks[0]['text'][:300]}")