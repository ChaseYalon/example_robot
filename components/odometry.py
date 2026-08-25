from lemonlib import vision
from wpimath import geometry, units
from photonlibpy.photonPoseEstimator import PhotonPoseEstimator
from components.swerve import SwerveDrive
import robotpy_apriltag
import wpilib

RED_HUB_TAGS = (4, 10)
BLUE_HUB_TAGS = (20, 26)


class Odometry:
    camera_front_left: vision.LemonCamera
    camera_front_right: vision.LemonCamera
    camera_back_left:vision.LemonCamera
    camera_back_right: vision.LemonCamera
    camera_middle: vision.LemonCamera
    drive: SwerveDrive
    def __init__(self, drive: SwerveDrive):
        self.drive = drive
        self.field_layout = robotpy_apriltag.AprilTagFieldLayout.loadField(
            robotpy_apriltag.AprilTagField.k2026RebuiltWelded
        )
        ox = 0.298
        oy = 0.298
        rtc_front_left = geometry.Transform3d(
            -0.279,
            0.222,
            0.229,
            geometry.Rotation3d(0.0, units.degreesToRadians(-30), units.degreesToRadians(45)),
        )
        rtc_front_right = geometry.Transform3d(
            -0.279,
            -0.222,
            0.229,
            geometry.Rotation3d(0.0, units.degreesToRadians(-30), units.degreesToRadians(-45)),
        )
        rtc_back_left = geometry.Transform3d(
            -ox,
            oy,
            0.21,
            geometry.Rotation3d(0.0, units.degreesToRadians(-10), units.degreesToRadians(135)),
        )
        rtc_back_right = geometry.Transform3d(
            -ox,
            -oy,
            0.21,
            geometry.Rotation3d(0.0, units.degreesToRadians(-10), units.degreesToRadians(-135)),
        )
        rtc_mid = geometry.Transform3d(
            -0.241,
            0.0,
            0.229,
            geometry.Rotation3d(0.0,units.degreesToRadians(-20),0.0)

        )

        self.camera_front_left = vision.LemonCamera(
            "Front_Left",  rtc_front_left, self.field_layout
        )
        self.camera_front_right = vision.LemonCamera(
            "Front_Right",  rtc_front_right, self.field_layout
        )

        self.camera_back_left = vision.LemonCamera(
            "Back_Left",  rtc_back_left, self.field_layout
        )
        self.camera_back_right = vision.LemonCamera(
            "Back_Right",  rtc_back_right, self.field_layout
        )

        self.camera_middle = vision.LemonCamera(
            "Middle", rtc_mid, self.field_layout
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

    def get_target_distance(self) -> units.meters:
        is_red = wpilib.DriverStation.getAlliance() == wpilib.DriverStation.Alliance.kRed
        tag_ids = RED_HUB_TAGS if is_red else BLUE_HUB_TAGS
        translations = []
        for tag_id in tag_ids:
            pose3d = self.field_layout.getTagPose(tag_id)
            if pose3d is None:
                raise TypeError(f"tag {tag_id} not in field layout")
            translations.append(pose3d.translation().toTranslation2d())
        target_position = (translations[0] + translations[1]) / 2
        return self.drive.get_pose().translation().distance(target_position)

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
                    pose.estimatedPose.toPose2d(), pose.timestampSeconds, std_devs
                )