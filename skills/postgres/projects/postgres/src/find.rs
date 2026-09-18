use crate::cli::FindObjectType;
use crate::db::escape_literal;

pub fn selected_find_types(types: &[FindObjectType]) -> Vec<FindObjectType> {
    if types.is_empty() {
        return FindObjectType::ALL.to_vec();
    }
    let mut selected = Vec::new();
    for object_type in types {
        if !selected.contains(object_type) {
            selected.push(*object_type);
        }
    }
    selected
}

pub fn build_find_sql(pattern: &str, types: &[FindObjectType]) -> String {
    let pattern = escape_literal(&format!("%{pattern}%"));
    let selected = selected_find_types(types);
    let include_schema = selected.contains(&FindObjectType::Schema);
    let include_table = selected.contains(&FindObjectType::Table);
    let include_view = selected.contains(&FindObjectType::View);
    let include_column = selected.contains(&FindObjectType::Column);
    let include_function = selected.contains(&FindObjectType::Function);
    let include_procedure = selected.contains(&FindObjectType::Procedure);

    let mut branches = Vec::new();
    if include_schema {
        branches.push(
            "  select 'schema'::text as object_type, n.nspname::text as object_schema, n.nspname::text as object_name, 'schema'::text as details
  from pg_namespace n
  where n.nspname <> 'information_schema' and n.nspname not like 'pg_%'
    and n.nspname ilike (select pat from p)",
        );
    }
    if include_table {
        branches.push(
            "  select 'table'::text as object_type, n.nspname::text as object_schema, c.relname::text as object_name,
         case c.relkind when 'r' then 'table' when 'p' then 'partitioned table' else c.relkind::text end as details
  from pg_class c join pg_namespace n on n.oid = c.relnamespace
  where c.relkind in ('r', 'p')
    and n.nspname <> 'information_schema' and n.nspname not like 'pg_%'
    and c.relname ilike (select pat from p)",
        );
    }
    if include_view {
        branches.push(
            "  select 'view'::text as object_type, n.nspname::text as object_schema, c.relname::text as object_name,
         case c.relkind when 'v' then 'view' when 'm' then 'materialized view' else c.relkind::text end as details
  from pg_class c join pg_namespace n on n.oid = c.relnamespace
  where c.relkind in ('v', 'm')
    and n.nspname <> 'information_schema' and n.nspname not like 'pg_%'
    and c.relname ilike (select pat from p)",
        );
    }
    if include_column {
        branches.push(
            "  select 'column'::text as object_type, cols.table_schema::text as object_schema, (cols.table_name || '.' || cols.column_name)::text as object_name,
         (cols.data_type || coalesce(' ' || cols.udt_name, ''))::text as details
  from information_schema.columns cols
  where cols.table_schema <> 'information_schema' and cols.table_schema not like 'pg_%'
    and (cols.table_name ilike (select pat from p) or cols.column_name ilike (select pat from p))",
        );
    }
    if include_function || include_procedure {
        branches.push(routine_branch(include_function, include_procedure));
    }

    format!(
        "with p as (
  select '{pattern}'::text as pat
)
select object_type, object_schema, object_name, details
from (
{}
) as results
order by object_type, object_schema, object_name;",
        branches.join("\n  union all\n")
    )
}

fn routine_branch(include_function: bool, include_procedure: bool) -> &'static str {
    match (include_function, include_procedure) {
        (true, true) => {
            "  select case proc.prokind when 'p' then 'procedure' else 'function' end as object_type,
         n.nspname::text as object_schema,
         proc.proname::text as object_name,
         (proc.proname || '(' || pg_get_function_identity_arguments(proc.oid) || ') returns ' || pg_get_function_result(proc.oid))::text as details
  from pg_proc proc
  join pg_namespace n on n.oid = proc.pronamespace
  where n.nspname <> 'information_schema' and n.nspname not like 'pg_%'
    and proc.proname ilike (select pat from p)"
        }
        (true, false) => {
            "  select 'function'::text as object_type,
         n.nspname::text as object_schema,
         proc.proname::text as object_name,
         (proc.proname || '(' || pg_get_function_identity_arguments(proc.oid) || ') returns ' || pg_get_function_result(proc.oid))::text as details
  from pg_proc proc
  join pg_namespace n on n.oid = proc.pronamespace
  where n.nspname <> 'information_schema' and n.nspname not like 'pg_%'
    and proc.prokind <> 'p'
    and proc.proname ilike (select pat from p)"
        }
        (false, true) => {
            "  select 'procedure'::text as object_type,
         n.nspname::text as object_schema,
         proc.proname::text as object_name,
         (proc.proname || '(' || pg_get_function_identity_arguments(proc.oid) || ') returns ' || pg_get_function_result(proc.oid))::text as details
  from pg_proc proc
  join pg_namespace n on n.oid = proc.pronamespace
  where n.nspname <> 'information_schema' and n.nspname not like 'pg_%'
    and proc.prokind = 'p'
    and proc.proname ilike (select pat from p)"
        }
        (false, false) => unreachable!("routine branch requires function or procedure"),
    }
}

#[cfg(test)]
mod tests {
    use super::{build_find_sql, selected_find_types};
    use crate::cli::FindObjectType;

    #[test]
    fn omitted_types_search_every_supported_class() {
        assert_eq!(selected_find_types(&[]), FindObjectType::ALL.to_vec());
        let sql = build_find_sql("demo", &[]);
        assert!(sql.contains("select 'schema'::text as object_type"));
        assert!(sql.contains("c.relkind in ('r', 'p')"));
        assert!(sql.contains("c.relkind in ('v', 'm')"));
        assert!(sql.contains("information_schema.columns"));
        assert!(sql.contains("case proc.prokind when 'p' then 'procedure' else 'function' end"));
        assert!(!sql.contains("regexp_replace(lower("));
    }

    #[test]
    fn each_supported_type_emits_its_object_class() {
        let cases = [
            (
                FindObjectType::Schema,
                "select 'schema'::text as object_type",
                "c.relkind in ('v', 'm')",
            ),
            (
                FindObjectType::Table,
                "c.relkind in ('r', 'p')",
                "c.relkind in ('v', 'm')",
            ),
            (
                FindObjectType::View,
                "c.relkind in ('v', 'm')",
                "c.relkind in ('r', 'p')",
            ),
            (
                FindObjectType::Column,
                "information_schema.columns",
                "c.relkind in ('v', 'm')",
            ),
            (
                FindObjectType::Function,
                "select 'function'::text",
                "proc.prokind = 'p'",
            ),
            (
                FindObjectType::Procedure,
                "select 'procedure'::text",
                "proc.prokind <> 'p'",
            ),
        ];
        for (object_type, expected, rejected) in cases {
            let sql = build_find_sql("demo", &[object_type]);
            assert!(sql.contains(expected), "{object_type:?}: {sql}");
            assert!(!sql.contains(rejected), "{object_type:?}: {sql}");
            assert!(sql.contains("as object_type"), "{object_type:?}: {sql}");
            assert!(sql.contains("as object_schema"), "{object_type:?}: {sql}");
            assert!(sql.contains("as object_name"), "{object_type:?}: {sql}");
            assert!(sql.contains("as details"), "{object_type:?}: {sql}");
            assert!(!sql.contains("regexp_replace(lower("), "{object_type:?}");
        }
    }

    #[test]
    fn pattern_quotes_are_escaped_and_types_are_not_interpolated() {
        let sql = build_find_sql("o'reilly; drop", &[FindObjectType::View]);
        assert!(sql.contains("'%o''reilly; drop%'"));
        assert!(!sql.contains("o'reilly; drop"));
        assert!(!sql.contains("regexp_replace(lower("));
        assert!(!sql.contains("regexp_split_to_array"));
    }
}
