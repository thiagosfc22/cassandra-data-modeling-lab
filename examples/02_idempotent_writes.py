"""INSERT is an upsert. Writing the same primary key twice overwrites — it never
duplicates. That's why a Cassandra write pipeline is idempotent for free: you can
reprocess the same batch and nothing doubles. Conflicts between versions resolve
by last-write-wins on the write timestamp.

(This is the same idea as an incremental MERGE keyed on a natural key in a Spark
pipeline — reprocess-safe by construction.)

Run: python examples/02_idempotent_writes.py
"""
import uuid
from datetime import datetime, timezone

from common import get_session

cluster, session = get_session()

customer_id = uuid.uuid4()
order_id = uuid.uuid4()
order_time = datetime.now(timezone.utc)

insert = session.prepare(
    "INSERT INTO orders_by_customer "
    "(customer_id, order_time, order_id, amount, status) VALUES (?, ?, ?, ?, ?)"
)

# Same primary key (customer_id, order_time, order_id) written three times;
# only status changes. Last write wins.
for status in ["pending", "paid", "shipped"]:
    session.execute(insert, (customer_id, order_time, order_id, 42.00, status))

rows = list(session.execute(
    "SELECT order_id, status FROM orders_by_customer WHERE customer_id=%s",
    (customer_id,),
))

print(f"3 writes to the same key -> {len(rows)} row, status='{rows[0].status}'")
assert len(rows) == 1 and rows[0].status == "shipped"
print("idempotent: same key overwrites, never duplicates (last-write-wins)")

cluster.shutdown()
