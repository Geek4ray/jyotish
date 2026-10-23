# The reading service (SPEC Tech stack, Ops): the engine, the API and the website in one image.
# Configuration comes from the environment only (docs/deploy.md): JYOTISH_DATABASE_URL,
# ANTHROPIC_API_KEY, JYOTISH_CANDIDATE_RULES, JYOTISH_CACHE_DIR, JYOTISH_SOURCE_URL. No key is
# baked in. Swiss Ephemeris is AGPL-3.0: a deployment offers its users the source (docs/deploy.md).

FROM python:3.12-slim AS build
# pyswisseph builds from source: a compiler in this stage only.
RUN apt-get update && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /src
COPY pyproject.toml README.md ./
COPY src ./src
RUN pip wheel --no-cache-dir --wheel-dir /wheels ".[api]"

FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 \
    JYOTISH_DATABASE_URL=sqlite:////data/jyotish.db \
    JYOTISH_CACHE_DIR=/data/cache \
    JYOTISH_CANDIDATE_RULES=/data/candidate_rules.jsonl
RUN useradd --create-home --uid 1000 jyotish && mkdir -p /data && chown jyotish /data
WORKDIR /app
COPY --from=build /wheels /wheels
RUN pip install --no-cache-dir /wheels/*.whl && rm -rf /wheels
# The engine finds its rules, website and examples beside its source (rules.RULES_DIR, api.REPO),
# so the checkout is installed in place.
COPY pyproject.toml README.md ./
COPY src ./src
COPY rules ./rules
COPY web ./web
COPY examples ./examples
RUN pip install --no-cache-dir --no-deps -e . && chown -R jyotish /app
USER jyotish
VOLUME /data
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s \
    CMD python -c "import os, urllib.request; urllib.request.urlopen(f'http://127.0.0.1:{os.environ.get(\"PORT\", \"8000\")}/health', timeout=4)"
# One process: the reading jobs run on its threads and the rate limit counts in its memory. $PORT is
# the host's when it sets one (Railway does). Uvicorn's access log is off: it prints query strings,
# and /places?q= carries a birthplace; the service logs requests itself, without them.
CMD ["sh", "-c", "exec uvicorn jyotish.api:app --host 0.0.0.0 --port ${PORT:-8000} --no-access-log --proxy-headers"]
