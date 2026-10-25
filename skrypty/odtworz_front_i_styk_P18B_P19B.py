"""Odtworzenie nowego etapu, bez ponawiania poprzednich kampanii przetworników."""
def main():
    from sprawdz_front_z_otworem_P18B import main as check
    from analiza_frontu_z_otworem_P18B import main as front
    from analiza_styku_frontu_P19B import main as contact
    from wykresy_frontu_i_styku_P18B_P19B import main as figures
    from manifest_frontu_P18B_P19B import main as manifest
    check();front();contact();figures();manifest()


if __name__=='__main__':main()
