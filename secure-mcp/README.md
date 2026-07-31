# Secure MCP Server & Client

An OAuth-protected MCP server built with FastMCP and Descope that exposes stock data and financial statements. A client built with LangChain and Ollama authenticates through Descope, gains access to the MCP server, and analyzes the retrieved stock data.

## Setup

Configure your MCP server in [Descope's Agentic Identity Hub](https://www.descope.ai/), then use its configuration URL in `mcp_server.py`.

Install the dependencies:

```bash
pip install -r requirements.txt
```

Start the MCP server:

```bash
python mcp_server.py
```

In a separate terminal, run the MCP client:

```bash
python mcp_client.py
```

Before the client can access the MCP server, an OAuth workflow opens in your browser. Complete it to grant the client access.
