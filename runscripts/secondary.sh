#!/bin/sh

SPPDIR=$1
CLIENT_ID=$2
COREMASK=$3
SEC_PORT=$4

#echo sudo -b -E $SPPDIR/nfv/nfv/x86_64-ivshmem-linuxapp-gcc/app/spp_nfv \
#  -c ${COREMASK} -n 4 --proc-type=secondary \
#  -- -n ${CLIENT_ID} -s 192.168.122.1:${SEC_PORT}

#sudo -b -E $SPPDIR/nfv/nfv/x86_64-ivshmem-linuxapp-gcc/app/spp_nfv \
sudo -E $SPPDIR/nfv/nfv/x86_64-ivshmem-linuxapp-gcc/app/spp_nfv \
  -c ${COREMASK} -n 4 --proc-type=secondary \
  -- -n ${CLIENT_ID} -s 192.168.122.1:${SEC_PORT}
#  2>&1 > log/secondary-${CLIENT_ID}.log
