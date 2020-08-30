# 3D GPU Rendering Pipeline
This script utilizes Python numpy and matplotlib libraries to render a 3D object. The script accepts a .raw file which is usually an artist render (from a software like Blender). Parameters like light position, camera position, object position, object orientation, field of view (fov), far and near can be set as well. 

The script follows a rendering pipeline of:
World Transformation --> View Transformation --> Lighting --> Projection Transformation --> Perspective Divide --> Z-Sorting --> Rasterization (handled by Matplotlib)

**Some Notes**
- This file follows the LHS system when performing matrix calculations. All matrixes are in the row convention (like D3D/XNA).
- RGB color of the diffuse material on the object (called m_diff here as parts of Lamebert Cosine Law)

Sample Renders:
[Example 1](https://drive.google.com/file/d/1nCXxQRFD7GvSrLxvJc7yC3MuZCLZT9Lr/view?usp=sharing)
[Example 2](https://drive.google.com/file/d/19R-S70DcecpGusfRgQmMGO8RV2Fcuzd9/view?usp=sharing)
