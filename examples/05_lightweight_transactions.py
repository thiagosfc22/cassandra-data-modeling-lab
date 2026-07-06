"""When you genuinely need linearizability — "insert only if it doesn't exist",
"update only if the current value is X" — Cassandra offers Lightweight
Transactions (compare-and-set) via an IF clause, backed by Paxos consensus.

They're correct but expensive: several consensus round-trips per operation. So
they're the exception, not the pattern. If you reach for them constantly, the
data model is fighting you.

Run: python examples/05_lightweight_transactions.py
"""
import uuid
from datetime import datetime, timezone

from common import get_session

cluster, session = get_session()

order_id = uuid.uuid4()
customer_id = uuid.uuid4()
order_time = datetime.now(timezone.utc)

insert_if_new = (
    "INSERT INTO orders_by_id "
    "(order_id, customer_id, order_time, amount, status) "
    "VALUES (%s, %s, %s, %s, %s) IF NOT EXISTS"
)

first = session.execute(
    insert_if_new, (order_id, customer_id, order_time, 99.0, "paid")
).one()
print(f"first insert IF NOT EXISTS -> applied={first.applied}")

second = session.execute(
    insert_if_new, (order_id, customer_id, order_time, 99.0, "paid")
).one()
print(f"same insert again          -> applied={second.applied}")

assert first.applied is True and second.applied is False
print("LWT gave us compare-and-set via Paxos — correct, but pay for it sparingly")

cluster.shutdown()
