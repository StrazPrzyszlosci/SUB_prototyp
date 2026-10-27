"""Mały etapP22A,bez archiwizacji i bez dotykania aktywnegoP21B."""
import os


def main():
    os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
    from analiza_portu_wzmacniacza_P22A import main as study
    from sprawdz_port_wzmacniacza_P22A import main as checks
    from raport_i_wykresy_portu_P22A import main as report
    from manifest_portu_P22A import main as manifest
    study();checks();report();manifest()


if __name__=='__main__':main()
