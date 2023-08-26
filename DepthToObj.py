import argparse
import numpy as np
import cv2
import math
import os

def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('--depthPath', dest='depthPath',
                        help='depth map path',
                        default='depth.png', type=str)
    parser.add_argument('--depthInvert', dest='depthInvert',
                        help='Invert depth map',
                        default=False, action='store_true')
    parser.add_argument('--texturePath', dest='texturePath',
                        help='corresponding image path',
                        default='', type=str)
    parser.add_argument('--objPath', dest='objPath',
                        help='output path of .obj file',
                        default='model.obj', type=str)
    parser.add_argument('--mtlPath', dest='mtlPath',
                        help='output path of .mtl file',
                        default='model.mtl', type=str)
    parser.add_argument('--matName', dest='matName',
                        help='name of material to create',
                        default='colored', type=str)
    parser.add_argument('--scaleToMeter', dest='scaleToMeter',
                        help='Scale to apply to the input depth matrix to convert it to meters. By default, expecting depth to be 16bit integer `.png` format in millimeter scale (kinect), therefore the default value is 0.001.',
                        default=0.001, type=float)
    parser.add_argument('--fieldOfView', dest='fieldOfView',
                        help='Angle in degrees of vertical field of view. Defines what the camera saw when recording depth matrix.',
                        default=45.0, type=float)

    args = parser.parse_args()
    return args

def create_mtl(mtlPath, matName, texturePath):
    if max(mtlPath.find('\\'), mtlPath.find('/')) > -1:
        os.makedirs(os.path.dirname(mtlPath), exist_ok=True)
    with open(mtlPath, "w") as f:
        f.write("newmtl " + matName + "\n"      )
        f.write("Ns 10.0000\n"                  )
        f.write("d 1.0000\n"                    )
        f.write("Tr 0.0000\n"                   )
        f.write("illum 2\n"                     )
        f.write("Ka 1.000 1.000 1.000\n"        )
        f.write("Kd 1.000 1.000 1.000\n"        )
        f.write("Ks 0.000 0.000 0.000\n"        )
        f.write("map_Ka " + texturePath + "\n"  )
        f.write("map_Kd " + texturePath + "\n"  )

def vete(v, vt):
    return str(v)+"/"+str(vt)

def extract_depth_matrix_from_raw(depthMatrixRaw : np.array, rgbChannelIndexToUse : int, scaleToMeter : float) -> (bool, np.array):
    '''
    Checks if a given raw map is a depth matrix and returns a 2D map if it's a depth matrix.

    Arguments:
        depthMatrixRaw: A map that is claimed to be a depth matrix.
        rgbChannelIndexToUse: index of the channel that will be channel in RGB that will be used.
            Has to be 0,1, or 2 (R, G, or B channel correspondingly).
            Meaningful if the depth matrix is encoded as an RGB image. Ignored if the raw depth matrix has only 1 channel.
        scaleToMeter: scale that should be applied to values to convert them to meters.

    Return:
        isSuccess: whether depthMatrixRaw is supported.
            If False, then we don't support such a format (yet).
        depthMatrix: In case of success, processed and scaled version of depthMatrixRaw.
            Otherwise will be None.
    '''

    # Check input for validity.
    if len(depthMatrixRaw.shape) not in [2, 3]:
        print('depthMatrix has to have 2 or 3 axes, but got shape: %r', depthMatrixRaw.shape)
        return False, None

    if len(depthMatrixRaw.shape) == 3 and rgbChannelIndexToUse >= depthMatrixRaw.shape[2]:
        print('Trying to read channel rgbChannelIndexToUse=%d, but depth matrix has only %d channels (shape=%r)', (rgbChannelIndexToUse, depthMatrixRaw.shape[2], depthMatrixRaw.shape))
        return False, None

    # Take a correct 2D map.
    depthMatrix = depthMatrixRaw
    if len(depthMatrixRaw.shape) == 3:
        depthMatrix = depthMatrixRaw[:,:,rgbChannelIndexToUse]

    # Convert to meters.
    depthMatrix *= scaleToMeter

    return True, depthMatrix


def create_obj(depthPath, fieldOfView, scaleToMeter, depthInvert, objPath, mtlPath, matName, useMaterial = True):
    
    img = cv2.imread(depthPath, -1).astype(np.float32)

    isExtractDepthMatrixSuccess, img = extract_depth_matrix_from_raw(
        depthMatrixRaw=img,
        rgbChannelIndexToUse=0,
        scaleToMeter=scaleToMeter)

    if not isExtractDepthMatrixSuccess:
        # Failed extracting depth matrix, can't create obj file.
        return

    if depthInvert == True:
        img = 1.0 - img

    w = img.shape[1]
    h = img.shape[0]

    # Convert from degrees to axis angle.
    fieldOfViewAxisAngle = fieldOfView / 180.0 * math.pi

    D = (img.shape[0]/2)/math.tan(fieldOfViewAxisAngle/2)

    if max(objPath.find('\\'), objPath.find('/')) > -1:
        os.makedirs(os.path.dirname(mtlPath), exist_ok=True)
    
    with open(objPath,"w") as f:    
        if useMaterial:
            f.write("mtllib " + mtlPath + "\n")
            f.write("usemtl " + matName + "\n")

        ids = np.zeros((img.shape[1], img.shape[0]), int)
        vid = 1

        for u in range(0, w):
            for v in range(h-1, -1, -1):

                d = img[v, u]

                ids[u,v] = vid
                if d == 0.0:
                    ids[u,v] = 0
                vid += 1

                x = u - w/2
                y = v - h/2
                z = -D

                norm = 1 / math.sqrt(x*x + y*y + z*z)

                t = d/(z*norm)

                x = -t*x*norm
                y = t*y*norm
                z = -t*z*norm        

                f.write("v " + str(x) + " " + str(y) + " " + str(z) + "\n")

        for u in range(0, img.shape[1]):
            for v in range(0, img.shape[0]):
                f.write("vt " + str(u/img.shape[1]) + " " + str(v/img.shape[0]) + "\n")

        for u in range(0, img.shape[1]-1):
            for v in range(0, img.shape[0]-1):

                v1 = ids[u,v]; v2 = ids[u+1,v]; v3 = ids[u,v+1]; v4 = ids[u+1,v+1]

                if v1 == 0 or v2 == 0 or v3 == 0 or v4 == 0:
                    continue

                f.write("f " + vete(v1,v1) + " " + vete(v2,v2) + " " + vete(v3,v3) + "\n")
                f.write("f " + vete(v3,v3) + " " + vete(v2,v2) + " " + vete(v4,v4) + "\n")

if __name__ == '__main__':
    print("STARTED")
    args = parse_args()
    useMat = args.texturePath != ''
    if useMat:
        create_mtl(
            args.mtlPath,
            args.matName,
            args.texturePath)

    create_obj(
        args.depthPath,
        args.fieldOfView,
        args.scaleToMeter,
        args.depthInvert,
        args.objPath,
        args.mtlPath,
        args.matName,
        useMat)

    print("FINISHED")
