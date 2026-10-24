"""P26: pasywny model modalny prostopadłościanu; exp(+jwt), wielkości RMS.

To model fenomenologiczny: sztywne funkcje bazowe, diagonalne straty.
Nie rozwiązuje rzeczywistego impedancyjnego warunku brzegowego ani obciążenia
głośnika. Wygładzenie Neumanna opisuje rozłożone źródło/odbiornik, nie kosz
lub membranę konkretnego głośnika. Nie utożsamiać tego parametru z promieniem.
"""
from dataclasses import dataclass
import numpy as np


@dataclass(frozen=True)
class ModalRoom:
    dimensions_xyz_m: tuple = (3.7, 4.6, 2.5)
    c_m_s: float = 343.0
    rho_kg_m3: float = 1.204

    def __post_init__(self):
        dims = np.asarray(self.dimensions_xyz_m, dtype=float)
        if dims.shape != (3,) or not np.all(np.isfinite(dims)) or np.any(dims <= 0):
            raise ValueError('Wymiary xyz muszą być trzema dodatnimi liczbami SI')
        if not np.isfinite(self.c_m_s) or self.c_m_s <= 0:
            raise ValueError('Dodatnia prędkość dźwięku')
        if not np.isfinite(self.rho_kg_m3) or self.rho_kg_m3 <= 0:
            raise ValueError('Dodatnia gęstość')

    @property
    def volume_m3(self):
        return float(np.prod(self.dimensions_xyz_m))

    def modes(self, kmax_m_inv):
        if not np.isfinite(kmax_m_inv) or kmax_m_inv < 0:
            raise ValueError('Skończony nieujemny zakres liczby falowej')
        dims = np.asarray(self.dimensions_xyz_m)
        limits = np.floor(kmax_m_inv * dims / np.pi).astype(int)
        grid = np.meshgrid(*(np.arange(n + 1) for n in limits), indexing='ij')
        n = np.stack([a.ravel() for a in grid], axis=1)
        wave = np.pi * n / dims
        k2 = np.sum(wave ** 2, axis=1)
        keep = k2 <= kmax_m_inv ** 2 * (1 + 8 * np.finfo(float).eps)
        return n[keep], k2[keep]

    def basis(self, indices, positions_xyz_m):
        n = np.asarray(indices)
        p = np.atleast_2d(np.asarray(positions_xyz_m, dtype=float))
        dims = np.asarray(self.dimensions_xyz_m)
        if n.ndim != 2 or n.shape[1] != 3 or np.any(n < 0) or np.any(n != np.floor(n)):
            raise ValueError('Indeksy modów: nieujemne całkowite trójki')
        if p.shape[1] != 3 or not np.all(np.isfinite(p)) or np.any(p < 0) or np.any(p > dims):
            raise ValueError('Pozycje xyz muszą należeć do domkniętego pokoju')
        # Średnia objętościowa iloczynu psi_n*psi_m = delta_nm.
        norm = np.prod(np.where(n == 0, 1.0, np.sqrt(2.0)), axis=1)
        return norm[:, None] * np.prod(np.cos(
            np.pi * n[:, None, :] * p[None, :, :] / dims), axis=2)

    def transfer(self, frequencies_hz, sources_xyz_m, receivers_xyz_m,
                 modal_t60_s, zero_relaxation_s, source_sigma_m=0.12,
                 receiver_sigma_m=0.03, kmax_m_inv=40.0):
        """H[f,r,s] = uśrednione p_r/U_s, Pa s/m³, bez sprzężenia źródła.

        sigma: odchylenie operatora wygładzającego heat-kernel Neumanna.
        T60 dotyczy obwiedni każdego niezerowego oscylatora modalnego.
        zero_relaxation=inf: szczelny człon kompresji; 0: jego brak.
        """
        f = np.atleast_1d(np.asarray(frequencies_hz, dtype=float))
        if f.ndim != 1 or np.any(~np.isfinite(f)) or np.any(f <= 0):
            raise ValueError('Dodatnie częstotliwości, granice DC osobno')
        if not np.isfinite(modal_t60_s) or modal_t60_s <= 0:
            raise ValueError('T60 musi być dodatni i skończony')
        if np.isnan(zero_relaxation_s) or zero_relaxation_s < 0:
            raise ValueError('Czas relaksacji >=0, dopuszczalne +inf')
        for val in (source_sigma_m, receiver_sigma_m):
            if not np.isfinite(val) or val < 0:
                raise ValueError('Skończona nieujemna szerokość wygładzenia')
        n, k2 = self.modes(kmax_m_inv)
        bs = self.basis(n, sources_xyz_m)
        br = self.basis(n, receivers_xyz_m)
        smooth = np.exp(-0.5 * (source_sigma_m ** 2 + receiver_sigma_m ** 2) * k2)
        coupling = (br[:, :, None] * bs[:, None, :] * smooth[:, None, None])
        shape = coupling.shape[1:]
        coupling = coupling.reshape(len(n), -1)
        sigma = 3 * np.log(10) / modal_t60_s
        out = np.empty((len(f), coupling.shape[1]), dtype=complex)
        prefactor = self.rho_kg_m3 * self.c_m_s ** 2 / self.volume_m3
        zero = np.all(n == 0, axis=1)
        for start in range(0, len(f), 48):
            sl = slice(start, start + 48)
            s = 2j * np.pi * f[sl, None]
            kernel = prefactor * s / (s * s + 2 * sigma * s + self.c_m_s ** 2 * k2)
            if zero_relaxation_s == 0:
                kernel[:, zero] = 0
            else:
                a0 = 0.0 if np.isposinf(zero_relaxation_s) else 1 / zero_relaxation_s
                kernel[:, zero] = prefactor / (s + a0)
            out[sl] = kernel @ coupling
        return out.reshape((len(f),) + shape)
