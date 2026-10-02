from pathlib import Path
from sqlalchemy import create_engine,select,func
from sqlalchemy.orm import Session
from database.models import Base,Document,SearchRecord,Dataset,Report
class Database:
    def __init__(self,url):
        if url.startswith("sqlite:///"): Path(url[10:]).parent.mkdir(parents=True,exist_ok=True)
        self.engine=create_engine(url); Base.metadata.create_all(self.engine)
    def add(self,obj):
        with Session(self.engine) as s: s.add(obj); s.commit(); s.refresh(obj); return obj
    def duplicate(self,checksum):
        with Session(self.engine) as s: return s.scalar(select(Document).where(Document.checksum==checksum))
    def documents(self):
        with Session(self.engine) as s: return list(s.scalars(select(Document).order_by(Document.created_at.desc())))
    def datasets(self):
        with Session(self.engine) as s: return list(s.scalars(select(Dataset).order_by(Dataset.created_at.desc())))
    def counts(self):
        with Session(self.engine) as s: return {"documents":s.scalar(select(func.count(Document.id))) or 0,"pages":s.scalar(select(func.coalesce(func.sum(Document.page_count),0))) or 0,"chunks":s.scalar(select(func.coalesce(func.sum(Document.chunk_count),0))) or 0,"searches":s.scalar(select(func.count(SearchRecord.id))) or 0,"datasets":s.scalar(select(func.count(Dataset.id))) or 0,"reports":s.scalar(select(func.count(Report.id))) or 0}
