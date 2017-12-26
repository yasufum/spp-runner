#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Run SPP, then QEMU within tmux.

import argparse
import os
import yaml

# params
sess_name = "spp"   # tmux session name
home_dir = os.environ["HOME"]
spp_srcdir = "%s/dpdk-home/spp/src" % home_dir
qemu_hda_dir = "%s/dpdk-home/qemu-hda" % home_dir
work_dir = os.path.dirname(__file__) + "/.."

run_vm_script = "bin/run-vm.py"
hda = "ubuntu-16.04.3-server-amd64.qcow2"
hda_path = "%s/hda/%s" % (qemu_hda_dir, hda)

# Load config
f = open(work_dir + "/conf.yml", "r")
conf = yaml.load(f)
f.close


def parse_args():
    parser = argparse.ArgumentParser(description="Run SPP and VMs")
    parser.add_argument(
        "-t", "--template",
        action="store_true",
        help="Boot template VM")
    parser.add_argument(
        "-p", "--portmask",
        type=str,
        help="Portmask")
    parser.add_argument(
        "-ns", "--nof-sec",
        type=int, default=2,
        help="Number of SPP secondaries")
    parser.add_argument(
        "-nr", "--nof-ring",
        type=int, default=0,
        help="Number of VMs running ring")
    parser.add_argument(
        "-nv", "--nof-vhost",
        type=int, default=0,
        help="Number of VMs running vhost")
    parser.add_argument(
        "-vn", "--vhost-num",
        type=int, default=1,
        help="Number of vhost interfaces")
    parser.add_argument(
        "-nw", "--nof-working",
        type=int, default=1,
        help="Number of working window")
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


def count_ports(portmask, base=16):
    portmask_bin = bin(int(portmask, base))
    bit_ary = portmask_bin.split("b")[1]
    cnt = 0
    for b in list(bit_ary):
        cnt += int(b)
    return cnt


def parse_vdev_opt(opt_str):
    """Parse IDs for vdev option

    It supports two types of description of IDs.
    1. Incremental number of a range ('1-3' or '10-20')
    2. discreted number separated with comma ('1,2,3' or '1,5,8')
    """

    # Return "1-3" as [1,2,3]
    if opt_str.find("-") != -1:
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
            raise(ValueError("Invalid vdev option: %s" % opt_str))


def parse_primary_opts(args, conf):
    coremask = conf["primary"]["coremask"]
    res = "-d %s -c %s" % (spp_srcdir, coremask)

    # Convert portmask to int for adding vdev ports
    if args.portmask:
        portmask = args.portmask
    else:
        portmask = conf["primary"]["portmask"]
    nof_ports = count_ports(conf["primary"]["portmask"])

    if args.vdev:
        res += " --vdev %s" % args.vdev
        nof_ports += 1
    if args.vdev_tap:
        res += " --vdev-tap %s" % args.vdev_tap
        nof_ports += len(parse_vdev_opt(args.vdev_tap))
    if args.vdev_vhost:
        res += " --vdev-vhost %s" % args.vdev_vhost
        nof_ports += len(parse_vdev_opt(args.vdev_vhost))
    res += " -p %s" % portmask

    if nof_ports == count_ports(portmask):
        return res
    else:
        msg = "Portmask '%s!' doesn't match with the number of ports %d!" % (
            portmask, nof_ports)
        raise(ValueError(msg))


def setup_windows(args, conf):
    """Return tmux windows"""

    windows = [
        # spp controller
        {
            "win_name": "ctrler",
            "dir": spp_srcdir,
            "cmd": "python spp.py",
            "opts": "-p %s -s %s" % (
                conf["controller"]["pri_port"],
                conf["controller"]["sec_port"]),
            "enter_key": True
        },

        # spp primary
        {
            "win_name": "pri",
            "dir": work_dir,
            "cmd": "python runscripts/primary.py",
            "opts": parse_primary_opts(args, conf),
            "enter_key": True
        }
    ]

    # spp secondaries
    windows.append({
        "win_name": "sec",
        "dir": work_dir,
        "cmd": "python runscripts/secondaries.py",
        "opts": "--num %s --sppdir %s" % (args.nof_sec, spp_srcdir),
        "enter_key": True
        })

    # VM - ring
    if args.template is True:
        windows.append({
            "win_name": "vm_r%s" % 0,
            "dir": qemu_hda_dir,
            "cmd": "./%s" % run_vm_script,
            "opts": "-t ring -i %s -f %s" % (0, hda_path),
            "enter_key": True
        })
    else:
        if args.nof_ring > 0:
            tmpary = []
            for i in range(0, args.nof_ring):
                tmpary.append(str(conf["vms_ring"][i]["id"]))
            nof_ring_str = ",".join(tmpary)

            windows.append({
                "win_name": "vm_r",
                "dir": qemu_hda_dir,
                "cmd": "./%s" % run_vm_script,
                "opts": "-t ring -i %s -f %s" % (nof_ring_str, hda_path),
                "enter_key": True
            })

    # VM - vhost
    if args.template is True:
        windows.append({
            "win_name": "vm_v%s" % 0,
            "dir": qemu_hda_dir,
            "cmd": "./%s" % run_vm_script,
            "opts": "-t vhost -i %s -f %s" % (0, hda_path),
            "enter_key": True
        })
    else:
        tmpary = []
        if args.nof_vhost > 0:
            for i in range(0, args.nof_vhost):
                tmpary.append(str(conf["vms_vhost"][i]["id"]))

            for vid in tmpary:
                remove_sock(vid)

            # args.nof_vhost is passed to run-vm.py as comma-separated values.
            nof_vhost_str = ",".join(tmpary)
            windows.append({
                "win_name": "vm_v",
                "dir": qemu_hda_dir,
                "cmd": "./%s" % run_vm_script,
                "opts": "-t vhost -i %s -vn %s -f %s" % (
                    nof_vhost_str, args.vhost_num, hda_path
                    ),
                "enter_key": True
                })

    # working windows
    if args.nof_working > 0:
        for i in range(0, args.nof_working):
            windows.append({
                "win_name": "w%d" % i,
                "dir": work_dir,
                "cmd": "",
                "opts": "",
                "enter_key": False
                })

    return windows


def gen_send_keys(win_name, cmd, opts, enter_key):
    """Generate options for tmux windows"""

    if cmd == "":
        send_keys = "tmux send-keys -t %s" % win_name
    elif opts == "":
        send_keys = "tmux send-keys -t %s \"%s\"" % (
            win_name,
            cmd)
    else:
        send_keys = "tmux send-keys -t %s \"%s %s\"" % (
            win_name,
            cmd,
            opts)

    if enter_key is True:
        send_keys += " C-m"

    return send_keys


def remove_sock(sid):
    """remove /tmp/sock* before run vhost VMs"""

    cmd = "sudo rm -f /tmp/sock%s*" % sid
    os.system(cmd)


def main():
    args = parse_args()

    cmd = []  # contains tmux commands
    for w in setup_windows(args, conf):
        if len(cmd) == 0:
            new_sess = "tmux new-session -d -s %s -n %s -c %s" % (
                sess_name,
                w["win_name"],
                w["dir"])
            send_keys = gen_send_keys(
                w["win_name"], w["cmd"], w["opts"], w["enter_key"])
            cmd.append(new_sess)
            cmd.append(send_keys)
        else:
            new_win = "tmux new-window -n %s -c \"%s\"" % (
                w["win_name"],
                w["dir"])
            send_keys = gen_send_keys(
                w["win_name"], w["cmd"], w["opts"], w["enter_key"])
            cmd.append(new_win)
            cmd.append(send_keys)

    cmd.append("tmux attach -t %s" % sess_name)

    for c in cmd:
        print(c)
        os.system(c)


if __name__ == '__main__':
    main()
