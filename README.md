# Retroteka

Spletna evidenca zbirk fizičnih retro iger.

Zbiratelji retro iger zbirko pogosto vodijo v Excelu ali po spominu, zato ne vedo zanesljivo, kaj že imajo in koliko je zbirka vredna. V Retroteki uporabnik igro poišče, podatki o njej (naslov, platforme, naslovnica) se preberejo iz IGDB, sam pa vpiše le lastnosti svojega izvoda: platformo, stanje in nakupno ceno. Sistem iz eBay doda okvirno tržno ceno in sešteje vrednost zbirke. Igre ureja v poljubno število zbirk, ki so lahko javne ali zasebne. Podprte so fizične igre za platforme do vključno 7. generacije (PS3, Xbox 360, Wii).

## Uporabljene tehnologije

| Področje | Tehnologije in orodja |
|---|---|
| Frontend | React, Vite, JavaScript, React Router, Axios, Tailwind CSS |
| Backend | Python, Django, Django REST Framework |
| Podatkovna baza | PostgreSQL |
| Avtentikacija | Django `auth`, JWT (`djangorestframework-simplejwt`) |
| Lokalni razvoj | Docker, Docker Compose |
| Zunanji API-ji | IGDB API (podatki o igrah), eBay Browse API (okvirne cene) |
| Drugo | Git, pytest |

## Struktura repozitorija

```
backend/    Django + DRF REST API
frontend/   React SPA
docs/       projektna dokumentacija in ADR-ji
```

## Lokalni zagon

Potrebna sta samo Docker in Docker Compose. Če imate starejšo samostojno različico, namesto `docker compose` pišite `docker-compose`.

```bash
cp .env.example .env
docker compose up --build
```

Ko storitve tečejo, v drugem terminalu pripravite bazo:

```bash
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py loaddata platforms
```

Frontend teče na http://localhost:5173, API na http://localhost:8000/api/.

> **Začasno:** ko bo dodan uporabniški model (#9), lokalne baze, ki je bila pripravljena pred tem, ne bo več mogoče posodobiti. Ponastavite jo z `docker compose down -v`, kar izbriše vse lokalne podatke, in znova poženite zgornja ukaza.

### Ključi za zunanje storitve

Aplikacija se zažene tudi brez ključev, vendar brez njih nekatere funkcije ne delujejo. Ključe vpišite v `.env`, ki se ne shrani v repozitorij.

| Spremenljivki | Kje jih dobite | Kaj brez njih ne deluje |
|---|---|---|
| `IGDB_CLIENT_ID`, `IGDB_CLIENT_SECRET` | [Twitch Developer Console](https://dev.twitch.tv/console/apps) | Iskanje iger, ki še niso shranjene v bazi |
| `EBAY_CLIENT_ID`, `EBAY_CLIENT_SECRET` | [eBay Developer Program](https://developer.ebay.com/my/keys) | Okvirne cene; izvodi se shranijo brez cene |

### Testi

Testi tečejo v kontejnerju na PostgreSQL, v ločeni testni bazi, in ne kličejo zunanjih storitev, zato ključi zanje niso potrebni.

```bash
docker compose exec backend pytest
docker compose exec backend pytest tests/test_setup.py::test_runs_on_postgresql
```

## Dokumentacija

Celotna dokumentacija je v mapi [`docs/`](docs/):

1. [Zasnova rešitve](docs/01-zasnova-resitve.md)
2. [Funkcionalnosti in obseg](docs/02-funkcionalnosti-in-obseg.md)
3. [Podatkovni model](docs/03-podatkovni-model.md)
4. [Arhitektura in tehnološki sklad](docs/04-arhitektura-in-tehnoloski-sklad.md)
5. [Uporabniške zgodbe](docs/05-uporabniske-zgodbe.md)
6. [Wireframes](docs/06-wireframes.md)

Arhitekturne odločitve so zapisane kot ADR-ji (format MADR) v mapi [`docs/adr/`](docs/adr/).
