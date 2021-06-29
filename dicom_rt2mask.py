#!/usr/bin/env python
# coding: utf-8
#%%
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.cm as cmx
import matplotlib
from mpl_toolkits.mplot3d import Axes3D
import os,time,subprocess,glob,re
import pandas
import pydicom as dicom
from PIL import Image,ImageDraw
import argparse

def write_dcm(ref_dicom,img0,outfn):
    salt = "9999"
    ref_dicom.file_meta.TransferSyntaxUID = dicom.uid.ExplicitVRLittleEndian #dicom.uid.ImplicitVRLittleEndian
    #ref_dicom.is_little_endian = True
    #ref_dicom.is_implicit_VR = False
    dt=ref_dicom.pixel_array.dtype
    img = (img0-ref_dicom.RescaleIntercept).astype(dt)
    ref_dicom.PixelData = img.tobytes()
    uid = ref_dicom[0x20,0x52].value.split(".")  # Frame of Reference UID
    uid[-1] = salt
    uidn = ".".join(uid)
    ref_dicom[0x20,0xe].value=uidn  #(0020, 000e) Series Instance UID   # necessary for RayStation
    ref_dicom[0x20,0x52].value=uidn  # Frame of Reference UID
    ref_dicom.save_as(outfn)


if __name__== "__main__":
    parser = argparse.ArgumentParser(description="Convert RT Structure into image values")
    # paths
    parser.add_argument("indir", default=None, type = str, help="path to DICOM images")
    parser.add_argument("--RTfile", '-r', default="IM-structure.dcm", type = str, help="path to DICOM containin RT-structure")
    parser.add_argument("--outdir", '-o', default="output", type = str, help="path to DICOM images")
    args = parser.parse_args()

    usedROIS = ["07 Bladder","11 Prostate","04 Rectum","03 SeminalVesicle"]

    ref = dicom.read_file(args.RTfile, force=True) 

    CS = dict()
    col = 0
    for roi,nm in zip(ref.ROIContourSequence,ref.StructureSetROISequence):
        if nm.ROIName in usedROIS:
            col += 1
            print(col, nm.ROIName)
            for cs in roi.ContourSequence:
                z = int(round(cs.ContourData[2]))
                cd = np.array(cs.ContourData, dtype=np.float64).reshape(-1,3)
                if z in CS:
                    CS[z].append((col,cd))
                else:
                    CS[z] = [(col,cd)]

    print("Maimum colour: ",col)
    os.makedirs(args.outdir,exist_ok=True)

    dcmfiles = glob.glob(os.path.join(args.indir,"*.dcm"))
    for pfn in dcmfiles:
        param = dicom.read_file(pfn, force=True)

        ps_x, ps_y = float(param.PixelSpacing[0]), float(param.PixelSpacing[1])
        sx, sy, sz = param.ImagePositionPatient
        w,h = param.pixel_array.shape

        z = int(sz)
        img = Image.new(mode='L', size=(w,h), color=0)
        img1 = ImageDraw.Draw(img)
        if z in CS.keys():
            for col,cs in CS[z]:
                cd = np.zeros_like(cs[:,:2])
                cd[:,0] = (cs[:,0]-sx)/ps_x
                cd[:,1] = (cs[:,1]-sy)/ps_y
                xy = list(cd.astype(int).ravel())
                if len(xy)>3:
                    img1.polygon(xy=xy, outline=0, fill=col)
            mask = np.array(img)
        else:
            mask = np.zeros_like(img)
        #print(z,np.sum(mask))
        write_dcm(param,mask,os.path.join(args.outdir,os.path.basename(pfn)))

    #c = matplotlib.path.Path(list(contour))
    #grid = c.contains_points(dosegridpoints)
    #grid = grid.reshape((len(doselut[1]), len(doselut[0])))

    # fig = plt.figure(figsize=(21,10))
    # axes = fig.subplots(1, 3)
    # axes[0].imshow(param.pixel_array, cmap="coolwarm")      
    # axes[1].imshow(mask,cmap="coolwarm",vmin=0,vmax=1)
    # plt.show()
    # print(len(CS),ps_x, ps_y, z, np.sum(mask))



# %%
