from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from rdflib import Graph
from rdflib.plugins.sparql import prepareQuery

app = FastAPI()

graph = Graph()
graph.parse("football_ontology.ttl", format="turtle")

class Query(BaseModel):
    query: str

@app.post("/sparql")
async def sparql_endpoint(query: Query):
    try:
        results = graph.query(prepareQuery(query.query))
        
        return {"results": list(results)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))