# GigaTIME-VMP MCP Server

A robust, type-safe, modular, and deterministic Model Context Protocol (MCP) server for clinical interpretation of spatial pathology architecture using the GigaTIME AI model.

## Overview

GigaTIME-VMP connects the official `healthcareai-toolkit` GigaTIME inference client with an MCP integration layer and an HTTP FastAPI server. It exposes endpoints and MCP tools designed to process Whole Slide Images (WSI), reduce their 4D tensor outputs into clinically relevant structured data, and interface with Google Gemini for plain-text clinical summaries.

## Features

- **Model Context Protocol (MCP):** Connects to MCP hosts via `stdio` for standard IDE integration.
- **Cloud Run / HTTP API:** Includes an out-of-the-box FastAPI app for standalone deployment.
- **Real Inference Backend:** Integrates directly with Azure ML deployments of GigaTIME via the `healthcareai-toolkit`.
- **Offline / Mock Mode:** Capable of running locally without Azure credentials by synthesizing biomarker tensors.
- **LLM Summary Generation:** Automates structured clinical pathology interpretations using Gemini 2.5 Flash.

## Setup & Local Usage

1. **Environment:** Setup a clean Python 3.11 environment (recommended tool: `uv`).
   ```bash
   uv venv -p 3.11
   source .venv/bin/activate
   ```
2. **Install dependencies:**
   ```bash
   uv pip install -r requirements.txt
   ```
3. **Configuration:**
   Copy the example environment file and add your credentials.
   ```bash
   cp .env.example .env
   ```
   *Note: Set `GIGATIME_MODEL_ENDPOINT=MOCK` if you are running locally without an Azure ML deployment.*

4. **Run the HTTP API (FastAPI):**
   ```bash
   uvicorn app:app --host 0.0.0.0 --port 8080
   ```

5. **Run as an MCP Tool:**
   Configure your MCP host (like Claude Desktop) to execute `python main.py` using your environment's python binary.

## Directory Structure

- `main.py` - The main entry point for the stdio MCP server.
- `app.py` - The FastAPI entrypoint for Cloud Run / HTTP routing.
- `integrations/` - Preprocessing WSI arrays, tensor reduction, Azure ML connections, and Gemini.
- `tools/` - Handlers for the MCP capabilities (`analyze_slide`, `fetch_biomarkers`, `summarize_spatial_architecture`).
- `store/` - Persistent storage mechanisms for background slide processing.
- `config/` - Environment configuration mapping via Pydantic.
- `models/` - Pydantic models for internal typing.
