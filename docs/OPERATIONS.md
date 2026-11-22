# Solacen organic system — 22 November 2026

## Latest expansion — supersedes the initial S5-only batch below

Live accounts reverified: Instagram @solacenstore and the Solacen Facebook Page. The library now holds 60 daily concepts: 24 S5 concepts, three for each of the other eleven products, and three comparisons. All twelve full product descriptions and existing featured images were retrieved from Shopify. Store design, prices, shipping and offers were preserved.

New assets: two AI lifestyle photographs (PageGlow reading corner and DawnRise winter morning), 36 reusable editorial layouts, distinct hook covers, and six original-instrumental music Reels. Product photographs are fitted whole into native layouts; no product geometry or controls are altered. Reels are 1080×1920, 30fps H.264/AAC slideshows, 11.3 seconds, with gentle dissolves. Audio is an original synthesized ambient composition, without samples, vocals or a claim to reproduce built-in device sounds. It is not a trending commercial song. No paid video credits or model API were used.

Fourteen existing scheduled posts were edited IN PLACE: seven each platform for 23–29 November. Dates, IDs and automatic publishing were preserved; no duplicates. API readback confirmed four music-Reel destinations in that week and optional Instagram self-disclosure OFF on all seven scheduled posts. The already published introduction is historical and was not edited. Meta can still apply its own labels; retain any required disclosure on future realistic synthetic video/audio.

Native music on photo/carousel posts requires manual completion in Buffer. Use automatic music Reels alongside silent carousels, never notification publishing for the daily system. Accepted video assets are not yet proof of scheduled Reel publication; observe at due time. Facebook links match pictured products/variants; comparisons lead to the collection. Instagram still uses the existing profile link, with limited post-level attribution. Campaign UTM: solacen_organic_2026.

Strategy: specific visual hooks, recognisable products, useful feature/choice carousels, evening routines and gifting without arrival promises. Instagram serves discovery and profile exploration; Facebook uses explanatory copy and product links. Views, saves and shares are early signals; Shopify visits, carts, real orders and contribution decide commercial value. Posting times and hook patterns remain hypotheses. Compare platforms and products separately; raw totals across unlike formats are not a controlled test.

The seven-day cloud-refilled Buffer reserve remains active. The first batch now lasts 60 days before evergreen retrieval, with a 60-day concept cooldown. This is batch production, not daily fresh AI photography. Thirteen local scheduler tests pass, including product-specific destinations, automatic video payloads and optional/required disclosure. The weekly local Codex review should replenish the batch from real performance; publishing itself remains external and independent of this chat/laptop.

Sources checked for this expansion:
- https://support.buffer.com/en-us/articles/using-instagram-with-buffer-YSjg2dXFV8
- https://support.buffer.com/en-us/articles/adding-music-stickers-and-other-effects-to-instagram-and-tiktok-posts-G5QrWfQL4k
- https://about.fb.com/news/2024/04/metas-approach-to-labeling-ai-generated-content-and-manipulated-media/

The following sections retain the original implementation history; the expansion above controls where counts, cycle length, media or campaign identifiers differ.

## Operating contract

Daily organic publishing is authorized to @solacenstore Instagram and the Solacen Facebook Page, with no daily content approval. No ad spend, subscription purchase, model API spending, new discounts, supplier orders or sensitive customer data transmission is part of this system. Reuse product descriptions and approved imagery. Do not manufacture customer testimonials or imply S5 is a neck massager.

## Architecture selected

AI-assisted batch content → persistent JSON library → GitHub Actions (three checks daily) → Buffer free API → Instagram + Facebook automatic publishing → per-destination post IDs and metrics → health report.

The content library holds 30 concepts with separate platform captions. Four new AI compositions and the three existing model cards provide the first image/carousel batch. Files are JPEG-encoded for publishing without creatively altering the approved source images. A seven-day rolling queue stays below Buffer's ten-pending-post limit per channel. GitHub runs independently of ChatGPT and the laptop. Buffer publishes already scheduled posts even between GitHub runs.

### Why this stack

| Option | Finding and decision |
|---|---|
| Buffer Free + GitHub | Selected: two brand channels fit within three free channels; API available. Cloud refills avoid the ten-post queue limitation. |
| Native Meta Business Suite | Free and useful for finite batches, but this session hit redirect failures. A finite queue alone would not replenish itself. |
| Direct Meta APIs | Technically viable; requires developer app, permissions, token lifecycle and asset hosting. More setup and maintenance for this small brand than Buffer's established connection. |
| Make Free | Possible, but adds another account and operation budget; not needed when a short script suffices. |
| Self-hosted n8n | Local hosting would stop with the laptop; cloud hosting adds operations/cost. No extra deployment selected. |
| Built-in image generation | Selected for batches using existing AI access. No paid image API activated. |
| Canva/free design tools | Useful for manual design, but not an unattended generation service by themselves. |
| Image APIs | Optional future improvement only after a bounded cost is approved; the report's model names and cent-per-image examples are not a verified quote. |

## Cadence and measurement

First scheduled day is 23 November. Proposed pilot times are 14:15 New York for Instagram and 14:35 for Facebook, corresponding to 21:15/21:35 Helsinki in November. These are a starting hypothesis, not algorithm-optimal times. Exact UTC times and daylight saving are calculated from an IANA timezone.

Instagram: product recognition in first frame; restrained hooks; useful colour/feature carousels; saves/shares as diagnostics; clear profile CTA. Facebook: same core assets, explanatory captions and clickable, uniquely tagged product links. No engagement bait, fabricated reviews or claim of guaranteed virality. Organic distribution cannot be geographically guaranteed.

Facebook links use utm_source=facebook, utm_medium=organic_social, campaign=s5_organic_2026 and a post ID in utm_content. Instagram feed captions are not assumed to have clickable links. Use a persistent profile link with utm_source=instagram, utm_medium=organic_social and utm_content=profile; do not pretend it identifies the exact viewed post. Buffer Shop Grid metadata can later associate posts with links where enabled; it does not make a normal Instagram caption URL clickable.

Use Shopify as order/revenue source of truth. Instagram/Facebook reach and likes are diagnostics. Export/report: tagged sessions → carts → checkouts → orders → contribution after landed product/gift/shipping, fees, refunds and tool costs. Do not count the old simulated Purchase event as a sale. Baseline first paid experiment is historical: EUR30.77, nine link clicks and zero customer sales; do not reuse it as an organic conversion forecast.

## Retries, state and account maintenance

- Every destination has its own identity: channel + exact caption + scheduled time.
- Read remote state before adding posts; preserve successful destinations.
- Persist write intent before sending. Network-uncertain creation is reconciled on the next run and is never blindly repeated.
- Reads retry transient failures up to three attempts. Definitive creation refusals can be retried on the next scheduler run.
- Confirmed transient publishing errors retry the SAME Buffer post ID, at most twice, within 24h. Invalid media, permissions, authentication or uncertain retry outcomes are flagged, not bypassed.
- Buffer manages the connected Meta token flow. A revoked/expired connection can still need a one-time owner reconnect. Never promise permanent, maintenance-free credentials.
- State is saved before surfacing workflow failure. GitHub concurrency prevents overlapping publisher runs. The rolling seven-day reserve tolerates a temporary scheduler interruption.
- API key stays in GitHub Actions secret BUFFER_API_KEY; local .buffer-key is ignored and excluded from deployment. Do not upload the Documents key text file.
- Pause: set enabled=false in config.json to stop refills; pause BOTH Buffer channel queues to stop already scheduled posts. Disabling GitHub alone does not cancel Buffer posts.

## Content replenishment and feedback limits

The first 30 days use the written batch. An evergreen fallback rotates the library at a 30-day concept cooldown with altered caption framing, without a fixed end date. This is retrieval/recomposition, not daily new model-generated photography. It keeps delivery running but is not the preferred long-term creative strategy. Produce new batches from actual objections and commercial-intent evidence in the weekly review. After twelve evergreen cycles, framing can repeat; do not describe the fallback as endlessly original. No monthly invoice or generation purchase is authorized automatically.

Performance ingestion is automatic where Buffer returns metrics; API fields can be null or not available on a plan. Buffer documents that some unreported metrics default to zero; absence of an available metric is not proof of zero engagement. Shopify conversion aggregation still needs store analytics access in the recurring runtime; no private Shopify API token is assumed to exist just because this chat's connector works.

A weekly Codex review is configured for Mondays at 19:00 local time, using the connected Shopify tools and private local reports. This can enrich the next content batch without daily owner approval, but depends on local Codex/computer availability. The cloud publisher and its Buffer metric collection do not depend on that review being online. Instagram's existing profile website link remains; its post-level attribution is coarse. Do not claim the biography link was changed to a post-specific UTM.

The initial system does not automatically rewrite live product prices, invent margin inputs or spend to pursue a high-engagement post. Creative selection should use contribution/purchases first, then carts and qualified visits; do not add euros, counts and rates into the report's unnormalised weighted score. With weak samples, label the uncertainty and keep exploration.

## Roadmap

| Horizon from activation | Action and decision |
|---|---|
| 14 days | Verify daily delivery on both channels; compare after-work, feature, colour, audio and offer concepts. Fix broken links, low clarity and actual customer objections. No arbitrary follower target. |
| 30 days | Review Shopify organic sessions and purchase funnel, replace estimated order costs with actual invoices, generate the next original batch. Allocate more posts to promising concepts without declaring low-sample winners. |
| 60 days | Develop additional original product-use explanations from questions; compare single image versus carousel and qualified traffic by platform. Verify fulfilled-order contribution and support workload. |
| 90 days | Keep formats that contribute to orders and margin; refresh the original library rather than depending on evergreen rotation. Consider a finite paid experiment only with separate affordable-loss budget approval. Organic performance is evidence, not a paid-performance guarantee. |

## Research reconciliation

Read the supplied complete report and all 14 video assessments. This does not mean 14 full videos were independently watched or creator revenue independently verified. Two entries have unresolved exact IDs in the report. Keep title-level assessment provenance and avoid inventing missing sources.

Documented: separate recommendation/ranking surfaces; personalised discovery can reach nonfollowers; original-content emphasis; official publishing APIs; Buffer queue limits and free API. Hypotheses: carousels will outperform for Solacen, a daily cadence will produce sales, ideal posting hour, creator hook formulas and automation-driven revenue claims. Corrected: S5 is an EYE massager, not a shoulder/neck treatment. Organic acquisition still has fulfilment, refund, fixed-store and time costs. A 30/90-day posting count does not guarantee enough observations for a reliable winner.

Sources checked 22 November 2026:
- https://about.fb.com/news/2026/03/rewarding-original-creators-on-facebook/
- https://about.fb.com/news/2026/10/introducing-your-algorithm-facebook/
- https://buffer.com/api
- https://support.buffer.com/en-us/articles/how-many-posts-can-i-schedule-in-advance-Kmy2IEecqm
- https://developers.buffer.com/reference.html
- https://developers.buffer.com/guides/rest-migration.html
- https://docs.github.com/en/actions/how-tos/manage-workflow-runs/disable-and-enable-workflows

## Setup status

Read activation-status.json and state/health.json for the latest verified state. A passing local test or connected Instagram is not proof that the cloud workflow is deployed or Facebook is connected. Keep remaining connection/deployment steps explicit.
