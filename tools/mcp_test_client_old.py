import asyncio
import os

from mcp.client.stdio import stdio_client
from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters


async def main():
    # Ensure the server sees our demo CSV
    env = os.environ.copy()
    env["RCA_CSV_PATH"] = "./data/example_incidents.csv"

    server = StdioServerParameters(
        command="python",
        args=["mcp_server.py"],
        env=env,
    )

    async with stdio_client(server) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()
            print("TOOLS:")
            for t in tools.tools:
                print("-", t.name)

            res = await session.call_tool("list_columns", {})
            print("\nlist_columns result:")
            print(res.content)

            res2 = await session.call_tool("list_incidents", {"limit": 5})
            print("\nlist_incidents result:")
            print(res2.content)


if __name__ == "__main__":
    asyncio.run(main())
