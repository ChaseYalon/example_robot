from lemonlib.grapple.libgrapplefrc import (
    LaserCAN as _LaserCAN,
)
from lemonlib.grapple.libgrapplefrc import (
    LaserCanMeasurement as _LaserCanMeasurement,
)
from lemonlib.grapple.libgrapplefrc import (
    LaserCanRangingMode,
    LaserCanTimingBudget,
    can_bridge_tcp,
)
from lemonlib.grapple.libgrapplefrc import (
    LaserCanRoi as _LaserCanRoi,
)
from lemonlib.grapple.libgrapplefrc import (
    MitoCANdria as _MitoCANdria,
)

__all__ = [
    "can_bridge_tcp",
    "LaserCAN",
    "LaserCanMeasurement",
    "LaserCanRangingMode",
    "LaserCanRoi",
    "LaserCanTimingBudget",
    "MitoCANdria",
]


class LaserCAN(_LaserCAN):
    """Wrapper for LaserCAN sensor."""

    pass


class LaserCanMeasurement(_LaserCanMeasurement):
    """Measurement result from LaserCAN."""

    pass


class LaserCanRoi(_LaserCanRoi):
    """Region of interest for LaserCAN."""

    pass


class MitoCANdria(_MitoCANdria):
    """CAN communication abstraction."""

    pass
