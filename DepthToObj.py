import argparse
import math
import os

import numpy as np
import PIL
import PIL.Image


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("--depthPath", dest="depthPath", help="depth map path", default="depth.png", type=str)
    parser.add_argument("--texturePath", dest="texturePath", help="corresponding image path", default="", type=str)
    parser.add_argument("--objPath", dest="objPath", help="output path of .obj file", default="model.obj", type=str)
    parser.add_argument("--mtlPath", dest="mtlPath", help="output path of .mtl file", default="model.mtl", type=str)
    parser.add_argument("--matName", dest="matName", help="name of material to create", default="colored", type=str)
    args = parser.parse_args()
    return args


def create_mtl(mtlPath, matName, texturePath):
    if max(mtlPath.find("\\"), mtlPath.find("/")) > -1:
        os.makedirs(os.path.dirname(mtlPath), exist_ok=True)
    with open(mtlPath, "w") as f:
        f.write("newmtl " + matName + "\n")
        f.write("Ns 10.0000\n")
        f.write("d 1.0000\n")
        f.write("Tr 0.0000\n")
        f.write("illum 2\n")
        f.write("Ka 1.000 1.000 1.000\n")
        f.write("Kd 1.000 1.000 1.000\n")
        f.write("Ks 0.000 0.000 0.000\n")
        f.write("map_Ka " + texturePath + "\n")
        f.write("map_Kd " + texturePath + "\n")


def vete(v, vt):
    return str(v) + "/" + str(vt)


def create_obj(depthPath, objPath, mtlPath, matName, useMaterial=True):

    img = PIL.Image.open(depthPath).convert("LA").convert("L")
    img = np.array(img) / 1000.0

    w = img.shape[1]
    h = img.shape[0]

    FOV = math.pi / 4
    D = (img.shape[0] / 2) / math.tan(FOV / 2)

    if max(objPath.find("\\"), objPath.find("/")) > -1:
        os.makedirs(os.path.dirname(mtlPath), exist_ok=True)

    with open(objPath, "w") as f:
        if useMaterial:
            f.write("mtllib " + mtlPath + "\n")
            f.write("usemtl " + matName + "\n")

        ids = np.zeros((img.shape[1], img.shape[0]), int)
        vid = 1

        for u in range(0, w):
            for v in range(h - 1, -1, -1):

                d = img[v, u]

                ids[u, v] = vid
                if d == 0.0:
                    ids[u, v] = 0
                vid += 1

                x = u - w / 2
                y = v - h / 2
                z = -D

                norm = 1 / math.sqrt(x * x + y * y + z * z)

                t = d / (z * norm)

                x = -t * x * norm
                y = t * y * norm
                z = -t * z * norm

                f.write("v " + str(x) + " " + str(y) + " " + str(z) + "\n")

        for u in range(0, img.shape[1]):
            for v in range(0, img.shape[0]):
                f.write("vt " + str(u / img.shape[1]) + " " + str(v / img.shape[0]) + "\n")

        for u in range(0, img.shape[1] - 1):
            for v in range(0, img.shape[0] - 1):

                v1 = ids[u, v]
                v2 = ids[u + 1, v]
                v3 = ids[u, v + 1]
                v4 = ids[u + 1, v + 1]

                if v1 == 0 or v2 == 0 or v3 == 0 or v4 == 0:
                    continue

                f.write("f " + vete(v1, v1) + " " + vete(v2, v2) + " " + vete(v3, v3) + "\n")
                f.write("f " + vete(v3, v3) + " " + vete(v2, v2) + " " + vete(v4, v4) + "\n")


if __name__ == "__main__":
    print("STARTED")
    args = parse_args()
    useMat = args.texturePath != ""
    if useMat:
        create_mtl(args.mtlPath, args.matName, args.texturePath)
    create_obj(args.depthPath, args.objPath, args.mtlPath, args.matName, useMat)
    print("FINISHED")
