#!/usr/bin/env python
# coding: utf-8

import os
import argparse
import subprocess

def parse_args():
    parser = argparse.ArgumentParser(description="Launch primary process")
    
    parser.add_argument(
            "-d", "--sppdir", 
            type=str, default='.',
            help="SPP dir"
            )
    parser.add_argument(
            "-c", "--coremask", 
            type=str, default='0x03',
            help="coremask"
            )
    parser.add_argument(
            "-p", "--portmask", 
            type=str, default='0x0f',
            help="portmask"
            )
    parser.add_argument(
            "-ch", "--ctrl-host", 
            type=str, default='127.0.0.1',
            help="controller ipaddr"
            )
    parser.add_argument(
            "-cp", "--ctrl-port", 
            type=int, default=5555,
            help="controller port num"
            )
    parser.add_argument(
            "-n", "--num-ring", 
            type=int, default=10,
            help="The number of rings"
            )
    parser.add_argument(
            "-m", "--mem", 
            type=int, default=1024,
            help="memory size"
            )
    parser.add_argument(
            "-mc", "--mem-chan", 
            type=int, default=4,
            help="The number of memory channels"
            )
    return parser.parse_args()


def main():
    args = parse_args()
    cmd_path = '%s/primary/%s/spp_primary' % (
            args.sppdir, os.getenv('RTE_TARGET')
            )
    if not os.path.isfile(cmd_path):
        cmd_path = '%s/primary/src/primary/%s/spp_primary' % (
                args.sppdir, os.getenv('RTE_TARGET')
                )
    subprocess.call('sudo pwd', shell=True)
    cmd = 'sudo -E %s \\\n' % cmd_path
    cmd += '  -c %s \\\n' % args.coremask
    cmd += '  -n %d \\\n' % args.mem_chan
    cmd += '  --socket-mem %d \\\n' % args.mem
    cmd += '  --huge-dir=/dev/hugepages \\\n'
    cmd += '  --proc-type=primary \\\n'
    cmd += '  -- \\\n'
    cmd += '  -p %s \\\n' % args.portmask
    cmd += '  -n %d \\\n' % args.num_ring
    cmd += '  -s %s:%d \\\n' % (args.ctrl_host, args.ctrl_port)
    
    print(cmd)
    subprocess.call(cmd, shell=True)

if __name__ == '__main__':
    main()