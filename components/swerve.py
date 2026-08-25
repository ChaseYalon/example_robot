import constants
from phoenix6 import swerve, hardware
from phoenix6.swerve import requests
from wpimath import geometry, units

class SwerveDrive:
    drivetrain: swerve.SwerveDrivetrain
    period = 0.02
    desired_pose = geometry.Pose2d()
    field_centric_req: requests.FieldCentric
    robot_centric_req: requests.RobotCentric
    def __init__(self):
        self.drivetrain = swerve.SwerveDrivetrain(
            hardware.TalonFX,
            hardware.TalonFX,
            hardware.CANcoder,
            constants.TunerConstants.drivetrain_constants,
            [
                constants.TunerConstants.front_left,
                constants.TunerConstants.front_right,
                constants.TunerConstants.back_left,
                constants.TunerConstants.back_right,
            ],
        )
        
        self.field_centric_req = (
            requests.FieldCentric()
                .with_deadband(0.0)
                .with_rotational_deadband(0.0)
                .with_drive_request_type(swerve.SwerveModule.DriveRequestType.VELOCITY)
                .with_steer_request_type(swerve.SwerveModule.SteerRequestType.POSITION)
        )
        self.robot_centric_req = (
            requests.RobotCentric()
            .with_deadband(0.0)
            .with_rotational_deadband(0.0)
            .with_drive_request_type(swerve.SwerveModule.DriveRequestType.VELOCITY)
            .with_steer_request_type(swerve.SwerveModule.SteerRequestType.POSITION)
        )
        self.drivetrain.seed_field_centric()

        self.pending_request = self.robot_centric_req.with_velocity_x(0.0).with_velocity_y(0.0).with_rotational_rate(0.0)
        
    def drive(self, transX: units.meters_per_second, transY: units.meters_per_second, rotX: units.radians, field_relative: bool):
        if field_relative:
            self.pending_request = (
                self.field_centric_req
                    .with_velocity_x(transX)
                    .with_velocity_y(transY)
                    .with_rotational_rate(rotX)
            )
        else:
            self.pending_request = (
                self.robot_centric_req
                    .with_velocity_x(transX)
                    .with_velocity_y(transY)
                    .with_rotational_rate(rotX)
            )
    def get_pose(self) -> geometry.Pose2d:
        return self.drivetrain.get_state().pose
    """pose, seconds_since_unix_epoch, (x, y, theta)"""
    def add_pose_info(self, pose_info: geometry.Pose2d, time: units.seconds, stddevs: tuple[float, float, float]):
        self.drivetrain.add_vision_measurement(pose_info, time, stddevs)
    def execute(self):
        self.drivetrain.set_control(self.pending_request)