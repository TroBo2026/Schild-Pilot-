# International sign taxonomy – design proposal

## Scope and current status

Schild Pilot is intended to become a free, global learning and research prototype. **The current UI, lesson pack and classifier are German-only.** This document defines a cautious foundation for adding jurisdictions; it does not claim that international recognition is implemented.

## Separate four concepts

Do not use one global numeric sign ID as both visual identity and legal meaning.

1. **Visual observation** – what is visible in the photo: shape, colors, pictogram/text, supplementary plate, condition, viewpoint and crop.
2. **Visual class** – a reusable description of a sign design or family. Similar-looking signs may remain separate when important details differ.
3. **Jurisdictional rule** – what the sign means under a specific country's/region's traffic rules, including exceptions and effective dates.
4. **Localized explanation** – a human-reviewed explanation in a language, linked to the jurisdiction and legal source. Translation alone is not legal verification.

## Proposed record fields

A future machine-readable catalog should use stable, explicit fields instead of silently reusing German class numbers:

| Field | Meaning |
|---|---|
| `visual_class_id` | Stable ID for the reviewed visual design/family |
| `visual_description` | Shape, colors, symbol/text and distinguishing details |
| `variants` | Known design variants; never collapse them without review |
| `jurisdiction` | Country/region code and scope |
| `rule_id` | Jurisdiction-specific rule identifier |
| `meaning` | Human-reviewed legal/educational meaning |
| `legal_source` | Official source, article/section and URL |
| `source_version` | Source edition or effective date |
| `verified_at` | Date the mapping was reviewed |
| `locale` | Explanation language |
| `translation_source` | Human review or translation provenance |
| `supplementary_signs` | Associated plates/conditions, if known |
| `status` | `verified`, `provisional`, or `unknown` |

This is a design proposal, not an implemented schema or legal database.

## Mapping rules

- A visual match must not automatically imply a universal legal meaning.
- Identical or similar designs across countries can have different rules; preserve jurisdiction-specific mappings.
- Text, arrows, colors, plates and local variants may change the class or interpretation.
- If the jurisdiction or variant cannot be established, show the visual description and **unknown/uncertain meaning**; do not guess.
- Keep visual classification separate from full-image detection. Detection locates candidate signs; classification describes a crop; jurisdictional lookup supplies a reviewed explanation.
- Never present model score as a calibrated probability or as a safety guarantee.

## Expansion gate for each jurisdiction

Before adding a country/region to lessons or evaluation:

- [ ] Official traffic-law source located and linked.
- [ ] Sign catalog/version and effective date documented.
- [ ] Visual examples and annotations have explicit usage rights.
- [ ] Class/variant mapping reviewed; ambiguous and unknown cases retained.
- [ ] Explanations are reviewed in the target language.
- [ ] Train/validation/test provenance and scene/location separation documented.
- [ ] Evaluation reports per-class and per-jurisdiction results, not only a global average.
- [ ] Dataset/license admission checklist completed.
- [ ] UI clearly identifies the selected jurisdiction and limitations.

## Evaluation for global coverage

Report, at minimum, per jurisdiction and per class: sample count, precision/recall (for detection), classification accuracy, accepted-prediction coverage, errors and abstentions. Where feasible, hold out scenes, locations or regions rather than random neighboring frames. A country with no validated data must be listed as unsupported, not hidden in a global metric.

## Incremental path

1. Keep the existing German lesson pack and classifier unchanged while the schema is reviewed.
2. Add one second jurisdiction only after official sources and image rights are verified.
3. Build a small, reviewed lesson pack and tests for mapping/unknown handling.
4. Later, evaluate cross-jurisdiction visual recognition separately from legal-meaning lookup.
5. Only after real-image evaluation consider on-device export and offline lookup.

No data collection, scraping, training, model-weight upload or paid service is authorized by this plan.
