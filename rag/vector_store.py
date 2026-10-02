from pathlib import Path
from core.embeddings import embeddings
class VectorStore:
    def __init__(self,settings): self.settings=settings; self.path=Path(settings.faiss_path); self.path.mkdir(parents=True,exist_ok=True); self.db=None
    def _load(self):
        if self.db is not None:return self.db
        if not (self.path/"index.faiss").exists():return None
        from langchain_community.vectorstores import FAISS
        self.db=FAISS.load_local(str(self.path),embeddings(self.settings.embedding_model),allow_dangerous_deserialization=True); return self.db
    def add(self,items):
        if not items:return
        from langchain_community.vectorstores import FAISS
        new=FAISS.from_texts([x["text"] for x in items],embeddings(self.settings.embedding_model),metadatas=[x["metadata"] for x in items]); old=self._load()
        if old: old.merge_from(new); self.db=old
        else:self.db=new
        self.db.save_local(str(self.path))
    def search(self,q,k=6):
        db=self._load(); return [] if db is None else db.similarity_search_with_score(q,k=k)
