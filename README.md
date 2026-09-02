# Awesome Agent APIs

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

A community-maintained catalog of third-party API tools — SEO, enrichment, social,
scraping, and beyond. Anyone can add a provider they already use with a single PR:
one YAML file, no code, no access to any private system.

This is a **reference catalog, not a live proxy**. Entries here are documentation —
base URL, auth shape, endpoints, pricing — for tools you call with your *own* API
key/account. Nothing in this repo executes a call on your behalf.

## Why this exists

The tools worth calling from an agent are scattered across dozens of vendors, each
with its own docs, auth quirks, and pricing page — and most of the useful ones sit
behind a subscription nobody buys for a single call (Semrush $139/mo, Moz $99/mo,
Crunchbase $99/mo), or behind docs vague enough that you don't know what a call
actually costs or returns until you've already signed up. This catalog puts the
facts that matter — auth shape, real pricing, a captured example response — in one
place, in one consistent shape, so an agent (or a person) can scan `providers/`
and know exactly what a tool needs before ever opening its docs.

## Quickstart

```bash
ls providers/                      # browse what's catalogued
cat capabilities.yaml              # browse by category instead — seo.*, people.*, social.*, ...
cat providers/<provider>.yaml      # base_url, auth, endpoints, pricing for one tool
```

## Add a tool

1. Copy `providers/_TEMPLATE.yaml` to `providers/<your-provider>.yaml`.
2. Fill it in against the provider's own public docs — see `CONTRIBUTING.md` for the
   full checklist, including the one non-negotiable step: **get a real key and
   confirm at least one endpoint actually works before opening the PR.** A schema
   that was never called against the real API is not accepted.
3. Run the validator locally:
   ```bash
   python3 scripts/catalog_validate.py providers/<your-provider>.yaml
   ```
4. Open a PR. A maintainer reviews the entry and, once confirmed, flips its
   `status` to `verified`.

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for the full guide, including selection
heuristics (what gets accepted vs. rejected) and common gotchas per auth style.

## Entry statuses

- `draft` — submitted, not yet independently verified by a maintainer.
- `verified` — a maintainer confirmed the entry against a real key and a real call;
  `examples/<id>.json` holds a real captured response.

Treat `draft` entries as a starting point, not a guarantee — verify before relying
on one yourself.

## Scope

- **In scope:** any tool with a self-serve API key (no sales call, no partner
  application) — SEO/backlinks, keyword/rank data, people/company enrichment,
  scraping, social/publishing, ads, market data, and similar.
- **Out of scope:** anything requiring a sales process, an enterprise-only tier
  with no public pricing, or a tool that's deprecated/no longer self-serve.

## Related Projects

- [MuAPI](https://muapi.ai) — Unified API for image, video, and audio generation across hundreds of AI models.
- [MuAPI agent skills docs](https://muapi.ai/docs/agent-skills) — How MuAPI's own skills/tool-catalog surface works for agents.
- [MuAPI access keys](https://muapi.ai/access-keys) — Create a key if you're pairing this catalog with MuAPI's own generative-media API.

## License

MIT — see [LICENSE](LICENSE).
