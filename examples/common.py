"""Shared connection helper for the examples.

Everything connects to the single-node lab cluster on localhost, defined in
docker-compose.yml. Bring it up and load the schema first: `make schema`.
"""
from cassandra.cluster import Cluster


def get_session(keyspace: str = "lab"):
    """Return (cluster, session). Caller is responsible for cluster.shutdown()."""
    cluster = Cluster(["127.0.0.1"], port=9042)
    session = cluster.connect()
    session.set_keyspace(keyspace)
    return cluster, session
