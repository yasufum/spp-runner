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
run_script = "run-vm.py"
work_dir = os.path.dirname(__file__) + "/.."
qemu_script_dir = "%s/qemu-hda/runscripts" % work_dir
hda = "ubuntu-16.04.3-server-amd64.qcow2"
hda_path = "%s/../qemu-hda/iso/%s" % (work_dir, hda)

# Load config
f = open(work_dir + "/conf.yml", "r")
y = yaml.load(f)
f.close

# spp controller
ctrler = y["controller"]

# spp primary
primary = y["primary"]

# spp secondaries
secondaries = y["secondaries"]

# ring VM
vms_ring = y["vms_ring"]

# vhost VM
vms_vhost = y["vms_vhost"]


def parse_args():
    parser = argparse.ArgumentParser(description="Run SPP and VMs")
    parser.add_argument(
        "-t", "--template",
        action="store_true",
        help="Boot template VM")
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
    return parser.parse_args()


# return tmux windows
def setup_windows(args):
    windows = [
        # spp controller
        {
            "win_name": "ctrler",
            "dir": spp_srcdir,
            "cmd": "python spp.py",
            "opts": "-p %s -s %s" % (
                ctrler["pri_port"], ctrler["sec_port"]),
            "enter_key": True
        },

        # spp primary
        {
            "win_name": "pri",
            "dir": work_dir,
            "cmd": "python runscripts/primary.py",
            "opts": "-d %s -c %s -ch %s -cp %s" % (
                spp_srcdir, primary["coremask"],
                ctrler["host"],
                ctrler["pri_port"]),
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
            "dir": qemu_script_dir,
            "cmd": "./%s" % run_script,
            "opts": "-t ring -i %s -f %s" % (0, hda_path),
            "enter_key": True
        })
    else:
        if args.nof_ring > 0:
            tmpary = []
            for i in range(0, args.nof_ring):
                tmpary.append(str(vms_ring[i]["id"]))
            nof_ring_str = ",".join(tmpary)

            windows.append({
                "win_name": "vm_r",
                "dir": qemu_script_dir,
                "cmd": "./%s" % run_script,
                "opts": "-t ring -i %s -f %s" % (nof_ring_str, hda_path),
                "enter_key": True
            })

    # VM - vhost
    if args.template is True:
        windows.append({
            "win_name": "vm_v%s" % 0,
            "dir": qemu_script_dir,
            "cmd": "./%s" % run_script,
            "opts": "-t vhost -i %s -f %s" % (0, hda_path),
            "enter_key": True
        })
    else:
        tmpary = []
        if args.nof_vhost > 0:
            for i in range(0, args.nof_vhost):
                tmpary.append(str(vms_vhost[i]["id"]))

            for vid in tmpary:
                remove_sock(vid)

            # args.nof_vhost is passed to run-vm.py as comma-separated values.
            nof_vhost_str = ",".join(tmpary)
            windows.append({
                "win_name": "vm_v",
                "dir": qemu_script_dir,
                "cmd": "./%s" % run_script,
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


# Generate options for tmux windows
def gen_send_keys(win_name, cmd, opts, enter_key):
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


# remove /tmp/sock* before run vhost VMs
def remove_sock(sid):
    cmd = "sudo rm -f /tmp/sock%s*" % sid
    os.system(cmd)


def main():
    args = parse_args()

    cmd = []  # contains tmux commands
    for w in setup_windows(args):
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
