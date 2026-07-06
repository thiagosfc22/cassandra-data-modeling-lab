USE lab;

-- Time-series / event data is the classic Cassandra use case — and the classic
-- way to blow it up. Partition only by device_id and that partition grows
-- forever (one row per reading, for the life of the device) until it's a
-- multi-gigabyte hot partition pinned to a single node.
--
-- Fix: bucket the partition key by time. (device_id, day) bounds each partition
-- to one day of readings, and you query a bucket (or a small range) at a time.
CREATE TABLE IF NOT EXISTS readings_by_device (
  device_id   uuid,
  day         date,          -- the time bucket — part of the partition key
  reading_at  timestamp,
  celsius     float,
  PRIMARY KEY ((device_id, day), reading_at)
) WITH CLUSTERING ORDER BY (reading_at DESC);

-- Picking the bucket size is a real design decision: the bucket must hold a
-- workable number of rows (not too many -> large partition; not too few -> you
-- read across too many partitions). Day is a sensible default for sensor data.
