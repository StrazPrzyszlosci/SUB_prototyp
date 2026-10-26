"""Odtworzenie P20A, bez ponawiania dawnych kampanii przetworników."""
import os


def main():
    os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
    from analiza_wkladow_P20A import main as modules
    from naped_z_wkladami_P20A import main as drive
    from sprawdz_wklady_P20A import main as checks
    from kanaliki_z_masa_P20A import main as neck
    from wykresy_i_ocena_wkladow_P20A import main as figures
    from manifest_regulacji_P20A import main as manifest
    modules();drive();checks();neck();figures();manifest()


if __name__=='__main__':main()
