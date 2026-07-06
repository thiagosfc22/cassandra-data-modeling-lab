# A tiny driver for the lab. `make schema` gets you from zero to a loaded cluster.
# COMPOSE defaults to the standalone `docker-compose` binary. If your Docker uses
# the plugin form, run: make COMPOSE="docker compose" up
COMPOSE ?= docker-compose
PY ?= python

.PHONY: up schema examples down logs cqlsh

up:  ## start the single-node Cassandra lab and wait until it accepts CQL
	$(COMPOSE) up -d
	@echo "waiting for Cassandra to accept CQL (first boot ~60-90s)..."
	@until docker exec cassandra-lab cqlsh -e 'describe keyspaces' >/dev/null 2>&1; do \
		printf '.'; sleep 3; done; echo " ready."

schema: up  ## load keyspace + tables
	@for f in schema/01_keyspace.cql schema/02_query_first.cql schema/03_timeseries.cql; do \
		echo "loading $$f"; docker exec -i cassandra-lab cqlsh < $$f; done

examples:  ## run every Python example in order
	@for f in examples/01_connect.py examples/02_idempotent_writes.py \
		examples/03_consistency_levels.py examples/04_partition_and_clustering.py \
		examples/05_lightweight_transactions.py; do \
		echo "\n=== $$f ==="; $(PY) $$f; done

cqlsh:  ## open an interactive CQL shell
	docker exec -it cassandra-lab cqlsh

logs:  ## tail Cassandra logs
	docker logs -f cassandra-lab

down:  ## stop and remove the lab (data is discarded)
	$(COMPOSE) down
