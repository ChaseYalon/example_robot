
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
BALL_WEIGHT = 15  # grams
BALL_DIAMETER = 0.1524  # meters = 6 inches
HOOP_RADIUS = 1.0922  # meters = 42 inches
HOOP_HEIGHT = 1.8288  # meters = 72 inches
ACCURACY_TOLERANCE = 0.0762  # meters = 3 inches
NET_HEIGHT = 3.048  # meters = 120 inches
BALL_EXIT_HEIGHT = 0.254  # meters = 10 inches
GRAVITY = 9.81  # m/s^2
EXIT_VELOCITY = 10.0  # m/s
MAX_ALLOWABLE_ITERATIONS = 1000#max allowable iterations to prevent infinite loops
SHOOTER_ANGLE = 23.0  # degrees, mechanically fixed - shooter can no longer pitch

def horizontal_distance_over_time(initialVelocity: float, angle: float, time: float) -> float:
    return initialVelocity * math.cos(math.radians(angle)) * time

def vertical_distance_over_time(initialVelocity: float, angle: float, time: float) -> float:
    return (BALL_EXIT_HEIGHT
            + initialVelocity * math.sin(math.radians(angle)) * time
            - 0.5 * GRAVITY * time ** 2)

def time_to_reach_target_horizontal_distance(initialVelocity: float, angle: float, horizontalDistance: float) -> float:
    return horizontalDistance / (initialVelocity * math.cos(math.radians(angle)))

def vertical_position_at_horizontal_distance(initialVelocity: float, angle: float, horizontalDistance: float) -> float:
    time = time_to_reach_target_horizontal_distance(initialVelocity, angle, horizontalDistance)
    return vertical_distance_over_time(initialVelocity, angle, time)

def volts_to_velocity(volts: float) -> float:
    return volts * 10

def hits_backboard(velocity: float, horizontalDistance: float) -> bool:
    """True if the ball is still at/above HOOP_HEIGHT when it reaches the back rim of the hoop -
    it clangs off the backboard instead of dropping through."""
    back_edge_x = horizontalDistance + HOOP_RADIUS - ACCURACY_TOLERANCE
    y_back = vertical_position_at_horizontal_distance(velocity, SHOOTER_ANGLE, back_edge_x)
    return y_back >= HOOP_HEIGHT


def shot_is_possible(horizontalDistance: float) -> bool:
    volts = 0.1  # start above 0 - volts_to_velocity(0) makes horizontal time undefined
    while volts <= 12.0:
        velocity = volts_to_velocity(volts)
        expectedVerticalPos = vertical_position_at_horizontal_distance(velocity, SHOOTER_ANGLE, horizontalDistance)

        if HOOP_HEIGHT <= expectedVerticalPos <= NET_HEIGHT and not hits_backboard(velocity, horizontalDistance):
            return True  # Some volts value lands cleanly in the hoop

        volts += 0.1  # Increment volts

    # If no volts value works at this fixed angle, shot is impossible
    return False


def calc_optimal_volts(horizontalDistance: float) -> float:
    maxVolts: float = 12
    minVolts: float = 0

    workingVolts: float = 0.0
    iterationCount = 0
    if not shot_is_possible(horizontalDistance):
        raise RuntimeError("The shot is physically impossible with given parameters.")
    while True:
        workingVolts = (maxVolts + minVolts) / 2
        velocity = volts_to_velocity(workingVolts)

        expectedVerticalPos = vertical_position_at_horizontal_distance(velocity, SHOOTER_ANGLE, horizontalDistance)

        if expectedVerticalPos < HOOP_HEIGHT:
            minVolts = workingVolts  # short - needs more power
        elif expectedVerticalPos > NET_HEIGHT or hits_backboard(velocity, horizontalDistance):
            maxVolts = workingVolts  # long, or clangs off the backboard - needs less power
        else:
            break  # clean make

        iterationCount += 1
        if iterationCount > MAX_ALLOWABLE_ITERATIONS:
            raise RuntimeError(f"NO SOLUTION Volts = {workingVolts}")

    return workingVolts

#</Algorithms_etc>
HORIZONTAL_DISTANCE_TEMP = 1.0
from indexer import Indexer
from shooter import Shooter
from wpimath import units
class Controller:
    indexer: Indexer
    shooter: Shooter
    """How many volts it takes the shooter to spin 1 rpm faster, NEEDS TUNING"""
    VOLTAGE_TO_VELOCITY = 1.0#temp number
    MAX_VOLTS = units.volts(12.0)
    should_shoot = False
    def __init__(self):
        self.indexer = Indexer()
        self.shooter = Shooter()
    def shoot(self):
        self.should_shoot = True
    def stop_shoot(self):
        self.should_shoot = False
    def execute(self):
        if not self.should_shoot:
            self.shooter.set_velocity(0.8 * self.MAX_VOLTS * self.VOLTAGE_TO_VELOCITY) #0.8 is a made up number, tune
            self.indexer.conveyor_off()
            self.indexer.kicker_off()
        else :
            raise RuntimeError #needs odometry first
            self.shooter.set_velocity(calc_optimal_volts(HORIZONTAL_DISTANCE_TEMP))
            self.indexer.kick_on()
            self.indexer.conv_on()

        self.indexer.execute()
        self.shooter.execute()