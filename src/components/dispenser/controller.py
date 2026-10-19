"""
ALGORITHM:
The shooter's pitch is mechanically fixed at SHOOTER_ANGLE - only volts (exit velocity) is adjustable.
Take the average of minVolts and maxVolts to get workingVolts.
Calculate where the ball will be, at SHOOTER_ANGLE, when it reaches horizontalDistance (undershooting,
overshooting, or landing in the net) and when it reaches the back rim of the hoop (to check the backboard).
If the ball falls short of HOOP_HEIGHT, set minVolts to workingVolts (need more power).
If the ball is still at or above HOOP_HEIGHT when it reaches the back rim edge, it clangs off the backboard -
treat this the same as overshooting: set maxVolts to workingVolts (need less power).
If the ball goes over NET_HEIGHT, set maxVolts to workingVolts (need less power).
Otherwise the ball lands cleanly between HOOP_HEIGHT and NET_HEIGHT without hitting the backboard - working
value found, exit loop.
"""

import math
import time

# CONSTANTS - These are made up numbers
# unused until the model accounts for air drag (a gravity-only projectile is
# independent of mass, and diameter only matters through drag/Magnus):
# BALL_WEIGHT = 15  # grams
# BALL_DIAMETER = 0.1524  # meters = 6 inches
HOOP_RADIUS = 1.0922  # meters = 42 inches
HOOP_HEIGHT = 1.8288  # meters = 72 inches
ACCURACY_TOLERANCE = 0.0762  # meters = 3 inches
NET_HEIGHT = 3.048  # meters = 120 inches
BALL_EXIT_HEIGHT = 0.254  # meters = 10 inches
GRAVITY = 9.81  # m/s^2
THETA = 23 #douible check this is right

# </Algorithms_etc>
from .indexer import Indexer
from .shooter import Shooter
from smartunits.voltage import volts
from smartunits import Distance
from smartunits.distance import meters
class Controller:
    indexer: Indexer
    shooter: Shooter
    """How many volts it takes the shooter to spin 1 rpm faster, NEEDS TUNING"""
    MAX_VOLTS = volts.of(12.0)
    should_shoot = False
    distance_from_target: Distance
    def __init__(self):
        self.indexer = Indexer()
        self.shooter = Shooter()

    def shoot(self, distance_from_target: Distance):
        self.should_shoot = True
        self.distance_from_target = distance_from_target
    def stop_shoot(self):
        self.should_shoot = False

    def execute(self):
        if not self.should_shoot:
            self.shooter.set_velocity(
                volts_to_velocity(0.8 * self.MAX_VOLTS.in_unit(volts))
            )  # 0.8 is a made up number, tune
            self.indexer.conveyor_off()
            self.indexer.kicker_off()
        else:
            self.shooter.set_velocity(calc_optimal_volts(self.distance_from_target.in_unit(meters)))
            self.indexer.kicker_on()
            self.indexer.conveyor_on()

        self.indexer.execute()
        self.shooter.execute()
