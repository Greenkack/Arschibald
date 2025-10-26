"""
Web Search Tools for KAI Agent
===============================

Provides web search capabilities using Tavily Search API for current
market data and information not available in the knowledge base.

Requirements: 9.1, 9.2, 9.3, 9.4, 9.5
"""

import os
import time
from langchain_core.tools import tool
from tavily import TavilyClient

# Import logging utilities
from agent.logging_config import get_logger, log_api_call

# Import error classes
from agent.errors import APIError, ConfigurationError

# Get logger for this module
logger = get_logger(__name__)


@tool
def tavily_search(query: str) -> str:
    """
    Search the internet with Tavily Search API for current information.

    This tool performs advanced web searches to find up-to-date information
    about renewable energy systems, market data, pricing, and technical details.

    Args:
        query: Search query string

    Returns:
        JSON string with search results (URLs + content snippets)

    Configuration:
        - search_depth: "advanced" for comprehensive results
        - Returns top results with URLs and content

    Requirements: 9.1, 9.2, 9.3, 9.4, 9.5

    Example:
        >>> tavily_search("aktuelle Photovoltaik Preise 2024")
        "[{'url': '...', 'content': '...'}]"
    """
    start_time = time.time()
    logger.info(f"Starting Tavily search: {query[:100]}")

    try:
        # Check API key
        api_key = os.getenv("TAVILY_API_KEY")
        if not api_key:
            logger.error("TAVILY_API_KEY not configured")
            raise ConfigurationError(
                "TAVILY_API_KEY not configured",
                missing_keys=["TAVILY_API_KEY"],
                solution=(
                    "Set TAVILY_API_KEY in your .env file:\n"
                    "  1. Get API key from https://tavily.com\n"
                    "  2. Add to .env: TAVILY_API_KEY=your_key_here\n"
                    "  3. Restart the application"
                )
            )

        # Initialize client
        logger.debug("Initializing Tavily client")
        try:
            client = TavilyClient(api_key=api_key)
        except Exception as e:
            logger.error(f"Failed to initialize Tavily client: {e}")
            raise APIError(
                "Failed to initialize Tavily client",
                api_name="Tavily",
                solution="Check TAVILY_API_KEY validity and network connection"
            )

        # Perform search
        logger.info("Executing Tavily search with depth=advanced")
        try:
            response = client.search(query=query, search_depth="advanced")
        except Exception as e:
            logger.error(f"Tavily search request failed: {e}")
            # Check for specific error types
            error_str = str(e).lower()
            if "401" in error_str or "unauthorized" in error_str:
                raise APIError(
                    "Tavily API authentication failed",
                    api_name="Tavily",
                    status_code=401,
                    solution="Check TAVILY_API_KEY in .env file"
                )
            elif "429" in error_str or "rate limit" in error_str:
                raise APIError(
                    "Tavily API rate limit exceeded",
                    api_name="Tavily",
                    status_code=429,
                    solution="Wait a few minutes and try again, or upgrade API plan")
            elif "503" in error_str or "unavailable" in error_str:
                raise APIError(
                    "Tavily API temporarily unavailable",
                    api_name="Tavily",
                    status_code=503,
                    solution="Wait a few minutes and try again"
                )
            else:
                raise APIError(
                    f"Tavily search failed: {str(e)}",
                    api_name="Tavily",
                    solution="Check network connection and API status"
                )

        # Extract results
        try:
            context = [
                {"url": obj["url"], "content": obj["content"]}
                for obj in response.get('results', [])
            ]
        except (KeyError, TypeError) as e:
            logger.error(f"Failed to parse Tavily response: {e}")
            raise APIError(
                "Failed to parse Tavily search results",
                api_name="Tavily",
                response=str(response)[
                    :200],
                solution="Check Tavily API documentation for response format changes")

        duration = time.time() - start_time
        logger.info(
            f"Tavily search completed: {
                len(context)} results in {
                duration:.2f}s")

        # Log successful API call
        log_api_call(
            logger,
            api_name="Tavily",
            method="search",
            status_code=200,
            duration=duration
        )

        return str(context)

    except (ConfigurationError, APIError) as e:
        # Re-raise our custom errors
        duration = time.time() - start_time
        log_api_call(
            logger,
            api_name="Tavily",
            method="search",
            duration=duration,
            error=str(e)
        )
        # Return user-friendly error message
        return f"❌ {
            e.__class__.__name__}: {
            e.message}\n\n💡 Solution:\n{
            e.solution}"

    except Exception as e:
        # Catch-all for unexpected errors
        duration = time.time() - start_time
        logger.error(f"Unexpected error in Tavily search: {e}", exc_info=True)

        log_api_call(
            logger,
            api_name="Tavily",
            method="search",
            duration=duration,
            error=str(e)
        )

        return (
            f"❌ Unexpected error during web search: {str(e)}\n\n"
            f"💡 Solution:\n"
            f"Check logs for details and ensure Tavily API is configured correctly."
        )
