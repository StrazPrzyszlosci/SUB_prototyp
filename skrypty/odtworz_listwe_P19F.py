"""Odtworzenie odrębnego zakresu listwy; nie ponawia starszych kampanii."""


def main():
    from analiza_listwy_stalego_frontu_P19F import main as study
    from sprawdz_listwe_P19F import main as independent
    from zapisz_pole_referencyjne_P19F import main as field
    from wykresy_listwy_P19F import main as plots
    from manifest_listwy_P19F import main as manifest
    study();independent();field();plots();manifest()


if __name__=='__main__':main()
