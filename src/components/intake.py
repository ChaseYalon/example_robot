from phoenix6 import hardware, configs, signals, controls, CANBus
import constants as constants
#gifrom lemonlib import control
from lemonlib import smart  # , util
import enum
from smartunits import Current, amps, volts
from wpilib import CANPort



class Intake: 

    # unused - hinge_alert = util.Alert("intake hinge has rotated too far!", util.AlertType.WARNING)
    # unused - break_alert = util.Alert("intake arm may be breaking! Check for mechanical issues.", util.AlertType.ERROR)
    # unused - bypass_alert = util.Alert("Bypassing intake limits!", util.AlertType.WARNING)

    spin_voltage: Current
    arm_voltage: Current

    def __init__(self):
        self.intake_canbus = CANBus(CANPort.CAN_S1)
        self.spin_motor = hardware.TalonFX(51, self.intake_canbus)
        self.left_motor = hardware.TalonFXS(52, self.intake_canbus)
        self.right_motor = hardware.TalonFXS(53, self.intake_canbus)
        # spin config
        spin_config = configs.TalonFXConfiguration()
        spin_config.motor_output.neutral_mode = signals.NeutralModeValue.BRAKE
        spin_config.current_limits.supply_current_limit = amps.of(60.0)
        spin_config.current_limits.supply_current_limit_enable = True
        self.spin_motor.configurator.apply(spin_config)


        # arm config
        arm_motor_config = configs.TalonFXSConfiguration()
        arm_motor_config.current_limits.stator_current_limit = amps.of(40.0)
        arm_motor_config.current_limits.stator_current_limit_enable = True
        arm_motor_config.motor_output.neutral_mode = signals.NeutralModeValue.BRAKE
        arm_motor_config.commutation.motor_arrangement = (
            signals.MotorArrangementValue.BRUSHED_DC
        )
        self.left_motor.configurator.apply(arm_motor_config)
        self.right_motor.configurator.apply(arm_motor_config)

        self._arm_slot0 = arm_motor_config.slot0

        # left follows right
        self.arm_follower = controls.Follower(
            self.right_motor.device_id, signals.MotorAlignmentValue.ALIGNED
        )
        self.left_motor.set_control(self.arm_follower)

    def set_voltage(self, voltage: Current):
        self.spin_voltage = voltage

    def set_arm_voltage(self, angle: Current):
        self.arm_voltage = angle

    def execute(self):
        try:
            self.spin_motor.set_control(controls.VoltageOut(self.spin_voltage.in_unit(volts)))
        except:
            pass
        try:
            # left motor is following
            self.right_motor.set_control(controls.VoltageOut(self.arm_voltage.in_unit(volts)))
        except:
            pass