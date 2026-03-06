"""
Neo4j driver wrapper for the skills ontology and job graph.
Uses settings from app.core.config (NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD).
"""

from contextlib import contextmanager
from typing import Any, List, Optional

from neo4j import GraphDatabase

from app.core.config import settings


def get_driver():
    """Return a Neo4j driver instance. Caller must close it when done."""
    return GraphDatabase.driver(
        settings.NEO4J_URI,
        auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD),
    )


@contextmanager
def session():
    """Context manager for a Neo4j session. Yields the session and closes driver after."""
    driver = get_driver()
    try:
        with driver.session() as s:
            yield s
    finally:
        driver.close()


def run_query(
    query: str,
    parameters: Optional[dict] = None,
) -> List[dict[str, Any]]:
    """
    Run a read or write Cypher query and return all records as list of dicts.
    Each record is {key: value} for each column in the result.
    """
    with session() as s:
        result = s.run(query, parameters or {})
        return [dict(record) for record in result]
