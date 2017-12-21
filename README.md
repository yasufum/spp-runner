# SPP Runner

## Table of Contents

- [What is this](#what-is-this)
- [Install](#install)
- [How to use](#how-to-use)
  - [Run SPP](#run-spp)
  - [Login to VMs](#login-to-vms)
- [Detailed usage](#detailed-usage)
  - [Prepare VM image](#prepare-vm-image)
  - [Configuration](#configuration)
  - [Generate templates for VMs](#generate-templates-for-vms)
  - [Runscripts](#runscripts )


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


## How to use

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

## Detailed usage

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
    portmask: "0x03"  # 2 ports
  
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
  - portmask: Mask for PHY ports

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


### Generate templates for VMs

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


### Runscripts

Runscripts are helper tools for launching SPP primary and secondaries for
providing more simple interfaces.
It is implemented in python and options are defined with argparse library
which means that runscripts provide help message and options have default
values.

However, you usually do not need to use them because 'wakeup.py' runs at
once with options defined in config.
You use runscripts if you need to customize options for them.

#### Primary

SPP primary is launched from 'runscripts/primary.py'. Refer details by running
it with '-h' option.
Default values are referred from source code. It is defined in 'parse_args' method.

```sh
$ python runscripts/primary.py
usage: primary.py [-h] [-d SPPDIR] [-c COREMASK] [-p PORTMASK] [-ch CTRL_HOST]
                  [-cp CTRL_PORT] [-n NUM_RING] [-m MEM] [-mc MEM_CHAN]
                  [-vd [VDEV [VDEV ...]]] [-vdt VDEV_TAP] [-vdv VDEV_VHOST]

Launch primary process

optional arguments:
  -h, --help            show this help message and exit
  -d SPPDIR, --sppdir SPPDIR
                        SPP dir
  -c COREMASK, --coremask COREMASK
                        coremask
  -p PORTMASK, --portmask PORTMASK
                        portmask
  -ch CTRL_HOST, --ctrl-host CTRL_HOST
                        controller ipaddr
  -cp CTRL_PORT, --ctrl-port CTRL_PORT
                        controller port num
  -n NUM_RING, --num-ring NUM_RING
                        The number of rings
  -m MEM, --mem MEM
                        memory size
  -mc MEM_CHAN, --mem-chan MEM_CHAN
                        The number of memory channels
  -vd [VDEV [VDEV ...]], --vdev [VDEV [VDEV ...]]
                        vdev options, separate with space if two or more
  -vdt VDEV_TAP, --vdev-tap VDEV_TAP
                        TUN/TAP vdev IDs, assing '1-3' or '1,2,3' for three
                        IDs
  -vdv VDEV_VHOST, --vdev-vhost VDEV_VHOST
                        vhost vdev IDs, assing '1-3' or '1,2,3' for three IDs
```

It requires location of SPP with '-d' option.

'vdev' is an option of DPDK for assigning virtual device such as vhost,
TUN/TAP or crypt.
You can use the same format as DPDK with '-vd' or '--vdev'. However, if you
assign several devices, you do not use several '--vdev' entry but use one entry
and separate them with whitespaces. Here is an example for TUN/TAP tdevices.

```sh
$ python runscripts/primary.py -c 0x03 ... --vdev 'net_tap0,iface=foo0' 'net_tap1,iface=foo1' ...
```

'-vdt' and '-vdv' are dedicated options for these devices. You can assign them
more simple options. For example, you assign two of vhost by which sock1
and sock3 are created in /tmp directory.

```sh
$ python runscripts/primary.py -c 0x03 ... -vdv 1,3
```

Please refer 
[Network Interface Controller Drivers](http://dpdk.org/doc/guides/nics/index.html)
for details of virtual devices.

#### Secondary
It is more simple than primary's runscript.

```sh
$ python runscripts/secondaries.py -h
usage: secondaries.py [-h] [-i ID] [-n NUM] [-d SPPDIR] [-nm NUM_MEMCHAN]
                      [-ch CTR_HOST] [-cp CTR_PORT]

Start up spp secondaries

optional arguments:
  -h, --help            show this help message and exit
  -i ID, --id ID        Secondary id
  -n NUM, --num NUM     Number of SPP secondaries
  -d SPPDIR, --sppdir SPPDIR
                        SPP's working dir
  -nm NUM_MEMCHAN, --num-memchan NUM_MEMCHAN
                        Number of memory channels
  -ch CTR_HOST, --ctr-host CTR_HOST
                        IP address of SPP controller
  -cp CTR_PORT, --ctr-port CTR_PORT
                        Port of SPP controller
```

It also requires location of SPP with '-d' option as primary.

As explaining by the name 'secondaries', this script launched several
processes with '-n' option at once. In this case, secondary ID is assgined
by referring config.
If you give '-i' option, launch only one process of given ID.

```sh
# Launch two secondary processes
$ python runscripts/secondaries.py -n 2 ...
```
