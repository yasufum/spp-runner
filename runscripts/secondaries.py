#!/usr/bin/env python
# coding: utf-8

# Run multiple spp secondaries in a single term

import os
import sys
import yaml
import argparse
import subprocess

# This command is intended to run from parent dir,
# so config file must be in the dir.
conf_path = "conf.yml"

# Load config
f = open(conf_path, "r")
y = yaml.load(f)
f.close()

home_dir = os.environ["HOME"]
parser = argparse.ArgumentParser(description="Start up spp secondaries")
parser.add_argument(
        "-i", "--id",
        type=int,
        help="Secondary id")
parser.add_argument(
        "-n", "--num",
        type=int, default=2,
        help="Number of SPP secondaries")
parser.add_argument("-d", "--sppdir",
        type=str, default="%s/dpdk-home/spp/src" % home_dir,
        help="SPP's working dir")

args = parser.parse_args()
spp_srcdir = args.sppdir


def main():

    cmd = ""
    if args.id != None: # run only specified sec
        ent = y["secondaries"][args.id-1] # sec id is assumed starting from 1
        subprocess.call([
            "sh",
            "runscripts/secondary.sh",
            spp_srcdir,
            str(ent["id"]),  # args for subprocess must be string
            ent["coremask"],
            y["controller"]["host"],
            str(y["controller"]["sec_port"]),
            ])
    else: # run all of secondaries
        for i in range(0, args.num):
            ent = y["secondaries"][i]
            subprocess.call([
                "sh",
                "runscripts/secondary.sh",
                spp_srcdir,
                str(ent["id"]),  # args for subprocess must be string
                ent["coremask"],
                y["controller"]["host"],
                str(y["controller"]["sec_port"]),
                ])


if __name__ == '__main__':
    main()
