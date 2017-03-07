#!/bin/sh 

SPPDIR=$1
COREMASK=$2
CTR_HOST=$3
CTR_PRI_PORT=$4

PORTMASK=0x0f
NUM_RINGS=10
SOCK_MEM=1024
NUM_MEM_CHAN=4

sudo -E ${SPPDIR}/primary/src/primary/x86_64-ivshmem-linuxapp-gcc/spp_primary \
  -c ${COREMASK} -n ${NUM_MEM_CHAN} --socket-mem ${SOCK_MEM} \
  --huge-dir=/dev/hugepages \
  --proc-type=primary \
  -- \
  -p ${PORTMASK} -n ${NUM_RINGS} \
  -s ${CTR_HOST}:${CTR_PRI_PORT} #\
#  2>&1 > log/primary.log
