#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
"$SCRIPT_DIR/psql_with_ssl_fallback.sh" -v ON_ERROR_STOP=1 -X -c "
with fk_constraints as (
  select
    c.oid as constraint_oid,
    c.conrelid,
    c.conname,
    c.conkey as fk_attnums,
    array_agg(a.attname order by cols.ordinality) as fk_columns
  from pg_constraint c
  join lateral unnest(c.conkey) with ordinality as cols(attnum, ordinality) on true
  join pg_attribute a
    on a.attrelid = c.conrelid
   and a.attnum = cols.attnum
   and a.attisdropped = false
  where c.contype = 'f'
  group by c.oid, c.conrelid, c.conname, c.conkey
),
supporting_indexes as (
  select
    i.indrelid as conrelid,
    array_agg(idx_col.attnum order by idx_col.ordinality)
      filter (where idx_col.ordinality <= i.indnkeyatts and idx_col.attnum > 0) as index_key_attnums
  from pg_index i
  cross join lateral unnest(i.indkey::smallint[]) with ordinality as idx_col(attnum, ordinality)
  where i.indpred is null
    and i.indisvalid
    and i.indisready
  group by i.indrelid, i.indexrelid, i.indnkeyatts
)
select
  fk.conrelid::regclass as table_name,
  fk.conname as constraint_name,
  array_to_string(fk.fk_columns, ', ') as fk_columns
from fk_constraints fk
where not exists (
  select 1
  from supporting_indexes si
  where si.conrelid = fk.conrelid
    and array_length(si.index_key_attnums, 1) >= array_length(fk.fk_attnums, 1)
    and si.index_key_attnums[1:array_length(fk.fk_attnums, 1)] = fk.fk_attnums
)
order by table_name::text, constraint_name;
"
