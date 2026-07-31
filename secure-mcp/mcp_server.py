import json
import os
from typing import Any

import yfinance as yf
from fastmcp import FastMCP
from fastmcp.server.auth.providers.descope import DescopeProvider
from pandas import DataFrame


SERVER_URL = os.getenv("SERVER_URL", "http://127.0.0.1:8000")
SERVER_HOST = os.getenv("SERVER_HOST", "127.0.0.1")
SERVER_PORT = int(os.getenv("SERVER_PORT", "8000"))

auth_provider = DescopeProvider(
    config_url="https://api.descope.com/v1/apps/agentic/P3GEX8xKtL4c5PEx53Ne7F9Br4OK/RS3Gxk1RQ32j1zLTw3FVW0chbCpw7/.well-known/openid-configuration",        # Your MCP Server .well-known URL
    base_url=SERVER_URL,
)

mcp = FastMCP(name="Stocks Server", auth=auth_provider)


def _json_safe(value: Any) -> Any:
    return json.loads(json.dumps(value, default=str, allow_nan=False))


def _table_to_records(table: DataFrame) -> list[dict[str, Any]]:
    if table.empty:
        return []
    return _json_safe(json.loads(table.T.to_json(orient="records", date_format="iso")))


@mcp.tool()
def fetch_stock_info(symbol: str) -> dict[str, Any]:
    """Get general company information for a stock ticker, e.g. AAPL or MSFT."""
    return _json_safe(yf.Ticker(symbol).info)


@mcp.tool()
def fetch_quarterly_financials(symbol: str) -> list[dict[str, Any]]:
    """Get quarterly financial statements for a stock ticker."""
    return _table_to_records(yf.Ticker(symbol).quarterly_financials)


@mcp.tool()
def fetch_annual_financials(symbol: str) -> list[dict[str, Any]]:
    """Get annual financial statements for a stock ticker."""
    return _table_to_records(yf.Ticker(symbol).financials)


if __name__ == "__main__":
    mcp.run("streamable-http", host=SERVER_HOST, port=SERVER_PORT)
