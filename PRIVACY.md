## Privacy

Last Updated: 04.09.2025

## 1. Introduction

This Privacy Policy describes how the Neo4j Querying Plugin for Dify (“the Plugin”) handles data. The Plugin has been designed with privacy in mind and processes only the information required to fulfill its intended functionality: running Cypher queries against a user-defined Neo4j database and returning the results within Dify workflows.

## 2. What Data We Access

Connection Information: The Plugin requires connection credentials provided directly by the user (e.g., host, username, password) to connect to Neo4j Aura database.

Query Input: The Plugin receives Cypher queries entered by the user or LLM.

Query Output: The Plugin retrieves and returns the query results from the connected Neo4j Aura instance.

## 3. What Data We Do Not Collect or Share

We do not log, store, or retain connection credentials, query text, or query results beyond the active session.

We do not transmit any data to external servers, websites, or APIs other than the user‑specified Neo4j Aura database.

We do not use or share user data for analytics, advertising, or any secondary purposes.

## 4. Data Processing

All data flow occurs exclusively:

From the user to the Plugin, to provide connection details and queries.

From the Plugin to Neo4j Aura, to execute queries.

From Neo4j Aura back to the Plugin, to return the query results.

No intermediate storage or third-party processing takes place. The parts that are executed by other Dify plugins, or operators are not subject of this policy. 

## 5. Security
 
Connection credentials are transmitted only as necessary to establish the session with Neo4j Aura.

The Plugin relies on the security measures of the Dify platform and Neo4j Aura service.

Users are responsible for safeguarding their credentials and access tokens.

## 6. User Control
 
Users may disconnect the Plugin at any time, which immediately terminates the active database session.

Any connection information resides only in the user’s configuration within Dify and is never sent elsewhere.

## 7. Changes to This Policy
We may update this Privacy Policy from time to time to reflect changes in functionality or applicable regulations. Users will be notified of any significant changes.

## 8. Contact
If you have any questions or concerns about this Privacy Policy, please submit issue in the Plugin's repository: https://github.com/neo4j-contrib/dify_neo4j/issues

