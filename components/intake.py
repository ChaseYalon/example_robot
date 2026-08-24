from phoenix6 import hardware, configs, signals, controls
from example_robot.lemonlib import control
from example_robot.lemonlib import smart#, util
from wpimath import units
import enum

import example_robot.constants as constants


class Intake:
    
    spin_motor = hardware.TalonFX(51)
    left_motor = hardware.TalonFXS(52)
    right_motor = hardware.TalonFXS(53)
    
    #unused - hinge_alert = util.Alert("intake hinge has rotated too far!", util.AlertType.WARNING)
    #unused - break_alert = util.Alert("intake arm may be breaking! Check for mechanical issues.", util.AlertType.ERROR)
    #unused - bypass_alert = util.Alert("Bypassing intake limits!", util.AlertType.WARNING)

    spin_voltage: units.volts
    arm_voltage: units.volts

    def __init__(self):
        #spin config
        spin_config = configs.TalonFXConfiguration()
        spin_config.motor_output.neutral_mode = signals.NeutralModeValue.BRAKE
        spin_config.current_limits.supply_current_limit = units.amperes(60)
        spin_config.current_limits.supply_current_limit_enable = True
        self.spin_motor.configurator.apply(spin_config)

        #arm pid gains
        self.profile = smart.SmartProfile(
            "intake_arm",
            {"kP": 10.0, "kI": 0.0, "kD": 0.0},
            constants.TUNING_ENABLED,
        )

        #arm config
        arm_motor_config = configs.TalonFXSConfiguration()
        arm_motor_config.current_limits.stator_current_limit = units.amperes(24)
        arm_motor_config.commutation.motor_arrangement = signals.MotorArrangementValue.BRUSHED_DC
        arm_motor_config.slot0 = self.profile.create_ctre_pid_controller()
        self.left_motor.configurator.apply(arm_motor_config)
        self.right_motor.configurator.apply(arm_motor_config)

        self._arm_slot0 = arm_motor_config.slot0
        self._last_gains = dict(self.profile.gains)

        #left follows right
        self.arm_follower = controls.Follower(
            self.right_motor.device_id, signals.MotorAlignmentValue.ALIGNED
        )
        self.left_motor.set_control(self.arm_follower)


    def set_voltage(self, voltage: units.volts):
        self.spin_voltage = voltage

    def set_arm_voltage(self, angle: units.volts):
        self.arm_voltage = angle

    def execute(self):
        self.spin_motor.set_control(controls.VoltageOut(self.spin_voltage))

        if constants.TUNING_ENABLED and self.profile.gains != self._last_gains:
            self._last_gains = dict(self.profile.gains)
            self._arm_slot0 = self.profile.create_ctre_pid_controller()
            self.left_motor.configurator.apply(self._arm_slot0)
            self.right_motor.configurator.apply(self._arm_slot0)

        #left motor is following
        self.right_motor.set_control(controls.VoltageOut(self.arm_voltage))