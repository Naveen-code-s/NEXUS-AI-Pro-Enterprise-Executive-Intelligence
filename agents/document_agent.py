from rag.pipeline import ask

class DocumentAgent:
    name = "Knowledge"
    def run(self, settings, q):
        answer, sources = ask(settings, q)
        return answer, sources
