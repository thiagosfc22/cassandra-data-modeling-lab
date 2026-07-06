"""Connect to the cluster and inspect the ring.

Every node is a peer — there is no master to connect to. The driver connects to
any node, learns the whole topology through it, and routes each query to a
replica that owns the data.

Run: python examples/01_connect.py
"""
from cassandra.cluster import Cluster

cluster = Cluster(["127.0.0.1"], port=9042)
session = cluster.connect()

row = session.execute(
    "SELECT cluster_name, release_version FROM system.local"
).one()
print(f"connected to '{row.cluster_name}', Cassandra {row.release_version}")

print("\nnodes in the ring:")
for host in cluster.metadata.all_hosts():
    print(f"  {host.address}  dc={host.datacenter}  rack={host.rack}  up={host.is_up}")

cluster.shutdown()
