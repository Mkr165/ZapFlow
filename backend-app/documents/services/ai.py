# documents/services/ai.py
import re
import requests
from django.conf import settings

STOPWORDS = {
    "de","da","do","das","dos","para","por","com","sem","entre","uma","um","uns","umas",
    "o","a","os","as","e","ou","em","no","na","nos","nas","ao","à","às","aos","que","se"
}

def _mock_analyze(text: str) -> dict:
    txt = (text or "").strip()
    words = re.findall(r"\b[\w-]{4,}\b", txt.lower())
    words = [w for w in words if w not in STOPWORDS]
    # tópicos por frequência
    freq = {}
    for w in words:
        freq[w] = freq.get(w, 0) + 1
    topics = [w for w, _ in sorted(freq.items(), key=lambda kv: (-kv[1], kv[0]))[:5]]

    # extrações simples
    emails = re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", txt)
    money  = re.findall(r"(?:R\$\s?\d[\d\.\,]*)", txt)
    cpf    = re.findall(r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b", txt)
    cnpj   = re.findall(r"\b\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}\b", txt)

    # risco heurístico
    lower = txt.lower()
    risk = 10
    for kw, inc in [
        ("multa", 15), ("exclusividade", 10), ("indenização", 15),
        ("prazo indeterminado", 15), ("renovação automática", 10),
        ("rescisão", -5), ("foro", -5), ("confidencialidade", -5),
    ]:
        if kw in lower:
            risk += inc
    risk = max(0, min(95, risk))

    summary = txt[:220] + ("..." if len(txt) > 220 else "")
    return {
        "summary": summary or "(sem conteúdo informado)",
        "topics": topics,
        "risk_score": risk,
        "extracted": {"emails": emails, "money": money, "cpf": cpf, "cnpj": cnpj},
        "flags": [
            msg for cond, msg in [
                ("rescisão" not in lower, "Possível falta de cláusula de rescisão"),
                ("foro" not in lower, "Possível falta de cláusula de foro"),
                ("confidencialidade" not in lower, "Possível falta de cláusula de confidencialidade"),
            ] if cond
        ],
    }

def _openai_analyze(text: str) -> dict:
    # se a chave faltar, cai pro mock
    if not settings.OPENAI_API_KEY:
        return _mock_analyze(text)

    prompt = (
        "Você é um assistente jurídico. Dado o texto de um contrato, produza um resumo em 2 linhas.\n"
        "Não repita o texto inteiro; foque no essencial.\n\n"
        f"Texto:\n{text}"
    )

    resp = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2,
        },
        timeout=25,
    )
    resp.raise_for_status()
    summary = resp.json()["choices"][0]["message"]["content"].strip()

    # mantém heurísticas locais para tópicos/risco/extrações
    base = _mock_analyze(text)
    base["summary"] = summary[:600]
    # ligeiro ajuste: não deixar risco muito baixo quando há termos críticos
    base["risk_score"] = max(base["risk_score"], 20 if any(k in text.lower() for k in ["multa","indenização"]) else base["risk_score"])
    return base

def analyze_text(text: str) -> dict:
    mode = getattr(settings, "AI_MODE", "mock")
    if mode == "openai":
        return _openai_analyze(text or "")
    return _mock_analyze(text or "")
