from functools import lru_cache
@lru_cache(maxsize=2)
def embeddings(model):
    from langchain_huggingface import HuggingFaceEmbeddings
    return HuggingFaceEmbeddings(model_name=model)
