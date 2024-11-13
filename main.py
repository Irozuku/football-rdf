from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from rdflib import Graph
from rdflib.plugins.sparql import prepareQuery

app = FastAPI()

graph = Graph()
graph.parse("football_ontology.ttl", format="turtle")

@app.get("/sparql")
async def sparql_endpoint(query: str):
    try:
        print(query)
        results = graph.query(prepareQuery(query))
        
        return {"results": list(results)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))