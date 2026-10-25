"""Odtworzenie czasowego styku;archiwalny pilot pozostaje jawnie archiwalny."""
from pathlib import Path
import os
import subprocess
import sys


def main():
    directory=Path(__file__).resolve().parent
    env=os.environ.copy();env.setdefault('OPENBLAS_NUM_THREADS','1')
    stages=[('sprawdz_styk_czasowy_P19C.py',[]),('analiza_styku_czasowego_P19C.py',['--independent','--full']),
            ('audyt_fizyki_P19C.py',[]),('wykresy_styku_czasowego_P19C.py',[]),('manifest_styku_czasowego_P19C.py',[])]
    for name,args in stages:subprocess.run([sys.executable,str(directory/name),*args],check=True,env=env)


if __name__=='__main__':main()
