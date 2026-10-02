from rag.retriever import retrieve
def search(settings,q,k=6):
    out=[]
    for d,score in retrieve(settings,q,k):
        m=d.metadata; out.append({"source_id":m.get("document_id",m.get("chunk_id")),"title":m.get("title") or m.get("filename","Local document"),"source_type":"LOCAL","provider":"Workspace","filename":m.get("filename"),"page":m.get("page"),"abstract":d.page_content,"relevance":1/(1+max(float(score),0))})
    return out
