# OKF Examples

## Spec-Minimal Concept

```markdown
---
type: Reference
---

This concept is valid in OKF v0.2 because it has parseable frontmatter and a
non-empty `type`.
```

## Provenance and Trust

~~~markdown
---
type: Metric
title: Gross Revenue
description: Total recognized revenue before refunds and discounts.
tags: [finance, revenue]
status: stable
generated: {"by": "process:catalog-refresh", "at": "2026-06-29T10:00:00Z"}
verified: {"by": "human:finance-owner", "at": "2026-06-29T11:00:00Z"}
stale_after: 2026-09-29T00:00:00Z
sources:
  - id: revenue-policy
    resource: https://example.com/finance/revenue-policy
    title: Revenue recognition policy
    last_modified: 2026-06-15T00:00:00Z
usage_window: {"from": "2026-06-01T00:00:00Z", "to": "2026-06-30T00:00:00Z"}
---

# Definition

Gross revenue follows the approved recognition policy.[^revenue-policy]

[^revenue-policy]: Revenue recognition policy
~~~

## Attested Computation

~~~markdown
---
type: Attested Computation
title: Gross revenue
runtime: postgres
parameters: [{"name": "fiscal_year", "type": "integer", "required": true}]
generated: {"by": "process:catalog-refresh", "at": "2026-06-29T10:00:00Z"}
---

# Computation

```sql
select sum(gross_revenue_usd)
from marts.revenue_daily
where fiscal_year = :fiscal_year;
```
~~~

## Index File

```markdown
# Tables

* [Orders](tables/orders.md) - One row per completed customer order.
* [Customers](tables/customers.md) - Customer profile and lifecycle attributes.
```

## Log File

```markdown
# Directory Update Log

## 2026-06-29
* **Creation**: Added [Orders](/tables/orders.md).
```
