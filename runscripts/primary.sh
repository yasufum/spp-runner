#!/bin/sh 

SPPDIR=$HOME/dpdk-home/spp/examples/multi_process/patch_panel

sudo $SPPDIR/primary/primary/x86_64-ivshmem-linuxapp-gcc/spp_primary \
  -c 0x02 -n 4 --socket-mem 1024 \
  --huge-dir=/dev/hugepages \
  --proc-type=primary \
  -- -p 0x03 -n 4 -s 192.168.122.1:5555
