# Solacen daily organic publishing

See [operations and strategy](docs/OPERATIONS.md), [30-post queue](queue.json), [current configuration](config.json), and [activation evidence](activation-status.json).

Expected incremental recurring cost: **EUR0** for the selected Buffer Free / public GitHub Actions / batch-image route within current free limits. Existing Shopify, domain, mailbox and AI-plan costs remain separate. No paid image API, n8n host, Make plan or ad expense is activated.

## Run

`python publisher.py` validates the library and prints a dry-run plan without publishing.

`python publisher.py --discover` checks Buffer organization/channels without publishing.

`python -m unittest discover -s tests -v` runs ten tests for duplicate prevention, partial failures, unknown write outcomes, queue limits, timezone/UTMs, the disabled guard, safe retries, overdue detection and ongoing evergreen coverage.

`python publisher.py --write` uses the exact configured accounts only when enabled=true. Reads BUFFER_API_KEY from environment, falling back to ignored local .buffer-key. Never print the key. See operations for stopping both queue refill and already scheduled posts.

## Deployment

Deploy publisher.py, config.json, product.json, queue.json, tests/, public JPEG assets/, docs/OPERATIONS.md and .github/workflows/organic.yml. Exclude .buffer-key, the supplied report, private financial records and downloaded documentation. Public assets are intentional marketing content; secrets belong in GitHub Actions secrets. Run the workflow manually once and inspect Buffer post readbacks before claiming activation.

No income or automatic audience growth is guaranteed. The system is a low-cost experiment with delivery records and accountable maintenance.

## Verified activation — 22 November 2026

- Both brand channels connected and unpaused.
- First introduction actually sent to [Instagram](https://www.instagram.com/p/DgDhl-JF1b-/) and [Facebook](https://www.facebook.com/122123202141501800/posts/122123203737501800).
- Seven automatic future posts per platform were read back from Buffer; first routine posts are due 23 November at 21:15 and 21:35 Helsinki/Kyiv time.
- Cloud refill and state persistence succeeded in [run 45058999595](https://github.com/Acryxis/solacen-organic/actions/runs/45058999595).
- Weekly organic review is active in Codex. Unlike the GitHub/Buffer publisher, that review depends on local Codex availability. It uses private Shopify evidence rather than publishing financial data to this repository.
- The initial library is thirty distinct concepts using four newly generated photographs and existing product cards. Evergreen fallback retrieves these assets with varied framing; it does not claim daily new AI photography.

Instagram's existing profile store link still works. Per-post Instagram attribution is limited; feed caption links are not treated as clickable. Facebook links carry individual post UTMs. Actual sales and contribution remain outcomes to measure, not a setup result.
