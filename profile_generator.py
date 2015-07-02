#!/usr/bin/python

import argparse
import os
import sys
import subprocess
import logging
import pdb

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

VERSION="0.1"
DEFAULT_LOGGING_LEVEL=logging.INFO

def get_autofdo_path():
    p = subprocess.Popen("./install_autofdo.sh", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    if p.returncode:
        logger.debug(out)
        logger.error(err)
        logger.error("AutoFDO compilation error")
        sys.exit(1)
    return out.split()[-1]

def parse_binaries(perf_file):
    binaries = []
    exist = False
    if not os.path.exists(perf_file) or not os.path.isfile(perf_file):
        logger.error("Perf data file wasn't found")
        sys.exit(1)
    p = subprocess.Popen(["perf", "report", "-i", perf_file, "-D"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    binaries = list(set([y.split()[2] for y in [x.strip() for x in out.split("\n") if x and x.startswith(" ...... dso: ")]]))
    return binaries

def generate_gcov(autofdo_path, perf_file, binaries):
    gcovs = []
    for binary in binaries:
        if not binary.startswith("["):
            gcov_file = binary.split("/")[-1]+".afdo"
            p = subprocess.Popen([os.path.join(autofdo_path, "create_gcov"), "--binary="+binary, "--profile="+perf_file, "--gcov="+gcov_file, "-gcov_version=1"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if not p.returncode:
                gcovs.append(gcov_file)
    return merge_gcovs(autofdo_path, gcovs) if len(gcovs) > 1 else gcovs[0]

def merge_gcovs(autofdo_path, gcovs):
    p = subprocess.Popen([os.path.join(autofdo_path, "profile_merger")] + gcovs + ["-gcov_version=1"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return "fbdata.afdo" if not p.returncode else ""

def upload_gcov(gcov):
    pass

if __name__ == "__main__":	
    parser = argparse.ArgumentParser(prog='./profile_generator.py',
                                     usage='%(prog)s [options]')
    parser.add_argument("perf_file", nargs=1,
                        help="Perf data file")
    parser.add_argument('-l', '--verbosity_level', dest='verbosity_level',
                        action='store', default=logging.getLevelName(DEFAULT_LOGGING_LEVEL),
                        choices=[logging.getLevelName(logging.DEBUG),
                                 logging.getLevelName(logging.INFO),
                                 logging.getLevelName(logging.ERROR)],
                        help='Set the verbosity level (default = {default})'.format(default=logging.getLevelName(DEFAULT_LOGGING_LEVEL)))
    parser.add_argument('-v', '--version', action='version',
                        version='%(prog)s Version: {version}'.format(version=VERSION),
                        help='Show version and exit')
    args = parser.parse_args()
    autofdo_path = get_autofdo_path()
    binaries = parse_binaries(args.perf_file[0])
    gcov = generate_gcov(autofdo_path, args.perf_file[0], binaries)
    upload_gcov(gcov)
