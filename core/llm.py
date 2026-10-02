from core.config import Settings
def invoke(settings:Settings,prompt:str):
    if not settings.groq_api_key: return None
    try:
        from langchain_groq import ChatGroq
        r=ChatGroq(api_key=settings.groq_api_key,model=settings.llm_model,temperature=0.1).invoke(prompt)
        return getattr(r,"content",str(r))
    except Exception: return None
