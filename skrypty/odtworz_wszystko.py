"""Pełny przebieg naukowy z zachowaniem poprzedniego stanu roboczego."""
from datetime import datetime
import hashlib
import json
from pathlib import Path
import shutil
from zoneinfo import ZoneInfo

ROOT=Path(__file__).resolve().parents[1]


def main():
    out=ROOT/'wyniki'
    previous=[p for p in out.iterdir() if p.is_file()] if out.exists() else []
    if previous:
        stamp=datetime.now(ZoneInfo('Europe/Warsaw')).strftime('%Y%m%dT%H%M%S_%f')
        archive=out/'archiwum'/stamp
        archive.mkdir(parents=True)
        old=json.loads((out/'manifest.json').read_text()) if (out/'manifest.json').exists() else {}
        mismatches=[]
        for p in previous:
            shutil.copy2(p,archive/p.name)
            expected=old.get('output_sha256',{}).get(str(p.relative_to(ROOT)))
            if expected and hashlib.sha256(p.read_bytes()).hexdigest()!=expected:
                mismatches.append(p.name)
        inputs=archive/'stan_wejsc'
        inputs.mkdir()
        for name in ('skrypty','dane'):
            shutil.copytree(ROOT/name,inputs/name,ignore=shutil.ignore_patterns('__pycache__'))
        for name in ('brief_system_audio_DIY_v0.6.md','DECYZJE_I_PYTANIA.md','PLAN_BADAN_NAUKOWYCH.md','PROGRAM_30_BADAN.md'):
            shutil.copy2(ROOT/name,inputs/name)
        (archive/'status_archiwum.json').write_text(json.dumps({
            'status':'migawka_poprzedniego_stanu_roboczego',
            'note':'Przy pierwszej archiwizacji mogą występować zmiany wykonane od ostatniego manifestu; nie jest to rzekomo odtworzony dawny przebieg.',
            'outputs_changed_since_manifest':mismatches},ensure_ascii=False,indent=2))
        print('Zachowano poprzedni stan roboczy:',archive.relative_to(ROOT))
    from sprawdz_model import main as checks
    from audyt_wykresow import main as images
    from analiza_fizyki import main as physics
    from analiza_celow_dsp import main as dsp
    from uruchom_badania import main as baseline
    from sprawdz_nieszczelnosci import main as leakage_checks
    from analiza_nieszczelnosci import main as leakage
    from porownaj_szeroka_pule import main as pool
    from analiza_granic_litrazu import main as volume_bounds
    from audyt_identyfikowalnosci import main as identify
    from raportuj_poszerzenie import main as reports
    from sprawdz_pokoj import main as room_checks
    from analiza_pokoju import main as room_analysis
    from raportuj_pokoj import main as room_report
    from sprawdz_niepewnosc import main as uncertainty_checks
    from analiza_niepewnosci import main as uncertainty_analysis
    from analiza_adwersarialna import main as adversarial
    from sprawdz_swiadkow_p06 import main as witness_checks
    from raportuj_niepewnosc import main as uncertainty_report
    from wizualizuj_sobol import main as sensitivity_plot
    from sprawdz_gaz_i_wypelnienie import main as gas_checks
    from audyt_termodynamiki import main as thermodynamic_identities
    from analiza_gazu_i_wypelnienia import main as gas_analysis
    from raportuj_gaz_i_wypelnienie import main as gas_report
    from sprawdz_pakiet_gazu import main as gas_tables
    from audyt_identyfikacji_wypelnienia import main as filling_identification
    from sprawdz_promieniowanie import main as radiation_checks
    from audyt_energii_promieniowania import main as radiation_energy
    from analiza_promieniowania import main as radiation_analysis
    from analiza_scian_i_sprzezen import main as radiation_coupling
    from gesty_skan_sprzezenia_pokoju import main as radiation_dense
    from replikacja_poprawki_czaszy import main as radiation_replication
    from sprawdz_zbieznosc_pokoju_P11 import main as radiation_spatial
    from sprawdz_pakiet_promieniowania import main as radiation_tables
    from raportuj_promieniowanie import main as radiation_report
    from analiza_geometrii_odsluchu import main as listening_geometry
    from sprawdz_naped_nieliniowy import main as nonlinear_checks
    from analiza_napedu_nieliniowego import main as nonlinear_analysis
    from analiza_kompensacji_gazu import main as nonlinear_compensation
    from sprawdz_kompensacje_gazu import main as compensation_checks
    from sprawdz_pakiet_nieliniowy import main as nonlinear_tables
    from raportuj_naped_nieliniowy import main as nonlinear_report
    from sprawdz_pamiec_cewki import main as coil_memory_checks
    from analiza_cewki_z_pamiecia import main as coil_memory_analysis
    from replikacja_sily_L2R2 import main as coil_force_replication
    from analiza_ident_Le_i_dopasowania import main as coil_identification
    from audyt_wykluczenia_1_bieguna import main as one_pole_audit
    from sprawdz_pakiet_pamieci import main as memory_tables
    from raportuj_pamiec_cewki import main as memory_report
    from analiza_P14A_sygnaly import main as p14a_analysis
    from sprawdz_P14A import main as p14a_checks
    from raportuj_P14A import main as p14a_report
    from analiza_P14B import main as p14b_analysis
    from rozstrzygnij_P14B import main as p14b_refine
    from audyt_dynamiki_P14B import main as p14b_linear_audit
    from sprawdz_emisje_P14B import main as p14b_emission_checks
    from podsumuj_studia_P14B import main as p14b_studies
    from projekcja_P14B import main as p14b_projection
    from sprawdz_kampanie_P14B import main as p14b_selected_audit
    from raportuj_pelne_P14B import main as p14b_report
    from analiza_topologii_termicznej_P15A import main as p15a_analysis
    from audyt_symboliczny_P15A import main as p15a_symbolic
    from sprawdz_granice_termiczne_P15A import main as p15a_limits
    from archiwum_P15B import restore as p15b_restore
    from analiza_sprzezenia_Re_T_P15B import main as p15b_analysis
    from audyt_sprzezenia_Re_T_P15B import main as p15b_audit
    from raportuj_sprzezenie_Re_T_P15B import main as p15b_report
    checks()
    images()
    physics()
    dsp()
    leakage_checks()
    leakage()
    if (ROOT/'dane/przetworniki/pula_rozszerzona.json').exists():
        pool()
        leakage_checks(ROOT/'dane/przetworniki/pula_rozszerzona.json')
        volume_bounds()
        identify()
        reports()
    room_checks()
    room_analysis()
    room_report()
    uncertainty_checks()
    uncertainty_analysis()
    sensitivity_plot()
    adversarial()
    witness_checks()
    uncertainty_report()
    gas_checks()
    thermodynamic_identities()
    gas_analysis()
    gas_tables()
    filling_identification()
    gas_report()
    radiation_checks()
    radiation_energy()
    radiation_analysis()
    radiation_coupling()
    radiation_dense()
    radiation_replication()
    radiation_spatial()
    radiation_tables()
    radiation_report()
    listening_geometry()
    nonlinear_checks()
    nonlinear_analysis()  # Zgodny dziennik wznawia przypadki; nie jest nową niezależną replikacją.
    nonlinear_compensation()
    compensation_checks()
    nonlinear_tables()
    nonlinear_report()
    coil_memory_checks()
    coil_memory_analysis()
    coil_force_replication()
    coil_identification()
    one_pole_audit()
    memory_tables()
    memory_report()
    p14a_analysis()
    p14a_checks()
    p14a_report()
    p14b_analysis()
    p14b_refine()
    p14b_linear_audit()
    p14b_emission_checks()
    p14b_studies()
    p14b_projection()
    p14b_selected_audit()
    p14b_report()
    p15a_analysis()
    p15a_symbolic()
    p15a_limits()
    p15b_restore()
    p15b_analysis()
    p15b_audit()
    p15b_report()
    baseline()  # Manifest powstaje po wszystkich obliczeniach.


if __name__=='__main__':
    main()
