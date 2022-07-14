import numpy as np

from hyp3_gamma.insar.unwrapping_geocoding import get_reference_pixel


def test_get_reference_pixel():
    array = np.array([
        [0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0],
    ])
    assert get_reference_pixel(array, window_size=(1, 1)) == (0, 0)
    assert get_reference_pixel(array, window_size=(3, 3)) == (0, 0)
    assert get_reference_pixel(array, window_size=(5, 5)) == (0, 0)

    array = np.array([
        [0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0],
        [0.0, 0.2, 0.0],
    ])
    assert get_reference_pixel(array, window_size=(1, 1)) == (0, 0)
    assert get_reference_pixel(array, window_size=(1, 1), coherence_threshold=0.2) == (2, 1)
    assert get_reference_pixel(array, window_size=(1, 1), coherence_threshold=0.20001) == (0, 0)
    assert get_reference_pixel(array, window_size=(3, 3)) == (0, 0)
    assert get_reference_pixel(array, window_size=(5, 5)) == (0, 0)

    array = np.array([
        [0.4, 0.6, 0.9, 0.4, 0.5, 0.2],
        [0.5, 0.9, 0.8, 0.6, 0.4, 0.1],
        [0.7, 0.5, 0.9, 0.4, 0.5, 0.2],
        [0.2, 0.5, 0.4, 0.8, 0.9, 0.4],
        [0.0, 0.4, 0.8, 0.6, 0.5, 0.3],
    ])
    assert get_reference_pixel(array, window_size=(1, 1)) == (0, 2)
    assert get_reference_pixel(array, window_size=(3, 3)) == (1, 1)

    array = np.array([
        [0.5, 0.5, 0.9],
        [0.4, 0.9, 0.6],
        [0.4, 0.7, 0.5],
    ])
    assert get_reference_pixel(array, window_size=(3, 3)) == (1, 1)

    array = np.array([
        [0.5, 0.2, 0.0, 0.3, 0.9, 0.7, 0.5, 0.8, 0.9, 0.4],
        [0.2, 0.2, 0.2, 0.6, 0.9, 0.5, 0.8, 0.3, 0.0, 1.0],
        [0.0, 0.2, 0.5, 0.5, 0.7, 0.8, 0.4, 0.7, 0.1, 0.0],
    ])
    assert get_reference_pixel(array, window_size=(3, 3)) == (1, 5)
    assert get_reference_pixel(array, window_size=(5, 5)) == (0, 0)

    array = np.array([
        [0.0, 0.1, 0.3, 0.4, 0.9, 0.6, 0.2, 0.7, 0.0, 0.0],
        [0.0, 0.1, 0.3, 0.4, 0.9, 0.6, 0.2, 0.7, 0.0, 0.0],
        [0.0, 0.1, 0.3, 0.4, 0.9, 0.6, 0.2, 0.7, 0.0, 0.0],
        [0.0, 0.1, 0.3, 0.4, 0.9, 0.6, 0.2, 0.7, 0.0, 0.0],
        [0.0, 0.1, 0.3, 0.7, 0.9, 0.8, 0.2, 0.7, 0.1, 0.0],
        [0.0, 0.1, 0.3, 0.4, 0.9, 0.9, 0.6, 0.7, 0.0, 0.0],
        [0.0, 0.1, 0.3, 0.5, 0.8, 0.9, 0.2, 0.7, 0.2, 0.0],
        [0.0, 0.1, 0.3, 0.4, 0.9, 0.6, 0.2, 0.7, 0.0, 0.1],
        [0.0, 0.1, 0.3, 0.4, 0.9, 0.6, 0.2, 0.7, 0.5, 0.2],
    ])
    assert get_reference_pixel(array, window_size=(1, 1)) == (0, 4)
    assert get_reference_pixel(array, window_size=(3, 3)) == (5, 4)
    assert get_reference_pixel(array, window_size=(3, 3)) == (5, 4)
    assert get_reference_pixel(array, window_size=(5, 5)) == (0, 0)
