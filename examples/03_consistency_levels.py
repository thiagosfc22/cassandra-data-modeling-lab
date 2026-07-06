"""Tunable consistency: every statement chooses its own consistency level, so
consistency stops being a property of the database and becomes a per-query
decision. W + R > RF guarantees the read set overlaps the write set.

On this single-node lab RF=1, so every level resolves to the one node — what you
see here is the API and the math. In a real 3-node cluster QUORUM=2, and a
QUORUM write + QUORUM read (2 + 2 > 3) is what buys a consistent read with no
leader.

Run: python examples/03_consistency_levels.py
"""
import uuid
from datetime import datetime, timezone

from cassandra import ConsistencyLevel
from cassandra.query import SimpleStatement

from common import get_session

cluster, session = get_session()

customer_id = uuid.uuid4()
order_time = datetime.now(timezone.utc)

write = SimpleStatement(
    "INSERT INTO orders_by_customer "
    "(customer_id, order_time, order_id, amount, status) VALUES (%s, %s, %s, %s, %s)",
    consistency_level=ConsistencyLevel.QUORUM,
)
session.execute(write, (customer_id, order_time, uuid.uuid4(), 10.0, "paid"))

read = SimpleStatement(
    "SELECT status FROM orders_by_customer WHERE customer_id=%s",
    consistency_level=ConsistencyLevel.QUORUM,
)
row = session.execute(read, (customer_id,)).one()

print(f"QUORUM write + QUORUM read -> status='{row.status}'")
print("\nlevels, weakest -> strongest:  ONE  <  QUORUM / LOCAL_QUORUM  <  ALL")
print("• ONE          : fast, highly available, but a stale replica can answer")
print("• QUORUM       : consistent read (W+R>RF), but may wait across datacenters")
print("• LOCAL_QUORUM : the production default — strong in the local DC, no cross-DC wait")
print("• ALL          : strongest, but one node down = the query fails")

cluster.shutdown()
