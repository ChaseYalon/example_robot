import wpilib
from components.intake import Intake
from lemonlib import control
from components.dispenser import Controller
from components.swerve import SwerveDrive
from components.odometry import Odometry
from wpimath import units
import math
class MyRobot(wpilib.TimedRobot):
    intake: Intake
    shot_controller: Controller
    swerve: SwerveDrive
    odometry: Odometry
    primary: control.LemonInput
    secondary: control.LemonInput
    MAX_METERS_PER_SECOND = units.meters_per_second(3)
    MAX_ROTATIONS_PER_SECOND = units.radians_per_second(math.pi)
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
            self.intake.set_voltage(-10.0)
        elif self.secondary.getLeftBumper():
            self.intake.set_voltage(10.0)
        # hinge
        if self.secondary.getXButton():
            self.intake.set_arm_voltage(12)
        elif self.secondary.getBButton():
            self.intake.set_arm_voltage(-6)
        # </Intake>

        # <Shooter>
        if self.secondary.getRightTriggerAxis() >= 0.8:
            self.shot_controller.shoot(self.odometry.get_target_distance())
        else:
            self.shot_controller.stop_shoot()
        # </Shooter>
        
        # <Swerve>
        self.swerve.drive(
            self.primary.getLeftX() * self.MAX_METERS_PER_SECOND,
            self.primary.getLeftY() * self.MAX_METERS_PER_SECOND,
            self.primary.getRightX() * self.MAX_ROTATIONS_PER_SECOND,
            self.primary.getLeftStickButton() #idk if this is a good button
        )
        #</Swerve>
        
        # <Execute>
        self.intake.execute()
        self.shot_controller.execute()
        self.swerve.execute()
        # </Execute>

    def teleopInit(self):
        self.primary = control.LemonInput(0)
        self.secondary = control.LemonInput(1)

    def autonomousPeriodic(self):
        pass
