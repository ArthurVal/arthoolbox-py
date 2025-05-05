#!/usr/bin/env python3

"""Module containing the sample decorator use to sample function calls.

Good tutorial on decorator:
https://realpython.com/primer-on-python-decorators/

Decorators list:
- sample | (opt) time_function | Compute mean period, stddev period, last_call
  delta T etc..
"""
from functools import wraps
from time import time

from atb.math.statistics import OnlineStatistics


def sample(_f=None, *, time_function=time.time):
    """Compute timing parameters (mean/stddev period call) for a function.

    This class is a decorator use to sample the decorated function. It can be
    use to obtain the last period measured in sec (func.period.measurement)
    between 2 function call, the mean, the variance and the sampled variance of
    the period between function calls with func.period.mean,
    func.period.variance and func.period.sampled_variance.

    Additionnaly, you can synchronise your code with the func.period.updated
    condition variable (threading.Condition) in order to be notified when new
    period statistic is computed.

    Attributs
    ---------
    last_call: float
        The last __get_time() returned value use to compute measurements
    period: atb.math.statistics.OnlineStatistics
        OnlineStatistics object use to compute mean and variance online

    Parameters
    ----------
    _f: Callable obj
        The function to wrap around the sampling
    time_function: Callable obj
        Function use to measure time point (Default time.time)
    """

    def decorator_sample(f):
        """Decorate and create the wrapper of f."""

        @wraps(f)
        def wrapper_sample(*args, **kwargs):
            """Wrap f and perform statistics before calling it."""
            # Function call -> Time measurements
            now = time_function()

            if wrapper_sample.last_call is not None:
                # Register the new measurement
                wrapper_sample.period.measurement = \
                    now - wrapper_sample.last_call

            wrapper_sample.last_call = now

            return f(*args, **kwargs)

        # Initialize the wrapper function with attribut (function are objects)
        wrapper_sample.last_call = None
        wrapper_sample.period = OnlineStatistics()

        return wrapper_sample

    if _f is None:
        # sample called without unamed arguments -> First argument is the
        # function:
        #
        # function = sample(function)
        #
        # OR
        #
        # @sample
        # def function():
        #   ...
        return decorator_sample

    else:
        # sample called with time_function:
        #
        # function = sample(time_function = toto)(function)
        #
        # OR
        #
        # @sample(time_function = toto)
        # def function():
        #   ...
        return decorator_sample(_f)
