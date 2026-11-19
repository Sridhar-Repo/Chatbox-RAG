import re


def chunk_text(text: str, size: int = 800, overlap: int = 100) -> list[str]:
    """Pack paragraphs into ~size-char chunks, with a little overlap between neighbours.

    Paragraphs are the natural unit of meaning, so we only cut mid-paragraph
    when one paragraph alone is longer than `size`.
    """
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]

    chunks: list[str] = []
    current = ""
    for para in paragraphs:
        while len(para) > size:  # one huge paragraph: hard split
            if current:
                chunks.append(current)
                current = ""
            chunks.append(para[:size])
            para = para[size - overlap:]
        if len(current) + len(para) + 2 <= size:
            current = f"{current}\n\n{para}".strip()
        else:
            tail = current[-overlap:] if current else ""
            if current:
                chunks.append(current)
            current = f"{tail} {para}".strip()
    if current:
        chunks.append(current)
    return chunks
