FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv (much faster than pip)
RUN pip install uv

# Copy uv files first (for better caching)
COPY api/pyproject.toml api/uv.lock ./

# Export dependencies to requirements format and install to system Python (better for containers)
RUN uv export --no-hashes --format requirements-txt > requirements.txt
RUN uv pip install --system -r requirements.txt

# Copy the API code
COPY api/ .

# Create a non-root user
RUN adduser --disabled-password --gecos '' appuser
RUN chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Start command - now uvicorn is available in system PATH
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
