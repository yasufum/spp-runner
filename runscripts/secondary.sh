#!/bin/sh

SPPDIR=$1
CLIENT_ID=$2
COREMASK=$3
CTR_HOST=$4
CTR_SEC_PORT=$5

NUM_MEM_CHAN=4

LOGFILE=log/secondary-${CLIENT_ID}.log

echo "Runnig spp sec"${CLIENT_ID}" ..."
echo "log file: "${LOGFILE}

sudo -E ${SPPDIR}/nfv/src/nfv/x86_64-ivshmem-linuxapp-gcc/app/spp_nfv \
  -c ${COREMASK} -n ${NUM_MEM_CHAN} --proc-type=secondary \
  -- \
  -n ${CLIENT_ID} -s ${CTR_HOST}:${CTR_SEC_PORT} \
  2>&1 > ${LOGFILE} \
  &
