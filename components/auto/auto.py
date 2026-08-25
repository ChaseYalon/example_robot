from enum import Enum
from typing import List
from wpimath.geometry import Pose2d, Rotation2d
from wpimath.units import meters, degrees, milliseconds
from components.swerve import SwerveDrive
from components.dispenser import Controller
from components.intake import Intake
from components.odometry import Odometry
import time
class StepStatus(Enum):
    RUNNING = 1
    DONE = 2

class AutoContext:
    sd: SwerveDrive
    it: Intake
    sc: Controller
    od: Odometry
    def __init__(self, sd: SwerveDrive, it: Intake, sc: Controller, od: Odometry):
        self.sd = sd
        self.it = it
        self.sc = sc
        self.od = od

class AutoStep:
    """Base class for all auto steps"""

    def execute(self, ctx: AutoContext) -> StepStatus:
        raise NotImplementedError


class AutoRunner:
    def __init__(self, steps: List[AutoStep]):
        self.steps = steps
        self.ctx = None
        self.index = 0

    def reset(self):
        self.index = 0

    def run(self, ctx: AutoContext):
        if self.index >= len(self.steps):
            return

        status = self.steps[self.index].execute(ctx)

        if status == StepStatus.DONE:
            self.index += 1


class ParallelStep(AutoStep):
    """
    Runs multiple steps at the same time.
    Finishes when ALL steps are DONE.
    """

    def __init__(self, *steps: AutoStep):
        self.steps = steps
        # Track which sub-steps have completed so we don't re-execute them
        self._done = [False] * len(steps)

    def execute(self, ctx: AutoContext) -> StepStatus:
        all_done = True
        for i in range(len(self.steps)):
            if self._done[i]:
                continue
            status = self.steps[i].execute(ctx)
            if status == StepStatus.DONE:
                self._done[i] = True
            else:
                all_done = False
        # If any step is not done yet, we're still running
        if not all_done:
            return StepStatus.RUNNING
        return StepStatus.DONE


class SwerveDriveAuto(AutoStep):
    """
    Field-oriented drive: takes absolute field coordinates (x, y in meters, heading in degrees).
    Uses WPILib coordinate system where (0,0) is at field corner from blue alliance perspective.
    """

    POSITION_TOLERANCE = 0.02  # meters

    def __init__(self, x: meters, y: meters, heading: degrees):
        self.x = x
        self.y = y
        self.heading_deg = heading

    def execute(self, ctx: AutoContext) -> StepStatus:
        # TODO: PID - it should do pid not just naivley drive there and dead stop
        # TODO: Angle tolerance
        #is field relative correct
        ctx.sd.drive(self.x, self.y, self.heading_deg, False)#this might be wrong, it might be delta rotations, not new heading

        distance = ctx.sd.get_distance_from_pose(Pose2d(self.x, self.y, Rotation2d(self.heading_deg)))
        if distance <= self.POSITION_TOLERANCE:
            return StepStatus.DONE
        return StepStatus.RUNNING

class SwerveDriveBotRelativeAuto(AutoStep):
    def __init__(self, x: meters, y: meters, heading: degrees):
        self.x = x
        self.y = y
        self.heading = heading
        self.target_pose = None
    def execute(self, ctx: AutoContext) -> StepStatus:
        raise Exception("TODO")
class IntakeAuto(AutoStep):
    """Lets you turn on or off the intake with the boolean parameter"""

    def __init__(self, is_on: bool):
        self.is_on = is_on
        self.applied = False

    def execute(self, ctx: AutoContext) -> StepStatus:
        if not self.applied:
            ctx.it.set_voltage(12 if self.is_on else 0)
            self.applied = True
        return StepStatus.DONE


class ShootAuto(AutoStep):
    def __init__(self):
        self.started = False
        self.duration = 5.0
        # TODO: This should have a durration parameter
    def execute(self, ctx: AutoContext) -> StepStatus:
        if self.start == 0:
            self.start = time.perf_counter()
        if time.perf_counter() - self.start > self.duration:
            return StepStatus.DONE
        ctx.sc.shoot(ctx.od.get_target_distance())
        return StepStatus.RUNNING
