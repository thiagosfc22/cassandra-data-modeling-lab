# Cassandra Data Modeling Lab

[🇧🇷 Português](README.pt-BR.md) · **🇬🇧 English**

A hands-on lab for the part of Cassandra that trips up everyone coming from SQL:
you don't model your data and then query it — you model your data **around the
query**. No joins, no ad-hoc `WHERE`, denormalize on purpose. Get that one shift
and the rest of Cassandra (the storage engine, the consistency knobs) falls into
place.

Every concept here is a runnable file against a real Cassandra 5.0 node in
Docker. The schema is CQL you can read top to bottom; the examples are small
Python scripts that each prove one idea and assert the result.

## The shift, in one line

A relational schema is normalized around *entities* and joined at query time.
A Cassandra schema is denormalized around *queries* — one table per access
pattern, the same data duplicated into whatever shape each read needs. There is
no join to reassemble it later, so you decide the shape up front.

## What's inside

| Concept | The one idea | File |
|--------|-------------|------|
| **Keyspace & replication** | Replication factor (RF) is set per keyspace — how many copies of every row exist. | [`schema/01_keyspace.cql`](schema/01_keyspace.cql) |
| **Query-first modeling** | One table per query. Same order stored two ways so two lookups are each one seek. | [`schema/02_query_first.cql`](schema/02_query_first.cql) |
| **Partition & clustering keys** | `PRIMARY KEY ((partition), clustering)` — partition picks the *node*, clustering picks the *sort order within it*. | [`examples/04_partition_and_clustering.py`](examples/04_partition_and_clustering.py) |
| **Time-series bucketing** | Bucket the partition key by time so a partition can't grow forever. | [`schema/03_timeseries.cql`](schema/03_timeseries.cql) |
| **Idempotent writes** | `INSERT` is an upsert; same key overwrites, never duplicates. Reprocess-safe for free. | [`examples/02_idempotent_writes.py`](examples/02_idempotent_writes.py) |
| **Tunable consistency** | Per-query consistency levels; `W + R > RF` guarantees a consistent read with no leader. | [`examples/03_consistency_levels.py`](examples/03_consistency_levels.py) |
| **Lightweight transactions** | Compare-and-set via Paxos (`IF NOT EXISTS`) — correct, but expensive; use sparingly. | [`examples/05_lightweight_transactions.py`](examples/05_lightweight_transactions.py) |
| **Anti-patterns** | Large partitions, `ALLOW FILTERING`, bad secondary indexes, tombstone pileups. | [`schema/99_antipatterns.cql`](schema/99_antipatterns.cql) |

<p align="center">
  <img src="docs/tunable-consistency.png" width="520" alt="With RF=3, a QUORUM write reaches 2 nodes and a QUORUM read reaches 2 nodes; since W + R > RF the two sets always overlap on at least one node that holds the latest write.">
  <br><em>Tunable consistency at a glance — why W + R &gt; RF gives a consistent read with no leader (<a href="examples/03_consistency_levels.py">03_consistency_levels.py</a>).</em>
</p>

## Why writes are cheap and reads need good modeling

Cassandra stores data in an **LSM tree**: a write appends to a commit log and an
in-memory memtable, then returns — that's it. When the memtable fills, it's
flushed to an **immutable SSTable** on disk. Because SSTables never change, an
`UPDATE` just writes a newer-timestamped version and a `DELETE` writes a
**tombstone**; background **compaction** later merges SSTables, keeps the latest
version (last-write-wins), and drops old tombstones. So writes are append-only
and fast, but a read may have to reconcile several SSTables — which is exactly
why the partition/clustering design matters so much.

## Running it

Requirements: Docker, Python 3.9+, and `make`.

```bash
pip install -r requirements.txt

make schema     # start Cassandra, wait for it, load the keyspace + tables
make examples   # run all five Python examples in order
make cqlsh      # optional: an interactive CQL shell
make down       # stop and remove the cluster
```

Two things worth knowing, both learned the hard way building this lab:

- **Cassandra is memory-hungry.** `docker-compose.yml` caps the JVM heap at 512M
  so it fits a laptop; give Docker at least ~2 GB or the container gets
  OOM-killed (exit 137) on first boot. First boot takes ~60–90s.
- **Compose command.** The `Makefile` calls the standalone `docker-compose`
  binary. If yours is the plugin form, run `make COMPOSE="docker compose" schema`.

## Single node vs. production

This lab is **one node with RF=1**, so every consistency level resolves to that
node — you see the API and the arithmetic, not the multi-node guarantee. In a
real cluster you'd use `NetworkTopologyStrategy` with RF=3, where `QUORUM`=2 and
a `QUORUM` write + `QUORUM` read (2 + 2 > 3) is what actually buys a consistent
read with no leader. In multi-datacenter setups the everyday choice is
`LOCAL_QUORUM`: strong consistency in the local DC without waiting on another
continent.

## Where this fits

Cassandra is the serving layer — fast writes, key-based reads, no joins or
cross-partition aggregation. The heavy analytics run elsewhere: a Spark job
reads Cassandra by token range and does the group-bys and rollups. And the
idempotent-upsert property here is the same reprocess-safety you want from an
incremental `MERGE` in a Spark pipeline — the two systems meet at "rerunning a
batch changes nothing."
