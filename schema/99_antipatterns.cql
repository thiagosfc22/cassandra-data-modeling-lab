-- Anti-patterns. These are here to READ, not to run. Each one is a good idea in
-- a relational database and a trap in Cassandra.

-- 1) Unbounded partition — no time bucket. Grows for the life of the device
--    until one partition is multiple GB on a single node (a "large partition").
--      CREATE TABLE readings_bad (
--        device_id uuid, reading_at timestamp, celsius float,
--        PRIMARY KEY ((device_id), reading_at));

-- 2) Low-cardinality partition key — every row for 'BR' hashes to the same node.
--    One giant partition per country = a permanent hot node. This is the
--    Cassandra equivalent of data skew.
--      PRIMARY KEY ((country), city, ...)

-- 3) ALLOW FILTERING — Cassandra refuses this query unless you force it, because
--    it's a full-cluster scan with no partition key. Needing it almost always
--    means the table is modeled for the wrong query. Build a query table instead.
--      SELECT * FROM orders_by_customer WHERE status = 'paid' ALLOW FILTERING;

-- 4) Secondary index on a high-cardinality or frequently-updated column — fans
--    the read across every node and accumulates tombstones. Prefer a purpose-
--    built table that IS the index for that access pattern.
--      CREATE INDEX ON orders_by_customer (status);

-- 5) Delete-heavy workload / short TTLs on wide partitions — every delete writes
--    a tombstone, and reads must scan past them. Enough tombstones and a read of
--    "almost no data" times out. Model so you drop whole partitions instead.
