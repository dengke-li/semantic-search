FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml /app/
RUN pip install --no-cache-dir poetry && \
poetry config virtualenvs.create false
COPY . /app
RUN poetry install

CMD ["poetry", "run", "python", "src/embedder/worker.py"]