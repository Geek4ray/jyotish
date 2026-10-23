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
| `JYOTISH_MODEL_FIXTURE` | Test only: every reading replays this recorded narration and calls no model (CI's smoke test). Never set it on a deployment; the log warns at start and `/health` says `"narration": "fixture"`. | none |

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

The smoke test CI runs on every push (`scripts/smoke.py`) can be run against this too: it needs a
reviewer token and a service replaying a recording, so it is for a throwaway database, not the real one.
In CI: the image on SQLite with `JYOTISH_MODEL_FIXTURE=/fixtures/narration_career_edited.json`, a token from
`docker exec app jyotish reviewer add smoke`, then `python scripts/smoke.py --url http://127.0.0.1:8000
--token <token>`: `/health`, a reading of the reference chart posted and done, its review page opened in
Chromium, the token taken, the three intro screens and the career question answered, the answer read
back from the server.

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

## From an empty Fly.io account to a working /review link

Fly.io, because every step is one documented command (Railway's CLI documents no flag for an empty
service, a volume's mount path or a command run in the container, so those steps would be clicks).
Region `sin` (Singapore): Fly has no region in India, and Singapore is the nearest with Managed
Postgres. Run everything from the repository's folder on your Mac, in Terminal. Where a line says
`<…>`, put in what it names.

**1. Install the Fly command and sign up.**

```bash
brew install flyctl
```

```bash
fly auth signup
```

A browser opens; sign up (Fly asks for a card before it runs anything). If you already have an account,
`fly auth login` instead.

**2. Name the app.** The name becomes the address, `https://<name>.fly.dev`, and must be free across all of
Fly. Pick one and keep it in your Terminal session (repeat this line in any new Terminal window):

```bash
export APP=jyotish-ray
```

```bash
fly apps create "$APP"
```

If the name is taken, choose another, run `export APP=…` again and repeat.

**3. A volume for the service's files** (the chart cache and the candidate rules; 1 GB):

```bash
fly volumes create jyotish_data --region sin --size 1 -a "$APP" -y
```

**4. The database.** Create a Managed Postgres cluster (Postgres 16, the Basic plan; Fly shows the price
before it creates anything):

```bash
fly mpg create --name jyotish-db --region sin --plan Basic --pg-major-version 16
```

It prints the cluster's ID when it is ready (a few minutes). If you lose it:

```bash
fly mpg list
```

Attach it to the app under the variable the service reads:

```bash
fly mpg attach <CLUSTER ID> -a "$APP" --variable-name JYOTISH_DATABASE_URL
```

**5. The secrets.** Your Anthropic API key, and where the source is offered (the licence section above;
the repository is public, so its address is enough):

```bash
fly secrets set ANTHROPIC_API_KEY=<your key> JYOTISH_SOURCE_URL=https://github.com/Geek4ray/jyotish -a "$APP" --stage
```

**6. Deploy.** Fly builds the image from the Dockerfile on its own builders (about five minutes the first
time) and starts the machine with `fly.toml`:

```bash
fly deploy -a "$APP"
```

**7. Check it.**

```bash
curl -s https://$APP.fly.dev/health
```

You want `"status": "ok"`, `"dialect": "postgresql"`, the same value for `"revision"` and `"head"`, and
`"narration": "live"`. Open `https://<your app>.fly.dev/` in a browser: the site.

**8. Tokens.** One for each reviewer, and one for you as the owner (it reads the costs). Each prints once;
send the reviewer's to the reviewer privately, keep yours in your password manager:

```bash
fly ssh console -a "$APP" -C "jyotish reviewer add judge-1"
```

```bash
fly ssh console -a "$APP" -C "jyotish owner add ray"
```

Each first prints the database it writes to: it must say `database: postgresql at …`. If it says
`sqlite`, the token went to a file the service does not read: stop, and check step 4's attach. A clerk
entering outcomes gets `jyotish clerk add <name>` the same way.

**9. A reading to review.** Make one on the site (the form at `https://<your app>.fly.dev/`), or from Terminal:

```bash
curl -s -X POST https://$APP.fly.dev/readings -H 'Content-Type: application/json' -d '{"date": "2001-03-12", "time": "10:10:25", "tz": "Asia/Kolkata", "lat": 28.1989, "lon": 76.617, "node": "mean", "place": "Rewari, Haryana", "question": "How will my career go, and when is the best time for a job change?", "depth": "astrologer"}'
```

It answers with an `id`. When the reading is done (a few minutes; the site shows it, or
`curl -s https://$APP.fly.dev/readings/<id>` says `"status": "done"`), the reviewer's link is:

```
https://<your app>.fly.dev/review/<id>
```

The page asks for the token once per browser tab. The judge page is the same link with `?mode=blind`.

**10. A blind comparison.** Two readings of the same birth data and question at different settings: post
the reading above twice, once with `"writer_effort": "medium"` and `"depth": "astrologer"`, once with
`"depth": "full"`, and send the reviewer

```
https://<your app>.fly.dev/compare/<first id>/<second id>
```

**Day to day.**

- What it has cost: `curl -s -H "Authorization: Bearer <your owner token>" https://$APP.fly.dev/costs/daily`
- Revoke a reviewer: `fly ssh console -a "$APP" -C "jyotish reviewer revoke judge-1"` (then `add` for a new token)
- The logs: `fly logs -a "$APP"` (JSON lines; no birth data is ever written to them)
- A new version: `git pull`, then `fly deploy -a "$APP"` (the database is migrated as the service starts)
- Readings are rate-limited to 30 per client per hour and 300 a day; to change it,
  `fly secrets set JYOTISH_READINGS_PER_HOUR=<n> JYOTISH_READINGS_PER_DAY=<n> -a "$APP"`

**Backups on Fly.** Managed Postgres backs the database up automatically (the retention is the plan's: see
the cluster's page in the Fly dashboard). For a copy of your own, the service's image has the backup
script; this writes a dump to the app's volume and keeps 14 days of them:

```bash
fly ssh console -a "$APP" -C "/app/scripts/pg_backup.sh"
```

## One host of your own, with Caddy

On a Linux server with Docker, a domain whose A record points at it, and ports 80 and 443 open:

```bash
git clone https://github.com/Geek4ray/jyotish.git && cd jyotish && cp .env.example .env
```

Fill in `POSTGRES_PASSWORD`, `ANTHROPIC_API_KEY`, `JYOTISH_SOURCE_URL` and `JYOTISH_DOMAIN` in `.env`, then:

```bash
docker compose --profile host up -d --build
```

Caddy obtains the certificate for the domain and serves the service at `https://<domain>/`; Postgres and
the service are reachable only from the host. The `backup` service runs `scripts/pg_backup.sh --nightly`:
a `pg_dump` at 03:00 UTC every night into `./backups`, each kept 14 days (`RETENTION_DAYS` in `.env`).
Copy `./backups` off the host now and then; a backup on the same disk is not a backup against the disk.
Tokens: `docker compose exec app jyotish reviewer add judge-1`. Restore a dump into an empty database:
`docker compose exec -T db pg_restore --no-owner -U jyotish -d jyotish < backups/<file>.dump`.
