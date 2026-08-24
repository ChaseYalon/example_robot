import wpilib
from example_robot.components.intake import Intake
from example_robot.lemonlib import control
class MyRobot(wpilib.TimedRobot):
    intake: Intake
    primary: control.LemonInput
    secondary: control.LemonInput
    def robotInit(self):
        self.intake = Intake()

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

        #<Execute>
        self.intake.execute()
        #</Execute>

    def teleopInit(self):
        self.primary = control.LemonInput(0)
        self.secondary = control.LemonInput(1)

    def autonomousPeriodic(self):
        pass
