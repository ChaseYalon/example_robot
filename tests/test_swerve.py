from components.swerve import SwerveDrive
from smartunits import meters_per_second, radians_per_second
def test_SwerveDrive():
    sd = SwerveDrive()
    sd.drive(meters_per_second.of(2), meters_per_second.of(3), radians_per_second.of(0.3), True)
    assert sd.pending_request.velocity_x == 2
    assert sd.pending_request.velocity_y == 3
    assert sd.pending_request.rotational_rate == 0.3
    print(sd.pending_request.steer_request_type)
    assert sd.pending_request.velocity_x == -1
    assert sd.pending_request.velocity_y == -2
    assert sd.pending_request.rotational_rate == 0.4
