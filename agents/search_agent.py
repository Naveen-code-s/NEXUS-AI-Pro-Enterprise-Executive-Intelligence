from search.global_search import search_global
class SearchAgent:
    name="Search"
    def run(self,settings,q): return search_global(settings,q)
