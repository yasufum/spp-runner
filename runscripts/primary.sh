#!/bin/sh 

SPPDIR=$1
CTR_HOST=$2
CTR_PRI_PORT=$3
NUM_RINGS=10

sudo -E $SPPDIR/primary/src/primary/x86_64-ivshmem-linuxapp-gcc/spp_primary \
  -c 0x02 -n 4 --socket-mem 1024 \
  --huge-dir=/dev/hugepages \
  --proc-type=primary \
  -- \
  -p 0x03 -n ${NUM_RINGS} \
  -s ${CTR_HOST}:${CTR_PRI_PORT} #\
#  2>&1 > log/primary.log
