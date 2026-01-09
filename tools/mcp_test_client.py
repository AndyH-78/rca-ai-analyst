import asyncio
import os

from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp import ClientSession


async def main():
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

            print("TOOLS:")
            tools = await session.list_tools()
            for t in tools.tools:
                print("-", t.name)

            print("\n--- Evaluating INC-1002 via MCP ---")
            res = await session.call_tool(
                "evaluate_incident_by_id",
                {
                    "incident_id": "INC-1002",
                    "incident_id_col": "issue_key",
                    "summary_col": "summary",
                    "description_col": "description",
                    "root_cause_col": "root_cause",
                    "resolution_col": "resolution",
                    "preventive_action_col": "preventive_action",
                },
            )

            for item in res.content:
                print(item.text)


if __name__ == "__main__":
    asyncio.run(main())
