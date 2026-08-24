import wpilib
from components.intake import Intake
from lemonlib import control
from components.dispenser import Controller
class MyRobot(wpilib.TimedRobot):
    intake: Intake
    shot_controller: Controller
    primary: control.LemonInput
    secondary: control.LemonInput
    def robotInit(self):
        self.intake = Intake()
        self.shot_controller = Controller()
    def teleopPeriodic(self):

        #<Intake>
        #rollers
        if self.secondary.getLeftTriggerAxis() >= 0.8:
            self.intake.set_voltage(-10.0)
        elif self.secondary.getLeftBumper():
            self.intake.set_voltage(10.0)
        #hinge
        if self.secondary.getXButton():
            self.intake.set_arm_voltage(12)
        elif self.secondary.getBButton():
            self.intake.set_arm_voltage(-6)
        #</Intake>

        #<Shooter>
        if self.secondary.getRightTriggerAxis() >= 0.8:
            self.shot_controller.shoot()
        else:
            self.shot_controller.stop_shoot()
        #</Shooter>
        #<Execute>
        self.intake.execute()
        self.shot_controller.execute()
        #</Execute>

    def teleopInit(self):
        self.primary = control.LemonInput(0)
        self.secondary = control.LemonInput(1)

    def autonomousPeriodic(self):
        pass
