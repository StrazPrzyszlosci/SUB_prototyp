# MES paneli i ściągów

Status: wykonane modele kontrolne P18A, nie pełna skrzynia.
[Raport029](../raporty/029_P18A_plyty_sciagi_i_dynamika.md) zawiera
172warianty, mody, naprężenia, warunki brzegowe i weryfikację.

**Teoria:** zginanie ma sztywność D~E*h³, masa powierzchniowa~rho*h.
Usztywnienie przeciwległych ścian może zmienić kształty drgań i podatność
silniej niż umiarkowane pogrubienie, ale przekazuje siłę do mocowań.

**Metoda:** prostokątna płytaMindlina z interpolacją ścinaniaMITC4.
Zwykły w pełni całkowanyQ4 może blokować ścinanie w cienkiej granicy.
Odrębny Navier i Ritz służą kontroli, a nie identyfikacji właściwościMDF.
Nie nazywamy tej implementacji pełną powłokąMITC4+.

**Ściąg:** w symetrycznym rozsuwaniu pary zwiększa sztywność.
Ruch niewydłużający pręta nie dostaje tej korzyści; masa może obniżyć
jego częstotliwość. Śledź postacie i udział w obciążeniu, nie tylko f1.

**Połączenia:** SSSS i CCCC są określonymi wzorcami z zadanym położeniem
krawędzi. Nie obejmują bezwarunkowo podatności naroży dowolnej skrzyni.
Pozostałość M_n na idealnymSSSS jest błędem dyskretyzacji, nie peel.

**Ważność:** duże w/h, wyboczenie pręta i znaczna reakcja powietrza
wymagają innych lub sprzężonych modeli. Unitpressure nie jest widmem
rzeczywistego subwoofera. Referencyjne MOR/IB nie zastępują S–N i3D.

**Kolejny zakres:** front z otworem, masa i obciążenie kosza, uszczelka,
pełna geometria i rzeczywiste mocowanie. Nie przygotowano plikówCNC.
