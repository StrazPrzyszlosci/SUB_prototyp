#!/usr/bin/env python3
"""Download and verify original manufacturer's public source documents.

Generated original documents are *local verification artifacts*, not
automatically republished because manufacturer copyright/license is unknown.
Machine-readable verified scalar specifications are committed separately.
Usage:
  python skrypty/odtworz_dokumentacje_producentow.py --out /tmp/sub_producers
  python skrypty/odtworz_dokumentacje_producentow.py --out /tmp/sub_producers --offline
"""
import argparse,hashlib,json,datetime
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.error import URLError,HTTPError

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/"dane/karty_producentow/2026-10-31_9_marek_weryfikacja.json"
def digest(b):return hashlib.sha256(b).hexdigest()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",type=Path,default=Path("/tmp/sub_producers_20261031"))
    ap.add_argument("--offline",action="store_true",help="Verify existing local source copies only")
    ns=ap.parse_args();ns.out.mkdir(parents=True,exist_ok=True)
    src=json.loads(SRC.read_text())
    rec=[]
    for model in src["models"]:
        for typ,key in (("official_product_html","official_product_url"),
                        ("original_datasheet","original_manufacturer_datasheet_url")):
            url=model.get(key)
            if not url:continue
            ext=".pdf" if typ=="original_datasheet" and (".pdf" in url) else ".html"
            path=ns.out/(model["id"]+"_"+typ+ext)
            status="cached" if path.exists() else "missing"
            err=None
            if not ns.offline:
                try:
                    req=Request(url,headers={"User-Agent":"SUB_prototyp-source-verifier/1.0 (research)"})
                    with urlopen(req,timeout=25) as response:
                        blob=response.read(20*1024*1024+1)
                        final_url=response.geturl()
                    if len(blob)>20*1024*1024:raise ValueError("oversized source")
                    if ext==".pdf" and not blob.startswith(b"%PDF-"):
                        raise ValueError("Downloaded content is not a PDF")
                    path.write_bytes(blob)
                    status="fetched"
                except (ValueError,URLError,HTTPError,TimeoutError) as e:
                    err=str(e); status="cached_on_fetch_failure" if path.exists() else "fetch_failed"
            current=path.read_bytes() if path.exists() else b""
            rec.append(dict(id=model["id"],manufacturer=model["brand"],model=model["model"],
                source_kind=typ,source_url=url,file=str(path),exists=path.exists(),
                downloaded=status.startswith("fetched"),status=status,
                sha256=digest(current) if current else None,bytes=len(current),error=err))
    manifest={"date_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),
              "source_registry_sha256":digest(SRC.read_bytes()),"sources":rec,
              "warning":"Original PDFs copyrighted; do not commit/republish without license. Saved scalar fact register remains in git."}
    (ns.out/"SOURCE_MANIFEST.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps({"ok":sum(x["exists"] for x in rec),"total":len(rec),
        "not_available":[{"id":x["id"],"source":x["source_kind"],"error":x["error"]}
                         for x in rec if not x["exists"]]},ensure_ascii=False,indent=2))
if __name__=="__main__":main()
