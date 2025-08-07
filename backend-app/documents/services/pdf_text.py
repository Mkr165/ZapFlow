import requests, io
from pdfminer.high_level import extract_text

def pdf_url_to_text(url: str, max_pages: int | None = 20) -> str:
    r = requests.get(url, timeout=20)
    r.raise_for_status()
    raw = io.BytesIO(r.content)

    text = extract_text(raw, maxpages=max_pages).strip()
    if not text:
        raise ValueError("Nenhum texto encontrado no PDF (possível PDF-imagem).")

    # limpa quebras duplicadas
    return "\n".join(l.rstrip() for l in text.splitlines() if l.strip())
