import sys, os
# vendored git submodules (each repo nests its package one level down)
for _p in ("vendor/smartunits", "vendor/lemonlib"):
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), _p))

import wpilib
from components.intake import Intake
from lemonlib import control
from components.dispenser import Controller
from components.swerve import SwerveDrive
from components.odometry import Odometry
from components.auto import AutoContext, AutoRunner
from smartunits import (
    meters_per_second, radians_per_second, volts,
    Velocity, AngularVelocity,
)
import math
class MyRobot(wpilib.TimedRobot):
    intake: Intake
    shot_controller: Controller
    swerve: SwerveDrive
    odometry: Odometry
    primary: control.LemonInput
    secondary: control.LemonInput
    MAX_LINEAR_VELOCITY : Velocity = meters_per_second.of(3)
    MAX_ANGULAR_VELOCITY : AngularVelocity = radians_per_second.of(math.pi)
    def robotInit(self):
        self.intake = Intake()
        self.shot_controller = Controller()
        self.swerve = SwerveDrive()
        self.odometry = Odometry(self.swerve)
        
    def teleopPeriodic(self):
        self.odometry.execute() #prevent datalag

        # <Intake>
        # rollers
        if self.secondary.getLeftTriggerAxis() >= 0.8:
            self.intake.set_voltage(volts.of(-10.0))
        elif self.secondary.getLeftBumper():
            self.intake.set_voltage(volts.of(10.0))
        # hinge
        if self.secondary.getXButton():
            self.intake.set_arm_voltage(volts.of(12.0))
        elif self.secondary.getBButton():
            self.intake.set_arm_voltage(volts.of(-6.0))
        # </Intake>

        # <Shooter>
        if self.secondary.getRightTriggerAxis() >= 0.8:
            self.shot_controller.shoot(self.odometry.get_target_distance())
        else:
            self.shot_controller.stop_shoot()
        # </Shooter>
        
        # <Swerve>
        self.swerve.drive(
            meters_per_second.of(self.primary.getLeftX() * self.MAX_LINEAR_VELOCITY.in_units(meters_per_second)),
            meters_per_second.of(self.primary.getLeftY() * self.MAX_LINEAR_VELOCITY.in_units(meters_per_second)),
            radians_per_second.of(self.primary.getRightX() * self.MAX_ANGULAR_VELOCITY.in_units(radians_per_second)),
            self.primary.getLeftStickButton() #idk if this is a good button
        )
        #</Swerve>
        
        # <Execute>
        #odometry moved to top
        self.intake.execute()
        self.shot_controller.execute()
        self.swerve.execute()
        # </Execute>

    def teleopInit(self):
        self.primary = control.LemonInput(0)
        self.secondary = control.LemonInput(1)
    def autonomousInit(self):
        self.ctx = AutoContext(self.swerve, self.intake, self.shot_controller, self.odometry)
        self.routine1 = AutoRunner("./choreo/BlueLeftIntakeShoot.traj")
    def autonomousPeriodic(self):
        self.routine1.execute(self.ctx)
        self.ctx.execute()
