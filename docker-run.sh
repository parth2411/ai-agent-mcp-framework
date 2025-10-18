#!/bin/bash

# docker-run.sh - Helper script to build and run the Docker container
# Usage: ./docker-run.sh [problem_directory]
# Example: ./docker-run.sh problems/001

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

IMAGE_NAME="reservation-agent"
PROBLEM_DIR="${1:-problems/001}"

echo -e "${BLUE}Building Docker image...${NC}"
docker build -t "$IMAGE_NAME" .

echo -e "${GREEN}Running test with problem directory: $PROBLEM_DIR${NC}"
docker run --rm -it "$IMAGE_NAME" ./run_test.sh "$PROBLEM_DIR" 