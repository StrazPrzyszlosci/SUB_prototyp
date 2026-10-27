"""Samodzielne,niewielkie P23A;nie dotyka aktywnego gazu3D lub archiwów."""
import os


def main():
    os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
    from analiza_filtrow_dyskretnych_P23A import main as study
    from sprawdz_filtry_dyskretne_P23A import main as checks
    from kolejnosc_i_zapas_filtrow_P23A import main as order
    from raport_i_wykresy_filtrow_P23A import main as report
    from manifest_filtrow_P23A import main as manifest
    study();checks();order();report();manifest()


if __name__=='__main__':main()
