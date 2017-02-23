""" An implementation of an occupancy field that you can use to implement
    your particle filter's laser_update function """

import rospy

from std_msgs.msg import Header, String
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import PoseStamped, PoseWithCovarianceStamped, PoseArray, Pose, Point, Quaternion
from nav_msgs.srv import GetMap
from copy import deepcopy

import tf
from tf import TransformListener
from tf import TransformBroadcaster
from tf.transformations import euler_from_quaternion, rotation_matrix, quaternion_from_matrix
from random import gauss

import math
import time

import numpy as np
from numpy.random import random_sample
from sklearn.neighbors import NearestNeighbors

from scipy.stats import halfnorm

class OccupancyField(object):
    """ Stores an occupancy field for an input map.  An occupancy field returns the distance to the closest
        obstacle for any coordinate in the map
        Attributes:
            map: the map to localize against (nav_msgs/OccupancyGrid)
            closest_occ: the distance for each entry in the OccupancyGrid to the closest obstacle
    """

    def __init__(self, map):
        self.MAX_DISTANCE_OUT_OF_BOUNDS = 4 # When point is out of the map, we set a placeholder error (or max distance of laser)
        self.map = map      # save this for later
        # build up a numpy array of the coordinates of each grid cell in the map
        X = np.zeros((self.map.info.width*self.map.info.height,2))

        # while we're at it let's count the number of occupied cells
        total_occupied = 0
        curr = 0
        for i in range(self.map.info.width):
            for j in range(self.map.info.height):
                # occupancy grids are stored in row major order, if you go through this right, you might be able to use curr
                ind = i + j*self.map.info.width
                if self.map.data[ind] > 0:
                    total_occupied += 1
                X[curr,0] = float(i)
                X[curr,1] = float(j)
                curr += 1

        # build up a numpy array of the coordinates of each occupied grid cell in the map
        O = np.zeros((total_occupied,2))
        curr = 0
        for i in range(self.map.info.width):
            for j in range(self.map.info.height):
                # occupancy grids are stored in row major order, if you go through this right, you might be able to use curr
                ind = i + j*self.map.info.width
                if self.map.data[ind] > 0:
                    O[curr,0] = float(i)
                    O[curr,1] = float(j)
                    curr += 1

        # use super fast scikit learn nearest neighbor algorithm
        nbrs = NearestNeighbors(n_neighbors=1,algorithm="ball_tree").fit(O)
        distances, indices = nbrs.kneighbors(X)

        self.closest_occ = np.zeros(100000000) # TODO: Figure out how to make this array dynamic to the input map.
        curr = 0
        for i in range(self.map.info.width):
            for j in range(self.map.info.height):
                ind = i + j*self.map.info.width
                self.closest_occ[ind] = distances[curr][0]*self.map.info.resolution
                curr += 1

    def get_closest_obstacle_distance(self,x,y):
        """ Compute the closest obstacle to the specified (x,y) coordinate in the map.  If the (x,y) coordinate
            is out of the map boundaries, nan will be returned. """
        x_coord = int((x - self.map.info.origin.position.x)/self.map.info.resolution)
        y_coord = int((y - self.map.info.origin.position.y)/self.map.info.resolution)

        # check if we are in bounds
        if x_coord > self.map.info.width or x_coord < 0:
            return float('nan')
        if y_coord > self.map.info.height or y_coord < 0:
            return float('nan')

        ind = x_coord + y_coord*self.map.info.width
        if ind >= self.map.info.width*self.map.info.height or ind < 0:
            return float('nan')
        return self.closest_occ[ind]

    def get_closest_obstacle_distance_matrix(self, x_array, y_array):
        """ The math below is same as the function 'get_closest_obstacle_distance' except
            that it accepts arrays for x and y to speed up the calculation"""
        x_coord_array = np.divide(np.subtract(x_array, self.map.info.origin.position.x), self.map.info.resolution)
        y_coord_array = np.divide(np.subtract(y_array, self.map.info.origin.position.y), self.map.info.resolution)
        x_coord_array = x_coord_array.astype(int)
        y_coord_array = y_coord_array.astype(int)

        x_nan_indexes = np.where(np.logical_or(x_coord_array > self.map.info.width, x_coord_array < 0))
        y_nan_indexes = np.where(np.logical_or(y_coord_array > self.map.info.height, y_coord_array < 0))
        out_of_bounds_indexes = np.unique(np.append(x_nan_indexes, y_nan_indexes))

        np.delete(x_coord_array, out_of_bounds_indexes)
        np.delete(y_coord_array, out_of_bounds_indexes)

        ind_array = np.add(x_coord_array, np.multiply(y_coord_array, self.map.info.width))

        # Returns the sum of the distances of all points.
        return halfnorm.pdf(np.sum(self.closest_occ[ind_array]) + len(out_of_bounds_indexes) * self.MAX_DISTANCE_OUT_OF_BOUNDS, scale=100)
