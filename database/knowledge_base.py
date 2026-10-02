from pathlib import Path
import uuid
from database.models import Document,Dataset
from rag.loader import load_document
from rag.chunker import chunk_pages
from rag.vector_store import VectorStore
from utils.files import checksum,safe_name
class KnowledgeBase:
    def __init__(self,db,settings): self.db=db; self.settings=settings; self.vector=VectorStore(settings); Path(settings.upload_dir).mkdir(parents=True,exist_ok=True)
    def ingest(self,name,data):
        name=safe_name(name); ext=Path(name).suffix.lower()
        if ext not in {".pdf",".docx",".txt",".csv",".xlsx"}: raise ValueError("Unsupported file type")
        h=checksum(data)
        if self.db.duplicate(h): return {"status":"duplicate","filename":name}
        path=Path(self.settings.upload_dir)/(uuid.uuid4().hex+"_"+name); path.write_bytes(data)
        if ext in {".csv",".xlsx"}:
            import pandas as pd
            df=pd.read_csv(path) if ext==".csv" else pd.read_excel(path)
            self.db.add(Dataset(id=uuid.uuid4().hex,filename=name,rows=len(df),columns=len(df.columns),path=str(path)))
            return {"status":"dataset","filename":name,"rows":len(df),"columns":len(df.columns),"path":str(path)}
        pages=load_document(path); chunks=chunk_pages(pages,self.settings.chunk_size,self.settings.chunk_overlap); did=uuid.uuid4().hex
        self.vector.add([{**c,"metadata":{**c["metadata"],"document_id":did,"filename":name,"source_type":"LOCAL","title":Path(name).stem}} for c in chunks])
        self.db.add(Document(id=did,filename=name,document_type=ext[1:],source="workspace",page_count=len(pages),chunk_count=len(chunks),checksum=h))
        return {"status":"indexed","filename":name,"pages":len(pages),"chunks":len(chunks)}
