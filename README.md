# Solacen daily organic publishing

See [operations and strategy](docs/OPERATIONS.md), [30-post queue](queue.json), [current configuration](config.json), and [activation evidence](activation-status.json).

Expected incremental recurring cost: **EUR0** for the selected Buffer Free / public GitHub Actions / batch-image route within current free limits. Existing Shopify, domain, mailbox and AI-plan costs remain separate. No paid image API, n8n host, Make plan or ad expense is activated.

## Run

`python publisher.py` validates the library and prints a dry-run plan without publishing.

`python publisher.py --discover` checks Buffer organization/channels without publishing.

`python -m unittest discover -s tests -v` checks duplicate prevention, partial failures, unknown write outcomes, queue limits, timezone/UTMs and the disabled guard.

`python publisher.py --write` uses the exact configured accounts only when enabled=true. Reads BUFFER_API_KEY from environment, falling back to ignored local .buffer-key. Never print the key. See operations for stopping both queue refill and already scheduled posts.

## Deployment

Deploy publisher.py, config.json, product.json, queue.json, tests/, public JPEG assets/, docs/OPERATIONS.md and .github/workflows/organic.yml. Exclude .buffer-key, the supplied report, private financial records and downloaded documentation. Public assets are intentional marketing content; secrets belong in GitHub Actions secrets. Run the workflow manually once and inspect Buffer post readbacks before claiming activation.

No income or automatic audience growth is guaranteed. The system is a low-cost experiment with delivery records and accountable maintenance.
