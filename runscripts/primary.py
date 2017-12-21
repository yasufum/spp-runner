#!/usr/bin/env python
# coding: utf-8

import argparse
import os
import subprocess


def parse_args():
    parser = argparse.ArgumentParser(description="Launch primary process")

    parser.add_argument(
        "-d", "--sppdir",
        type=str, default='.',
        help="SPP dir")
    parser.add_argument(
        "-c", "--coremask",
        type=str, default='0x03',
        help="coremask")
    parser.add_argument(
        "-p", "--portmask",
        type=str, default='0x03',
        help="portmask")
    parser.add_argument(
        "-ch", "--ctrl-host",
        type=str, default='127.0.0.1',
        help="controller ipaddr")
    parser.add_argument(
        "-cp", "--ctrl-port",
        type=int, default=5555,
        help="controller port num")
    parser.add_argument(
        "-n", "--num-ring",
        type=int, default=10,
        help="The number of rings")
    parser.add_argument(
        "-m", "--mem",
        type=int, default=1024,
        help="memory size")
    parser.add_argument(
        "-mc", "--mem-chan",
        type=int, default=4,
        help="The number of memory channels")
    parser.add_argument(
        "-vd", "--vdev",
        type=str, nargs='*',
        help="vdev options, separate with space if two or more")
    parser.add_argument(
        "-vdt", "--vdev-tap",
        type=str,
        help="TUN/TAP vdev IDs, assing '1-3' or '1,2,3' for three IDs")
    parser.add_argument(
        "-vdv", "--vdev-vhost",
        type=str,
        help="vhost vdev IDs, assing '1-3' or '1,2,3' for three IDs")
    return parser.parse_args()


def parse_vdev_opt(opt_str):
    """Parse IDs for vdev option

    It supports two types of description of IDs.
    1. Incremental number of a range ('1-3' or '10-20')
    2. discreted number separated with comma ('1,2,3' or '1,5,8')
    """

    # Return "1-3" as [1,2,3]
    if opt_str.find("-") != -1:
        print(opt_str.find("-"))
        print("opt_str: %s" % opt_str)
        tmp = opt_str.split("-")
        return range(int(tmp[0]), int(tmp[1])+1)

    # Return "1,3,5" as [1,3,5]
    elif opt_str.find(",") != -1:
        ary = []
        for s in opt_str.split(","):
            ary.append(int(s))
        return ary
    # Return "1" as [1], or raise if invalid option
    else:
        import re
        matched = re.match(r"\d+", opt_str)
        if matched:
            return [int(opt_str)]
        else:
            raise("Invalid vdev option!")


def clean_sock_file(sock_id):
    """Remove socket file before creating vhost interface

    Argument ids is expected to be an int.
    """

    sock_dir = "/tmp"
    cmd = "sudo rm -f %s/sock%d" % (sock_dir, sock_id)
    subprocess.call(cmd, shell=True)


def main():
    args = parse_args()
    cmd_path = '%s/primary/%s/spp_primary' % (
        args.sppdir, os.getenv('RTE_TARGET'))

    if not os.path.isfile(cmd_path):
        cmd_path = '%s/primary/src/primary/%s/spp_primary' % (
            args.sppdir, os.getenv('RTE_TARGET'))

    subprocess.call('sudo pwd', shell=True)
    cmd = 'sudo -E %s \\\n' % cmd_path
    cmd += '  -c %s \\\n' % args.coremask
    cmd += '  -n %d \\\n' % args.mem_chan
    cmd += '  --socket-mem %d \\\n' % args.mem
    cmd += '  --huge-dir=/dev/hugepages \\\n'
    cmd += '  --proc-type=primary \\\n'
    if args.vdev:
        for vd in args.vdev:
            cmd += '  --vdev \'%s\' \\\n' % vd
    if args.vdev_tap:
        vdev_ary = parse_vdev_opt(args.vdev_tap)
        for i in vdev_ary:
            opt = 'net_tap%d,iface=vtap%d' % (i, i)
            cmd += '  --vdev \'%s\' \\\n' % opt
    if args.vdev_vhost:
        vdev_ary = parse_vdev_opt(args.vdev_vhost)
        for i in vdev_ary:
            clean_sock_file(i)
            nof_q = 1  # Number of vhost queues
            opt = 'net_vhost%d,iface=/tmp/sock%d,queues=%d' % (
                i, i, nof_q)
            cmd += '  --vdev \'%s\' \\\n' % opt
    cmd += '  -- \\\n'
    cmd += '  -p %s \\\n' % args.portmask
    cmd += '  -n %d \\\n' % args.num_ring
    cmd += '  -s %s:%d \\\n' % (args.ctrl_host, args.ctrl_port)

    print(cmd)
    subprocess.call(cmd, shell=True)


if __name__ == '__main__':
    main()
