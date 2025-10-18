#!/bin/bash

# run_test.sh - Test runner script for reservation agent
# Usage: ./run_test.sh <problem_directory>
# Example: ./run_test.sh problems/001

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if problem directory argument is provided
if [ $# -eq 0 ]; then
    print_error "Usage: $0 <problem_directory>"
    print_error "Example: $0 problems/001"
    exit 1
fi

PROBLEM_DIR="$1"

# Validate problem directory exists
if [ ! -d "$PROBLEM_DIR" ]; then
    print_error "Problem directory '$PROBLEM_DIR' does not exist"
    exit 1
fi

# Validate required files exist in problem directory
USER_PROMPT_FILE="$PROBLEM_DIR/user_prompt.txt"
PROBLEM_DATA_DIR="$PROBLEM_DIR/data"

if [ ! -f "$USER_PROMPT_FILE" ]; then
    print_error "User prompt file '$USER_PROMPT_FILE' does not exist"
    exit 1
fi

if [ ! -d "$PROBLEM_DATA_DIR" ]; then
    print_error "Data directory '$PROBLEM_DATA_DIR' does not exist"
    exit 1
fi

# Validate system prompt exists
SYSTEM_PROMPT_FILE="prompts/system_prompt.txt"
if [ ! -f "$SYSTEM_PROMPT_FILE" ]; then
    print_error "System prompt file '$SYSTEM_PROMPT_FILE' does not exist"
    exit 1
fi

# Create results directory if it doesn't exist
RESULTS_ROOT="results"
if [ ! -d "$RESULTS_ROOT" ]; then
    mkdir -p "$RESULTS_ROOT"
    print_status "Created results directory: $RESULTS_ROOT"
fi

# Generate timestamp for results directory
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
RESULTS_DIR="$RESULTS_ROOT/$TIMESTAMP"

# Create timestamped results directory
mkdir -p "$RESULTS_DIR"
print_status "Created timestamped results directory: $RESULTS_DIR"

# Copy data from problem directory to results directory
print_status "Copying data from '$PROBLEM_DATA_DIR' to '$RESULTS_DIR'..."
cp -r "$PROBLEM_DATA_DIR"/* "$RESULTS_DIR/"

# Verify data was copied
if [ ! -f "$RESULTS_DIR/reservations.json" ]; then
    print_warning "Expected reservations.json file not found in copied data"
fi

print_success "Data copied successfully to $RESULTS_DIR"

# Display test information
echo
echo "========================================="
echo "           TEST EXECUTION"
echo "========================================="
echo "Problem Directory: $PROBLEM_DIR"
echo "Results Directory: $RESULTS_DIR"
echo "System Prompt: $SYSTEM_PROMPT_FILE"
echo "User Prompt: $USER_PROMPT_FILE"
echo "Data Directory: $RESULTS_DIR"
echo "========================================="
echo

# Run the agent with the specified parameters
print_status "Running agent..."
echo

# Execute the agent command
uv run python agent.py \
    --system-prompt "$SYSTEM_PROMPT_FILE" \
    --user-prompt "$USER_PROMPT_FILE" \
    --data-dir "$RESULTS_DIR"

AGENT_EXIT_CODE=$?

echo
echo "========================================="
echo "           VALIDATION"
echo "========================================="

# Check if check_result.py exists in the problem directory
CHECK_RESULT_SCRIPT="$PROBLEM_DIR/check_result.py"
if [ -f "$CHECK_RESULT_SCRIPT" ]; then
    print_status "Running validation script..."
    echo
    
    # Run the check_result.py script from the problem directory
    # Get absolute path to results directory before changing directories
    RESULTS_ABS_PATH="$(pwd)/$RESULTS_DIR"
    cd "$PROBLEM_DIR"
    uv run python check_result.py "$RESULTS_ABS_PATH"
    CHECK_EXIT_CODE=$?
    
    # Check if results.json was created and display its content
    if [ -f "$RESULTS_ABS_PATH/results.json" ]; then
        echo
        # Use custom table printer for better formatting
        uv run python "../../print_results.py" "$RESULTS_ABS_PATH/results.json"
    fi
    
    cd - > /dev/null
    
    echo
    if [ $CHECK_EXIT_CODE -eq 0 ]; then
        print_success "Validation completed successfully"
    else
        print_error "Validation failed with exit code: $CHECK_EXIT_CODE"
    fi
else
    print_warning "Validation script '$CHECK_RESULT_SCRIPT' not found - skipping validation"
fi

echo
echo "========================================="
echo "           TEST RESULTS"
echo "========================================="

if [ $AGENT_EXIT_CODE -eq 0 ]; then
    print_success "Agent execution completed successfully"
    print_success "Results saved in: $RESULTS_DIR"
else
    print_error "Agent execution failed with exit code: $AGENT_EXIT_CODE"
    print_error "Check the output above for error details"
fi

echo "Test timestamp: $TIMESTAMP"
echo "========================================="

exit $AGENT_EXIT_CODE 