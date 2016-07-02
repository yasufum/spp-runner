#!/bin/sh 

PRI_PORT=$1
SPPDIR=$HOME/dpdk-home/spp/examples/multi_process/patch_panel
NUM_RINGS=8

#echo sudo -b -E $SPPDIR/primary/primary/x86_64-ivshmem-linuxapp-gcc/spp_primary \
#  -c 0x02 -n 4 --socket-mem 1024 \
#  --huge-dir=/dev/hugepages \
#  --proc-type=primary \
#  -- -p 0x03 -n 4 -s 192.168.122.1:${PRI_PORT}\
#  2>&1 > log/primary.log

#sudo -b -E $SPPDIR/primary/primary/x86_64-ivshmem-linuxapp-gcc/spp_primary \
sudo -E $SPPDIR/primary/primary/x86_64-ivshmem-linuxapp-gcc/spp_primary \
  -c 0x02 -n 4 --socket-mem 1024 \
  --huge-dir=/dev/hugepages \
  --proc-type=primary \
  -- \
  -p 0x03 -n ${NUM_RINGS} \
  -s 192.168.122.1:${PRI_PORT} #\
#  2>&1 > log/primary.log
