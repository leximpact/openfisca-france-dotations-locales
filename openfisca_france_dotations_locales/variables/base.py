import numpy as np


def safe_divide(a, b, value_if_error=0):
    return np.where(b != 0, np.divide(a, b), value_if_error)
