#!/usr/bin/env python
# coding: utf-8

# Run multiple spp secondaries in a single term

import os
import sys
import yaml
import argparse
import subprocess

# This command is intended to run from parent dir,
# so config file must be in the dir.
conf_path = "conf.yml"

home_dir = os.environ["HOME"]

def parse_args():
    parser = argparse.ArgumentParser(description="Start up spp secondaries")
    parser.add_argument(
            "-i", "--id",
            type=int,
            help="Secondary id")
    parser.add_argument(
            "-n", "--num",
            type=int, default=2,
            help="Number of SPP secondaries")
    parser.add_argument(
            "-d", "--sppdir",
            type=str, default="%s/dpdk-home/spp/src" % home_dir,
            help="SPP's working dir")
    parser.add_argument(
            "-nm", "--num-memchan",
            type=int, default=4,
            help="Number of memory channels")
    parser.add_argument(
            "-ch", "--ctr-host",
            type=str, default='127.0.0.1',
            help="IP address of SPP controller")
    parser.add_argument(
            "-cp", "--ctr-port",
            type=int, default=6666,
            help="Port of SPP controller")
    return parser.parse_args()

def main():
    # Load config
    f = open(conf_path, "r")
    y = yaml.load(f)
    f.close()

    args = parse_args()

    if args.id != None: # run specified sec
        ent = y["secondaries"][args.id-1] # sec id is assumed starting from 1
        logfile = 'log/secondary-%d.log' % ent["id"]
        cmd = ['sudo', '-E',
                '%s/nfv/src/nfv/x86_64-ivshmem-linuxapp-gcc/app/spp_nfv' % args.sppdir,
                '-c', ent["coremask"],
                '-n', str(args.num_memchan),
                '--proc-type=secondary',
                '--',
                '-n', str(ent["id"]),
                '-s', '%s:%d' % (args.ctr_host, args.ctr_port),
                '2>&1 > %s' % logfile
                ]
        subprocess.call(cmd)
    else: # run all of secondaries
        for i in range(0, args.num):
            ent = y["secondaries"][i]
            logfile = 'log/secondary-%d.log' % ent["id"]
            cmd = ['sudo', '-E',
                    '%s/nfv/src/nfv/x86_64-ivshmem-linuxapp-gcc/app/spp_nfv' % args.sppdir,
                    '-c', ent["coremask"],
                    '-n', str(args.num_memchan),
                    '--proc-type=secondary',
                    '--',
                    '-n', str(ent["id"]),
                    '-s', '%s:%d' % (args.ctr_host, args.ctr_port),
                    '2>&1 > %s' % logfile
                    ]
            subprocess.call(cmd)


if __name__ == '__main__':
    main()
