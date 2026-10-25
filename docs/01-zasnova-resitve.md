# 01 – Zasnova rešitve

## Ime rešitve

**Retroteka** – spletna evidenca zbirk fizičnih retro iger.

## Namen rešitve in problem

Zbiratelji retro iger zbirko vodijo v Excelu ali po spominu. Zato ne vedo zanesljivo, kaj že imajo in koliko je zbirka vredna, kupujejo dvojnike in podatke o igrah vnašajo ročno.

V Retroteki uporabnik igro poišče, podatki o njej (naslov, platforme, naslovnica) se preberejo iz zunanjega API-ja, sam pa vpiše le lastnosti svojega izvoda. Sistem doda okvirno tržno ceno. Igre ureja v poljubno število zbirk. Podprte so fizične igre za platforme do vključno 7. generacije (PS3, Xbox 360, Wii).

## Ciljni uporabniki

- **Zbiratelj retro iger:** doma ureja zbirke, na sejmu pa na telefonu preveri, ali igro že ima in koliko je vredna.
- **Obiskovalec:** brez računa išče igre in si ogleda javne zbirke drugih.

## Kratek opis delovanja

1. Uporabnik se registrira in ustvari zbirko, na primer »PS2« ali »Za prodajo«.
2. Poišče igro. Rezultati se preberejo iz IGDB.
3. Igro doda v zbirko ter vpiše platformo, stanje izvoda in nakupno ceno.
4. Sistem pridobi okvirno tržno ceno izvoda in sešteje vrednost zbirke.
5. Zbirko lahko označi kot javno, da jo vidijo drugi.

Primerjava zbirk in forum sta predvidena kot nadaljnji razvoj.
