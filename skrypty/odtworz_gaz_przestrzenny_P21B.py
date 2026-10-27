"""P21B bez powtarzania dawnych kampanii przetworników.

Podczas aktywnego P21B nie uruchamiać drugiej kopii;wznawianie odbywa się
po hashu wejść,nie jest nową niezależną replikacją.
"""
import os


def main():
    os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
    from odtworz_wszystko import assert_no_live_spatial_campaign
    assert_no_live_spatial_campaign()
    from sprawdz_gaz_3D_P21B import main as checks
    from analiza_gazu_przestrzennego_P21B import main as study
    from granica_obciazenia_P21B import main as bound
    from asymptotyka_gazu_P21B import main as asymptote
    from wykresy_i_ocena_gazu_P21B import main as figures
    from raportuj_gaz_przestrzenny_P21B import main as report
    from manifest_gazu_przestrzennego_P21B import main as manifest
    checks();study();bound();asymptote();figures();report();manifest()


if __name__=='__main__':main()
