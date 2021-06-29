#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import print_function
import argparse
import cv2
import os
import numpy as np
from numpy.random import *
import pydicom as dicom
from PIL import Image
import glob
from skimage.morphology import remove_small_objects

#########################
def main():
    parser = argparse.ArgumentParser(description='apply mask to DICOM images')
    parser.add_argument('imagedir', default=None,
                        help='directory containing DCM files')
    parser.add_argument('--size', '-s', type=int, default=64,
                        help='minimum area')
    parser.add_argument('--threshold', '-t', type=int, default=200,
                        help='threshold 0--256')
    parser.add_argument('--maskdir', '-m', default=None,
                        help='directory containing mask image files')
    parser.add_argument('--outdir', '-o', default='out',
                        help='directory to output masked DCM files')
    parser.add_argument('--anonimise', '-a', action="store_true", help='strip personal information from saved DICOM')
    args = parser.parse_args()

    os.makedirs(args.outdir, exist_ok=True)

    ###
    for file in sorted(glob.glob(args.imagedir+"/*.dcm", recursive=False)):
        print("processing...:", file)
        fn,ext = os.path.splitext(file)
        bfn = os.path.basename(fn)

        ref_dicom = dicom.read_file(file, force=True)
        ref_dicom.file_meta.TransferSyntaxUID = dicom.uid.ImplicitVRLittleEndian
        dt=ref_dicom.pixel_array.dtype
        dat = ref_dicom.pixel_array.astype(np.float32) +ref_dicom.RescaleIntercept
        print(dat.shape,np.min(dat),np.mean(dat),np.max(dat))

        if args.maskdir is not None:
            imgfn=os.path.join(args.maskdir,bfn+".jpg")
            print("applying mask: ", imgfn)
            mask = np.array(Image.open(imgfn).convert('L')) < args.threshold
            mask = remove_small_objects(mask,min_size=args.size,in_place=True)
            mask = ~remove_small_objects(~mask,min_size=args.size)
            dat[mask] = -2048
        dat -= ref_dicom.RescaleIntercept
        dat = dat.astype(dt)           
        ref_dicom.PixelData = dat.tobytes()
        if args.anonimise:
            ref_dicom.remove_private_tags()
            for tag in ref_dicom.keys():
                print(ref_dicom[tag])
                if 'Name' in ref_dicom[tag].name:
                    ref_dicom[tag].value = '00'
        ref_dicom.save_as(os.path.join(args.outdir,bfn+".dcm"))



if __name__ == '__main__':
    main()
