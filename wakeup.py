#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Run SPP, then QEMU within tmux.

import os
import sys

# params
sess_name = "spp"
default_nof_sec = 2
run_dir = "."
spp_srcdir = "$HOME/dpdk-home/spp/src"
qemu_dir = "$HOME/dpdk-home/qemu-setup/runscripts"

# spp controller
ctrler = {
        "host": "127.0.0.1",
        "pri_port": 5555,
        "sec_port": 6666
        }

# spp primary (2 cores per process)
primary = {"coremask": "0x03"}

# spp secondaries (2 cores per process)
secondaries = [
        {"id": 1, "coremask": "0x0C"},
        {"id": 2, "coremask": "0x30"},
        {"id": 3, "coremask": "0xC0"},
        {"id": 4, "coremask": "0x300"}
        ]

# ring VM
ring_sh = "ring.sh"
ring_vms = [
        {"id": 1}
        ]

# vhost VM
vhost_sh = "vhost.sh"
vhost_vms = [
        {"id": 1}
        ]

# return tmux windows
def setup_windows(nof_sec, nof_ring, nof_vhost):
    windows = [
            {
                "win_name": "ctrler",
                "dir": spp_srcdir,
                "cmd": "python spp.py",
                "opts": "-p %s -s %s" % (
                    ctrler.get("pri_port"), ctrler.get("sec_port")),
                "enter_key": True
                },

            {
                "win_name": "pri",
                "dir": run_dir,
                "cmd": "sh runscripts/primary.sh",
                "opts": "%s %s %s %s" % (
                    spp_srcdir, primary.get("coremask"),
                    ctrler.get("host"),
                    ctrler.get("pri_port")),
                "enter_key": True
                }
            ]

    for i in range(nof_sec):
        windows.append({
            "win_name": "sec%s" % i,
            "dir": run_dir,
            "cmd": "sh runscripts/secondary.sh",
            "opts": "%s %s %s %s %s" % (
                spp_srcdir,
                secondaries[i].get("id"),
                secondaries[i].get("coremask"),
                ctrler.get("host"),
                ctrler.get("sec_port")),
            "enter_key": True
            })

    for i in range(nof_ring):
        windows.append({
            "win_name": "vm_r%s" % i,
            "dir": qemu_dir,
            "cmd": "./%s" % ring_sh,
            "opts": "%s" % ring_vms[i].get("id"),
            "enter_key": True
            })

    for i in range(nof_vhost):
        windows.append({
            "win_name": "vm_v%s" % i,
            "dir": qemu_dir,
            "cmd": "./%s" % vhost_sh,
            "opts": "%s" % vhost_vms[i].get("id"),
            "enter_key": True
            })
            
    return windows


def main():
    # [TODO] 引数の取り方を見直す
    args = sys.argv
    if len(args) > 1:
        nof_sec = int(args[1])
    else:
        nof_sec = default_nof_sec

    if nof_sec > len(secondaries):
        nof_sec = len(secondaries)

    nof_ring = len(ring_vms)
    nof_vhost = len(vhost_vms)

    cmd = []  # contains tmux commands
    for w in setup_windows(nof_sec, nof_ring, nof_vhost):
        if len(cmd) == 0:
            new_sess = "tmux new-session -d -s %s -n %s -c %s" % (
                    sess_name,
                    w.get("win_name"),
                    w.get("dir"))
            send_keys = "tmux send-keys -t %s \"%s %s\" C-m" % (
                    w.get("win_name"),
                    w.get("cmd"),
                    w.get("opts"))
            cmd.append(new_sess)
            cmd.append(send_keys)
        else:
            new_win = "tmux new-window -n %s -c \"%s\"" % (
                    w.get("win_name"),
                    w.get("dir"))
            if w.get("enter_key") == True:
                send_keys = "tmux send-keys -t %s \"%s %s\" C-m" % (
                      w.get("win_name"),
                      w.get("cmd"),
                      w.get("opts"))
            else:
                send_keys = "tmux send-keys -t %s \"%s %s\"" % (
                      w.get("win_name"),
                      w.get("cmd"),
                      w.get("opts"))
            cmd.append(new_win)
            cmd.append(send_keys)
  
    cmd.append("tmux attach -t %s" % sess_name)
   
  
    for c in cmd:
        print(c)
        os.system(c)

if __name__ == '__main__':
    main()
