from collections.abc import Generator
from typing import Any
from neo4j import GraphDatabase, basic_auth
import re
import itertools
import json

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class Neo4jQueryTool(Tool):
    # Instance-level driver storage (initialized on first use)
    _driver = None
    _driver_url = None
    _driver_username = None
    _driver_password = None
    
    def _get_or_create_driver(self, url: str, username: str, password: str):
        """
        Get existing driver or create a new one if credentials changed.
        The driver is reused across multiple queries for efficiency.
        """
        if (self._driver is None or 
            self._driver_url != url or 
            self._driver_username != username or 
            self._driver_password != password):
            
            # Close existing driver if credentials changed
            if self._driver is not None:
                self._driver.close()
            
            # Create new driver with custom user agent for tracking
            self._driver = GraphDatabase.driver(
                url, 
                auth=basic_auth(username, password),
                connection_timeout=30.0,  # 30 second timeout for DNS resolution
                max_connection_lifetime=3600,  # 1 hour
                user_agent="dify-neo4j-plugin/1.0"
            )
            self._driver_url = url
            self._driver_username = username
            self._driver_password = password
        
        return self._driver
    
    def _validate_query_basic(self, query: str) -> None:
        """
        Basic validation of a Cypher query.
        Only checks query format and length.
        """
        if not query or not isinstance(query, str):
            raise ValueError("Query must be a non-empty string")
        
        # Limit query length
        if len(query) > 2000:
            raise ValueError("Query too long (max 2000 characters)")
    
    def _execute_preflight_check(self, session, query: str, parameters: dict[str, Any], allow_write: bool) -> None:
        """
        Execute a preflight check using EXPLAIN to validate the query.
        Checks for syntax errors and query type.
        
        Args:
            session: Neo4j session
            query: The Cypher query to check
            parameters: Query parameters
            allow_write: Whether write queries are allowed
            
        Raises:
            ValueError: If query validation fails
        """
        try:
            # Execute EXPLAIN to check query without running it
            explain_result = session.run(f"EXPLAIN {query}", parameters)
            summary = explain_result.consume()
            
            # Check query type from the summary
            query_type = summary.query_type
            
            if not allow_write:
                # Only allow read ('r') and schema ('s') queries
                if query_type not in ['r', 's']:
                    raise ValueError(
                        f"Write queries are not allowed. Query type: '{query_type}'. "
                        "Enable 'Allow Write Queries' to execute write operations."
                    )
        except ValueError:
            # Re-raise our validation errors as-is
            raise
        except Exception as e:
            # Handle Neo4j specific errors
            error_msg = str(e)
            error_code = getattr(e, 'code', '')
            
            # Syntax errors have specific error codes
            if 'SyntaxError' in error_code or 'SyntaxError' in error_msg:
                raise ValueError(f"Query syntax error: {error_msg}")
            
            # Other Neo4j errors
            raise ValueError(f"Query validation failed: {error_msg}")

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        # Access credentials from provider config
        url = self.runtime.credentials.get("NEO4J_URL")
        username = self.runtime.credentials.get("NEO4J_USERNAME")
        password = self.runtime.credentials.get("NEO4J_PASSWORD")
        query = tool_parameters.get("query")
        parameters_str = tool_parameters.get("parameters", "")
        database = tool_parameters.get("database")  # Optional database parameter
        max_records = tool_parameters.get("max_records", 1000)  # Maximum records to fetch
        allow_write = tool_parameters.get("allow_write_queries", False)  # Write query permission

        if not all([url, username, password, query]):
            yield self.create_text_message("Missing required parameters or credentials.")
            return

        try:
            # Basic validation (administrative operations check)
            self._validate_query_basic(query)
            
            # Parse parameters string to dict
            safe_params = {}
            if parameters_str and parameters_str.strip():
                try:
                    safe_params = json.loads(parameters_str)
                    if not isinstance(safe_params, dict):
                        raise ValueError("Parameters must be a JSON object")
                except json.JSONDecodeError as e:
                    # Try to fix common issue: unquoted string values from variable substitution
                    # Example: {"name":cardiomyopathy} -> {"name":"cardiomyopathy"}
                    try:
                        import re
                        # Pattern to find unquoted values after colons
                        # Matches :value} or :value, where value doesn't start with quote, bracket, or brace
                        fixed_params = re.sub(r':([a-zA-Z0-9_][a-zA-Z0-9_\s\-\.]*)([\},])', r':"\1"\2', parameters_str)
                        safe_params = json.loads(fixed_params)
                        if not isinstance(safe_params, dict):
                            raise ValueError("Parameters must be a JSON object")
                        yield self.create_text_message(f"Note: Auto-corrected parameter format from '{parameters_str}' to '{fixed_params}'")
                    except:
                        raise ValueError(
                            f"Invalid JSON in parameters: {str(e)}\n"
                            f"Received: {parameters_str}\n"
                            f"Tip: When using variables, ensure proper JSON format. "
                            f"Example: {{\"name\":\"{{{{#llm.text#}}}}\"}}"
                        )
            
            # Get or create the driver (reused across queries)
            driver = self._get_or_create_driver(url, username, password)
            
            # Execute the parameterized query with fetch_size configuration
            # Use specified database or default for the user
            session_kwargs = {
                "fetch_size": min(max_records, 1000)  # Use fetch_size for efficient streaming
            }
            if database:
                session_kwargs["database"] = database
                
            with driver.session(**session_kwargs) as session:
                # Preflight check: EXPLAIN the query to validate syntax and check query type
                self._execute_preflight_check(session, query, safe_params, allow_write)
                
                # Execute the actual query
                result = session.run(query, safe_params)
                
                # Efficiently fetch only up to max_records using islice
                # This stops iteration after max_records without loading all data
                records = [record.data() for record in itertools.islice(result, max_records)]

            # Send JSON message with full results
            yield self.create_json_message({"results": records})
            
            # Send text message with formatted summary
            if records:
                # Create a readable text summary
                text_summary = f"Found {len(records)} results from Neo4j query.\n\n"
                text_summary += "Results (JSON):\n"
                text_summary += json.dumps(records, indent=2, ensure_ascii=False)
                yield self.create_text_message(text_summary)
            else:
                yield self.create_text_message("No results found for the specified query.")
                
        except ValueError as e:
            yield self.create_text_message(f"Invalid query: {str(e)}")
        except Exception as e:
            yield self.create_text_message(f"Error executing Neo4j query: {str(e)}")
