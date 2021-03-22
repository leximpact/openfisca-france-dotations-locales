import numpy as np
from openfisca_france_dotations_locales.variables.base import safe_divide


def test_safe_divide():
    a = np.array([1, 1, 0, 0, -1])
    b = np.array([1, 0, 2, 0, -1])
    assert all(safe_divide(a, b) == [1, 0, 0, 0, 1])
    assert all(safe_divide(a, b, 12) == [1, 12, 0, 12, 1])
