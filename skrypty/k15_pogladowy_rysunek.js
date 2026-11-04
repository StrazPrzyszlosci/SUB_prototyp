#!/usr/bin/env node
"use strict";
// K15 view generated ONLY from the same P30E/K15 assembly JSON; output is not a toolpath.
const fs=require("node:fs"),path=require("node:path");
function k15Preview(o){
  const scale=.54,ox=52,oy=160,tx=728,ty=160,cx=231,cz=250;
  const box=(x,y,w,h,fill,stroke="#5d6f7d",opacity=1,strokeWidth=1.5)=>`<rect x="${x.toFixed(2)}" y="${y.toFixed(2)}" width="${w.toFixed(2)}" height="${h.toFixed(2)}" fill="${fill}" fill-opacity="${opacity}" stroke="${stroke}" stroke-width="${strokeWidth}"/>`;
  const text=(x,y,value,size=16,fill="#203a51",weight="normal")=>`<text x="${x}" y="${y}" fill="${fill}" font-size="${size}" font-weight="${weight}" font-family="DejaVu Sans, Arial">${value}</text>`;
  const front=[
    box(ox,oy,1020*scale,500*scale,"#e2cdb5","#97765d"),
    `<circle cx="${ox+cx*scale}" cy="${oy+cz*scale}" r="${(388.4/2*scale).toFixed(2)}" fill="none" stroke="#49647d" stroke-width="3"/>`,
    `<circle cx="${ox+cx*scale}" cy="${oy+cz*scale}" r="${(355.8/2*scale).toFixed(2)}" fill="#fbfcfe" stroke="#374d60" stroke-width="3"/>`,
    `<circle cx="${ox+cx*scale}" cy="${oy+cz*scale}" r="${(368/2*scale).toFixed(2)}" fill="none" stroke="#c37328" stroke-width="1.5" stroke-dasharray="6 6"/>`,
    ...Array.from({length:8},(_,i)=>{
      const a=i*Math.PI/4;return `<circle cx="${(ox+(cx+184*Math.cos(a))*scale).toFixed(2)}" cy="${(oy+(cz-184*Math.sin(a))*scale).toFixed(2)}" r="4" fill="#b14538"/>`;
    }),
    text(ox+10,oy+295,"A — Front MDF44, oś (231,250), PCD Ø368",17),
    text(ox+10,oy+319,"Ø6,5 mm = tylko metalowy KOSZ",14,"#a34532","bold"),
    text(ox+10,oy+340,"Brak wybranych otworów pod śruby w MDF",14)
  ].join("\n");
  const top=[
    box(tx,ty,1020*scale,425*scale,"#e2cdb5","#97765d"),
    box(tx+22*scale,ty+44*scale,976*scale,359*scale,"#f9fbfd","#acb6bb",1),
    ...o.module_positions.map(m=>{
      const p=m.global_origin_xyz_mm;return box(tx+p[0]*scale,ty+p[1]*scale,m.dims_xyz_mm[0]*scale,m.dims_xyz_mm[1]*scale,"#78a5c9","#42698f",.25,1);
    }),
    ...[220,448,723].map(x=>box(tx+x*scale,ty+44*scale,22*scale,359*scale,"#347f9c","#254a60",.45)),
    box(tx+22*scale,ty+353*scale,976*scale,50*scale,"#c5d8a7","#5e8b51",.23),
    text(tx+12,ty+270,"B — Widok z góry: wręgi + 20 modułów",17),
    text(tx+12,ty+294,"Bryły AABB / położenia z modelu P30E",14),
    text(tx+12,ty+315,"Szablon regulacji: 100/120/150 l",14)
  ].join("\n");
  return `<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="680" viewBox="0 0 1400 680">
  <rect width="1400" height="680" fill="#f4f7fa"/>
  ${text(52,52,"K15 — spójny model obudowy i modułów",30,"#1f4058","bold")}
  ${text(52,82,"P30E: 1020 × 425 × 500 mm • model numeryczny, nie zweryfikowany projekt CNC",19,"#50677a")}
  ${box(35,110,595,430,"#fff","#dae1e5",1,1)}
  ${box(706,110,660,430,"#fff","#dae1e5",1,1)}
  ${front}
  ${top}
  ${text(52,585,"7 płatów korpusu  +  11 usztywnień  +  120 płatów modułów  =  138 formatek nominalnych",19,"#1b4560","bold")}
  ${text(52,619,"Szablony montażu, łączniki, tolerancje frezu, złącza i szczelność NIE są jeszcze zaprojektowane.",16,"#a04a34")}
  ${text(52,651,"Źródła: P30E/P30A; generator: skrypty/k15_pre_cnc_model.js. Materiały i liczba płatów: do kwalifikacji. CNC HOLD.",15,"#50677a")}
</svg>\n`;
}
function main(){const root=path.resolve(__dirname,".."),a=JSON.parse(fs.readFileSync(path.join(root,"wyniki/k15_p30e_przed_CNC_zestawienie.json"),"utf8"));const doc=k15Preview(a);fs.writeFileSync(path.join(root,"wyniki/k15_widoki_obudowy_i_wkladow_NIE_CNC.svg"),doc);console.log("K15 SVG generated");}
if(require.main===module)main();module.exports={k15Preview,main};
