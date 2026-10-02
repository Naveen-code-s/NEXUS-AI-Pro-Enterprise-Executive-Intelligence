from rag.vector_store import VectorStore
def retrieve(settings,q,k=6): return VectorStore(settings).search(q,k)
