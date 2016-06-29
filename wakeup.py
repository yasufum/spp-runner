#!/usr/bin/env python

# Run SPP, then QEMU within tmux.

import os

run_dir = "."
spp_dir = "$HOME/dpdk-home/spp/examples/multi_process/patch_panel"

spp_pri_port = 5555
spp_sec_port = 6666
sess_name = "spp"

secondaries = [
        {"id": "sec1", "coremask": "0x06"},
        {"id": "sec2", "coremask": "0x0A"},
        ]

windows = [
   {
    "win_name": "ctrler",
    "dir": spp_dir,
    "cmd": "python spp.py",
    "opts": "-p %s -s %s" % (spp_pri_port, spp_sec_port)
    },

   {
    "win_name": "pri",
    "dir": run_dir,
    "cmd": "sh runscripts/primary.sh",
    "opts": ""
    },

   {
    "win_name": "sec1",
    "dir": run_dir,
    "cmd": "sh runscripts/secondary.sh",
    "opts": "%s %s" % (secondaries[0].get("coremask"), secondaries[0].get("id"))
    },

   {
    "win_name": "sec2",
    "dir": run_dir,
    "cmd": "sh runscripts/secondary.sh",
    "opts": "%s %s" % (secondaries[1].get("coremask"), secondaries[1].get("id")) 
    }

  ]


def main():
  
  cmd = []

  for w in windows:
    if len(cmd) == 0:
      new_sess = "tmux new-session -d -s %s -n %s -c %s" % (sess_name, w.get("win_name"), w.get("dir"))
      send_keys = "tmux send-keys -t %s \"%s %s\" C-m" % (w.get("win_name"), w.get("cmd"), w.get("opts"))
      cmd.append(new_sess)
      cmd.append(send_keys)
    else:
      new_win = "tmux new-window -n %s -c \"%s\"" % (w.get("win_name"), w.get("dir"))
      send_keys = "tmux send-keys -t %s \"%s %s\" C-m" % (w.get("win_name"), w.get("cmd"), w.get("opts"))
      cmd.append(new_win)
      cmd.append(send_keys)

  cmd.append("tmux attach -t %s" % sess_name)
 

  for c in cmd:
    print(c)
    os.system(c)

if __name__ == '__main__':
  main()
