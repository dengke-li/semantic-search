FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml /app/
RUN pip install --no-cache-dir poetry && \
poetry config virtualenvs.create false
COPY . /app
RUN poetry install
EXPOSE 8000
CMD ["poetry", "run", "python", "src/app/api.py"]
#CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]