"""P24A:domyślnie odczyt świadków i niezależne kontrole,bez nowegoSDP.

--search wymaga opcjonalnego requirements_p24.txt i nadal wznawia pasujące
rekordy. Nie usuwa starych świadków,nie archiwizuje aktywnego P21B.
"""
from pathlib import Path
import argparse,fcntl,os

ROOT=Path(__file__).resolve().parents[1]


def main(search=False):
    os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
    for path in (ROOT/'.p24a_locks').glob('*.lock'):
        with path.open('r') as fd:
            try:fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
            except BlockingIOError:raise RuntimeError('P24A search active;do not overwrite its live summary/tables.')
            else:fcntl.flock(fd,fcntl.LOCK_UN)
    if search:
        try:from analiza_obszarow_P24A import main as run_search
        except ImportError as e:raise RuntimeError('Optional search needs an environment with requirements_p24.txt;stored-witness verification needs no CVXPY.') from e
        run_search()
    from sprawdz_swiadkow_P24A import main as exact
    from tabela_z_certyfikatow_P24A import main as export
    from audyt_tozsamosci_P24A import main as symbols
    from naped_i_trajektorie_P24A import main as trajectories
    from raport_i_wykresy_obszarow_P24A import main as report
    from manifest_obszarow_P24A import main as manifest
    exact();export();symbols();trajectories();report();manifest()


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--search',action='store_true')
    main(parser.parse_args().search)
