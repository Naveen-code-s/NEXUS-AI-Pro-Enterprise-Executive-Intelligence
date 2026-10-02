from rag.retriever import retrieve
from core.llm import invoke
def ask(settings,q,k=6):
    hits=retrieve(settings,q,k); sources=[]; ctx=[]
    for doc,score in hits:
        m=doc.metadata; sources.append({"source_id":m.get("document_id",m.get("chunk_id","local")),"title":m.get("title") or m.get("filename","Local document"),"source_type":"LOCAL","provider":"Workspace","filename":m.get("filename"),"page":m.get("page"),"abstract":doc.page_content,"relevance":1/(1+max(float(score),0))}); ctx.append(f"[{m.get('filename','unknown')}, p.{m.get('page','N/A')}]\n{doc.page_content}")
    if not hits:return "No local evidence was found.",[]
    prompt="Use only the evidence below. Never invent citations or facts.\nQuestion: "+q+"\nEvidence:\n"+"\n\n".join(ctx)
    answer=invoke(settings,prompt) or "LLM is not configured. Retrieved evidence is shown below. Add GROQ_API_KEY for synthesis."
    return answer,sources
