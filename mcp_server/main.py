import asyncio
from mcp.server import MCPServer
from packages.mcp_server import tools

def main():
    """
    Initializes and runs the MCP server.
    """
    server = MCPServer(
        tools=[
            tools.open_session,
            tools.close_session,
            tools.create_page,
            tools.get_page,
            tools.list_pages,
            tools.update_page,
            tools.delete_page,
            tools.navigate_to_url,
            tools.get_dom,
            tools.get_screenshot,
            tools.test_xpath,
        ]
    )

    print("MCP Server configured with all tools. Running with stdio transport.")
    asyncio.run(server.run_stdio())

if __name__ == "__main__":
    main()