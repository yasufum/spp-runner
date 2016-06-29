#!/bin/sh

CLIENT_ID=$1
COREMASK=$2
SEC_PORT=$3

SPPDIR=$HOME/dpdk-home/spp/examples/multi_process/patch_panel

echo $SPPDIR/nfv/nfv/x86_64-ivshmem-linuxapp-gcc/app/spp_nfv \
  -c ${COREMASK} -n 4 --proc-type=secondary \
  -- -n ${CLIENT_ID} -s 192.168.122.1:${SEC_PORT}
$SPPDIR/nfv/nfv/x86_64-ivshmem-linuxapp-gcc/app/spp_nfv \
  -c ${COREMASK} -n 4 --proc-type=secondary \
  -- -n ${CLIENT_ID} -s 192.168.122.1:${SEC_PORT}
  2>&1 > log/secondary-${CLIENT_ID}.log
