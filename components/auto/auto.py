from wpimath import units
from components.swerve import SwerveDrive
from components.dispenser import Controller
from components.intake import Intake
from components.odometry import Odometry
import json
import time
import math
class AutoContext:
    sd: SwerveDrive
    it: Intake
    sc: Controller
    od: Odometry
    def __init__(self, sd: SwerveDrive, it: Intake, sc: Controller, od: Odometry):
        self.sd = sd
        self.it = it
        self.sc = sc
        self.od = od
    def execute(self):
        self.od.execute()
        self.it.execute()
        self.sc.execute()
        self.sd.execute()
callbacks = {#the python type system wont allow type hints in lambdas, because it is bad.
    "IntakeOn": lambda ctx: ctx.it.set_voltage(units.volts(12)),
    "IntakeOff": lambda ctx: ctx.it.set_voltage(units.volts(0)),
    "Shoot": lambda ctx: ctx.sc.shoot(ctx.od.get_distance_from_target())
}

class AutoRunner():
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.first_iteration = True
    def execute(self, ctx: AutoContext):
        if self.first_iteration:
            self.start_time_s = time.time_ns() / 1e9
            with open(self.file_path, "r") as file:
                self.contents = json.loads(file.read())
            self.first_iteration = False
        dt = time.time_ns() / 1e9 - self.start_time_s
        vx = 0
        vy = 0
        omega = 0
        samples = self.contents["trajectory"]["samples"]
        for i, row in enumerate(samples): #if perf becomes an issue, binary search here would be an easy optimization
            if dt - row["t"] < 0:
                distFromLastPos = abs(dt - samples[i - 1]["t"])
                distFromFirstNeg = abs(dt - row["t"])
                relativeDistPos = distFromLastPos / (distFromLastPos + distFromFirstNeg)
                relativeDistNeg = distFromFirstNeg / (distFromLastPos + distFromFirstNeg)
                vx += relativeDistNeg * samples[i - 1]["vx"]
                vy += relativeDistNeg * samples[i - 1]["vy"]
                omega += relativeDistNeg * samples[i - 1]["omega"]
                vx += relativeDistPos * row["vx"]
                vy += relativeDistPos * row["vy"]
                omega += relativeDistPos * row["omega"]
                break
        ctx.sd.drive(vx, vy, omega, True)
        EVENT_TOLERANCE = 0.03 #30 ms
        for event in self.contents["events"]:
            if abs(event["from"]["targetTimestamp"] - dt) < EVENT_TOLERANCE:
                callbacks[event["name"]](ctx)