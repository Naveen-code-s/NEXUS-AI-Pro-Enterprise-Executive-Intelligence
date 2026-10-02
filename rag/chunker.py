def chunk_pages(pages,size=900,overlap=120):
    out=[]
    for p in pages:
        text=p.get("text",""); start=0; i=0
        while start<len(text):
            end=min(len(text),start+size); out.append({"text":text[start:end],"metadata":{"page":p.get("page",1),"chunk_id":f"{p.get('page',1)}-{i}"}})
            if end>=len(text): break
            start=max(0,end-overlap); i+=1
    return out
