"""Odtwórz wykonany zakres mechaniki. To nie cały program prototypu."""


def main():
    from archiwum_mechaniki_P18_P19 import restore
    from analiza_plyt_i_sciagow_P18A import main as plates
    from sprawdz_MITC_P18 import main as mitc
    from niezalezny_Ritz_P18 import main as ritz
    from emisja_i_sprzezenie_plyty_P18 import main as projection
    from reakcja_powietrza_P21A import main as air
    from sprawdz_reakcje_powietrza_P21A import main as air_checks
    from analiza_polaczen_normalnych_P19A import main as joints
    from sprawdz_polaczenie_normalne_P19 import main as joint_checks
    from analiza_scinania_i_szczelnosci_P19 import main as shear_leak
    from wymagania_zlaczy_i_pretow_P19 import main as edges_rods
    from wymagany_modul_relaksacji_P19 import main as relaxation
    from wykresy_mechaniki_P18_P19_P21 import main as figures
    from manifest_mechaniki_P18_P19_P21 import main as manifest
    restore('p18a');plates();mitc();ritz();projection();air();air_checks()
    restore('p19a');joints();joint_checks();shear_leak();edges_rods();relaxation();figures();manifest()


if __name__=='__main__':main()
