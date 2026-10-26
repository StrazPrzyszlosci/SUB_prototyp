"""Etap P20C: bryła/spoiny, pełne porty, siatka, ciągłe E i napęd.

Zgodne18rekordów są wznawiane po hashu; osobne audyty mają własne równania.
Nie uruchamia dawnych kampanii24baz lub całego modelu pokoju.
"""
import os


def main():
    os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
    from sprawdz_modul_3D_P20C import main as checks
    from analiza_modulu_3D_P20C import main as study
    from wymagany_modul_kleju_P20C import main as modulus
    from naped_z_modulem_3D_P20C import main as drive
    from sprawdz_siatke_modulu_P20C import main as mesh
    from dalsza_siatka_modulu_P20C import main as refine
    from wykresy_i_ocena_modulu_P20C import main as figures
    from manifest_modulu_3D_P20C import main as manifest
    checks();study();modulus();drive();mesh();refine();figures();manifest()


if __name__=='__main__':main()
