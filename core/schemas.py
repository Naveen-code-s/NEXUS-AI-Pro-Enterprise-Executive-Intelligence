from pydantic import BaseModel
class Source(BaseModel):
    source_id:str; title:str; source_type:str; provider:str="Unknown"; url:str|None=None; doi:str|None=None
    authors:list[str]=[]; year:int|None=None; abstract:str|None=None; page:int|None=None; filename:str|None=None
    relevance:float|None=None; citation_count:int|None=None
