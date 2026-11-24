

\# 07 – Pregled prevzetega projekta



\## 1. Namen projekta



Retroteka je spletna aplikacija za vodenje zbirk fizičnih retro videoiger. Uporabnikom omogoča iskanje iger, organizacijo lastnih zbirk, evidentiranje posameznih fizičnih izvodov ter spremljanje njihove okvirne tržne vrednosti.



\## 2. Uporabljene tehnologije



\- Frontend: React, Vite, JavaScript, React Router, Axios in Tailwind CSS.

\- Backend: Python, Django in Django REST Framework.

\- Podatkovna baza: PostgreSQL.

\- Avtentikacija: JWT.

\- Zunanji storitvi: IGDB API in eBay Browse API.

\- Razvojno okolje: Docker in Docker Compose.

\- Testiranje: pytest.



\## 3. Pregled implementiranih funkcionalnosti MVP



Projekt predvideva naslednje funkcionalnosti MVP:



1\. Registracija in prijava uporabnikov z uporabniškimi vlogami.

2\. Iskanje retro iger prek zunanje storitve IGDB.

3\. Ustvarjanje in upravljanje uporabniških zbirk.

4\. Dodajanje in urejanje fizičnih izvodov iger v zbirkah.

5\. Ogled javnih zbirk in moderiranje neprimerne vsebine.

6\. Pridobivanje okvirnih cen iz eBaya in izračun vrednosti zbirke.



V repozitoriju so prisotni backend API-ji, podatkovni modeli, serializerji in pripadajoči testi za navedene funkcionalnosti.



Upravljanje uporabniških vlog je podprto tudi prek Django Admina.



\## 4. Pregled petih uporabniških zgodb



\### US-01 – Registracija



Uporabnik lahko ustvari račun z uporabniškimi podatki. Backend podpira registracijo, preverjanje podatkov in ustvarjanje uporabniškega računa.



Preverjanje: `test\_register.py`.



Ocena: Funkcionalnost je podprta in ima avtomatizirane teste.



\### US-02 – Prijava in odjava



Registrirani uporabnik se lahko prijavi in odjavi. Za avtentikacijo se uporabljajo JWT žetoni, podprta je tudi njihova blacklist funkcionalnost.



Preverjanje: `test\_auth.py`.



Ocena: Funkcionalnost je implementirana in ima avtomatizirane teste.



\### US-03 – Iskanje iger po naslovu



Uporabnik lahko išče retro igre prek storitve IGDB. Implementirani so iskanje, predpomnjenje rezultatov, rezervni podatki in straničenje.



Preverjanje: `test\_game\_search.py` in `test\_game\_search\_api.py`.



Ocena: Funkcionalnost je implementirana in ima avtomatizirane teste.



\### US-04 – Filtriranje rezultatov po platformi



Iskanje omogoča filtriranje iger glede na izbrano platformo. Projekt vsebuje API za pridobivanje platform in teste za pripadajočo funkcionalnost.



Preverjanje: `test\_platforms\_api.py`.



Ocena: Funkcionalnost je implementirana na backendu in ima avtomatizirane teste.



\### US-05 – Ustvarjanje zbirke



Prijavljeni uporabnik lahko ustvarja lastne zbirke. Implementirano je upravljanje zbirk, njihova vidnost in preverjanje uporabniških dovoljenj.



Preverjanje: `test\_collection\_api.py` in `test\_collection\_serializer.py`.



Ocena: Funkcionalnost je implementirana in ima avtomatizirane teste.



\## 5. Preverjanje testov



Projekt sem lokalno zagnala z uporabo Docker Compose.



Uspešno sem izvedel migracije podatkovne baze in naložil začetne podatke o platformah.



Backend teste sem zagnal z ukazom:



`docker compose exec backend pytest`



Rezultat:



\- Število zbranih testov: 489.

\- Uspešno opravljenih testov: 489.

\- Neuspešnih testov: 0.

\- Čas izvajanja: 146,58 sekunde.



Med izvajanjem se je pojavilo 232 opozoril, predvsem zaradi prekratkega JWT ključa in opozorila glede prihodnje različice Django.



\## 6. Sklep



Projekt vsebuje obsežno implementacijo glavnih funkcionalnosti MVP. Backend vključuje registracijo in avtentikacijo uporabnikov, iskanje iger, upravljanje zbirk in izvodov, javne zbirke, moderiranje ter pridobivanje in spremljanje cen.



Pet pregledanih uporabniških zgodb ima pripadajoče backend teste. Rezultat 489 uspešno opravljenih testov potrjuje, da obstoječi backend testi uspešno prestanejo preverjanje.



Za popolno potrditev skladnosti z uporabniškimi zgodbami je treba preveriti tudi delovanje funkcionalnosti v uporabniškem vmesniku.



Projekt sem lokalno uspešno pripravil z Dockerjem, s čimer je omogočeno nadaljnje delo na vzpostavitvi CI/CD cevovoda.
