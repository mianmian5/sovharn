FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml README.md ./
COPY sovharn/ ./sovharn/
COPY data/ ./data/
COPY frontend/ ./frontend/
RUN pip install --no-cache-dir -e .
EXPOSE 8080
CMD ["sovharn"]
