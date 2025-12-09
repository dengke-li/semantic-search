## Description
This is backend service which provides RESTful API endpoints to transform 
input request into vector embeddings and retrieve from vector db.

## Example input query
POST /search
{
  "query": "Trouver les top eletromenager chez lidle",
  "limit": 6
}