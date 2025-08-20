from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError
from neo4j import GraphDatabase, basic_auth


class Neo4jQueryProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        url = credentials.get("AURA_URL")
        username = credentials.get("AURA_USERNAME")
        password = credentials.get("AURA_PASSWORD")
        if not all([url, username, password]):
            raise ToolProviderCredentialValidationError("All Neo4j credentials must be provided.")
        try:
            with GraphDatabase.driver(url, auth=basic_auth(username, password)) as driver:
                driver.verify_connectivity()
        except Exception as e:
            raise ToolProviderCredentialValidationError(f"Neo4j credential validation failed: {e}")
