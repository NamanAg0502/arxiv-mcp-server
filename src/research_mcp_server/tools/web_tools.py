"""Web scraping tool — fetch and extract content from any URL."""

import json
import logging
from typing import Any, Dict, List

import mcp.types as types

from ..clients.web_client import WebClient

logger = logging.getLogger("research-mcp-server")

web_tool = types.Tool(
    name="web",
    description="Fetch and extract content from any URL — articles, links, or metadata.",
    inputSchema={
        "type": "object",
        "required": ["url"],
        "properties": {
            "url": {
                "type": "string",
                "description": "URL to fetch. Must be a valid HTTP/HTTPS URL.",
            },
            "extract": {
                "type": "string",
                "enum": ["article", "links", "metadata", "raw"],
                "description": "Extraction mode. Default: article.",
            },
            "max_length": {
                "type": "integer",
                "minimum": 1000,
                "maximum": 50000,
                "description": "Max characters for text content. Default: 10000.",
            },
        },
    },
)


# Block internal/private network URLs
_BLOCKED_HOSTS = {
    "localhost", "127.0.0.1", "0.0.0.0", "::1",
    "metadata.google.internal", "169.254.169.254",  # Cloud metadata
}


def _validate_url(url: str) -> str | None:
    """Validate and sanitize URL. Returns error message if invalid, None if OK."""
    from urllib.parse import urlparse

    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        return f"Invalid scheme '{parsed.scheme}'. Only http/https allowed."
    if parsed.hostname and parsed.hostname.lower() in _BLOCKED_HOSTS:
        return f"Blocked host: {parsed.hostname}. Cannot access internal/private networks."
    if parsed.hostname and (parsed.hostname.endswith(".local") or parsed.hostname.startswith("192.168.")):
        return f"Blocked host: {parsed.hostname}. Cannot access private networks."
    return None


async def handle_web(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Fetch and extract web content."""
    url = arguments.get("url")
    if not url:
        return [types.TextContent(type="text", text="Error: 'url' is required.")]

    # Prepend https if missing
    if not url.startswith(("http://", "https://")):
        url = f"https://{url}"

    # Security: validate URL
    error = _validate_url(url)
    if error:
        return [types.TextContent(type="text", text=f"Error: {error}")]

    client = WebClient()
    extract = arguments.get("extract", "article")
    max_length = arguments.get("max_length", 10000)

    try:
        result = await client.fetch(url=url, extract=extract, max_length=max_length)
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
    except Exception as e:
        logger.error(f"Web tool error for {url}: {e}")
        return [types.TextContent(type="text", text=f"Error fetching {url}: {str(e)}")]
