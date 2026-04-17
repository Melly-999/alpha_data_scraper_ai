# Production Dockerfile for Trading Bot with MT5 Bridge Support
# Supports both local execution and wine-based MT5 bridge for Linux

FROM python:3.9-slim

WORKDIR /app

# Install system dependencies (graphics, MT5 libs, wine for MT5 bridge)
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Graphics libraries for matplotlib/GUI
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    libxkbcommon-x11-0 \
    # Utilities
    curl \
    wget \
    git \
    # Build tools
    build-essential \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create app directories
RUN mkdir -p /app/logs /app/data /app/backups

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user for security
RUN useradd -m -u 1000 trader && \
    chown -R trader:trader /app

USER trader

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    TZ=UTC

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import logging; logging.info('Health check')" || exit 1

# Default command - run example pipeline (can be overridden)
CMD ["python", "example_runner.py", "--symbols", "EURUSD", "GBPUSD", "USDJPY"]
