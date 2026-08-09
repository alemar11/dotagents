# PostgreSQL SQL Capability Router

Load this router only when requested SQL may depend on the PostgreSQL major.
It covers high-impact capability families, not every release-note item.

## Selection contract

1. Determine the oldest PostgreSQL major that must execute the SQL. When a live
   connection is authorized, prefer:

   ```sql
   show server_version;
   select current_setting('server_version_num')::integer;
   ```

   Otherwise inspect the project's image, CI matrix, deployment configuration,
   or migration policy. If environments differ, target the oldest one unless
   the caller narrows the scope.
2. Select one capability below and load only its linked guide sections. Do not
   read the complete release series for an ordinary SQL task.
3. For an unlisted feature, search the release catalogs by its exact term or
   check the versioned official documentation.
4. For an upgrade review or broad "what changed" request, load only the
   catalogs between the source and target majors.
5. Label version-dependent output, such as `PostgreSQL 17+`, and include a
   fallback when an older or unknown target is possible.
6. Check extension versions independently from core PostgreSQL. Recommend a
   maintained minor release when correctness depends on post-`.0` fixes.

## Inclusion rule

Keep a family here only when it changes the SQL or recommended pattern, has an
easy-to-misremember version boundary, and carries a semantic, concurrency,
locking, privilege, replication, or operational consequence. Leave convenience
functions in the release catalogs.

## Capability routes

- **DML, `MERGE`, and `RETURNING` — 15/17/18/19 development.** Preserve
  snapshot, locking, trigger, and retry semantics in fallbacks. Load
  [PG15 `MERGE`](postgres-sql-15.md#batch-synchronization-with-merge),
  [PG17 action reporting](postgres-sql-17.md#expanded-merge-and-action-reporting),
  [PG18 `OLD`/`NEW`](postgres-sql-18.md#explicit-old-and-new-in-dml-returning), or
  [PG19 get-or-create](postgres-sql-19.md#on-conflict-do-select-with-returning-preview).

- **SQL/JSON — 14/16/17.** Older targets use `jsonb` operators, builders, path
  functions, and lateral record expansion; preserve null, error, and coercion
  behavior. Load [PG14 subscripting](postgres-sql-14.md#jsonb-subscripting),
  [PG16 construction/validation](postgres-sql-16.md#sqljson-constructors-and-validation),
  or [PG17 querying/projection](postgres-sql-17.md#json_table-and-sqljson-query-functions).

- **Recursive and graph queries — 14/19 development.** Fall back to joins or
  recursive CTEs with explicit order and visited paths. SQL/PGQ is a logical
  relational read model, not Cypher or a native graph store. Load
  [PG14 traversal](postgres-sql-14.md#recursive-cte-search-order-and-cycle-detection)
  or [PG19 SQL/PGQ](postgres-sql-19.md#sqlpgq-property-graphs-preview).

- **Generated, temporal, and integrity constraints — 15/17/18/19 development.**
  Fallbacks include partial/expression indexes, recreated generated columns,
  views, exclusion/custom constraints, and transactional range splitting. Load
  [PG15 integrity](postgres-sql-15.md#unique-null-values-with-nulls-not-distinct),
  [PG17 generated expressions](postgres-sql-17.md#changing-a-generated-column-expression),
  [PG18 generated columns](postgres-sql-18.md#virtual-generated-columns),
  [PG18 temporal integrity](postgres-sql-18.md#temporal-keys-and-foreign-keys), or
  [PG19 temporal DML](postgres-sql-19.md#for-portion-of-temporal-dml-preview).

- **`COPY` and ingestion — 15/16/17/18/19 development.** Older targets need
  client validation or text staging. Define bounded rejection, observability,
  and retry policy before accepting malformed rows. Load
  [PG15 headers](postgres-sql-15.md#validated-csv-headers),
  [PG16 defaults](postgres-sql-16.md#copy-from-default-value-sentinels),
  [PG17 tolerant input](postgres-sql-17.md#error-tolerant-copy-from),
  [PG18 reject limits](postgres-sql-18.md#bounded-bad-row-tolerance-in-copy), or
  [PG19 JSON/`set_null`](postgres-sql-19.md#copy-json-and-field-level-error-handling-preview).

- **Partitioning and table rewrites — 14/15/19 development.** Use maintenance
  windows or explicit cutovers on older targets; estimate locks, disk, WAL,
  replica lag, and recovery. Load
  [PG14 detach](postgres-sql-14.md#concurrent-partition-detach),
  [PG15 access-method rewrite](postgres-sql-15.md#changing-a-table-access-method),
  [PG19 repack](postgres-sql-19.md#core-repack-preview), or
  [PG19 partition changes](postgres-sql-19.md#merge-and-split-partitions-preview).

- **Planner, indexes, and diagnostics — 14/16/17/18/19 development.** Combine
  older `EXPLAIN`, statistics views, and OS telemetry; observed plans are not
  permanent guarantees. Load
  [PG14 expression statistics](postgres-sql-14.md#extended-statistics-on-expressions),
  [PG16 generic plans](postgres-sql-16.md#generic-prepared-statement-plans),
  [PG16 I/O statistics](postgres-sql-16.md#cluster-io-diagnostics),
  [PG17 planning diagnostics](postgres-sql-17.md#explain-planner-memory-and-output-serialization),
  [PG18 skip scan](postgres-sql-18.md#b-tree-skip-scan-diagnostics), or
  [PG19 request diagnostics](postgres-sql-19.md#explain-analyze-io-preview).

- **Replication, privileges, and read consistency — 15/16/18/19 development.**
  Older targets may need broader publications, explicit role separation,
  primary reads, or replay-LSN polling. Check RLS, privileges, lag, timeout, and
  failover. Load [PG15 publications](postgres-sql-15.md#filtered-logical-publications),
  [PG15 invoker views](postgres-sql-15.md#security-invoker-views),
  [PG16 roles](postgres-sql-16.md#independent-role-membership-options),
  [PG18 generated-column replication](postgres-sql-18.md#logical-replication-of-stored-generated-columns),
  [PG19 replica waits](postgres-sql-19.md#wait-for-lsn-preview), or
  [PG19 publications](postgres-sql-19.md#publication-sequences-and-exclusions-preview).

- **Ranges, time, and identifiers — 14/18.** Normalize ranges explicitly, use
  controlled bucket arithmetic, and do not infer guarantees beyond the chosen
  identifier generator. Load
  [PG14 multiranges](postgres-sql-14.md#multirange-types),
  [PG14 time buckets](postgres-sql-14.md#arbitrary-time-buckets-with-date_bin), or
  [PG18 UUIDv7](postgres-sql-18.md#core-uuidv7-generation).

## Release catalogs

Load a complete catalog only for upgrade analysis, broad release comparison,
or targeted lookup of an unlisted feature: [14](postgres-sql-14.md),
[15](postgres-sql-15.md), [16](postgres-sql-16.md),
[17](postgres-sql-17.md), [18](postgres-sql-18.md), and
[19 development snapshot](postgres-sql-19.md).

The PostgreSQL 19 guide owns its dated development status. Recheck the current
official documentation and exact target build before relying on it.

## Answer checklist

- State the minimum major and whether it was observed or assumed.
- Include an older-version fallback when needed.
- Separate core features from extensions.
- Flag rewrite, lock, concurrency, replication, privilege, and trigger effects.
- For PostgreSQL 19, report a freshly verified release stage.
