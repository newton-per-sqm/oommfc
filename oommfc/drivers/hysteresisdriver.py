import numpy as np

from .driver import Driver


class HysteresisDriver(Driver):
    """Hysteresis driver.

    Only attributes in ``_allowed_attributes`` can be defined. For details on
    possible values for individual attributes and their default values, please
    refer to ``Oxs_MinDriver`` documentation (https://math.nist.gov/oommf/).

    Examples
    --------
    1. Defining driver with a keyword argument.

    >>> import oommfc as mc
    ...
    >>> hd = mc.HysteresisDriver(stopping_mxHxm=0.01)

    2. Passing an argument which is not allowed.

    >>> import oommfc as mc
    ...
    >>> md = mc.HysteresisDriver(myarg=1)
    Traceback (most recent call last):
       ...
    AttributeError: ...

    3. Getting the list of allowed attributes.

    >>> import oommfc as mc
    ...
    >>> hd = mc.HysteresisDriver()
    >>> hd._allowed_attributes
    [...]

    """

    _allowed_attributes = [
        "evolver",
        "stopping_mxHxm",
        "stage_iteration_limit",
        "total_iteration_limit",
        "stage_count",
        "stage_count_check",
        "checkpoint_file",
        "checkpoint_interval",
        "checkpoint_disposal",
        "start_iteration",
        "start_stage",
        "start_stage_iteration",
        "start_stage_start_time",
        "start_stage_elapsed_time",
        "start_last_timestep",
        "normalize_aveM_output",
        "report_max_spin_angle",
        "report_wall_time",
    ]

    def _checkargs(self, **kwargs):
        # check the default arguments for a symmetric hysteresis loop
        if any(item in kwargs for item in ["Hmin", "Hmax", "n"]) and "Hsteps" in kwargs:
            msg = "Cannot define both (Hmin, Hmax, n) and Hsteps."
            raise ValueError(msg)

        if all(item in kwargs for item in ["Hmin", "Hmax", "n"]):
            self._checkvalues(kwargs["Hmin"], kwargs["Hmax"], kwargs["n"])
        elif "Hsteps" in kwargs:
            for Hstart, Hend, n in kwargs["Hsteps"]:
                self._checkvalues(Hstart, Hend, n)
        else:
            msg = (
                "Some of the required arguments are missing. "
                "(Hmin, Hmax, n) or Hsteps must be defined."
            )
            raise ValueError(msg)

    @staticmethod
    def _checkvalues(Hstart, Hend, n):
        for i in [Hstart, Hend]:
            if not isinstance(i, (list, tuple, np.ndarray)):
                msg = "Hstart (Hmin) and Hend (Hmax) must have array_like values."
                raise ValueError(msg)
            if len(i) != 3:
                msg = "Hstart (Hmin) and Hend (Hmax) must have length 3."
                raise ValueError(msg)
        if not isinstance(n, int):
            msg = f"Cannot drive with {type(n)=}."
            raise ValueError(msg)
        if n <= 1:  # OOMMF counts steps, not points (n -> n-1)
            msg = f"Cannot drive with {n=}."
            raise ValueError(msg)

    @property
    def _x(self):
        return "B_hysteresis"
