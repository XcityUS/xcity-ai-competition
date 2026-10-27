# Pilot area

Two parts, both in the south-west parcel, both planned by XCITY. **Neither is open to design.**

| File | What |
|---|---|
| `pilot_area.geojson` | Three agrivoltaic fields (01–03), 13.9 km² of outline, 1,000 arrays each |
| `pilot_living_area.geojson` | The living quarter, phase 1: 2.48 km² in the south of the south-west parcel, about 11 km east of the fields. Housing in the west, estates in the east. Only its outline is published |

## What a scheme must respect

- Nothing may be built inside either part of the pilot area, and neither may be redrawn. The self-check tests your geometry against both.
- The living quarter is the city's first neighbourhood. How the city meets it — streets, water, services, the next quarters around it — is for the scheme to answer.
- Under the arrays is a symbiotic system already running: jojoba, rosemary, forage cactus and alpaca. Its layout is fixed.
- Tall and climbing crops — pistachio, olive, vine — cannot enter the arrays; where they go and how much is for the scheme to propose.
- The pilot area already exists. The city grows beside it: how that edge is organised, and how it moves as the city grows, is the scheme's to answer.

## Fixed-context representation and checks

Agrivoltaic outlines: `structure.system = agri_production`; land-use context labels `agriculture` or `energy`. Living-quarter outline: `structure.system = living`; context labels `residential`, `mixed_use`, `civic`, `open_space`, `infrastructure` or `agriculture` for estate agriculture. The living quarter is not an agricultural field merely because both parts belong to the pilot. Only its outline is published: do not invent internal boundaries, existing building stock or measured capacity. Show it as fixed sourced context, state how its land and any assumed capacity enter your accounts, and design connections outside it. New submitted buildings remain prohibited in both parts. G9 checks land-use compatibility separately and lists structure-label conflicts for content review.

## Provenance and limits

Source: `SRC-PILOT`; acquisition date and measured positional accuracy are not supplied. These are fixed competition outlines, not a field survey or a comprehensive as-built inventory. Issued statuses differ: fields are described as built first by XCITY; the living outline is described as planned by XCITY. Do not infer verified completion dates, internal layouts or operating capacities from either outline. Record assumed capacities separately. See `../evidence-index.json`.
