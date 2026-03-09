FROM python:3.13-slim

WORKDIR /app

# Install system deps for pymupdf and other native packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Copy all source before install (needed for non-editable build)
COPY pyproject.toml uv.lock ./
COPY app/ app/

# Install uv for fast dependency resolution, then install deps
RUN pip install --no-cache-dir uv && \
    uv pip install --system "."

# Create uploads directory
RUN mkdir -p uploads

EXPOSE 8000

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port 8000"]
