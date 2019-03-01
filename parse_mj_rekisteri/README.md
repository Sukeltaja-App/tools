# Museoviraston paikkatietoaineisto

Museoviraston paikkatietoaineisto hylyistä json ja csv-muodossa ([lähde](https://www.museovirasto.fi/fi/palvelut-ja-ohjeet/tietojarjestelmat/kulttuuriympariston-tietojarjestelmat/kulttuuriympaeristoen-paikkatietoaineistot)).

Lähdetiedostona on käytetty tiedostoa `Muinaisjaannospisteet_t_point.dbf`. Tiedostosta on suodatettu vain tyyppiä `alusten hylyt,  ,  ,` sisältävät rivit. Sen jälkeen tiedostoa on siivottu hieman käsin ennen muuntamista csv-muotoon muuntamisen helpottamiseksi.

Paikkatietoaineisto on julkaistu
[CC-BY 4.0](http://paikkatieto.nba.fi/aineistot/tutkija.html) -lisenssillä.

## Käyttö

1. Asenna [python](https://www.python.org/download/releases/3.0/).
2. `python3 parse_mj_rekisteri.py <csv input filename> <json output filename>`
