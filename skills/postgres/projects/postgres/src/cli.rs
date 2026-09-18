use clap::{ArgAction, Args, Parser, Subcommand, ValueEnum};
use std::path::PathBuf;

#[derive(Debug, Parser)]
#[command(name = "postgres", version, about = "Rust-first Postgres skill CLI")]
pub struct Cli {
    #[arg(
        long,
        global = true,
        action = ArgAction::SetTrue,
        help = "Print machine-readable JSON output"
    )]
    pub json: bool,

    #[arg(long, global = true, help = "Use a saved profile from config.toml")]
    pub profile: Option<String>,

    #[arg(long, global = true, help = "Resolve config from this project root")]
    pub project_root: Option<PathBuf>,

    #[arg(long, global = true, help = "Use a one-off PostgreSQL connection URL")]
    pub url: Option<String>,

    #[arg(
        long,
        global = true,
        value_name = "MODE",
        help = "Override local access_mode: read, write, or read-write"
    )]
    pub access_mode: Option<String>,

    #[command(subcommand)]
    pub command: Command,
}

#[derive(Debug, Subcommand)]
pub enum Command {
    #[command(about = "Report config resolution and runtime readiness")]
    Doctor,
    #[command(about = "Manage and inspect connection profiles")]
    Profile(ProfileCommand),
    #[command(about = "Run SQL, explain queries, and search database objects")]
    Query(QueryCommand),
    #[command(about = "Inspect runtime activity and control matching sessions")]
    Activity(ActivityCommand),
    #[command(about = "Inspect schema, indexes, roles, and vacuum state")]
    Schema(SchemaCommand),
    #[command(about = "Search official PostgreSQL documentation")]
    Docs(DocsCommand),
}

#[derive(Debug, Args)]
pub struct ProfileCommand {
    #[command(subcommand)]
    pub command: ProfileSubcommand,
}

#[derive(Debug, Subcommand)]
pub enum ProfileSubcommand {
    #[command(about = "Show the active connection URL, profile, and source")]
    Resolve,
    #[command(about = "Prompt for a profile and optionally save it")]
    Bootstrap(BootstrapArgs),
    #[command(about = "Verify that the active profile can connect")]
    Test,
    #[command(about = "Print connection details and key server settings")]
    Info,
    #[command(about = "Summarize database identity, object counts, activity, and key settings")]
    Overview,
    #[command(about = "Inspect PostgreSQL runtime settings")]
    Settings(ProfileSettingsCommand),
    #[command(about = "Show the PostgreSQL server version")]
    Version,
    #[command(
        name = "migrate-config",
        alias = "migrate-toml",
        about = "Migrate legacy or older config to the canonical schema"
    )]
    MigrateConfig,
    #[command(about = "Persist ssl_mode for a saved profile")]
    SetSslMode(SetSslModeArgs),
    #[command(name = "set-ssl", hide = true)]
    SetSsl(SetSslArgs),
}

#[derive(Debug, Args)]
pub struct BootstrapArgs {
    #[arg(long, help = "Write the prompted profile to config.toml")]
    pub save: bool,
}

#[derive(Debug, Args)]
pub struct SetSslModeArgs {
    #[arg(help = "Profile name to update")]
    pub profile: String,
    #[arg(help = "SSL mode: disable or require")]
    pub ssl_mode: String,
}

#[derive(Debug, Args)]
pub struct SetSslArgs {
    #[arg(help = "Profile name to update")]
    pub profile: String,
    #[arg(help = "Legacy SSL value: true/require or false/disable")]
    pub sslmode: String,
}

#[derive(Debug, Args)]
pub struct ProfileSettingsCommand {
    #[command(subcommand)]
    pub command: ProfileSettingsSubcommand,
}

#[derive(Debug, Subcommand)]
pub enum ProfileSettingsSubcommand {
    #[command(about = "List autovacuum settings and table-level overrides")]
    Autovacuum,
    #[command(about = "List memory-related PostgreSQL settings")]
    Memory,
}

#[derive(Debug, Args)]
pub struct QueryCommand {
    #[command(subcommand)]
    pub command: QuerySubcommand,
}

#[derive(Debug, Subcommand)]
pub enum QuerySubcommand {
    #[command(about = "Execute SQL from -c, -f, or stdin")]
    Run(SqlInputArgs),
    #[command(about = "Run EXPLAIN for SQL, defaulting to ANALYZE")]
    Explain(ExplainArgs),
    #[command(about = "Return a JSON query plan without executing by default")]
    Plan(QueryPlanArgs),
    #[command(about = "Search schemas, tables, columns, views, and routines by name")]
    Find(FindArgs),
}

#[derive(Debug, Args, Clone)]
pub struct SqlInputArgs {
    #[arg(short = 'c', long, help = "SQL text to execute")]
    pub command: Option<String>,

    #[arg(short = 'f', long, help = "Path to a SQL file to execute")]
    pub file: Option<PathBuf>,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn canonical_and_legacy_migration_commands_share_one_handler() {
        for command in ["migrate-config", "migrate-toml"] {
            let cli = Cli::try_parse_from(["postgres", "profile", command]).unwrap();
            assert!(matches!(
                cli.command,
                Command::Profile(ProfileCommand {
                    command: ProfileSubcommand::MigrateConfig
                })
            ));
        }
    }

    #[test]
    fn ssl_commands_keep_canonical_and_legacy_inputs_separate() {
        let canonical =
            Cli::try_parse_from(["postgres", "profile", "set-ssl-mode", "local", "require"])
                .unwrap();
        assert!(matches!(
            canonical.command,
            Command::Profile(ProfileCommand {
                command: ProfileSubcommand::SetSslMode(_)
            })
        ));

        let legacy =
            Cli::try_parse_from(["postgres", "profile", "set-ssl", "local", "true"]).unwrap();
        assert!(matches!(
            legacy.command,
            Command::Profile(ProfileCommand {
                command: ProfileSubcommand::SetSsl(_)
            })
        ));
    }

    #[test]
    fn query_find_accepts_enumerated_types() {
        let cli = Cli::try_parse_from([
            "postgres",
            "query",
            "find",
            "demo",
            "--types",
            "schema,table,view,column,function,procedure",
        ])
        .unwrap();
        match cli.command {
            Command::Query(QueryCommand {
                command: QuerySubcommand::Find(args),
            }) => {
                assert_eq!(args.pattern, "demo");
                assert_eq!(
                    args.types,
                    vec![
                        FindObjectType::Schema,
                        FindObjectType::Table,
                        FindObjectType::View,
                        FindObjectType::Column,
                        FindObjectType::Function,
                        FindObjectType::Procedure,
                    ]
                );
            }
            other => panic!("unexpected command: {other:?}"),
        }
    }

    #[test]
    fn query_find_rejects_unknown_or_malformed_types() {
        for types in ["view'", "view;", "index", "table,drop"] {
            let err = Cli::try_parse_from(["postgres", "query", "find", "demo", "--types", types])
                .unwrap_err();
            let message = err.to_string();
            assert!(
                message.contains("invalid value") || message.contains("possible values"),
                "{types}: {message}"
            );
        }
    }

    #[test]
    fn query_find_accepts_case_insensitive_and_trimmed_types() {
        let cli = Cli::try_parse_from([
            "postgres",
            "query",
            "find",
            "demo",
            "--types",
            "TABLE, view",
        ])
        .unwrap();
        match cli.command {
            Command::Query(QueryCommand {
                command: QuerySubcommand::Find(args),
            }) => {
                assert_eq!(
                    args.types,
                    vec![FindObjectType::Table, FindObjectType::View]
                );
            }
            other => panic!("unexpected command: {other:?}"),
        }
    }

    #[test]
    fn docs_search_accepts_positional_or_named_limit() {
        let positional =
            Cli::try_parse_from(["postgres", "docs", "search", "transaction isolation", "3"])
                .unwrap();
        match positional.command {
            Command::Docs(DocsCommand {
                command: DocsSubcommand::Search(args),
            }) => {
                assert_eq!(args.query, "transaction isolation");
                assert_eq!(args.limit, Some(3));
                assert_eq!(args.named_limit, None);
            }
            other => panic!("unexpected command: {other:?}"),
        }

        let named = Cli::try_parse_from([
            "postgres",
            "docs",
            "search",
            "transaction isolation",
            "--limit",
            "5",
        ])
        .unwrap();
        match named.command {
            Command::Docs(DocsCommand {
                command: DocsSubcommand::Search(args),
            }) => {
                assert_eq!(args.limit, None);
                assert_eq!(args.named_limit, Some(5));
            }
            other => panic!("unexpected command: {other:?}"),
        }
    }

    #[test]
    fn catalog_commands_accept_limit_and_full() {
        let inspect =
            Cli::try_parse_from(["postgres", "schema", "inspect", "--limit", "5"]).unwrap();
        match inspect.command {
            Command::Schema(SchemaCommand {
                command: SchemaSubcommand::Inspect(args),
            }) => {
                assert_eq!(args.limit, 5);
                assert!(!args.full);
                assert_eq!(args.row_limit().unwrap(), Some(5));
            }
            other => panic!("unexpected command: {other:?}"),
        }

        let full = Cli::try_parse_from(["postgres", "schema", "inspect", "--full"]).unwrap();
        match full.command {
            Command::Schema(SchemaCommand {
                command: SchemaSubcommand::Inspect(args),
            }) => {
                assert!(args.full);
                assert_eq!(args.row_limit().unwrap(), None);
            }
            other => panic!("unexpected command: {other:?}"),
        }
    }
}

#[derive(Debug, Args)]
pub struct ExplainArgs {
    #[command(flatten)]
    pub sql: SqlInputArgs,

    #[arg(long, action = ArgAction::SetTrue, help = "Run EXPLAIN without ANALYZE")]
    pub no_analyze: bool,
}

#[derive(Debug, Args)]
pub struct QueryPlanArgs {
    #[command(flatten)]
    pub sql: SqlInputArgs,

    #[arg(long, action = ArgAction::SetTrue, help = "Run EXPLAIN ANALYZE")]
    pub analyze: bool,
}

fn parse_find_object_type(value: &str) -> Result<FindObjectType, String> {
    <FindObjectType as ValueEnum>::from_str(value.trim(), true)
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, ValueEnum)]
#[value(rename_all = "lower")]
pub enum FindObjectType {
    Schema,
    Table,
    View,
    Column,
    Function,
    Procedure,
}

impl FindObjectType {
    pub const ALL: [Self; 6] = [
        Self::Schema,
        Self::Table,
        Self::View,
        Self::Column,
        Self::Function,
        Self::Procedure,
    ];

    pub fn as_str(self) -> &'static str {
        match self {
            Self::Schema => "schema",
            Self::Table => "table",
            Self::View => "view",
            Self::Column => "column",
            Self::Function => "function",
            Self::Procedure => "procedure",
        }
    }
}

#[derive(Debug, Args)]
pub struct FindArgs {
    #[arg(help = "Case-insensitive object-name search pattern")]
    pub pattern: String,

    #[arg(
        long,
        value_enum,
        value_delimiter = ',',
        value_parser = parse_find_object_type,
        ignore_case = true,
        help = "Object types to search: schema, table, view, column, function, procedure"
    )]
    pub types: Vec<FindObjectType>,

    #[command(flatten)]
    pub catalog: CatalogBoundArgs,
}

#[derive(Debug, Args)]
pub struct CatalogBoundArgs {
    #[arg(long, default_value_t = 100, help = "Maximum rows to return")]
    pub limit: u32,

    #[arg(
        long,
        action = ArgAction::SetTrue,
        help = "Return all matching rows"
    )]
    pub full: bool,
}

impl CatalogBoundArgs {
    pub fn row_limit(&self) -> anyhow::Result<Option<u32>> {
        if self.full {
            return Ok(None);
        }
        if self.limit == 0 {
            anyhow::bail!("--limit must be greater than 0");
        }
        Ok(Some(self.limit))
    }
}

#[derive(Debug, Args)]
pub struct ActivityCommand {
    #[command(subcommand)]
    pub command: ActivitySubcommand,
}

#[derive(Debug, Subcommand)]
pub enum ActivitySubcommand {
    #[command(about = "List non-idle sessions in pg_stat_activity")]
    Overview(LimitArgs),
    #[command(about = "List active sessions in pg_stat_activity")]
    ActiveQueries(LimitArgs),
    #[command(about = "Show blocked and blocking sessions")]
    Locks(CatalogBoundArgs),
    #[command(about = "List top pg_stat_statements entries by total time")]
    Slow(LimitArgs),
    #[command(about = "List active queries older than a minute threshold")]
    LongRunning(LongRunningArgs),
    #[command(about = "Cancel matching active queries after confirmation")]
    Cancel(ActivityActionArgs),
    #[command(about = "Terminate matching active sessions after confirmation")]
    Terminate(ActivityActionArgs),
    #[command(about = "Cancel specific backend PIDs after confirmation")]
    CancelPid(PidArgs),
    #[command(about = "Terminate specific backend PIDs after confirmation")]
    TerminatePid(PidArgs),
    #[command(about = "Alias for top pg_stat_statements entries")]
    PgStatTop(LimitArgs),
    #[command(about = "List replication slots")]
    ReplicationSlots,
}

#[derive(Debug, Args)]
pub struct LimitArgs {
    #[arg(default_value_t = 20, help = "Maximum rows to return")]
    pub limit: u32,
}

#[derive(Debug, Args)]
pub struct LongRunningArgs {
    #[arg(default_value_t = 5, help = "Minimum active-query age in minutes")]
    pub minutes: u32,

    #[arg(default_value_t = 20, help = "Maximum rows to return")]
    pub limit: u32,
}

#[derive(Debug, Args)]
pub struct ActivityActionArgs {
    #[arg(long, help = "Match active queries containing this text")]
    pub query: Option<String>,

    #[arg(long, help = "Match sessions owned by this database user")]
    pub user: Option<String>,

    #[arg(long, help = "Backend PID to target; repeat for multiple PIDs")]
    pub pid: Vec<i32>,

    #[arg(long, default_value_t = 20, help = "Maximum candidate rows to inspect")]
    pub limit: u32,

    #[arg(long, action = ArgAction::SetTrue, help = "Skip interactive confirmation")]
    pub yes: bool,
}

#[derive(Debug, Args)]
pub struct PidArgs {
    #[arg(long, value_delimiter = ',', help = "Comma-separated backend PID list")]
    pub pid: Vec<i32>,

    #[arg(long, action = ArgAction::SetTrue, help = "Skip interactive confirmation")]
    pub yes: bool,
}

#[derive(Debug, Args)]
pub struct SchemaCommand {
    #[command(subcommand)]
    pub command: SchemaSubcommand,
}

#[derive(Debug, Subcommand)]
pub enum SchemaSubcommand {
    #[command(
        about = "Inspect tables, columns, constraints, indexes, views, routines, and extensions"
    )]
    Inspect(CatalogBoundArgs),
    #[command(about = "List focused schema object groups")]
    List(SchemaListCommand),
    #[command(about = "List available or installed extensions")]
    Extensions(ExtensionListArgs),
    #[command(about = "List largest user tables by total relation size")]
    TableSizes(LimitArgs),
    #[command(about = "Show missing-index candidates and unused indexes")]
    IndexHealth(LimitArgs),
    #[command(about = "List indexes that are invalid, not ready, or not live")]
    InvalidIndexes,
    #[command(about = "Estimate top user tables by dead tuples")]
    TopBloatedTables(LimitArgs),
    #[command(about = "Find foreign keys without a supporting leading index")]
    MissingFkIndexes,
    #[command(about = "Show vacuum and analyze status for user tables")]
    VacuumStatus,
    #[command(about = "List roles and key role attributes")]
    Roles(CatalogBoundArgs),
}

#[derive(Debug, Args)]
pub struct SchemaListCommand {
    #[command(subcommand)]
    pub command: SchemaListSubcommand,
}

#[derive(Debug, Subcommand)]
pub enum SchemaListSubcommand {
    #[command(about = "List user-visible base, partitioned, and foreign tables")]
    Tables(CatalogBoundArgs),
    #[command(about = "List user-visible views")]
    Views(CatalogBoundArgs),
    #[command(about = "List user-visible schemas")]
    Schemas(CatalogBoundArgs),
    #[command(about = "List user-defined triggers")]
    Triggers(CatalogBoundArgs),
    #[command(about = "List user-visible indexes")]
    Indexes(CatalogBoundArgs),
    #[command(about = "List user-visible sequences")]
    Sequences(CatalogBoundArgs),
}

#[derive(Debug, Args)]
pub struct ExtensionListArgs {
    #[arg(
        long,
        conflicts_with = "installed",
        help = "List extensions available to install"
    )]
    pub available: bool,

    #[arg(long, conflicts_with = "available", help = "List installed extensions")]
    pub installed: bool,
}

#[derive(Debug, Args)]
pub struct DocsCommand {
    #[command(subcommand)]
    pub command: DocsSubcommand,
}

#[derive(Debug, Subcommand)]
pub enum DocsSubcommand {
    #[command(about = "Search official PostgreSQL current documentation")]
    Search(DocsSearchArgs),
}

#[derive(Debug, Args)]
pub struct DocsSearchArgs {
    #[arg(help = "Documentation search query")]
    pub query: String,

    #[arg(help = "Maximum results to return")]
    pub limit: Option<usize>,

    #[arg(
        long = "limit",
        value_name = "LIMIT",
        help = "Maximum results to return"
    )]
    pub named_limit: Option<usize>,
}
