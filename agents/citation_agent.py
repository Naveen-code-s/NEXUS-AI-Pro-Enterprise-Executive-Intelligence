from rag.citations import citations
class CitationAgent:
    name="Citation"
    def run(self,sources): return citations(sources)
