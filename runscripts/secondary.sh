#!/bin/sh

SPPDIR=$1
CLIENT_ID=$2
COREMASK=$3
CTR_HOST=$4
CTR_SEC_PORT=$5

sudo -E $SPPDIR/nfv/nfv/x86_64-ivshmem-linuxapp-gcc/app/spp_nfv \
  -c ${COREMASK} -n 4 --proc-type=secondary \
  -- \
  -n ${CLIENT_ID} -s ${CTR_HOST}:${CTR_SEC_PORT}
#  2>&1 > log/secondary-${CLIENT_ID}.log
