#!/usr/bin/env python3
"""
Pretty print validation results in table format.
Usage: python print_results.py [results.json]
"""

import json
import sys
from pathlib import Path


def print_colored(text, color_code):
    """Print text with color."""
    print(f"\033[{color_code}m{text}\033[0m")


def print_table(results):
    """Print results in a nice table format."""
    if not results:
        print("No results found.")
        return
    
    # Calculate column widths
    max_name_width = max(len(result['name']) for result in results)
    max_comment_width = max(len(result.get('comment', '')) for result in results)
    
    # Minimum widths
    name_width = max(max_name_width, 20)
    status_width = 8
    comment_width = max(max_comment_width, 20) if max_comment_width > 0 else 0
    
    # Header
    print_colored("=" * 80, "1;34")  # Bold blue
    print_colored("                        VALIDATION RESULTS", "1;34")
    print_colored("=" * 80, "1;34")
    
    # Table header
    header = f"{'TEST NAME':<{name_width}} {'STATUS':<{status_width}}"
    if comment_width > 0:
        header += f" {'COMMENT':<{comment_width}}"
    print_colored(header, "1;37")  # Bold white
    
    # Separator line
    separator = "-" * name_width + " " + "-" * status_width
    if comment_width > 0:
        separator += " " + "-" * comment_width
    print_colored(separator, "0;37")  # Gray
    
    # Results rows
    passed_count = 0
    for result in results:
        name = result['name']
        passed = result['passed']
        comment = result.get('comment', '')
        
        # Format status
        if passed:
            status = "✓ PASS"
            status_color = "1;32"  # Bold green
            passed_count += 1
        else:
            status = "✗ FAIL"
            status_color = "1;31"  # Bold red
        
        # Print row
        row = f"{name:<{name_width}} "
        print(row, end="")
        print_colored(f"{status:<{status_width}}", status_color)
        
        # Print comment on next line if it exists and is not empty
        if comment and comment.strip():
            comment_indent = " " * (name_width + status_width + 2)
            print_colored(f"{comment_indent}→ {comment}", "0;33")  # Yellow
    
    # Summary
    total_count = len(results)
    print_colored("-" * 80, "0;37")
    
    if passed_count == total_count:
        print_colored(f"✓ ALL TESTS PASSED ({passed_count}/{total_count})", "1;32")
    else:
        failed_count = total_count - passed_count
        print_colored(f"✗ {failed_count} TEST(S) FAILED ({passed_count}/{total_count} passed)", "1;31")
    
    print_colored("=" * 80, "1;34")


def main():
    # Default to results.json in current directory
    results_file = Path("results.json")
    
    # Check if file path provided as argument
    if len(sys.argv) > 1:
        results_file = Path(sys.argv[1])
    
    # Check if file exists
    if not results_file.exists():
        print_colored(f"Error: Results file '{results_file}' not found", "1;31")
        sys.exit(1)
    
    try:
        # Read and parse results
        with open(results_file, 'r') as f:
            results = json.load(f)
        
        # Print table
        print_table(results)
        
    except json.JSONDecodeError as e:
        print_colored(f"Error: Invalid JSON format in '{results_file}': {e}", "1;31")
        sys.exit(1)
    except Exception as e:
        print_colored(f"Error reading '{results_file}': {e}", "1;31")
        sys.exit(1)


if __name__ == "__main__":
    main() 