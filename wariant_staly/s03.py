"""S03: independent plate bending and axial contact screening. Units SI."""
import json
from pathlib import Path

import numpy as np
from numpy.polynomial import Legendre
from numpy.polynomial.legendre import leggauss
from scipy.linalg import eigh, solve
from scipy.sparse import csr_matrix, diags
from scipy.sparse.linalg import spsolve

from s02 import solve as solve_cabinet

HERE = Path(__file__).resolve().parent
THICKNESS = 0.022
POISSON = 0.30
RIGIDITY = 2e9 * THICKNESS**3 / (12 * (1 - POISSON**2))


def axis_basis(length, order, clamped):
    points, weights = leggauss(order + 6)
    edge = Legendre([1]) - Legendre.identity()**2
    functions = [edge**(1 + int(clamped)) * Legendre.basis(i) for i in range(order)]
    basis = [np.array([f.deriv(d)(points) for f in functions]) * (2 / length)**d
             for d in range(3)]
    weights *= length / 2

    def gram(i, j):
        return (basis[i] * weights) @ basis[j].T

    return gram, basis[0] @ weights, [f(0) for f in functions]


def plate(a, b, order, clamped):
    x, fx, cx = axis_basis(a, order, clamped)
    y, fy, cy = axis_basis(b, order, clamped)
    mixed = np.kron(x(2, 0), y(0, 2))
    stiffness = RIGIDITY * (
        np.kron(x(2, 2), y(0, 0)) + np.kron(x(0, 0), y(2, 2))
        + POISSON * (mixed + mixed.T)
        + 2 * (1 - POISSON) * np.kron(x(1, 1), y(1, 1)))
    mass = 800 * THICKNESS * np.kron(x(0, 0), y(0, 0))
    area = np.kron(fx, fy)
    displacement = solve(stiffness, 1000 * area, assume_a='pos')
    eigenvalue = eigh(stiffness, mass, subset_by_index=[0, 0], eigvals_only=True)[0]
    return dict(center_mm=1000 * np.kron(cx, cy) @ displacement,
                swept_cm3=1e6 * area @ displacement, first_Hz=np.sqrt(eigenvalue)/(2*np.pi))


def ring(nodes, bed, active_bolts):
    # Periodic unrolled beam, one-sided Winkler bed and eight 6 mm load patches.
    width, thickness = .021, .006
    length = 2 * np.pi * .1895
    step = length / nodes
    i = np.arange(nodes)
    curvature = csr_matrix((np.tile([1., -2., 1.], nodes),
                            (np.repeat(i, 3), ((i[:, None] + [-1, 0, 1]) % nodes).ravel())),
                           shape=(nodes, nodes)) / step**2
    bending = 200e9 * width * thickness**3 / 12 * (curvature.T @ curvature)
    force = np.zeros(nodes)
    for bolt in range(active_bolts):
        distance = abs((i * step - bolt * length / 8 + length / 2) % length - length / 2)
        overlap = np.clip(.003 + step / 2 - distance, 0, min(.006, step))
        force += (800 / active_bolts) * overlap / overlap.sum() / step
    contact = np.ones(nodes, dtype=bool)
    for _ in range(50):
        w = spsolve(bending + diags(bed * width * contact), force)
        new_contact = w > 0
        if np.array_equal(contact, new_contact):
            break
        contact = new_contact
    else:
        raise RuntimeError('Unconverged unilateral contact')
    pressure = bed * np.maximum(w, 0)
    np.testing.assert_allclose(step * width * sum(pressure), 800, rtol=2e-6)
    return dict(peak_to_mean=max(pressure) / (800 / (length * width)),
                peak_MPa=max(pressure)/1e6, contact_fraction=float(contact.mean()),
                peak_indentation_mm=1000 * max(w))


def run():
    shapes = json.loads((HERE / 's01_wyniki.json').read_text())['shapes']
    plates = {}
    for name, shape in shapes.items():
        a, b = np.array(shape['inner_mm'][:2]) / 1000
        plates[name] = {}
        for edge in ('hinged', 'clamped'):
            series = [plate(a, b, n, edge == 'clamped') for n in (4, 6, 8)]
            for metric in series[-1]:
                np.testing.assert_allclose(series[-2][metric], series[-1][metric], rtol=.005)
            plates[name][edge] = series
        reference = plates[name]['hinged'][-1]
        for metric, target in [('center_mm', shape['rear_center_mm_1kPa']),
                               ('swept_cm3', shape['rear_swept_cm3_per_kPa']),
                               ('first_Hz', shape['rear_modes'][0][0])]:
            np.testing.assert_allclose(reference[metric], target, rtol=.001)
    a, b, _ = np.array(shapes['B']['inner_mm']) / 1000
    np.testing.assert_allclose(a, b)
    square_frequency = plates['B']['clamped'][-1]['first_Hz']
    square_parameter = 2 * np.pi * square_frequency * a**2 * np.sqrt(800 * THICKNESS / RIGIDITY)
    np.testing.assert_allclose(square_parameter, 35.99, rtol=.001)
    contacts = []
    for bed in (2e9, 2e10, 2e11):
        for bolts in (8, 7):
            coarse, fine = [ring(n, bed, bolts) for n in (512, 1024)]
            np.testing.assert_allclose(coarse['peak_to_mean'], fine['peak_to_mean'], rtol=.01)
            contacts.append(dict(bed_N_m3=bed, bolts=bolts, coarse=coarse, fine=fine))
    reference = json.loads((HERE / 's02_wyniki.json').read_text())['A'][-1]
    assert reference['h_mm'] == 30 and not reference['vertical']
    surrogate = solve_cabinet(shapes['A'], .030, ring_modulus=2e9)
    np.testing.assert_allclose(reference['mass_kg'], surrogate['mass_kg'])
    def summary(case):
        return dict(rear_mm=case['rear_bow_mm'], compliance_cm3_kPa=case['compliance_cm3_kPa'],
                    elastic_Hz=[m['Hz'] for m in case['modes'] if m['flexible_mass_fraction'] > .5])
    return dict(plate_order=[4, 6, 8], plates=plates, ring=contacts,
                cabinet=dict(bonded=summary(reference), equivalent_MDF=summary(surrogate)))


if __name__ == '__main__':
    (HERE / 's03_wyniki.json').write_text(json.dumps(run(), indent=2) + '\n')
