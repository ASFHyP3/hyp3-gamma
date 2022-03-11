import numpy as np

from hyp3_gamma.insar.unwrapping_geocoding import get_neighbors


def test_get_neighbors():
    array = np.arange(0, 5 * 5)
    array.shape = (5, 5)

    assert np.array_equal(get_neighbors(array, 0, 0), np.array([[0, 1], [5, 6]]))
    assert np.array_equal(get_neighbors(array, 0, 4), np.array([[3, 4], [8, 9]]))
    assert np.array_equal(get_neighbors(array, 4, 0), np.array([[15, 16], [20, 21]]))
    assert np.array_equal(get_neighbors(array, 4, 4), np.array([[18, 19], [23, 24]]))

    assert np.array_equal(get_neighbors(array, 0, 2), np.array([[1, 2, 3], [6, 7, 8]]))
    assert np.array_equal(get_neighbors(array, 2, 0), np.array([[5, 6], [10, 11], [15, 16]]))
    assert np.array_equal(get_neighbors(array, 2, 4), np.array([[8, 9], [13, 14], [18, 19]]))
    assert np.array_equal(get_neighbors(array, 4, 2), np.array([[16, 17, 18], [21, 22, 23]]))

    assert np.array_equal(get_neighbors(array, 2, 2), np.array([[6, 7, 8], [11, 12, 13], [16, 17, 18]]))


def test_get_neighbors_bigger_n():
    array = np.arange(0, 5 * 5)
    array.shape = (5, 5)

    assert np.array_equal(get_neighbors(array, 1, 1, n=2),
                          np.array([[0, 1, 2, 3], [5, 6, 7, 8], [10, 11, 12, 13], [15, 16, 17, 18]]))
    assert np.array_equal(get_neighbors(array, 1, 1, n=3), array)
    assert np.array_equal(get_neighbors(array, 1, 1, n=4), array)
