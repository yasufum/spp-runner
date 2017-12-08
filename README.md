# SPP Runner

## Table of Contents

- [What is this](#what-is-this)
- [Install](#install)
- [Usage](#usage)


## What is this

A management tool for SPP.


### SPP

[SPP](http://www.dpdk.org/browse/apps/spp/)
is a framework to easily interconnect DPDK applications together,
and assign resources dynamically to these applications.
It is implemented using Intel DPDK.
You can configure network path between applications on host and guest VMs
with SPP.
SPP provides not only high-performance connectivity, but also flexibility
with patch panel like interface.


## Install

Use apt command for following packages.
- python
- qemu
- [tmux](https://tmux.github.io/)

SPP and qemu-hda are required and must be cloned same directory
as spp-runner.

- SPP
- qemu-hda

```sh
$ cd /path/to/working_dir
$ git clone [spp repo]
$ git clone [spp-runner repo]
$ git clone [qemu-hda repo]
```


## Usage

### Run SPP

You start by running `bin/wakeup.py` which is a script for launching SPP.
This script opens several windows with [tmux](https://tmux.github.io/)
for SPP primary process,
secondary processes and VMs on which SPP process runs.

```sh
$ ./bin/wakeup.py -ns 2 -nv 1

# It is defined as default value. It's also the same.
$ ./bin/wakeup.py
```

`wakeup.py` command opens several windows for following processes.

  1. SPP controller
  1. SPP primary
  1. SPP secondaries
  1. QEMU(ring VMs) (It is deprecated in DPDK 16.11 or later!)
  1. QEMU(vhost VMs)
  1. working dir

Refer help for details.

  ```sh
  $ ./bin/wakeup.py -h
  usage: wakeup.py [-h] [-t] [-ns NOF_SEC] [-nr NOF_RING] [-nv NOF_VHOST]
                   [-vn VHOST_NUM] [-nw NOF_WORKING]

  Run SPP and VMs

  optional arguments:
    -h, --help            show this help message and exit
    -t, --template        Boot template VM
    -ns NOF_SEC, --nof-sec NOF_SEC
                          Number of SPP secondaries
    -nr NOF_RING, --nof-ring NOF_RING
                          Number of VMs running ring
    -nv NOF_VHOST, --nof-vhost NOF_VHOST
                          Number of VMs running vhost
    -vn VHOST_NUM, --vhost-num VHOST_NUM
                          Number of vhost interfaces
    -nw NOF_WORKING, --nof-working NOF_WORKING
                          Number of working window
  ```

### Login to VMs

After launching VMs successfully, you login to VMs to setup DPDK and
SPP. IP addresses registerd to
`/var/lib/libvirt/dnsmasq/virbr0.status` while launching VMs.

You can login with ssh refering `virbr0.status` or sppsh command which
is a helper tool for managing several VMs with simple commands.
Run sppsh with list option `-l` to show information.

```sh
$ ./bin/sppsh -l
id:0, host:spp0, ipaddr:192.168.122.157
id:1, host:spp1, ipaddr:192.168.122.57
...
```

There are three identifiers, VM ID, host name and IP address. You can
login using one of them.
You can also use different account other than host with `-a` option.

```sh
# login to VM ID 0 using same account on host
$ ./bin/sppsh 0  
# or
# login to host named 'spp0' using account 'user1'
$ ./bin/sppsh -a user1 spp0  
```

## How to use

### Prepare VM image

First, you need to create a template image with qemu-hda.
This spp-runner uses a template and its instances to launch several
VMs. In other words, template is an original and instances are its
clones.
VM ID 0 is reserved for template.

```sh
# Launch template VM for vhost
$ /path/to/qemu-hda/bin/run-vm.py -i 0 -t vhost -f [HDA_PATH]
```

Then, you login to it and install DPDK and SPP to template, 
It is better to use spp-vm-installer to install them.

To launch instance VMs, run `run-vm.py` with VM ID other than 0.

```sh
# Launch three instance VMs (ID 1, 2 and 3) for vhost
$ /path/to/qemu-hda/bin/run-vm.py -i 1-3 -t vhost -f [HDA_PATH]
```

### Configuration

Configuration is described in `conf.yml`.
Basically, you don't need to edit without change core assignment.

  ```
  ---
  
  controller:
    host: "127.0.0.1"
    pri_port: 5555
    sec_port: 6666
  
  primary:
    coremask: 0x03  # 2 cores
  
  secondaries:
    - id: 1
      coremask: "0x0C"  # 2 cores
    - id: 2
      coremask: "0x30"  # 2 cores
    - id: 3
      coremask: "0xC0"  # 2 cores
    - id: 4
      coremask: "0x300"  # 2 cores
    - id: 5
      coremask: "0xC00"  # 2 cores
    #- id: 6
    #- coremask: "0x3000"  # 2 cores
  
  vms_ring:
    - id: 6
    - id: 7
    - id: 8
    - id: 9
    - id: 10
  
  vms_vhost:
    - id: 11
    - id: 12
    - id: 13
    - id: 14
    - id: 15
  ```

It's divided into five parts each of which responds to
entity as following.

#### SPP controller

  - host: IP address of controller node
  - pri_port: Port SPP primary process connects to (should not change)
  - sec_port: Port SPP secondary processes connect to (should not change)

#### SPP primary 

  - coremask: CPU cores SPP primary uses

You must avoid to overlap with secondary processes.
So, confirm not to overlap with them if you change it.

You can monitor statistics if you assign two or more.
It requires at least one core and monitoring is disabled
in this case.


#### SPP secondary

  - id: secondary ID
  - coremask: CPU cores SPP secondary uses

id attr responds to secondary ID and it's given to
`runscripts/secondary.sh` to use it as a option for
running secondary process.

#### VM(ring)

  - id: VM ID respond to secondary ID running on the VM

#### VM(vhost)

  - id: VM ID respond to secondary ID running on the VM


### Generate templates for ring and vhost VMs

VMs are booted from `wakeup.py`.
But you have to confirm that you have already prepared 
tempaltes before running VMs.

#### Understand how to manage images

There are two steps for running VMs.
First, you generate templates for ring and vhost from template.

Then, generate images for each of VMs as instances from
ring or vhost template. This instance images are put into
`qemu-setup/runscripts/img/`.

As you run `wakeup.py`, it tries to boot VMs using image in
`qemu-setup/runscripts/img/`.
If there is no image in the `img` directory, then `wakeup.py`
tries to generate instance from ring or vhost template.
In the same manner, ring and vhost templates are generated
from base template if they don't exist.

Therefore, you have to put only base template image at first time.

#### Setup ring and vhost templates

Run `wakeup.py`.

  ```sh
  $ ./bin/wakeup.py
  ```

It launches tmux and open windows for each processes.
In primary, secondaries and VMs window, command is prompted for input
password
(SPP controller doesn't require sudo).

As described in SPP's documents, you have to run processes in order.

  1. SPP controller
  1. primary
  1. seconrdaries
  1. ring VM (deprecated in DPDK 16.11 or later)
  1. vhost VM (after create socket)
