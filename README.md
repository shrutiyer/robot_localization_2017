# robot_localization_2017
This is the base repo for the robot  localization assignment in CompRobo, spring 2017.

## TODO List
- [x] Initialize the particles via random sampling
- [X] Update the particles using data from odometry
  - [X] Figure out what the `delta` is
  - [X] Apply the `delta` to all of our particles
- [X] Reweight the particles based on their compatibility with the laser scan
- [X] Resample without replacement a new set of particles with probability proportional to their weights
- [ ] You must include a couple of bag files of your code in action.  Place the bag files in a subdirectory of your ROS package called "bags".  In this folder, create a README file that explains each of the bag files (how they were collected, what you take from the results, etc.).
- [ ] Writeup
