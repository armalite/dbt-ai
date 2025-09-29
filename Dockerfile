# Multi-stage build for dbt-ai MCP Server
FROM python:3.10-slim as builder

# Install system dependencies for building
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy project files
COPY pyproject.toml .
COPY README.md .
COPY MANIFEST.in .
COPY dbt_ai/ ./dbt_ai/

# Install the package and dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -e .

# Production stage
FROM python:3.10-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash dbtai

# Set working directory
WORKDIR /app

# Copy installed packages from builder stage
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /app /app

# Change ownership to non-root user
RUN chown -R dbtai:dbtai /app

# Switch to non-root user
USER dbtai

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Expose MCP server port
EXPOSE 8080

# Health check for the MCP server
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8080/health', timeout=5)" || exit 1

# Default command - start hostable MCP server
# Users can mount their dbt project at /dbt-project
CMD ["data-product-hub", "serve", "-f", "/dbt-project", "--mcp-host", "0.0.0.0", "--mcp-port", "8080"]
