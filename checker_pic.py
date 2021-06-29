#!/usr/bin/python

import sys
import os
from PIL import Image
import numpy as np
import argparse


if __name__== "__main__":
    parser = argparse.ArgumentParser(description="combine two images into a draughtboard image")
    # paths
    parser.add_argument("in1", default=None, type = str, help="path to image1")
    parser.add_argument("in2", default=None, type = str, help="path to image2")
    parser.add_argument("--block_width", '-bw', default=50, type = int, help="block size")
    parser.add_argument("--block_height", '-bh', default=50, type = int, help="block size")
    parser.add_argument("--output", '-o', default="draughtboard.jpg", type = str, help="output image file name")
    parser.add_argument("--greyscale", '-g', action="store_true", help="greyscale")
    args = parser.parse_args()

    img1 = Image.open(args.in1)
    img2 = Image.open(args.in2)
    img2 = img2.resize(img1.size)
    if args.greyscale:
        img1 = img1.convert("L")
        img2 = img2.convert("L")

    w,h=img1.size
    print("input image sizes: ", img1.size, img2.size)

    mask = np.zeros((h,w), dtype=np.uint8)
    for i in range(w//args.block_width+1):
        for j in range((i%2)*args.block_height,h,2*args.block_height):
            mask[j:j+args.block_height,i*args.block_width:(i+1)*args.block_width] = 255

    img1.paste(img2, (0, 0), Image.fromarray(mask))
    img1.save(args.output, quality=90)
    print("saved as ",args.output)
