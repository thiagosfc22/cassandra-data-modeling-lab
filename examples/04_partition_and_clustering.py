"""How the primary key shapes storage and queries — the most important idea in
Cassandra data modeling.

    PRIMARY KEY ((customer_id), order_time, order_id)
                 ^^^^^^^^^^^^^  ^^^^^^^^^^^^^^^^^^^^^^
                 partition key   clustering columns

* partition key    -> hashed to decide WHICH NODE the row lives on. All of one
  customer's orders are co-located, so reading them is one node, one seek.
* clustering columns -> the sort order WITHIN the partition. We declared
  order_time DESC, so "newest first" is how it's stored — no ORDER BY needed.

Run: python examples/04_partition_and_clustering.py
"""
import uuid
from datetime import datetime, timedelta, timezone

from common import get_session

cluster, session = get_session()

customer_id = uuid.uuid4()
base = datetime.now(timezone.utc)

insert = session.prepare(
    "INSERT INTO orders_by_customer "
    "(customer_id, order_time, order_id, amount, status) VALUES (?, ?, ?, ?, ?)"
)
# Insert five orders in deliberately shuffled time order.
for hours in [2, 0, 4, 1, 3]:
    session.execute(
        insert,
        (customer_id, base + timedelta(hours=hours), uuid.uuid4(), 10.0 + hours, "paid"),
    )

# No ORDER BY in the query — clustering order already stores them newest-first.
rows = list(session.execute(
    "SELECT order_time, amount FROM orders_by_customer WHERE customer_id=%s",
    (customer_id,),
))
print("orders as stored (CLUSTERING ORDER BY order_time DESC):")
for row in rows:
    print(f"  {row.order_time:%H:%M}   ${row.amount}")

times = [r.order_time for r in rows]
assert times == sorted(times, reverse=True), "expected newest-first"
print("read back newest-first from a single partition, no sort at query time")

# token() is the hash that places this partition on the ring.
token = session.execute(
    "SELECT token(customer_id) AS t FROM orders_by_customer WHERE customer_id=%s",
    (customer_id,),
).one()
print(f"\nthis partition's ring token (where it lives): {token.t}")

cluster.shutdown()
