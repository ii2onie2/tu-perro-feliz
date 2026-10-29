# Wikimedia candidate visuals — 2026-10-29 secondary slots

Status: CANDIDATE_NOT_APPROVED. These are **not** approved assets and are intentionally not referenced from `content/2026-10-29-educacion.json` or `content/2026-10-29-sabias.json`. Keep both research JSONs as `RESEARCH_DRAFT_UNAPPROVED` and media `NOT_SELECTED` until full checks pass.

Candidate research on Commons file-description pages, 2026-10-29:

| Slot | Exact Commons title | Author; displayed license | Evidence / editorial limitation |
| --- | --- | --- | --- |
| 16:00 waiting at doorway | `File:Brown dog with curly hair sitting and waiting at the door with woman in the background.jpg` | Shixart1985; CC BY 2.0, https://creativecommons.org/licenses/by/2.0 | The photo depicts a dog waiting near a doorway; **not** evidence that the proposed training method was performed or effective. 12.14 MB below the current media size cap, but download/integrity audit not run. |
| 19:00 tail language | `File:Dog tail.jpg` | Primestarsupply; CC BY-SA 3.0, https://creativecommons.org/licenses/by-sa/3.0 | Close-up of a tail, not an example of tail *wagging* or a dog's emotional state; cannot depict happiness or anxiety from this image. The file page credits original `Spotted_ring_tail_dog_2014-05-04_21-23.jpg`. |

File pages:
- https://commons.wikimedia.org/wiki/File:Brown_dog_with_curly_hair_sitting_and_waiting_at_the_door_with_woman_in_the_background.jpg
- https://commons.wikimedia.org/wiki/File:Dog_tail.jpg

Prerequisites, all still **pending**:
1. Call Commons API for original imageinfo.extmetadata; confirm machine-readable allowed license, exact author/credit and clean source URL, download under controlled `media/`, SHA256 compare; run `scripts/audit_commons_licenses.py` / `scripts/fetch_media.py` with an isolated copy, never write straight into production content before approval.
2. Review image relevance and legal attribution/modified-image notice; for BY-SA ensure license compatibility with video distribution, do not imply the still photo proves body-language state.
3. Complete editorial verification of Dogs Trust/Blue Cross source claims and anti-duplicate check; execute canonical validator, media gate, isolated render and visual QC.
4. Promotion requires explicit content status and rights verification supported by evidence; no silently fabricated or old content.

No asset imported or authorized; no media integrity hash or render success claimed. No posting.
