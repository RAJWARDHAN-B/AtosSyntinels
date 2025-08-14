import argparse
import json
import io
import os
import sys
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import httpx

try:
    import fitz  # PyMuPDF
except Exception:  # pragma: no cover
    fitz = None

try:
    import docx  # python-docx
except Exception:  # pragma: no cover
    docx = None

try:
    import pytesseract
    from PIL import Image
except Exception:  # pragma: no cover
    pytesseract = None
    Image = None


DEFAULT_OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
DEFAULT_LLM_MODEL = os.environ.get("LLM_MODEL", "llama3.1")


@dataclass
class ExtractionResult:
    document_id: str
    clauses: List[Dict]
    summaries: Dict[str, str]
    raw_text_preview: str


def read_pdf_text(input_path: Path, ocr_if_needed: bool = True) -> str:
    if fitz is None:
        raise RuntimeError("PyMuPDF is not installed. Please `pip install pymupdf`. ")

    doc = fitz.open(input_path.as_posix())
    all_text_parts: List[str] = []

    for page_index in range(doc.page_count):
        page = doc.load_page(page_index)
        text = page.get_text("text")
        if text and text.strip():
            all_text_parts.append(text)
            continue

        if ocr_if_needed and Image is not None and pytesseract is not None:
            # Fallback: rasterize the page and OCR
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
            img_bytes = pix.tobytes("png")
            with Image.open(io.BytesIO(img_bytes)) as img:  # type: ignore[attr-defined]
                ocr_text = pytesseract.image_to_string(img)
                if ocr_text and ocr_text.strip():
                    all_text_parts.append(ocr_text)

    return "\n\n".join(all_text_parts).strip()


def read_docx_text(input_path: Path) -> str:
    if docx is None:
        raise RuntimeError("python-docx is not installed. Please `pip install python-docx`. ")
    document = docx.Document(input_path.as_posix())
    paragraphs = [p.text for p in document.paragraphs if p.text and p.text.strip()]
    return "\n".join(paragraphs).strip()


def read_txt_text(input_path: Path) -> str:
    return input_path.read_text(encoding="utf-8", errors="ignore")


def load_document_text(input_path: Path) -> Tuple[str, str]:
    suffix = input_path.suffix.lower()
    if suffix in {".pdf"}:
        return "pdf", read_pdf_text(input_path)
    if suffix in {".docx"}:
        return "docx", read_docx_text(input_path)
    if suffix in {".txt"}:
        return "txt", read_txt_text(input_path)
    raise ValueError(f"Unsupported file type: {suffix}. Use PDF, DOCX, or TXT.")


def truncate_for_prompt(text: str, max_chars: int = 12000) -> str:
    if len(text) <= max_chars:
        return text
    head = text[: max_chars - 1000]
    tail = text[-800 :]
    return head + "\n\n[...truncated...]\n\n" + tail


def call_ollama_chat(model: str, messages: List[Dict[str, str]], base_url: str = DEFAULT_OLLAMA_BASE_URL) -> str:
    url = f"{base_url.rstrip('/')}/api/chat"
    payload = {"model": model, "messages": messages, "stream": False}
    with httpx.Client(timeout=httpx.Timeout(120.0)) as client:
        resp = client.post(url, json=payload)
        resp.raise_for_status()
        data = resp.json()
        content = data.get("message", {}).get("content") or data.get("response")
        if not content:
            raise RuntimeError("No content from Ollama response")
        return content


def extract_clauses_with_llm(full_text: str, model: str, base_url: str) -> List[Dict]:
    system_prompt = (
        "You are a contracts analyst. Extract clauses and map to a standard taxonomy. "
        "Return STRICT JSON with the schema: {\"clauses\":[{\"type\":string,\"text\":string,\"confidence\":number}]} only."
    )
    user_prompt = (
        "Extract clauses from the following contract text. "
        "Use types such as Termination, Indemnity, Confidentiality, Governing Law, etc. "
        "Provide a confidence in [0,1].\n\nTEXT:\n" + truncate_for_prompt(full_text)
    )
    raw = call_ollama_chat(model=model, messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ], base_url=base_url)
    return _parse_json_with_fallback(raw).get("clauses", [])


def generate_summaries_with_llm(full_text: str, model: str, base_url: str) -> Dict[str, str]:
    system_prompt = (
        "You produce succinct summaries for different audiences. "
        "Return STRICT JSON: {\"executive\": string, \"legal\": string, \"procurement\": string}."
    )
    user_prompt = (
        "Create three short summaries (<=120 words each) for executive, legal, and procurement audiences.\n\nTEXT:\n"
        + truncate_for_prompt(full_text)
    )
    raw = call_ollama_chat(model=model, messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ], base_url=base_url)
    data = _parse_json_with_fallback(raw)
    return {
        "executive": data.get("executive", ""),
        "legal": data.get("legal", ""),
        "procurement": data.get("procurement", ""),
    }


def _parse_json_with_fallback(raw: str) -> Dict:
    raw = raw.strip()
    # Try direct JSON
    try:
        return json.loads(raw)
    except Exception:
        pass
    # Try to find first JSON code block
    start = raw.find("{")
    end = raw.rfind("}")
    if start != -1 and end != -1 and end > start:
        snippet = raw[start : end + 1]
        try:
            return json.loads(snippet)
        except Exception:
            pass
    raise ValueError("LLM did not return valid JSON. Raw response:\n" + raw[:1000])


def process_document(input_path: Path, out_dir: Path, model: str, base_url: str) -> ExtractionResult:
    doc_type, text = load_document_text(input_path)
    if not text:
        raise RuntimeError("No text extracted from the input document.")

    clauses = extract_clauses_with_llm(text, model=model, base_url=base_url)
    summaries = generate_summaries_with_llm(text, model=model, base_url=base_url)

    document_id = uuid.uuid4().hex[:12]
    out_dir.mkdir(parents=True, exist_ok=True)
    output_payload = {
        "documentId": document_id,
        "inputFile": str(input_path),
        "documentType": doc_type,
        "clauses": clauses,
        "summary": summaries,
    }
    (out_dir / f"{document_id}.json").write_text(json.dumps(output_payload, ensure_ascii=False, indent=2), encoding="utf-8")

    return ExtractionResult(
        document_id=document_id,
        clauses=clauses,
        summaries=summaries,
        raw_text_preview=text[:1000],
    )


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Process a contract document locally with a local LLM (Ollama).")
    parser.add_argument("--input", required=True, help="Path to input PDF/DOCX/TXT")
    parser.add_argument("--out", required=False, default="output", help="Output directory for JSON (default: output)")
    parser.add_argument("--model", required=False, default=DEFAULT_LLM_MODEL, help=f"LLM model name (default: {DEFAULT_LLM_MODEL})")
    parser.add_argument(
        "--ollama", required=False, default=DEFAULT_OLLAMA_BASE_URL, help=f"Ollama base URL (default: {DEFAULT_OLLAMA_BASE_URL})"
    )
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    input_path = Path(args.input).expanduser().resolve()
    if not input_path.exists():
        print(f"Input not found: {input_path}", file=sys.stderr)
        return 2
    out_dir = Path(args.out).expanduser().resolve()

    try:
        result = process_document(input_path=input_path, out_dir=out_dir, model=args.model, base_url=args.ollama)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(json.dumps({
        "documentId": result.document_id,
        "clausesCount": len(result.clauses),
        "summaryKeys": list(result.summaries.keys()),
        "outputFile": str(out_dir / f"{result.document_id}.json"),
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


