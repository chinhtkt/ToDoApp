from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    name="mcp_server",
)

@mcp.tool()
def add(a:int, b: int) -> int:
    """Adds two numbers together"""
    return a + b


@mcp.tool()
def get_current_temperature_by_city(city_name: str) -> str:
    """Get temperature by city name"""
    return "20 degrees Celsius"


@mcp.resource("resource://ma_so_thue")
def get_ma_so_thue() -> str:
    """Get tax code"""
    return  "1234"

if __name__ == "__main__":
    print("Listening...")
    mcp.run(transport='sse')