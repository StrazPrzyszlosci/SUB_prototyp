"""Odtwarzalny odczyt oryginalnego rysunku, bez tablic wygenerowanych przezAI.

Etap pozyskania źródła, uruchamiany osobno po uzyskaniu PDF o wskazanymSHA.
Zwykłe obliczenia używają wersjonowanego CSV i nie wymagają prywatnej kopii PDF.
"""
import csv
import hashlib
from itertools import product
import json
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]


def main():
    import fitz
    cfg=json.loads((ROOT/'dane/konfiguracje/p12c_digitalizacja_Lgen.json').read_text())
    if fitz.VersionBind!=cfg['pymupdf_version_used']:
        raise RuntimeError('Do odtworzenia tego odczytu potrzebna wersja z requirements_zrodla.txt; inny renderer wymaga nowej wersji danych.')
    source=ROOT/cfg['private_pdf_path']
    assert hashlib.sha256(source.read_bytes()).hexdigest()==cfg['source_pdf_sha256']
    page=fitz.open(source)[cfg['page_index']]
    pix=page.get_pixmap(matrix=fitz.Matrix(cfg['render_dpi']/72,cfg['render_dpi']/72),
                        clip=fitz.Rect(*cfg['clip_pdf_points']),alpha=False)
    pix.save(ROOT/'.firecrawl/p12c_Purifi_Fig4_native.png')
    pixels=np.frombuffer(pix.samples,np.uint8).reshape(pix.height,pix.width,pix.n)[:,:,:3].astype(int)
    left,right=cfg['x_pixel_ticks'];lowx,highx=cfg['x_ticks_mm'];top,bottom=cfg['y_pixel_ticks']
    def ordinate(y,yt=top,yb=bottom):
        return 10**(np.log10(cfg['y_ticks_mh'][0])+(y-yt)/(yb-yt)*np.log10(cfg['y_ticks_mh'][1]/cfg['y_ticks_mh'][0]))*1e-3
    rows=[];lo,hi=cfg['curve_roi_y_pixels'];n=cfg['column_half_width_pixels']
    for position in cfg['positions_mm']:
        xp=int(round(left+(position-lowx)/(highx-lowx)*(right-left)))
        patch=pixels[lo:hi,xp-n:xp+n+1]
        r,g,b=patch[:,:,0],patch[:,:,1],patch[:,:,2]
        masks={'red':(r>180)&(g<100)&(b<100),'black':np.maximum.reduce([r,g,b])<55,
               'blue':(b>180)&(r<100)&(g<100),'orange':(r>180)&(g>100)&(g<220)&(b<100),
               'magenta':(r>160)&(b>180)&(g<100),'green':(g>160)&(r<100)&(b<100)}
        for color,frequency in cfg['colors_frequency_hz'].items():
            selected=np.where(np.any(masks[color],axis=1))[0]+lo
            if color=='black':
                runs=np.split(selected,np.where(np.diff(selected)>1)[0]+1)
                runs=[x for x in runs if len(x)>=cfg['minimum_black_run_length_pixels']]
                if len(runs)!=1:raise ValueError(f'Niejednoznaczna czarna krzywa: x={position}, grup={len(runs)}')
                selected=runs[0]
            if not len(selected):raise ValueError('Brak pikseli krzywej')
            ylo,yhi=float(selected.min()),float(selected.max());center=(ylo+yhi)/2
            t=cfg['tick_uncertainty_pixels'];stroke=cfg['extra_stroke_uncertainty_pixels']
            values=[ordinate(y,top+dt,bottom+db) for y,dt,db in product([ylo-stroke,yhi+stroke],[-t,t],[-t,t])]
            xvalues=[lowx+(x-xl)/(xr-xl)*(highx-lowx) for x,xl,xr in product([xp-n,xp+n],[left-t,left+t],[right-t,right+t])]
            rows.append(dict(position_mm=position,f_hz=frequency,x_pixel=xp,y_pixel_low=ylo,y_pixel_high=yhi,
                             Lgen_magnitude_h=float(ordinate(center)),digitization_lower_h=float(min(values)),
                             digitization_upper_h=float(max(values)),position_lower_mm=float(min(xvalues)),
                             position_upper_mm=float(max(xvalues)),source_id=cfg['source_id'],
                             data_type='DIGITIZED_MANUFACTURER_GRAPH_NOT_RAW_MEASUREMENT'))
    target=ROOT/'dane/zrodla/digitalizacja/Purifi_NAB01_Lgen_fig4.csv';target.parent.mkdir(parents=True,exist_ok=True)
    with target.open('w',newline='') as handle:
        writer=csv.DictWriter(handle,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    meta=dict(source_pdf_sha256=cfg['source_pdf_sha256'],derived_csv_sha256=hashlib.sha256(target.read_bytes()).hexdigest(),
              rows=len(rows),pymupdf_version=fitz.VersionBind,render_shape=[pix.width,pix.height],
              definition='|Lgen|, nieRe(Lgen) i nieLd. Oryginalne osie sprawdzono wzrokowo.',
              extraction='Selekcja koloru, osobne odrzucenie cienkiej czarnej siatki; jawna kalibracja logarytmicznej osi.',
              uncertainty_scope=cfg['uncertainty_scope'])
    target.with_suffix('.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2))
    print(json.dumps(meta,ensure_ascii=False,indent=2));return rows


if __name__=='__main__':main()
