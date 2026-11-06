"""Check element physics, global equilibrium and reproducibility of stored S02 results."""
import json
import sys
import numpy as np
from s02 import CORNERS, HERE, hex8


def check_element():
    lengths = (.035, .022, .040)
    points = CORNERS * lengths
    stiffness = hex8(lengths)
    eigenvalues = np.linalg.eigvalsh(stiffness)
    assert np.max(abs(eigenvalues[:6])) < 1e-12
    assert eigenvalues[6] > 1e-5
    # Uniaxial strain with free lateral contraction gives uniaxial stress.
    displacements = (points * [1, -.3, -.3]).ravel()
    np.testing.assert_allclose(displacements @ stiffness @ displacements, np.prod(lengths))


def check_result(results):
    for cases in results.values():
        for case in cases:
            forces = case['foot_N']
            assert min(forces) > 0
            np.testing.assert_allclose(sum(forces), 9.81 * case['mass_kg'], rtol=1e-6)
            assert case['rear_bow_mm'] > 0 and case['compliance_cm3_kPa'] > 0
            for mode in case['modes']:
                assert mode['Hz'] > 0 and 0 <= mode['flexible_mass_fraction'] <= 1.000001


def compare(actual, expected):
    if isinstance(expected, dict):
        assert actual.keys() == expected.keys()
        for key in expected:
            compare(actual[key], expected[key])
    elif isinstance(expected, list):
        assert len(actual) == len(expected)
        for a, b in zip(actual, expected):
            compare(a, b)
    elif isinstance(expected, str):
        assert actual == expected
    else:
        np.testing.assert_allclose(actual, expected, rtol=2e-5, atol=1e-7)


if __name__ == '__main__':
    check_element()
    current = json.loads((HERE / 's02_wyniki.json').read_text())
    check_result(current)
    if len(sys.argv) == 2:
        with open(sys.argv[1]) as reference:
            compare(current, json.load(reference))
