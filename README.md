# GigaTIME MCP Server

A robust, type-safe, modular, and deterministic Model Context Protocol (MCP) server.

## Overview

GigaTIME MCP Server implements the foundational architecture for an MCP server wrapper. It is designed to handle MCP protocol communication, provide a solid `ToolRegistry` for metadata management, and establish a clear entry point (`main.py`) using `stdio` for integration. It adheres to strict separation between core infrastructure and future business logic or external integrations.

## Features

- **Type-safe:** Uses `pydantic` schemas for robust configuration and state management.
- **Modular:** Clear boundaries between server implementation, routing, and tools.
- **Deterministic:** Core mechanisms are built avoiding side effects.
- **Extensible:** An internal tool registry allows easy registration of additional MCP capabilities.

## Setup

1. **Environment:** Ensure you have Python installed. You can set up your virtual environment using `venv` or `uv`:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   *(Note: The project may also use `pyproject.toml` for standard packaging.)*

3. **Configuration:**
   Copy the example environment file and configure it as needed.
   ```bash
   cp .env.example .env
   ```

## Usage

To start the MCP server, run:

```bash
python main.py
```

It is intended to communicate over stdio, so it is typically run by a client or another orchestration agent (such as an MCP client).

## Directory Structure

- `main.py` - The main entry point for the stdio server.
- `config/` - Configuration management.
- `models/` - Pydantic models and schemas.
- `server/` - Core MCP server logic and ToolRegistry.
- `integrations/` - External platform connections.
- `tools/` - Handlers for various tools exposed by the MCP server.
- `store/` - Persistent storage mechanisms or interfaces.
- `tests/` - Test suite.
- `TechnicalDocumentation/` - Detailed architectural and technical docs.
