from search.global_search import search_global
class ResearchAgent:
    name="Research"
    def run(self,settings,q): return search_global(settings,q,False,True)
