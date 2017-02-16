# robot_localization_2017
This is the base repo for the robot  localization assignment in CompRobo, spring 2017.

## TODO List
- [x] Initialize the particles via random sampling
- [X] Update the particles using data from odometry
  - [X] Figure out what the `delta` is
  - [X] Apply the `delta` to all of our particles
- [ ] Reweight the particles based on their compatibility with the laser scan
- [ ] Resample without replacement a new set of particles with probability proportional to their weights
