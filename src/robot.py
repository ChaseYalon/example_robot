import wpilib
import constants as constants
from components.intake import Intake
from lemonlib import LemonInput
from components.dispenser import Controller
from components.swerve import SwerveDrive
if constants.ODOMETRY:
    from components.odometry import Odometry
from components.auto import AutoContext, AutoRunner
from smartunits import (
    meters_per_second, radians_per_second, volts,
    Velocity, AngularVelocity,
)
import math
from lemonlib.util import curve, AlertManager, AlertType
from pathlib import Path
class MyRobot(wpilib.TimedRobot):
    intake: Intake
    shot_controller: Controller
    swerve: SwerveDrive
    odometry: Odometry

    def __init__(self):
        super().__init__()
        self.MAX_LINEAR_VELOCITY : Velocity = meters_per_second.of(3)
        self.MAX_ANGULAR_VELOCITY : AngularVelocity = radians_per_second.of(math.pi)

        self.intake = Intake()
        self.shot_controller = Controller()
        self.swerve = SwerveDrive()
        self.odometry = Odometry(self.swerve)
        self.DEADBAND = 0.1 #arbitrary
    def teleop_init(self):
        self.primary = LemonInput(0)  # Gotta create on telop init so we know that driver station is
        self.secondary = LemonInput(1)  # connected to robot and to get most up to date info

    def teleop_periodic(self):
        self.odometry.execute() #prevent datalag

        # <Intake>
        # rollers
        if self.secondary.getLeftTriggerAxis() >= 0.8:
            self.intake.set_voltage(volts.of(-10.0))
        elif self.secondary.getLeftBumper():
            self.intake.set_voltage(volts.of(10.0))
        else:
            self.intake.set_voltage(volts.of(0.0))
        # hinge
        if self.secondary.getXButton():
            
            self.intake.set_arm_voltage(volts.of(-10.0))
        elif self.secondary.getBButton():
            self.intake.set_arm_voltage(volts.of(6.0))
        # </Intake>

        # <Shooter>
        if self.secondary.getRightTriggerAxis() >= 0.8:
            self.shot_controller.shoot(self.odometry.get_target_distance())
        else:
            self.shot_controller.stop_shoot()
        # </Shooter>
        
        # <Swerve>
        self.curve = curve(
            lambda x: 1.89 * x**3 + 0.61 * x,
            0.0,
            deadband=0.1,
            max_mag=1.0
        )

        # Scale dimensionless joystick inputs by the maximum speeds.
        vx = meters_per_second.of(
            self.curve(self.primary.getLeftY())
            * self.MAX_LINEAR_VELOCITY.into(meters_per_second)
        ).into(meters_per_second)

        vy = meters_per_second.of(
            self.curve(self.primary.getLeftX())
            * self.MAX_LINEAR_VELOCITY.into(meters_per_second)
        ).into(meters_per_second)

        omega = -radians_per_second.of(
            self.curve(self.primary.getRightX())
            * self.MAX_ANGULAR_VELOCITY.into(radians_per_second)
        ).into(radians_per_second)

        self.swerve.drive(
            vx,
            vy,
            omega,
            field_relative=True
        )
        if self.primary.getSquareButton():
            self.swerve.reset_heading()

        #</Swerve>
        
        # <Execute>
        #odometry moved to top
        self.intake.execute()
        try:
            self.shot_controller.execute()
        except RuntimeError:
            AlertManager.instant_alert("Shot physicaly impossible with given parameters", AlertType.ERROR)
        self.swerve.execute()
        # </Execute>

    def teleopInit(self):
        self.primary = LemonInput(0)
        self.secondary = LemonInput(1)
    def autonomous_init(self):
        self.ctx = AutoContext(self.swerve, self.intake, self.shot_controller, self.odometry)
        try:
            self.routine1 = AutoRunner("./py/deploy/choreo/BlueLeftIntakeShoot.traj")
        except:
            AlertManager.instant_alert("file not found", AlertType.ERROR)
    def autonomous_periodic(self):
        files = [item.name for item in Path("./py/deploy/").iterdir()]
        AlertManager.instant_alert(f"hey we are running auto {files}", AlertType.INFO, timeout=60)
        self.routine1.execute(self.ctx)
        self.ctx.execute()
