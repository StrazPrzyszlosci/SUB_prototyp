"""P22B:nowe trajektorie i odrębneODE,bez pełnych archiwów i aktywnegoP21B."""
import os


def main():
    os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
    from analiza_nasycenia_i_pradu_P22B import main as study
    from sprawdz_nasycenie_P22B import main as checks
    from raport_i_wykresy_nasycenia_P22B import main as report
    from manifest_nasycenia_P22B import main as manifest
    study();checks();report();manifest()


if __name__=='__main__':main()
