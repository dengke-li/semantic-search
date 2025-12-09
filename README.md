## Description
This app contains following services:
1. Ingestion Service: Crawls news articles from various news RSS feed sources and stores it in a database for further processing.
2. Embedding worker Service: Fetch from above database and Generates text embeddings using pre-trained models and stores them 
into a vector db for efficient retrieval.
3. Backend Service: Provides RESTful API endpoints to transform input request into vector embeddings and retrieve 
relevant articles from the vector db.
4. Embedding service: A Restful service that generates text embeddings using pre-trained models.
5. Postgres Service: A relational database to store crawled news articles.
6. Vector DB Service: A vector database to store and retrieve text embeddings efficiently.

## start all services
docker-compose up --build

## clean all data and shut down services
docker-compose down -v