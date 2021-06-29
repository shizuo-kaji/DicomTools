#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import argparse
import random

import numpy as np
import os, shutil,re
import glob

parser = argparse.ArgumentParser(description='Simple image registration by translation')
parser.add_argument('--root', '-R', help='copy from')
parser.add_argument('--output', '-o', default="data/cbct_2p8", help='copy to')
parser.add_argument('--slices_per_patient', '-s', default=8, type=int, help='')
parser.add_argument('--trainA', '-a', default=[5,8], type=int, nargs="*", help='patient ID')
parser.add_argument('--trainB', '-b', default=[5,8], type=int, nargs="*", help='patient ID')
parser.add_argument('--testA', '-ta', default=[1,2], type=int, nargs="*", help='patient ID')
parser.add_argument('--testB', '-tb', default=[1,2], type=int, nargs="*", help='patient ID')
args = parser.parse_args()

targets = {
           "trainA": ["dicom_CBCT_p{:02}_1".format(i) for i in args.trainA],
           "trainB": ["dicom_PlanCT_p{:02}_1_rigid".format(i) for i in args.trainB],
           "testA": ["dicom_CBCT_p{:02}_1".format(i) for i in args.testA],
           "testB": ["dicom_PlanCT_p{:02}_1_rigid".format(i) for i in args.testB]
           }

num = lambda val : int(re.sub("\\D", "", val+"0"))
for dn in ["trainA","trainB","testA","testB"]:
    os.makedirs(os.path.join(args.output,dn), exist_ok=True)
    cdir = os.path.join(args.root,dn)
    for root, dirs, files in os.walk(cdir):
#        print(root,dirs,files)
        for dirname in dirs:
            if dirname in targets[dn]:
                ipath = os.path.join(root,dirname)
                fns = [f for f in os.listdir(ipath) if (".dcm" in f) ]
                fns.sort(key=num)
                s = len(fns)//args.slices_per_patient
                fns = fns[::s]
                opath = os.path.join(os.path.join(args.output,dn),dirname)
                os.makedirs(opath, exist_ok=True)
                for f in fns:
                    shutil.copy(os.path.join(ipath,f), opath)



