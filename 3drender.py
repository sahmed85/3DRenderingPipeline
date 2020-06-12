###########################################################################################################
# File: 3drender.py
# Name: Shadman Ahmed
# Date Created:  06/01/2020
# Last Modified: Ongoing 
# Usage: N/A
# Overview: This python script implements geometry and lighting calculations to render 
# 			an image of a scene of an 3-D object.
# Github/Git: sahmed85/3DRenderingPipeline
# Project: 3-D GPU Rendering Pipeline Homework #1
############################################################################################################

################################################### NOTES: ##################################################
# This file follows the LHS system when performing matrix calculations. All matrixes are in the
# row convention (like D3D/XNA). Below are variables that are set before calculations to:
# - Set the XYZ position of the light source
# - World Space XYZ position of the camera
# - XYZ position the camera is looking at
# - World Space position and orientation of the 3-D object.
# - The field of view and near and far distances of the perpectice projection viewing frustum.
# - RGB color of the diffuse material on the object (called m_diff here as parts of Lamebert Cosine Law)
############################################################################################################

######################### import libraries for matrix calculations and plotting ##############################
from numpy import *
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection

############################################ INITIAL PARAMETER VALUES: #######################################
filename = 'shark_ag.raw'
light_pos = [0,40,-75]
camera_pos = [0,40,-75]
camera_look = [0,30,4]
obj_pos = [0,-7,0]
obj_orient = [-90,135,0]
fov = 80.0
near = 1.0
far = 200.0
m_diff = [192/255, 192/255, 192/255] # rgb_color of the material; used in the c_diff calculation
##############################################################################################################

########################## some helper functions for handling calculations ###################################
def normal(vec):
	norm = linalg.norm(vec)
	if norm == 0:
		return vec
	else:
		return vec/norm

def sort_avgz(vec):
	return average([vec[0][2], vec[1][2], vec[2][2]])

def rgb_color(vec):
	red = min(vec[0],1.0)
	green = min(vec[1],1.0)
	blue = min(vec[2],1.0)
	return [red,green,blue]

########################## matrix declarations and pre-multiplications that can be done ######################
# translation matrix holds the new position the object hold in the world space based on obj_pos
translation_mat = array([ [1, 0, 0, 0],
						 [0, 1, 0, 0],
						 [0, 0, 1, 0],
						 [obj_pos[0], obj_pos[1], obj_pos[2], 1] ])
# rotation/orientation x,y,z (in that order) matrices hold the rotation of the object based on obj_orient	
rotateX_mat = array([ [1, 0, 0, 0],
					 [0, cos(deg2rad(obj_orient[0])), sin(deg2rad(obj_orient[0])), 0],
					 [0, -sin(deg2rad(obj_orient[0])), cos(deg2rad(obj_orient[0])), 0],
					 [0, 0, 0 , 1] ])
rotateY_mat = array([ [cos(deg2rad(obj_orient[1])), 0, -sin(deg2rad(obj_orient[1])), 0], 
					 [0, 1, 0, 0],
					 [sin(deg2rad(obj_orient[1])), 0, cos(deg2rad(obj_orient[1])), 0],
					 [0, 0, 0, 1] ])
rotateZ_mat = array([ [cos(deg2rad(obj_orient[2])), sin(deg2rad(obj_orient[2])), 0, 0],
					 [-sin(deg2rad(obj_orient[2])), cos(deg2rad(obj_orient[2])), 0, 0],
					 [0, 0, 1, 0],
					 [0, 0, 0, 1] ])
# combine the effects of all of the transformation matrices above
rot_mat = matmul(matmul(rotateX_mat,rotateY_mat),rotateZ_mat)
worldtrans_mat = matmul(rot_mat,translation_mat)

# view transformation matrix - this calculation is derived from the Microsoft D3D documentation
# pEye corresponds to the camera_pos; pAt corresponds to the camera_look; the up vector is (0,1,0)
up = array([0,1,0])
zaxis = normal(subtract(camera_look,camera_pos))
xaxis = normal(cross(up,zaxis))
yaxis = cross(zaxis, xaxis)
viewtrans_mat = array([ [xaxis[0], yaxis[0], zaxis[0], 0],
					   [xaxis[1], yaxis[1], zaxis[1], 0],
					   [xaxis[2], yaxis[2], zaxis[2], 0],
					   [-dot(xaxis,camera_pos), -dot(yaxis, camera_pos), -dot(zaxis, camera_pos), 1] ])

# perspective transformation matrices - this calculation is derived from the Microsoft D3D documentation
# we are assuming an aspect ratio of 1; cot(x) is 1/tan(x); zf is the far view; zn is near view; 
# fovy is field of view in radians
yscale = 1/(tan(fov/2.0))
xscale = yscale
perspectivetrans_mat = array([ [xscale, 0, 0, 0],
							  [0, yscale, 0, 0],
							  [0, 0, far/float(far-near), 1],
							  [0, 0, -(near*far)/float(far-near), 0] ])

#combine the effects of the view and perspective matrices
projection_mat = matmul(viewtrans_mat,perspectivetrans_mat)

################################################# where some coding happens ##################################
# read in the raw file and put the vertices into an array; loadtext() is a numpy function
# each row hold a 3 points corresponding to a triangle
raw_model = loadtxt(filename)
# need to make the points into individual arrays and apply the transformation to the object in world coordinates
world_model = []
for triangle in raw_model:
	triangle_arr = []
	for i in range(3):
		# modify the read-in raw_model so that each xyz is its own array and add the w coordinate for all 3 them
		# then append that array to the triangle_arr 
		this_point = array([triangle[i*3], triangle[(i*3) + 1], triangle[(i*3) + 2], 1])
		# while we are here, apply the worldtrans_mat transformation to this point
		this_point = matmul(this_point,worldtrans_mat)
		triangle_arr.append(this_point)
	# the world model holds all the array of the array of 3 points with world transformation done
	world_model.append(triangle_arr)

# need to do the lighting calculations; lighting calc is following the Lamberts Cosine Law
# the normal computed here is not the artist rendered normal but instead the normal of the point (backface culling method)
# the normal is calculated as the cross product of 2 given vectors (points in the triangle)
# will append the color to the array holding the triangle vertices
world_color_model = []
for triangle in world_model:
	#compute the normal of the triangle
	vec_1 = array([(triangle[1][0] - triangle[0][0]), (triangle[1][1] - triangle[0][1]), (triangle[1][2] - triangle[0][2])])
	vec_2 = array([(triangle[2][0] - triangle[0][0]), (triangle[2][1] - triangle[0][1]), (triangle[2][2] - triangle[0][2])])
	vec_norm = normal(cross(vec_1,vec_2))
	# light is all ones so we dont have to the colorwise product 
	#compute the average position of the three vertices (as mentioned in Piazza Post)
	avg_pos = ((triangle[0] + triangle[1] + triangle[2])/3.0)[0:3]
	light_vec = subtract(light_pos, avg_pos) # need only x,y,z points of avg_pos
	#normalize the light_vec
	lightNormal_vec = normal(array([light_vec[0], light_vec[1], light_vec[2]]))
	normallight_dot = dot(lightNormal_vec,vec_norm)
	multiplier = max(0,normallight_dot)
	c_diff = array([m_diff[0]*multiplier, m_diff[1]*multiplier, m_diff[2]*multiplier])
	# lets append this c_diff to the triangle so we know the color of that triangle
	triangle.append(c_diff)
	world_color_model.append(triangle)
# need to apply the projection_mat which holds the matrix view and perpective changes
model = []
for triangle in world_color_model:
	triangle_arr = []
	for i in range(3):
		this_point = triangle[i]
		# apply the matrix
		this_point = matmul(this_point,projection_mat)
		# divide all by the w coordinate
		perspective_point = array([this_point[0]/this_point[3], this_point[1]/this_point[3], this_point[2]/this_point[3], this_point[3]/this_point[3]])
		triangle_arr.append(perspective_point)
	#append the color as well
	triangle_arr.append(triangle[3])
	model.append(triangle_arr)
# next need to use the painters algoritm (z sorting)
model.sort(key = sort_avgz, reverse = True)
# now we plot points that are only within the z range of 0 to 1
fig, ax = plt.subplots()
patches = []
for triangle in model:
	if (triangle[0][2] >= 0 and triangle[1][2] >= 0 and triangle[2][2] >= 0) or (triangle[0][2] <= 1 and triangle[1][2] <= 1 and triangle[2][2] <= 1):
		#if meets above condition of being between 0 and 1 we plot the triangle with its corresponding color
		polygon_triangle = Polygon(array([ [triangle[0][0], triangle[0][1]], [triangle[1][0],triangle[1][1]], [triangle[2][0],triangle[2][1]] ]), True, color = rgb_color(triangle[3]))
		patches.append(polygon_triangle)

p = PatchCollection(patches, match_original = True)
# colors = array([100,100,100])
# p.set_array(colors)

ax.add_collection(p)
plt.show()


