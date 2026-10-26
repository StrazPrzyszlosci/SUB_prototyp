"""Odtworzenie P20B bez ponawiania dawnych kampanii24baz."""
import os


def main():
    os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
    from analiza_przegrod_P20B import main as study
    from naped_z_przegroda_P20B import main as drive
    from sprawdz_przegrode_P20B import main as checks
    from porownanie_materialow_P20B import main as material
    from wykresy_i_ocena_przegrody_P20B import main as figures
    from manifest_przegrody_P20B import main as manifest
    study();drive();checks();material();figures();manifest()


if __name__=='__main__':main()
