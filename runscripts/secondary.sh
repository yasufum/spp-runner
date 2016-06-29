#!/bin/sh

COREMASK=$1
CLIENT_ID=$2

SPPDIR=$HOME/dpdk-home/spp/examples/multi_process/patch_panel

sudo $SPPDIR/nfv/nfv/x86_64-ivshmem-linuxapp-gcc/app/spp_nfv \
  -c ${COREMASK} -n 4 --proc-type=secondary \
  -- -n ${CLIENT_ID} -s 192.168.122.1:6666
