# Use Python 3.10 as base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    bash \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

# Copy dependency files first for better Docker layer caching
COPY pyproject.toml uv.lock README.md ./

# Install Python dependencies
RUN uv sync --frozen

# Copy the entire project
COPY . .

# Make run_test.sh executable
RUN chmod +x run_test.sh

# Set environment variables
ENV PYTHONPATH=/app
ENV UV_PYTHON_PREFERENCE=only-system

# Create results directory
RUN mkdir -p results

# Set default command to run the test script
# Users can override with: docker run <image> problems/002
CMD ["./run_test.sh", "problems/001"] 