# Deploying the reading service

The service (`jyotish.api`: the API, the website, the review step and the blind comparison) runs as
one container beside a Postgres database. This file says how it is configured and what its licences
ask of a deployment; the step-by-step guide to one host follows it.

## Configuration: the environment only

The service reads its configuration from environment variables and from nothing else (no config file,
no key in the image). The Dockerfile sets defaults for a single container on SQLite; a deployment sets
the rest.

| Variable | What it is | Default in the image |
| --- | --- | --- |
| `JYOTISH_DATABASE_URL` | The database. Postgres deployed: `postgresql+psycopg://user:password@host:5432/db`; a host's `postgres://…` URL is accepted as it is. | `sqlite:////data/jyotish.db` |
| `ANTHROPIC_API_KEY` | The model key the narration uses. Read by the Anthropic SDK; never stored, logged or returned (`/health` says only whether one is set). | none: readings fail with "the server has no model key" |
| `JYOTISH_CANDIDATE_RULES` | Where depth-full readings append their `[tradition:]` sentences for triage (docs/triage.md). | `/data/candidate_rules.jsonl` |
| `JYOTISH_CACHE_DIR` | The chart cache (assessed charts by birth data, conventions and engine hash). Safe to lose. | `/data/cache` |
| `JYOTISH_SOURCE_URL` | Where users can get the source of the running version (the licence section below). | none: `/source` answers 404 |
| `PORT` | The port to listen on, when the host sets one. | 8000 |

Everything the service writes outside the database goes under `/data`, a volume.

The database is migrated when the service starts (`jyotish.db.migrate`, Alembic, `src/jyotish/migrations`):
a new database is created at the head revision; a database made before the migrations existed (a local
`jyotish.db`) is adopted and stamped without losing a row. Run one service process per database: the
reading jobs run on its threads, and the rate limit counts in its memory.

## Running it locally with Docker

```bash
cp .env.example .env
```

Fill in `POSTGRES_PASSWORD` (any long random string) and `ANTHROPIC_API_KEY` in `.env`, then:

```bash
docker compose up -d --build
```

```bash
curl -s http://127.0.0.1:8000/health
```

`/health` answers 200 with the engine's version and hash, the database's dialect, its revision and the
head, and `"narration": "live"` once a key is set; it answers 503 when the database cannot be reached.
The website is at <http://127.0.0.1:8000/>.

## The licence position

**Swiss Ephemeris.** The engine computes positions with `pyswisseph`, the Python binding of the Swiss
Ephemeris, including its built-in Moshier routines when no ephemeris files are installed (the image
installs none). Swiss Ephemeris is licensed either under the GNU Affero General Public License v3
(AGPL-3.0) or under Astrodienst's paid Swiss Ephemeris Professional License; there is no permissive
fallback (SPEC, Tech stack). The image ships it under the AGPL. Running the service on a server that
people use over the network (a reviewer opening `/review`, a client using the form) is the case AGPL
section 13 is about: the service must offer every such user the Corresponding Source of the version it
runs, the engine's own code included, under the AGPL. In this deployment:

- `JYOTISH_SOURCE_URL` names where that source is: a repository or archive at the exact commit deployed,
  which every user of the service can open. If the repository is private, that is not enough: publish
  the deployed commit somewhere users can reach (a public mirror or a release archive), or give the users
  access.
- The website's footer links to `/source`, which redirects to it, and `/health` reports it.
- Changing the code changes nothing here: whatever runs is what must be offered.

The alternatives SPEC names, for a product that should not be under the AGPL: buy the Astrodienst
professional licence, or compute positions from JPL kernels with `jplephem` or `skyfield` (MIT) and an
in-house sidereal conversion, validated against Swiss Ephemeris in development. Neither is built.

**What else is in the image.** GeoNames' place list (CC BY 4.0) is credited in the footer. PyJHora (AGPL)
is a development-time reference for the cross-check and is not installed in the image (the `crosscheck`
extra is not built). Astro-Databank data is not used by the service.

This is the project's reading of the licences, not legal advice; a commercial launch is the moment to
have it read by someone who gives it.
