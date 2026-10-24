"""Niezależne kontrole normalizacji, granic i pasywności P26."""
import json
from pathlib import Path
import numpy as np
from numpy.polynomial.legendre import leggauss
from model_pokoju import ModalRoom

ROOT = Path(__file__).resolve().parents[1]


def main():
    room = ModalRoom()
    assert abs(room.volume_m3 - 42.55) < 1e-12
    dims = np.array(room.dimensions_xyz_m)
    axial = room.c_m_s / (2 * dims)
    assert np.allclose(axial, [46.35135135135135, 37.28260869565218, 68.6])
    # Niezależne całkowanie iloczynów funkcji bazowych w objętości.
    g, w = leggauss(18)
    coord = [(g + 1) * d / 2 for d in dims]
    grids = np.meshgrid(*coord, indexing='ij')
    points = np.stack([a.ravel() for a in grids], axis=1)
    weights = np.einsum('i,j,k->ijk', w / 2, w / 2, w / 2).ravel()
    ns = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1], [2, 3, 1]])
    b = room.basis(ns, points)
    orth_err = float(np.max(abs((b * weights) @ b.T - np.eye(len(ns)))))
    assert orth_err < 1e-10
    # Odrębne rozwiązanie 1D Neumanna z warunkami skoku Greena.
    L, area = dims[1], dims[0] * dims[2]
    ys, yr, t60 = 0.65, 3.1, 0.4
    f = np.array([10., 20., 37.2826087, 63., 100.])
    s = 2j * np.pi * f
    sigma = 3 * np.log(10) / t60
    k = np.sqrt(-(s * s + 2 * sigma * s)) / room.c_m_s
    closed = (-room.rho_kg_m3 * s / area * np.cos(k * min(ys, yr)) *
              np.cos(k * (L - max(ys, yr))) / (k * np.sin(k * L)))
    ny = np.arange(40001)
    norm2 = np.where(ny == 0, 1., 2.)
    modal = (room.rho_kg_m3 * room.c_m_s ** 2 / room.volume_m3 * s *
             np.sum(norm2 * np.cos(ny * np.pi * ys / L) * np.cos(ny * np.pi * yr / L) /
                    (s[:, None] ** 2 + 2 * sigma * s[:, None] +
                     (room.c_m_s * ny * np.pi / L) ** 2), axis=1))
    one_d_error = float(np.max(abs(modal / closed - 1)))
    assert one_d_error < 2e-8
    src = np.array([[0.65, 0.65, 0.3], [3.05, 0.65, 0.3]])
    rec = np.array([[1.85, 3.1, 1.1], [1.7, 3.1, 1.1]])
    kwargs = dict(modal_t60_s=0.4, zero_relaxation_s=0.2, kmax_m_inv=35)
    h = room.transfer(f, src, rec, **kwargs)
    reverse = room.transfer(f, rec, src, source_sigma_m=0.03,
                            receiver_sigma_m=0.12, **kwargs)
    reciprocity = float(np.max(abs(h - reverse.transpose(0, 2, 1))) / np.max(abs(h)))
    assert reciprocity < 1e-12
    # Porty z takim samym uśrednieniem: Hermitowska część impedancji >=0.
    ports = room.transfer(f, src, src, receiver_sigma_m=0.12, **kwargs)
    real_parts = (ports + ports.conj().transpose(0, 2, 1)) / 2
    min_eigenvalue = float(np.min(np.linalg.eigvalsh(real_parts)))
    assert min_eigenvalue >= -1e-9
    ns_all, _ = room.modes(8)
    bs = room.basis(ns_all, src)
    odd = ns_all[:, 0] % 2 == 1
    symmetry = float(np.max(abs(bs[odd, 0] + bs[odd, 1])))
    assert symmetry < 1e-12
    center = float(np.max(abs(h[:, 0, 0] / h[:, 0, 1] - 1)))
    assert center < 1e-12
    # Sam człon jednorodny: końce tau=0, tau=inf, granica s->0.
    pref = room.rho_kg_m3 * room.c_m_s ** 2 / room.volume_m3
    h0 = room.transfer([1e-9], src[:1], rec[:1], 0.4, np.inf, kmax_m_inv=0)[0, 0, 0]
    assert abs(h0 * 2j * np.pi * 1e-9 / pref - 1) < 1e-14
    hzero = room.transfer([20], src[:1], rec[:1], 0.4, 0, kmax_m_inv=0)[0, 0, 0]
    assert hzero == 0
    hfinite = room.transfer([1e-9], src[:1], rec[:1], 0.4, 0.2, kmax_m_inv=0)[0, 0, 0]
    assert abs(hfinite / (pref * 0.2) - 1) < 2e-9
    # Ujemne częstotliwości, rozmiary i pozycje nie opisują naszych wejść.
    invalid = [lambda: ModalRoom((0, 4.6, 2.5)),
               lambda: room.transfer([0], src, rec, **kwargs),
               lambda: room.transfer([20], [[-1, 0, 0]], rec, **kwargs),
               lambda: room.transfer([20], src, rec, -1, 0.2),
               lambda: room.transfer([20], src, rec, 0.4, -1),
               lambda: room.transfer([20], src, rec, 0.4, 0.2, source_sigma_m=-1)]
    for action in invalid:
        try:
            action()
        except ValueError:
            pass
        else:
            raise AssertionError('Nie odrzucono błędnego wejścia')
    result = dict(status='PASS_KONTROLE_MODELU_NIE_WALIDACJA_POKOJU',
                  mean_volume_orthogonality_max_error=orth_err,
                  independent_1d_green_max_relative_error=one_d_error,
                  reciprocity_relative_error=reciprocity,
                  port_real_hermitian_min_eigenvalue_pa_s_m3=min_eigenvalue,
                  odd_width_mode_pair_coupling_max=symmetry,
                  symmetric_pair_center_transfer_relative_error=center,
                  invalid_classes=len(invalid),
                  limits=['tau0=0', 'tau0=inf', 'f->0', 'kmax=0'],
                  limitations='Diagonalne straty i rozłożone źródła są założeniami; brak pomiarów pokoju.')
    (ROOT / 'wyniki/p26_weryfikacja.json').write_text(json.dumps(result, ensure_ascii=False, indent=2))
    print('P26: niezależna funkcja Greena 1D, normalizacja, wzajemność, pasywność i granice poprawne')
    return result


if __name__ == '__main__':
    main()
