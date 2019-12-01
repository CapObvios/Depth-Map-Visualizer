# Depth Map Visualizer
A python script that converts a depth map to a 3D mesh in .obj format.

### Why is it needed?
Visualizing depth maps as a 3D mesh rather than a 2D grayscale image gives a better clue of what goes wrong in depth estimation.   
Most papers on depth estimation visualize their results as a 3D mesh. However, they don't provide any code to do so. For this reason, I implemented this mini-script.


## Usage

The simplest usage is to put the script in the same folder as depth map and, optionally, the texture and call:
```
python DepthToObj.py --depthPath [DEPTH_NAME_OR_PATH] --texturePath [TEXTURE_NAME_OR_PATH]
```

### Options and input
**required:**   
   `--depthPath` – path to the depth file. Depth file is required to be stored in a 16bit `.png` format in millimeter scale. It is then converted to float and divided by 1000 to obtain meters. Defaults to `'depth.png'`.   
**optional:**   
   `--texturePath` – path to the texture file. Defaults to empty string. If not defined, `.mtl` will not be created.   
   `--objPath` – output path and name of `.obj` file. Defaults to `model.obj`. If path or file doesn't exist, they will be created.   
   `--mtlPath` – output path and name of `.mtl` file. Defaults to `model.mtl`. If path or file doesn't exist, they will be created. If `--texturePath` was not defined, this file will not be created.   
   `--matName` – name of material to be created with the texture. Defaults to `colored`.
