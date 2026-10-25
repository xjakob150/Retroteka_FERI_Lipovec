# 02 – Funkcionalnosti in obseg

## Uporabniške vloge

| Vloga | Kaj lahko počne | Katerih pravic nima |
|---|---|---|
| **Gost** | Išče igre, gleda javne zbirke. | Nima zbirk, ničesar ne vnaša. |
| **Zbiratelj** | Ustvarja zbirke, vanje dodaja igre, določa, ali so javne. | Ne ureja tujih zbirk, ne vidi zasebnih zbirk drugih. |
| **Moderator** | Kot zbiratelj; skrije javno zbirko z neprimerno vsebino. | Ne briše tujih zbirk, ne upravlja uporabnikov. |
| **Administrator** | Kot moderator; dodeljuje vloge in blokira račune. | Ne vidi gesel, ne spreminja vsebine tujih zbirk. |

## Predvidene funkcionalnosti

★ pomeni domensko specifično funkcionalnost.

| # | Funkcionalnost | Opis | MVP |
|---|---|---|---|
| 1 | Registracija in prijava z vlogami | Račun z geslom; pravice so odvisne od vloge. | **MVP** |
| 2 | Iskanje iger prek IGDB | Iskanje po naslovu in platformi. Rezultati se berejo iz IGDB in so omejeni na retro platforme. | **MVP** ★ |
| 3 | Zbirke | Uporabnik ustvari več poimenovanih zbirk, vsaka je javna ali zasebna. | **MVP** ★ |
| 4 | Dodajanje igre v zbirko | Izbrani igri uporabnik določi platformo, stanje (samo nosilec, komplet, zapakirano), nakupno ceno in opombe. | **MVP** ★ |
| 5 | Ogled javnih zbirk | Gostje in drugi uporabniki vidijo javne zbirke; moderator neprimerno zbirko skrije. | **MVP** |
| 6 | Okvirna cena in vrednost zbirke | Okvirna cena izvoda iz eBay API-ja glede na igro, platformo, regijo in stanje; seštevek za zbirko. Vsak pregled cene se ohrani, zato ima izvod zgodovino cen. | **MVP** ★ |
| 7 | Primerjava zbirk | Skupne igre in igre, ki jih ima samo eden od dveh zbirateljev. | |
| 8 | Seznam želja | Seznam iger, ki jih uporabnik še išče. Ni zbirka: vsak uporabnik ima svoj seznam želja. | |
| 9 | Filtri in statistika zbirke | Po platformi in stanju; število iger po platformah. | |
| 10 | Uvoz in izvoz zbirke (CSV) | Selitev iz Excelove evidence. | |
| 11 | Upravljanje uporabnikov v aplikaciji | Administrator dodeljuje vloge in blokira račune; v MVP to dela v Django adminu. | |

### Ključni delovni proces: dodajanje igre v zbirko

1. Uporabnik vpiše naslov. Backend povpraša IGDB in vrne zadetke za retro platforme.
2. Uporabnik izbere igro in zbirko ter vpiše platformo, stanje in nakupno ceno.
3. Backend preveri, da je igra izšla na izbrani platformi in da zbirka pripada uporabniku.
4. Če igre še ni v bazi, shrani igro (ID iz IGDB, naslov, naslovnico, leto, žanre, opis) in platforme, na katerih je izšla.
5. Pri eBay API-ju poišče okvirno ceno in jo shrani kot prvi pregled cene izvoda. Če API ni dosegljiv, se izvod shrani brez cene.

## Kasnejše nadgradnje

- Forum s kanali, objavami in komentarji, ki ga ureja moderator.
- Priporočilni sistem glede na zbirke.
- Cenovni alarm, ki zbiratelja obvesti ob spremembi cene.
- Skeniranje črtne kode s kamero telefona.
- Ujemanje za menjavo med zbiratelji.
- Evidenca konzol in dodatne opreme.

## Out of scope

- Klepet in zasebna sporočila.
- Tržnica: nakup, prodaja in plačila.
- Digitalne igre, emulacija in ROM-i.
- Platforme po 7. generaciji.
- Lastna baza podatkov o igrah; podatki se berejo iz IGDB.
- Nativna mobilna aplikacija.
