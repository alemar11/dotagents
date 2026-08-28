---
name: eli5
description: Create a picture-first beginner explainer for a topic, code path, design tradeoff, or incident using large visuals and very few words. Use when the user invokes $eli5, asks for an explain-like-I-am-five explanation, or wants a dead-simple visual explanation.
---

# ELI5

Turn the requested topic into an accurate visual explainer for someone with no
prior knowledge.

## Ground the explanation

- Preserve the user's requested topic, language, audience, scope, and format.
- When the request concerns code, a design decision, or an incident, inspect
  the available evidence before explaining it. Do not invent intent, history,
  or causality.
- Simplify the vocabulary and presentation without changing the important
  relationships. State material uncertainty or omitted nuance plainly.

## Create the explainer

- Deliver one self-contained HTML visual explainer. Show it directly in the
  conversation when the environment supports rendered HTML; otherwise save a
  standalone `.html` artifact and provide a link to it.
- Use big, clear visuals and very few words. Prefer simple shapes, arrows,
  icons, and restrained motion over paragraphs or decorative detail.
- Use only as many panels as the topic needs, with one idea per panel and a
  clear reading order. Choose a visual structure that fits the subject, such
  as a flow, before-and-after comparison, system map, or cause-and-effect
  sequence.
- Start with the central takeaway, introduce unfamiliar actors before showing
  their interactions, and finish with one compact memory hook.
- Keep labels, colors, and metaphors consistent. Make the explainer readable
  on narrow and wide screens with sufficient contrast and reduced-motion
  support.
- Use plain, age-neutral language. Explain simply without talking down to the
  user or pretending they are literally a child.

Do not substitute a dense article, conventional slide deck, or code dump for
the visual explainer. Keep any necessary evidence links compact and secondary
to the explanation.
