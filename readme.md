# Football RDF Project

This project aims to create and manage RDF (Resource Description Framework) data for football (soccer) statistics and information. The RDF data can be used for various applications, including data analysis, visualization, and integration with other datasets.

## Overview

This project consists of three main components:

1. **generate_rdf.py**: This script is responsible for generating the RDF graph from CSV files.
2. **query.py**: This script contains various SPARQL queries to interact with the RDF graph.
3. **main.py**: This script serves as a FastAPI endpoint to provide an API interface for interacting with the RDF graph and executing SPARQL queries.

## Files

### generate_rdf.py
- **Description**: Generates the RDF graph from the provided CSV files.

### query.py
- **Description**: Contains SPARQL queries to interact with the RDF graph.

### main.py
- **Description**: FastAPI endpoint to provide an API interface for interacting with the RDF graph and executing SPARQL queries.

## Usage

1. **Generating RDF Graph**:
  - Run `generate_rdf.py` to generate the RDF graph from the CSV files.

2. **Executing SPARQL Queries**:
  - Use the functions in `query.py` to execute SPARQL queries on the RDF graph.

3. **API Endpoint**:
  - Start the FastAPI server by running `main.py` to expose the API endpoints for interacting with the RDF graph and executing SPARQL queries.

## Requirements

- Python 3.x
- FastAPI
- RDFLib
- Other dependencies as specified in `requirements.txt`

## Installation

1. Clone the repository.
2. Install the required dependencies using `pip install -r requirements.txt`.

## Running the Project

1. Generate the RDF graph:
  ```sh
  python generate_rdf.py
  ```
2. Start the FastAPI server:
  ```sh
  uvicorn main:app --reload
  ```

## API Endpoints

- **GET /sparql**: Endpoint to execute SPARQL queries.
