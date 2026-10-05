from components.intake import Intake
from smartunits import volts
def test_intake():
    i = Intake()
    i.set_arm_voltage(volts.of(10))
    assert i.arm_voltage.in_unit(volts) == volts.of(10).in_unit(volts)