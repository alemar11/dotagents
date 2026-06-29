# OKF Examples

## Spec-Minimal Concept

```markdown
---
type: Reference
---

This concept is valid in `spec` mode because it has parseable frontmatter and a
non-empty `type`.
```

## Reference-Agent-Compatible Concept

~~~markdown
---
type: Metric
title: Gross Revenue
description: Total recognized revenue before refunds and discounts.
tags: [finance, revenue]
timestamp: 2026-06-29T10:00:00Z
---

# Examples

```sql
select sum(gross_revenue_usd) from marts.revenue_daily;
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
