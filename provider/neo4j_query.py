from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError
from neo4j import GraphDatabase, basic_auth


class Neo4jQueryProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        url = credentials.get("NEO4J_URL")
        username = credentials.get("NEO4J_USERNAME")
        password = credentials.get("NEO4J_PASSWORD")
        
        # Check which credentials are missing or empty
        missing_credentials = []
        if not url:
            missing_credentials.append("Neo4j URL")
        if not username:
            missing_credentials.append("Neo4j Username")
        if not password:
            missing_credentials.append("Neo4j Password")
        
        if missing_credentials:
            missing_str = ", ".join(missing_credentials)
            raise ToolProviderCredentialValidationError(
                f"Missing or empty credentials: {missing_str}. Please provide all required Neo4j connection details."
            )
        
        # Validate URL scheme
        supported_schemes = ['bolt://', 'bolt+ssc://', 'bolt+s://', 'neo4j://', 'neo4j+ssc://', 'neo4j+s://']
        if not any(url.startswith(scheme) for scheme in supported_schemes):
            # Check for common typo
            if url.startswith('neo4+s://'):
                raise ToolProviderCredentialValidationError(
                    f"Invalid URL scheme. You entered 'neo4+s://' but it should be 'neo4j+s://' (with a 'j').\n"
                    f"Your URL: {url}\n"
                    f"Corrected URL should be: {url.replace('neo4+s://', 'neo4j+s://')}"
                )
            raise ToolProviderCredentialValidationError(
                f"Invalid URL scheme in: {url}\n"
                f"Supported schemes: bolt://, bolt+s://, bolt+ssc://, neo4j://, neo4j+s://, neo4j+ssc://\n"
                f"Examples:\n"
                f"  - Neo4j Aura: neo4j+s://xxxxx.databases.neo4j.io\n"
                f"  - Local: bolt://localhost:7687 or neo4j://localhost:7687"
            )
        
        try:
            # Use a timeout for connection verification
            # Set max_connection_lifetime to handle Aura connections better
            with GraphDatabase.driver(
                url, 
                auth=basic_auth(username, password),
                connection_timeout=30.0,  # 30 second timeout for DNS resolution
                max_connection_lifetime=3600,  # 1 hour
                user_agent="dify-neo4j-plugin/1.0"
            ) as driver:
                driver.verify_connectivity()
        except Exception as e:
            error_msg = str(e)
            # Provide more specific error messages
            if "authentication" in error_msg.lower() or "unauthorized" in error_msg.lower():
                raise ToolProviderCredentialValidationError(
                    f"Authentication failed. Please check your Neo4j username and password."
                )
            elif "dns" in error_msg.lower() or "name or service not known" in error_msg.lower():
                raise ToolProviderCredentialValidationError(
                    f"DNS resolution failed. Please verify:\n"
                    f"1. Your Neo4j URL is correct (e.g., neo4j+s://xxxxx.databases.neo4j.io)\n"
                    f"2. Your Dify instance has internet access\n"
                    f"3. DNS resolution is working in your environment\n"
                    f"Current URL: {url}"
                )
            elif "connection" in error_msg.lower() or "timeout" in error_msg.lower():
                raise ToolProviderCredentialValidationError(
                    f"Connection failed. Please check your Neo4j URL and ensure the database is accessible. Error: {error_msg}"
                )
            else:
                raise ToolProviderCredentialValidationError(f"Neo4j credential validation failed: {error_msg}")
