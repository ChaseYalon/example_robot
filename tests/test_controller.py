import pytest
from components.dispenser import Controller
from components.dispenser import controller as ctrl
from components.dispenser.controller import calc_optimal_volts, MAX_ALLOWABLE_ITERATIONS

def test_shot_controller_controller():

    #controller.execute case 1
    c = Controller()
    c.stop_shoot()
    c.execute()
    assert c.indexer.conv_on == False
    assert c.indexer.kick_on == False
    assert c.shooter.velocity == 0.8 * c.MAX_VOLTS

    #controler execute case 2
    c = Controller()
    c.shoot(3)
    c.distance_from_target = 3
    c.execute()
    assert c.indexer.conv_on == True
    assert c.indexer.kick_on == True
    assert c.shooter.velocity == calc_optimal_volts(3)
def test_shot_controller_calc_optimal_volts():
    #exception path: unreachable distance raises, makeable distance does not
    with pytest.raises(RuntimeError):
        calc_optimal_volts(1000)
    assert calc_optimal_volts(3) > 0
    assert calc_optimal_volts(3) > 6.0
    volts = calc_optimal_volts(3)
    velocity = ctrl.volts_to_velocity(volts)
    landing = ctrl.vertical_position_at_horizontal_distance(velocity, ctrl.SHOOTER_ANGLE, 3)
    assert ctrl.HOOP_HEIGHT <= landing <= ctrl.NET_HEIGHT
    assert not ctrl.hits_backboard(velocity, 3)

    #test itteration overflow
    MAX_ALLOWABLE_ITERATIONS = -1
    with pytest.raises(RuntimeError):
        calc_optimal_volts(1)