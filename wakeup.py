#!/usr/bin/env python

# Run SPP, then QEMU within tmux.

import os


# params
run_dir = "."
spp_dir = "$HOME/dpdk-home/spp/examples/multi_process/patch_panel"
qemu_dir = "$HOME/dpdk-home/qemu-setup/runscript"

spp_pri_port = 5555
spp_sec_port = 6666

secondaries = [
        {"id": "1", "coremask": "0x06"},
        {"id": "2", "coremask": "0x0A"},
        ]

monitor_port = "4444"

sess_name = "spp"


# tmux windows
windows = [
   {
    "win_name": "ctrler",
    "dir": spp_dir,
    "cmd": "python spp.py",
    "opts": "-p %s -s %s" % (spp_pri_port, spp_sec_port),
    "enter": True
    },

   {
    "win_name": "pri",
    "dir": run_dir,
    "cmd": "sh runscripts/primary.sh",
    "opts": "%s" % spp_pri_port,
    "enter": True
    },

   {
    "win_name": "sec1",
    "dir": run_dir,
    "cmd": "sh runscripts/secondary.sh",
    "opts": "%s %s %s" % (secondaries[0].get("id"), secondaries[0].get("coremask"), spp_sec_port),
    "enter": True
    },

   {
    "win_name": "sec2",
    "dir": run_dir,
    "cmd": "sh runscripts/secondary.sh",
    "opts": "%s %s %s" % (secondaries[1].get("id"), secondaries[1].get("coremask"), spp_sec_port),
    "enter": True
    },

   {
    "win_name": "qemu",
    "dir": qemu_dir,
    "cmd": "",
    "opts": "",
    "enter": False 
    },

   {
    "win_name": "monitor",
    "dir": qemu_dir,
    "cmd": "telnet",
    "opts": "localhost %s" %  monitor_port,
    "enter": False
    }

  ]


def main():
  cmd = []  # contains tmux commands
  for w in windows:
    if len(cmd) == 0:
      new_sess = "tmux new-session -d -s %s -n %s -c %s" % (sess_name, w.get("win_name"), w.get("dir"))
      send_keys = "tmux send-keys -t %s \"%s %s\" C-m" % (w.get("win_name"), w.get("cmd"), w.get("opts"))
      cmd.append(new_sess)
      cmd.append(send_keys)
    else:
      new_win = "tmux new-window -n %s -c \"%s\"" % (w.get("win_name"), w.get("dir"))
      if w.get("enter") == True:
        send_keys = "tmux send-keys -t %s \"%s %s\" C-m" % (w.get("win_name"), w.get("cmd"), w.get("opts"))
      else:
        send_keys = "tmux send-keys -t %s \"%s %s\"" % (w.get("win_name"), w.get("cmd"), w.get("opts"))
      cmd.append(new_win)
      cmd.append(send_keys)

  cmd.append("tmux attach -t %s" % sess_name)
 

  for c in cmd:
    print(c)
    os.system(c)

if __name__ == '__main__':
  main()
