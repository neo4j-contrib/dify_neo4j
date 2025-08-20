from collections.abc import Generator
from typing import Any
from neo4j import GraphDatabase,basic_auth

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class Neo4jQueryTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        # Access credentials from provider config
        url = self.runtime.credentials.get("AURA_URL")
        username = self.runtime.credentials.get("AURA_USERNAME")
        password = self.runtime.credentials.get("AURA_PASSWORD")
        query = tool_parameters.get("query")

        if not all([url, username, password, query]):
            yield self.create_text_message("Missing required parameters or credentials.")
            return

        try:
            driver = GraphDatabase.driver(url, auth=basic_auth(username, password))
            with driver.session() as session:
                result = session.run(query)
                records = [record.data() for record in result]
            driver.close()

            yield self.create_json_message({"results": records})
            yield self.create_text_message(str(records))
        except Exception as e:
            yield self.create_text_message(f"Error executing Neo4j query: {str(e)}")
