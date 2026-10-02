from pathlib import Path
import re
def clean(s): return re.sub(r"[ \t]+"," ",s.replace("\x00"," ")).strip()
def load_document(path):
    ext=Path(path).suffix.lower()
    if ext==".pdf":
        import fitz; d=fitz.open(path); return [{"page":i+1,"text":clean(p.get_text())} for i,p in enumerate(d)]
    if ext==".docx":
        from docx import Document; d=Document(path); return [{"page":1,"text":clean("\n".join(p.text for p in d.paragraphs))}]
    return [{"page":1,"text":clean(Path(path).read_text(encoding="utf-8",errors="ignore"))}]
