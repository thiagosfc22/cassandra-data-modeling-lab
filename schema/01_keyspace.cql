-- A keyspace is Cassandra's top-level namespace (think "database").
-- Replication is defined HERE, per keyspace: how many copies of every row exist,
-- and how they're spread across the topology.

CREATE KEYSPACE IF NOT EXISTS lab
WITH replication = {
  'class': 'SimpleStrategy',   -- single datacenter, fine for a local lab
  'replication_factor': 1      -- RF = copies per row. 1 here because the lab is one node.
};

-- In production you'd use NetworkTopologyStrategy so replicas are placed across
-- racks/datacenters, and RF ≥ 3 so the quorum math has room to work:
--
--   CREATE KEYSPACE app WITH replication = {
--     'class': 'NetworkTopologyStrategy', 'dc1': 3
--   };
--
-- With RF=3, QUORUM = 2, and a QUORUM write + QUORUM read (2 + 2 > 3) gives you
-- a consistent read with no leader. On this RF=1 lab every level resolves to the
-- single node — you still see the API, just not the multi-node guarantee.
