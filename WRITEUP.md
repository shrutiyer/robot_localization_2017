# Robot Localization Writeup

### David Zhu, Shruti Iyer, Yuzhong Huang

## Goal

The major goal of the project is to learn how to position a robot in a space using a particle filter algorithm. We do that by generating and resampling random particles, using data from sensors (laser scans, robot’s odometry, etc) to increase/decrease probability of all particles and their orientation. 

## High-level Implementation

We start by initializing a particle cloud, where we draw a particle’s location and heading from a normal distribution. Then, we update the particles in the particle cloud using data from the actual robot’s odometry. After all of the particles have been updated, we re-weigh each particle based on their compatibility with data from the laser scan. In this step, we wrote our own occupancy field evaluation function by computing the data in matrix form. We then resample a new set of particles by simple random sampling from the old particle cloud with probability proportional to their weight.

Our robot localizer in action:

![alt text](https://github.com/shrutiyer/robot_localization_2017/blob/master/my_localizer/images/ac109_2.gif)

## Design Decisions

We wanted to reduce time to compute the closest neighbor for multiple angles of multiple particles. So we used numpy and made the computation faster by using arrays. 

```python
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
        return np.sum(halfnorm.pdf(self.closest_occ[ind_array], scale=self.error_distribution_scale)) + np.sum(len(out_of_bounds_indexes) * self.MAX_DISTANCE_OUT_OF_BOUNDS)
```
## Challenges Faced

When we were starting on this project, we had trouble understanding the whole code structure and the system. It was hard to see how each function or class participates in the bigger picture. We didn’t know where to start. For debugging, we had to debug how multiple functions affect the particles rather than unit testing. Visualizations helped to see the overall effect but not so much for smaller groups of functions. We tried to use non-blocking matplotlib plots to see some outputs but it was difficult to get it to work.

## Future Improvements

As next steps, we could improve the way we reweigh the particle. Our particles are always a little more scattered compared to the builtin localizer.

## Lessons Learned/Insights Gained

We learned a real-life application for Bayes Law and probability. We also learned how to test the code using sensor data from a rosbag instead of the robot. 
