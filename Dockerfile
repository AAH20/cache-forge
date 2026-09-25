FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml README.md ./
COPY cache_forge/ ./cache_forge/
COPY tests/ ./tests/

RUN pip install --no-cache-dir -e .

ENTRYPOINT ["cache-forge"]
CMD ["benchmark"]
