import asyncio
import logging
import sys
from dotenv import load_dotenv

load_dotenv()

from mcp.server.stdio import stdio_server

from server.mcp_server import GigaTIMEMCPServer
from store.job_store import JobStore
from integrations.azure_integrator import AzureIntegrator
from tools.analyze_slide import AnalyzeSlideTool
from tools.fetch_biomarkers import FetchBiomarkersTool
from integrations.gemini_interpreter import GeminiInterpreter
from tools.summarize_spatial_architecture import SummarizeSpatialArchitectureTool

logging.basicConfig(level=logging.INFO, stream=sys.stderr)
logger = logging.getLogger("mcp_main")



async def run() -> None:
    """Main entry point to boot the MCP server over stdio."""
    server_wrapper = GigaTIMEMCPServer()
    
    # Initialize Core State and Integrations
    job_store = JobStore()
    azure_integrator = AzureIntegrator(job_store=job_store)
    
    try:
        gemini_interpreter = GeminiInterpreter()
    except ValueError as e:
        logger.error(f"Startup error: {e}")
        sys.exit(1)
    
    # Instantiate tools with injected dependencies
    analyze_tool = AnalyzeSlideTool(azure_integrator=azure_integrator)
    fetch_tool = FetchBiomarkersTool(job_store=job_store)
    summarize_tool = SummarizeSpatialArchitectureTool(
        job_store=job_store,
        gemini_interpreter=gemini_interpreter
    )
    
    # Register the real analysis tool
    server_wrapper.registry.register(
        name=analyze_tool.name,
        description=analyze_tool.description,
        input_schema=analyze_tool.input_schema,
        handler=analyze_tool.handler
    )
    
    # Register the fetch biomarkers tool
    server_wrapper.registry.register(
        name=fetch_tool.name,
        description=fetch_tool.description,
        input_schema=fetch_tool.input_schema,
        handler=fetch_tool.handler
    )
    
    # Register the summarize spatial architecture tool
    server_wrapper.registry.register(
        name=summarize_tool.name,
        description=summarize_tool.description,
        input_schema=summarize_tool.input_schema,
        handler=summarize_tool.handler
    )
    
    logger.info("Starting GigaTIME MCP Server on stdio...")
    
    # Start stdio transport and run the MCP server event loop
    async with stdio_server() as (read_stream, write_stream):
        await server_wrapper.app.run(
            read_stream,
            write_stream,
            server_wrapper.app.create_initialization_options()
        )

def main():
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        logger.info("Server stopped.")

if __name__ == "__main__":
    main()
