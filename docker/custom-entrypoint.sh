#!/bin/bash
set -e
set -o pipefail

DATA_DIR="/var/lib/impala"
LOG_DIR="$DATA_DIR/logs"

export JAVA_HOME=$(which javac | xargs readlink -f | sed "s:/bin/javac::")

function start_hive_metastore() {
  if [ ! -d "${DATA_DIR}/metastore/metastore_db" ]; then
    schematool -dbType derby -initSchema
  fi
  hive --service metastore &
}

function start_statestored() {
  daemon_entrypoint.sh statestored -log_dir=${DATA_DIR}/logs &
}

function start_catalogd() {
  # Tắt cờ -invalidate_tables_on_memory_pressure để tránh lỗi lặp vô tận (GC spin loop) trên Docker Mac M1
  daemon_entrypoint.sh catalogd -log_dir=${DATA_DIR}/logs \
    -abort_on_config_error=false \
    -catalog_topic_mode=minimal \
    -hms_event_polling_interval_s=0 \
    -invalidate_tables_on_memory_pressure=false &
}

function start_impalad() {
  daemon_entrypoint.sh impalad -log_dir=${DATA_DIR}/logs \
    -abort_on_config_error=false \
    -mem_limit_includes_jvm=true \
    -use_local_catalog=true \
    -rpc_use_loopback=true &
}

mkdir -p $DATA_DIR
mkdir -p $LOG_DIR
start_hive_metastore
start_statestored
start_catalogd
start_impalad
tail -F ${LOG_DIR}/impalad.INFO
