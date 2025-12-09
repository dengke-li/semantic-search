FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml /app/
RUN pip install --no-cache-dir poetry && \
poetry config virtualenvs.create false
COPY . /app
RUN poetry install
EXPOSE 8080
CMD ["poetry", "run", "python", "src/embedding_service/api.py"]