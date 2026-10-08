import constants
if constants.ODOMETRY:
    from lemonlib import vision
    from photonlibpy import PhotonPoseEstimator
    from robotpy_fields import FieldId, get_field
import wpimath
from components.swerve import SwerveDrive
import wpilib
from smartunits.angle import radians, degrees
from smartunits import Distance
from smartunits.distance import meters
from smartunits.time import seconds

RED_HUB_TAGS = (4, 10)
BLUE_HUB_TAGS = (20, 26)
if constants.ODOMETRY:
    FIELD_ID = FieldId.FRC_2026_REBUILT_WELDED

if constants.ODOMETRY:
    class Odometry:
        camera_front_left: vision.LemonCamera
        camera_front_right: vision.LemonCamera
        camera_back_left:vision.LemonCamera
        camera_back_right: vision.LemonCamera
        camera_middle: vision.LemonCamera
        drive: SwerveDrive
        def __init__(self, drive: SwerveDrive):
            self.drive = drive
            self.field_layout = get_field(FIELD_ID)
            ox = 0.298
            oy = 0.298
            rtc_front_left = wpimath.Transform3d(
                -0.279,
                0.222,
                0.229,
                wpimath.Rotation3d(0.0, degrees.of(-30).in_unit(radians), degrees.of(45).in_unit(radians)),
            )
            rtc_front_right = wpimath.Transform3d(
                -0.279,
                -0.222,
                0.229,
                wpimath.Rotation3d(0.0, degrees.of(-30).in_unit(radians), degrees.of(-45).in_unit(radians)),
            )
            rtc_back_left = wpimath.Transform3d(
                -ox,
                oy,
                0.21,
                wpimath.Rotation3d(0.0, degrees.of(-10).in_unit(radians), degrees.of(135).in_unit(radians)),
            )
            rtc_back_right = wpimath.Transform3d(
                -ox,
                -oy,
                0.21,
                wpimath.Rotation3d(0.0, degrees.of(-10).in_unit(radians), degrees.of(-135).in_unit(radians)),
            )
            rtc_mid = wpimath.Transform3d(
                -0.241,
                0.0,
                0.229,
                wpimath.Rotation3d(0.0, degrees.of(-20).in_unit(radians),0.0)

            )

            self.camera_front_left = vision.LemonCamera(
                "Front_Left",  rtc_front_left, FIELD_ID
            )
            self.camera_front_right = vision.LemonCamera(
                "Front_Right",  rtc_front_right, FIELD_ID
            )

            self.camera_back_left = vision.LemonCamera(
                "Back_Left",  rtc_back_left, FIELD_ID
            )
            self.camera_back_right = vision.LemonCamera(
                "Back_Right",  rtc_back_right, FIELD_ID
            )

            self.camera_middle = vision.LemonCamera(
                "Middle", rtc_mid, FIELD_ID
            )

            cameras = (
                self.camera_front_left,
                self.camera_front_right,
                self.camera_middle,
                # self.camera_back_left,
                # self.camera_back_right,
            )
            self.camera_estimator_pairs = tuple(
                (cam, PhotonPoseEstimator(self.field_layout, cam.camera_to_bot))
                for cam in cameras
            )


        BASELINE_STD = 0.1  # meters, tune by watching the pose jump on the dashboard

        def get_target_distance(self) -> Distance:
            is_red = wpilib.MatchState.get_alliance() == wpilib.Alliance.RED
            tag_ids = RED_HUB_TAGS if is_red else BLUE_HUB_TAGS
            translations = []
            for tag_id in tag_ids:
                pose3d = self.field_layout.get_tag_pose(tag_id)
                if pose3d is None:
                    raise TypeError(f"tag {tag_id} not in field layout")
                translations.append(pose3d.translation().to_translation2d())
            target_position = (translations[0] + translations[1]) / 2
            return meters.of(self.drive.get_pose().translation().distance(target_position))

        def execute(self):
            for cam, estimator in self.camera_estimator_pairs:
                cam.update()
                for result in cam.results:
                    pose = estimator.estimateCoprocMultiTagPose(result)
                    if pose is None:
                        continue

                    tag_count = len(pose.targetsUsed)
                    avg_dist = sum(
                        t.getBestCameraToTarget().translation().norm()
                        for t in pose.targetsUsed
                    ) / tag_count
                    std = self.BASELINE_STD * (avg_dist ** 2) / tag_count
                    std_devs = (std, std, std * 2)

                    self.drive.add_pose_info(
                        pose.estimatedPose.to_pose2d(), seconds.of(pose.timestampSeconds), std_devs
                    )
else:
    class Odometery():
        def __init__(self):
            pass
        def execute(self):
            pass
        def get_target_distance(self, *args):
            pass