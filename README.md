# AI Agent Testing Framework

![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![MCP](https://img.shields.io/badge/MCP-Protocol-orange.svg)

A production-ready testing framework for evaluating AI agent performance using the **Model Context Protocol (MCP)** for hotel reservation management. This project demonstrates modern AI engineering practices, async Python patterns, and comprehensive test automation.

## Features & Skills Demonstrated

### Core Capabilities
- **MCP Integration**: Custom MCP server implementation with FastMCP for AI tool orchestration
- **AI Agent Orchestration**: Claude AI agent with async stdio communication
- **Data Validation**: Pydantic models with business logic enforcement
- **Test Automation**: Comprehensive validation framework with multiple test scenarios
- **Containerization**: Docker support for reproducible deployment
- **Modern Python**: Async/await patterns, type hints, and clean architecture

### Technical Stack
- **Language**: Python 3.10+
- **AI/ML**: Anthropic Claude API, Model Context Protocol (MCP)
- **Validation**: Pydantic 2.0+
- **Package Management**: uv (ultra-fast Python package manager)
- **Containerization**: Docker
- **Testing**: Custom validation framework with pytest-ready structure

## Architecture

### Components
- **[agent.py](agent.py)**: Claude AI agent with MCP client integration (431 lines)
- **[src/reservation_server.py](src/reservation_server.py)**: FastMCP server providing reservation management tools (279 lines)
- **[src/models/reservation.py](src/models/reservation.py)**: Pydantic data models with validation
- **[src/storage/json_storage.py](src/storage/json_storage.py)**: JSON-based persistence layer
- **[problems/](problems/)**: Structured test scenarios with automated validation

### Available MCP Tools
1. `create_reservation` - Create new hotel reservations with validation
2. `get_reservation` - Retrieve reservation by ID
3. `update_reservation` - Modify existing reservations
4. `delete_reservation` - Cancel reservations
5. `list_reservations` - Query all reservations
6. Service management tools (create, update, delete services)

### Business Logic
- Date validation (check-out must be after check-in)
- Business rule enforcement (e.g., January booking restrictions)
- Service attachment and pricing
- Multi-step workflow orchestration

## Quick Start

### Prerequisites
- Docker (recommended) OR Python 3.10+ with `uv`
- Anthropic API key

### Setup

1. **Clone and navigate to project**
   ```bash
   cd agent-workforce-test
   ```

2. **Configure API key**
   ```bash
   cp .env.example .env
   # Edit .env and add your ANTHROPIC_API_KEY
   ```
   Get your API key from: https://console.anthropic.com/

3. **Run tests**

   Using Docker (recommended):
   ```bash
   ./docker-run.sh problems/001
   ```

   Using uv directly (faster):
   ```bash
   ./run_test.sh problems/001
   ```

## Test Scenarios

### Problem 001: Baseline (Pass Example)
**Goal**: Verify basic reservation creation
- Creates reservation for guest with specified dates
- Validates data persistence and retrieval
- **Status**: ✅ Pass

### Problem 002: Business Rule Enforcement
**Goal**: Test January restriction compliance
- Attempts to create January reservation
- Agent must refuse per system prompt rules
- **Status**: ✅ Pass

### Problem 003: Service Management
**Goal**: Add services to existing reservations
- Attaches multiple services to reservation
- Validates service persistence
- **Status**: ✅ Pass

### Problem 004: Nightmare Mode (Complex Multi-Step)
**Goal**: Complex consolidation with conditional logic
- Multi-guest booking consolidation
- Room upgrades and date extensions
- Selective service transfers
- Conditional business rules (e.g., Spa package eligibility)
- 10-point validation checklist
- **Status**: ⚠️ Challenging (may fail, but demonstrates advanced reasoning)

## Project Structure

```
agent-workforce-test/
├── agent.py                      # Main Claude AI agent
├── src/
│   ├── reservation_server.py     # MCP server implementation
│   ├── models/
│   │   └── reservation.py        # Data models
│   └── storage/
│       └── json_storage.py       # Persistence layer
├── problems/                     # Test scenarios
│   ├── 001/                      # Baseline test
│   ├── 002/                      # Rule enforcement
│   ├── 003/                      # Service management
│   └── 004/                      # Complex multi-step
├── prompts/
│   └── system_prompt.txt         # Agent behavioral instructions
├── Dockerfile                    # Containerization
├── docker-run.sh                 # Docker test runner
├── run_test.sh                   # Direct test runner (uv)
└── print_results.py              # Test result formatter
```

## How It Works

1. **Agent Initialization**: Claude AI agent connects to MCP server via stdio
2. **Tool Discovery**: Agent receives available tools from MCP server
3. **Task Execution**: Agent processes user prompts using available tools
4. **Validation**: Automated scripts verify correct agent behavior
5. **Results**: Rich terminal output shows pass/fail status

**System Prompt**: Agent behavioral instructions and business rules are defined in [prompts/system_prompt.txt](prompts/system_prompt.txt)

## Development

### Running All Tests
```bash
# Test all scenarios
for problem in problems/*/; do
  ./docker-run.sh "$problem"
done
```

### Viewing Results
```bash
python print_results.py
```

### Adding New Tests
1. Create new directory in `problems/`
2. Add `description.md`, `user_prompt.txt`, `check_result.py`
3. Provide initial data in `data/` subdirectory
4. Run test to validate

## Skills Highlighted

This project demonstrates expertise in:
- **AI/ML Engineering**: Agent orchestration, prompt engineering, MCP protocol
- **Async Programming**: Proper async/await patterns, context managers
- **API Integration**: Anthropic Claude API, MCP client/server
- **Data Engineering**: Pydantic validation, JSON persistence
- **Testing**: Automated validation, test scenario design
- **DevOps**: Docker containerization, reproducible environments
- **Software Architecture**: Clean separation of concerns, modular design
- **Python Best Practices**: Type hints, error handling, modern tooling

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE).

## Author

**Parth Bhalodiya**

This project is a demonstration/portfolio piece showcasing AI/ML engineering capabilities.

## Acknowledgments

- Built with [Anthropic Claude](https://www.anthropic.com/claude) API
- Uses [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) for tool integration
- Powered by [FastMCP](https://github.com/jlowin/fastmcp) framework
