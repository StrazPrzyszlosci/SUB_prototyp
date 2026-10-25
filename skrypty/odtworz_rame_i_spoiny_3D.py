"""Odtworzenie wykonanego etapu3D,bez starszych kampanii przetwornikow."""
from pathlib import Path
import os,subprocess,sys


def main():
    directory=Path(__file__).resolve().parent;env=os.environ.copy();env.setdefault('OPENBLAS_NUM_THREADS','1')
    stages=['sprawdz_bryly_i_rame_P18C.py','analiza_ramy_3D_P18C.py','uzupelnienie_siatki_ramy_P18C.py',
            'sprawdz_warstwy_ramy_P18C.py','rozwarstwienie_spoiny_P19D.py','sprawdz_styk_i_defekt_P19D.py',
            'wymagany_modul_spoin_ramy_P19E.py','wykresy_ramy_3D_P18C.py','manifest_ramy_i_spoin_3D.py']
    for name in stages:subprocess.run([sys.executable,str(directory/name)],check=True,env=env)


if __name__=='__main__':main()
