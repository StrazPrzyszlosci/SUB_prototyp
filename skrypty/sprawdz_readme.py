#!/usr/bin/env python3
"""Niezależny od pakietów naukowych audyt README i jego ilustracji."""
import re, struct, sys, zlib
from pathlib import Path
from urllib.parse import unquote
from xml.etree import ElementTree
root=Path(__file__).resolve().parents[1]
readme=(root/"README.md").read_text(encoding="utf-8")
links=re.findall(r'!?\[[^\]]*\]\(([^)]+)\)',readme)
images=re.findall(r'!\[[^\]]*\]\(([^)]+)\)',readme)
bad=[]
def target(s):
    s=s.split("#",1)[0].split(' "',1)[0].strip("<>")
    return None if not s or s.startswith(("http:", "https:", "mailto:", "data:")) else unquote(s)
for item in links:
    f=target(item)
    if f and not (root/f).exists(): bad.append("Zepsuty link: "+f)
def png_ok(path):
    data=path.read_bytes()
    if not data.startswith(b"\x89PNG\r\n\x1a\n"): return False
    off=8; got_ihdr=False; got_iend=False
    while off+12<=len(data):
        n=struct.unpack(">I",data[off:off+4])[0]
        if n>len(data)-off-12:return False
        ty=data[off+4:off+8]; chunk=data[off+8:off+8+n]
        crc=struct.unpack(">I",data[off+8+n:off+12+n])[0]
        if zlib.crc32(ty+chunk)&0xffffffff !=crc:return False
        off+=12+n
        if ty==b"IHDR":got_ihdr=n==13
        if ty==b"IEND":got_iend=True;break
    return got_ihdr and got_iend and off==len(data)
for item in set(images):
    p=target(item)
    if p and (root/p).is_file():
        try:
            if p.endswith(".png") and not png_ok(root/p):bad.append("Bledny PNG: "+p)
            if p.endswith(".svg"):
                element=ElementTree.parse(root/p).getroot()
                if not element.tag.endswith("svg") or not element.attrib.get("viewBox"):
                    bad.append("Bledny SVG: "+p)
        except Exception as exc:bad.append("Nieczytelny obraz "+p+": "+str(exc))
for label in ("34 modele głośników","35 konfiguracji elektrycznych","19 producentów","108 raportów"):
    if label not in readme:bad.append("Nieaktualny naglowek: "+label)
if len(images)<101:bad.append("Brak diagramow wymaganych przez test P42: "+str(len(images)))
if re.search(r'\bklient\w*\b',readme,re.I):bad.append("Niedozwolony termin klient")
if "wyniki/106_P21G_komora_i_podatne_panele.svg" in readme:bad.append("Zepsuty P21G")
for e in bad:print("ERROR: "+e,file=sys.stderr)
if bad:sys.exit(1)
print(f"OK: {len(links)} odniesien, {len(images)} obrazow, {len(set(images))} unikalnych")
