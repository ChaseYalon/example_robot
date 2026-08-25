from phoenix6 import hardware, configs, signals, controls
from lemonlib import smart
from wpimath import units
import constants


class Shooter:
    left_motor = hardware.TalonFX(2)
    right_motor = hardware.TalonFX(3)
    shooter_profile: smart.SmartProfile
    base_config: configs.TalonFXConfiguration
    velocity: float  # should be a better unit

    def __init__(self):
        slot0 = self.shooter_profile.create_ctre_flywheel_controller()
        slot1 = (
            configs.Slot1Configs()
            .with_k_p(slot0.k_p + 0.1)
            .with_k_v(slot0.k_v)
            .with_k_a(slot0.k_a)
        )

        config = configs.TalonFXConfiguration()

        config.motor_output.neutral_mode = signals.NeutralModeValue.COAST
        config.motor_output.inverted = signals.InvertedValue.CLOCKWISE_POSITIVE

        config.feedback = (
            configs.FeedbackConfigs()
            .with_feedback_sensor_source(signals.FeedbackSensorSourceValue.ROTOR_SENSOR)
            .with_sensor_to_mechanism_ratio(1.0)
        )

        config.current_limits.stator_current_limit = units.amperes(120)
        config.current_limits.stator_current_limit_enable = True

        config.current_limits.supply_current_limit = units.amperes(70)
        config.current_limits.supply_current_limit_enable = True

        config.torque_current.peak_forward_torque_current = units.amperes(140)
        config.torque_current.peak_reverse_torque_current = -units.amperes(140)

        config.slot0 = slot0
        config.slot1 = slot1

        self.right_motor.configurator.apply(config)
        self.left_motor.configurator.apply(config)

        # right follows the left
        self.shooter_follower = controls.Follower(
            self.left_motor.device_id, signals.MotorAlignmentValue.OPPOSED
        )
        self.right_motor.set_control(self.shooter_follower)
        self.base_config = config

    def set_velocity(self, velocity: float):
        self.velocity = velocity

    def on_enable(self):
        if constants.TUNING_ENABLED:
            self.slot0 = self.shooter_profile.create_ctre_flywheel_controller()
            self.slot1 = (
                configs.Slot1Configs()
                .with_k_p(self.slot0.k_p + 0.1)
                .with_k_v(self.slot0.k_v)
                .with_k_a(self.slot0.k_a)
            )

            self.base_config.slot0 = self.slot0
            self.base_config.slot1 = self.slot1
            self.right_motor.configurator.apply(self.base_config)
            self.left_motor.configurator.apply(self.base_config)

    def execute(self):
        self.left_motor.set_control(
            controls.VelocityVoltage(self.velocity).with_slot(0)
        )
