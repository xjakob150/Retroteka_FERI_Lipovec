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

## Dokumentacija

Celotna dokumentacija je v mapi [`docs/`](docs/):

1. [Zasnova rešitve](docs/01-zasnova-resitve.md)
2. [Funkcionalnosti in obseg](docs/02-funkcionalnosti-in-obseg.md)
3. [Podatkovni model](docs/03-podatkovni-model.md)
4. [Arhitektura in tehnološki sklad](docs/04-arhitektura-in-tehnoloski-sklad.md)
5. [Uporabniške zgodbe](docs/05-uporabniske-zgodbe.md)
6. [Wireframes](docs/06-wireframes.md)

Arhitekturne odločitve so zapisane kot ADR-ji (format MADR) v mapi [`docs/adr/`](docs/adr/).
