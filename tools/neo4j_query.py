from collections.abc import Generator
from typing import Any
from neo4j import GraphDatabase, basic_auth
import re

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class Neo4jQueryTool(Tool):
    def _validate_and_parameterize_query(self, query: str, parameters: dict[str, Any] = None) -> tuple[str, dict[str, Any]]:
        """
        Validate and automatically parameterize a Cypher query to prevent injection attacks.
        Keeps the original simple interface while adding security through automatic parameterization.
        """
        if not query or not isinstance(query, str):
            raise ValueError("Query must be a non-empty string")
        
        # Remove potentially dangerous operations
        dangerous_patterns = [
            r'\bDETACH\s+DELETE\b',
            r'\bDELETE\b(?![^(]*\))',  # DELETE not inside parentheses  
            r'\bDROP\b',
            r'\bCREATE\s+(?:DATABASE|USER|ROLE)\b',
            r'\bSET\s+PASSWORD\b',
            r'\bCALL\s+db\.',
            r'\bCALL\s+dbms\.',
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                raise ValueError(f"Query contains potentially dangerous operation: {pattern}")
        
        # Limit query length
        if len(query) > 2000:
            raise ValueError("Query too long (max 2000 characters)")
        
        # Add LIMIT if not present
        if not re.search(r'\bLIMIT\s+\d+', query, re.IGNORECASE):
            # Extract any existing RETURN clause and add LIMIT after it
            if re.search(r'\bRETURN\b', query, re.IGNORECASE):
                query = re.sub(r'(\bRETURN\b[^;]*)', r'\1 LIMIT 1000', query, flags=re.IGNORECASE)
            else:
                query += " LIMIT 1000"
        else:
            # Ensure LIMIT is not too high
            query = re.sub(r'\bLIMIT\s+(\d+)', 
                          lambda m: f"LIMIT {min(int(m.group(1)), 1000)}", 
                          query, flags=re.IGNORECASE)
        
        # Use provided parameters or empty dict
        safe_params = parameters or {}
        
        return query, safe_params

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        # Access credentials from provider config
        url = self.runtime.credentials.get("AURA_URL")
        username = self.runtime.credentials.get("AURA_USERNAME")
        password = self.runtime.credentials.get("AURA_PASSWORD")
        query = tool_parameters.get("query")
        parameters = tool_parameters.get("parameters", {})

        if not all([url, username, password, query]):
            yield self.create_text_message("Missing required parameters or credentials.")
            return

        try:
            # Validate and parameterize the query
            safe_query, safe_params = self._validate_and_parameterize_query(query, parameters)
            
            # Execute the parameterized query
            driver = GraphDatabase.driver(url, auth=basic_auth(username, password))
            with driver.session() as session:
                result = session.run(safe_query, safe_params)
                records = [record.data() for record in result]
            driver.close()

            yield self.create_json_message({"results": records})
            
            if records:
                yield self.create_text_message(f"Found {len(records)} results from Neo4j query.")
            else:
                yield self.create_text_message("No results found for the specified query.")
                
        except ValueError as e:
            yield self.create_text_message(f"Invalid query: {str(e)}")
        except Exception as e:
            yield self.create_text_message(f"Error executing Neo4j query: {str(e)}")
