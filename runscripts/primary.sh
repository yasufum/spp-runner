#!/bin/sh 

SPPDIR=$1
COREMASK=$2
CTR_HOST=$3
CTR_PRI_PORT=$4
PORTMASK=0x03
NUM_RINGS=10

sudo -E ${SPPDIR}/primary/src/primary/x86_64-ivshmem-linuxapp-gcc/spp_primary \
  -c ${COREMASK} -n 4 --socket-mem 1024 \
  --huge-dir=/dev/hugepages \
  --proc-type=primary \
  -- \
  -p ${PORTMASK} -n ${NUM_RINGS} \
  -s ${CTR_HOST}:${CTR_PRI_PORT} #\
#  2>&1 > log/primary.log
