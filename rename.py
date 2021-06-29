#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import print_function
import argparse
import os
import numpy as np
from numpy.random import *
import pydicom as dicom
from chainercv.utils import write_image,read_image
import glob,re
from skimage.morphology import remove_small_objects

num = lambda val : int(re.sub("\\D", "", val+"0"))

#########################
def main():
    parser = argparse.ArgumentParser(description='create sinograms for artificial images')
    parser.add_argument('--input', '-i', default='in')
    parser.add_argument('--outdir', '-o', default='out',
                        help='directory to output masked DCM files')
    args = parser.parse_args()
    args.imgtype = ""

    os.makedirs(args.outdir, exist_ok=True)

    dirlist = []
    for f in os.listdir(args.input):
        if os.path.isdir(os.path.join(args.input, f)):
            dirlist.append(f)
    j = 0  # dir index
    for dirname in sorted(dirlist):
        for cl,ocl in zip(["sharp","soft"],["trainA","trainB"]):
            dn = os.path.join(args.outdir,ocl,dirname)
            os.makedirs(dn, exist_ok=True)
            files = [os.path.join(args.input, dirname, cl, fname) for fname in sorted(os.listdir(os.path.join(args.input, dirname,cl)), key=num) if fname.endswith(args.imgtype)]
            for i,f in enumerate(files):
                #print(f, os.path.join(dn,"{:0>5}.dcm".format(i)))
                os.rename(f, os.path.join(dn,"{:0>5}.dcm".format(i)))

if __name__ == '__main__':
    main()
