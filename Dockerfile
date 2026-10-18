FROM python:3.12-slim

WORKDIR /app

# Prevent Python from writing pyc files and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy package definition and source code
COPY pyproject.toml .
COPY src/ ./src/

# Install production dependencies directly from pyproject.toml
RUN pip install --no-cache-dir .

# Copy remaining project files
COPY . .

# Run bot as modular package
CMD ["python", "-m", "src"]
