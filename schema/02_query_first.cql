USE lab;

-- The rule that breaks a SQL brain: model a table to answer ONE query.
-- No joins, no ad-hoc WHERE. Same data, denormalized into whatever shape each
-- access pattern needs — even if that means storing it twice.

-- Query A: "give me a customer's orders, newest first."
--   partition key = customer_id  -> all of one customer's orders live on one node
--   clustering    = order_time DESC, order_id -> stored pre-sorted, newest first
CREATE TABLE IF NOT EXISTS orders_by_customer (
  customer_id  uuid,
  order_time   timestamp,
  order_id     uuid,
  amount       decimal,
  status       text,
  PRIMARY KEY ((customer_id), order_time, order_id)
) WITH CLUSTERING ORDER BY (order_time DESC, order_id ASC);

-- Query B: "look up a single order by its id."
--   A different question is a different table. We duplicate the row on purpose —
--   storage is cheap, and there are no joins to reassemble it otherwise.
CREATE TABLE IF NOT EXISTS orders_by_id (
  order_id     uuid,
  customer_id  uuid,
  order_time   timestamp,
  amount       decimal,
  status       text,
  PRIMARY KEY ((order_id))
);
