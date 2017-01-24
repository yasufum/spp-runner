#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Run SPP, then QEMU within tmux.

import os
import sys
import argparse
import yaml

# params
sess_name = "spp"
default_nof_sec = 2
run_dir = "."
spp_srcdir = "$HOME/dpdk-home/spp/src"
qemu_dir = "$HOME/dpdk-home/qemu-setup/runscripts"

# Load config
f = open("conf.yml", "r")
y = yaml.load(f)
f.close

# spp controller
ctrler = y["controller"]

# spp primary (2 cores per process)
primary = y["primary"]

# spp secondaries (2 cores per process)
secondaries = y["secondaries"]

# ring VM
ring_sh = "ring.sh"
vms_ring = y["vms_ring"]

# vhost VM
vhost_sh = "vhost.sh"
vms_vhost = y["vms_vhost"]

parser = argparse.ArgumentParser(description="Run SPP and VMs")
parser.add_argument(
        "-ns", "--nof-sec",
        type=int, default=2,
        help="Number of SPP secondaries")
parser.add_argument(
        "-nr", "--nof-ring",
        type=int, default=1,
        help="Number of VMs running ring")
parser.add_argument("-nv", "--nof-vhost",
        type=int, default=1,
        help="Number of VMs running vhost")
args = parser.parse_args()


# return tmux windows
def setup_windows(nof_sec, nof_ring, nof_vhost):
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
                "dir": run_dir,
                "cmd": "sh runscripts/primary.sh",
                "opts": "%s %s %s %s" % (
                    spp_srcdir, primary["coremask"],
                    ctrler["host"],
                    ctrler["pri_port"]),
                "enter_key": True
                }
            ]

    # spp secondaries
    home_dir = os.environ["HOME"]
    spp_dir = "%s/dpdk-home/spp/src" % home_dir
    windows.append({
        "win_name": "sec",
        "dir": run_dir,
        "cmd": "sudo python runscripts/secondaries.py",
        "opts": "--num %s --sppdir %s" % (nof_sec, spp_dir),
        "enter_key": True
        })

    # VM - ring
    for i in range(nof_ring):
        windows.append({
            "win_name": "vm_r%s" % i,
            "dir": qemu_dir,
            "cmd": "./%s" % ring_sh,
            "opts": "%s" % vms_ring[i]["id"],
            "enter_key": True
            })

    # VM - vhost
    for i in range(nof_vhost):
        windows.append({
            "win_name": "vm_v%s" % i,
            "dir": qemu_dir,
            "cmd": "./%s" % vhost_sh,
            "opts": "%s" % vms_vhost[i]["id"],
            "enter_key": True
            })
            
    # working dir for login VMs
    windows.append({
        "win_name": "wdir",
        "dir": run_dir,
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

    if enter_key == True:
        send_keys += " C-m"

    return send_keys


def main():
    nof_sec = args.nof_sec
    nof_ring = args.nof_ring
    nof_vhost = args.nof_vhost

    cmd = []  # contains tmux commands
    for w in setup_windows(nof_sec, nof_ring, nof_vhost):
        if len(cmd) == 0:
            new_sess = "tmux new-session -d -s %s -n %s -c %s" % (
                    sess_name,
                    w["win_name"],
                    w["dir"])
            send_keys = gen_send_keys(w["win_name"], w["cmd"], w["opts"], w["enter_key"])
            cmd.append(new_sess)
            cmd.append(send_keys)
        else:
            new_win = "tmux new-window -n %s -c \"%s\"" % (
                    w["win_name"],
                    w["dir"])
            send_keys = gen_send_keys(w["win_name"], w["cmd"], w["opts"], w["enter_key"])
            cmd.append(new_win)
            cmd.append(send_keys)
  
    cmd.append("tmux attach -t %s" % sess_name)
   
  
    for c in cmd:
        print(c)
        os.system(c)


if __name__ == '__main__':
    main()
