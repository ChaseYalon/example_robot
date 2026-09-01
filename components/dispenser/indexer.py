from phoenix6 import hardware, configs, signals, controls
from smartunits import amps


class Indexer:
    left_kicker_motor = hardware.TalonFXS(4)
    right_kicker_motor = hardware.TalonFXS(5)
    conveyor_motor = hardware.TalonFXS(6)
    kicker_amps = amps.of(40.0)
    conveyor_amps = amps.of(20.0)

    kick_on = False
    conv_on = False

    def __init__(self):
        kicker_motor_configs = configs.TalonFXSConfiguration()
        kicker_motor_configs.motor_output.neutral_mode = signals.NeutralModeValue.BRAKE
        kicker_motor_configs.commutation.motor_arrangement = (
            signals.MotorArrangementValue.NEO550_JST
        )
        kicker_motor_configs.current_limits.supply_current_limit = self.kicker_amps

        self.left_kicker_motor.configurator.apply(kicker_motor_configs)
        self.right_kicker_motor.configurator.apply(kicker_motor_configs)

        conveyor_motor_configs = configs.TalonFXSConfiguration()
        conveyor_motor_configs.motor_output.neutral_mode = (
            signals.NeutralModeValue.COAST
        )
        conveyor_motor_configs.commutation.motor_arrangement = (
            signals.MotorArrangementValue.BRUSHED_DC
        )
        conveyor_motor_configs.current_limits.supply_current_limit = self.conveyor_amps

        self.conveyor_motor.configurator.apply(conveyor_motor_configs)

    def kicker_on(self):
        self.kick_on = True

    def kicker_off(self):
        self.kick_on = False

    def conveyor_on(self):
        self.conv_on = True

    def conveyor_off(self):
        self.conv_on = False

    def execute(self):
        if self.kick_on:
            self.left_kicker_motor.set_control(controls.VoltageOut(12))
            self.right_kicker_motor.set_control(controls.VoltageOut(12))
        if self.conv_on:
            self.conveyor_motor.set_control(controls.VoltageOut(-12))
