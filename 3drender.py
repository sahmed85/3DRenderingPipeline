###########################################################################################################
# File: 3drender.py
# Name: Shadman Ahmed
# Date Created:  06/01/2020
# Last Modified: Ongoing 
# Usage: N/A
# Overview: This python script implements geometry and lighting calculations to render 
# 			an image of a scene of an 3-D object.
# Github/Git: sahmed85/3DRenderingPipeline
# Project: ECE 4795 3-D GPU Rendering Pipeline Homework #1
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

############################################ INITIAL PARAMETER VALUES: #######################################
filename = 'shark_ag.raw'
light_pos = []
camera_pos = []
camera_look = []
obj_pos = []
obj_orient = []
fov = 90
near = 1
far = 200
rgb_color = [227, 143, 143]
##############################################################################################################

######################### import libraries for matrix calculations and plotting ##############################
from numpy import *
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection

########################## some helper functions for handling calculations ###################################
def normal(vec):
	norm = linalg.norm(vec)
	if norm == 0:
		return vec
	else:
		return vec/norm

########################## matrix declarations and pre-multiplications that can be done ######################
# translation matrix holds the new position the object hold in the world space based on obj_pos
translation_mat = array([ [1, 0, 0, 0],
						 [0, 1, 0, 0],
						 [0, 0, 0, 1],
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
worldtrans_mat = matmul(matmul(matmul(rotateX_mat,rotateY_mat),rotateZ_mat),translation_mat)

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
yscale = 1/tan(deg2rad(fov/2))
xscale = yscale / 1
perspectivetrans_mat = array([ [xscale, 0, 0, 0],
							  [0, yscale, 0, 0],
							  [0, 0, far/float(far-near), 1],
							  [0, 0, -(near*far)/float(far-near), 0] ])

#combine the effects of the view and perspective matrices
projection_mat = matmul(viewtrans_mat,perspectivetrans_mat)

################################################# Where some coding happens ##################################
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
		this_point = array([triangle[x*3], triangle[x*3] + 1, triangle[x*3] + 2, 1])
		# while we are here, apply the worldtrans_mat transformation to this point
		this_point = matmul(this_point,worldtrans_mat)
		triangle_arr.append(this_point)
	# the world model holds all the array of the array of 3 points with world transformation done
	world_model.append(triangle_arr)
# we need to do the lighting calculations