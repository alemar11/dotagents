use crate::config::{RuntimeContext, SslMode, update_ssl_mode};
use anyhow::{Context, Result, anyhow, bail};
use serde::Serialize;
use serde_json::{Map, Value, json};
use std::time::Duration;
use tokio_postgres::SimpleQueryMessage;
use tokio_postgres::tls::MakeTlsConnect;
use tokio_postgres::{Client, Connection, NoTls, Socket};
use tokio_postgres_rustls::MakeRustlsConnect;

const DEFAULT_CONNECT_TIMEOUT_MS: u64 = 10_000;
const MAX_CONNECT_TIMEOUT_MS: u64 = 86_400_000;

#[derive(Debug, Clone, Serialize)]
pub struct QueryTable {
    pub columns: Vec<String>,
    pub rows: Vec<Vec<Option<String>>>,
}

#[derive(Debug, Clone, Serialize)]
pub struct QueryStatement {
    pub statement: usize,
    pub row_count: u64,
    pub columns: Vec<String>,
    pub rows: Vec<Vec<Option<String>>>,
}

#[derive(Debug, Clone, Serialize)]
pub struct QueryExecution {
    pub statements: Vec<QueryStatement>,
}

#[derive(Debug)]
pub struct DbClient {
    ctx: RuntimeContext,
}

impl DbClient {
    pub fn new(ctx: RuntimeContext) -> Self {
        Self { ctx }
    }

    pub fn context(&self) -> &RuntimeContext {
        &self.ctx
    }

    pub async fn query(&self, sql: &str) -> Result<QueryTable> {
        let execution = self.simple_query(sql).await?;
        match execution.statements.len() {
            0 => Ok(QueryTable {
                columns: vec![],
                rows: vec![],
            }),
            1 => {
                let statement = &execution.statements[0];
                Ok(QueryTable {
                    columns: statement.columns.clone(),
                    rows: statement.rows.clone(),
                })
            }
            count => Err(anyhow!(
                "Expected a single SQL statement result, got {count}. Use `query run` for multi-statement SQL."
            )),
        }
    }

    pub async fn simple_query(&self, sql: &str) -> Result<QueryExecution> {
        let messages = self.run_with_retry(sql).await?;
        Ok(query_execution_from_messages(messages))
    }

    async fn run_with_retry(&self, sql: &str) -> Result<Vec<SimpleQueryMessage>> {
        match self.run_once(&self.ctx.url, sql).await {
            Ok(messages) => Ok(messages),
            Err(error)
                if self.ctx.ssl_mode == SslMode::Disable
                    && looks_like_ssl_failure(&error.to_string()) =>
            {
                let retry_url = set_sslmode(&self.ctx.url, "require")?;
                let messages = self.run_once(&retry_url, sql).await?;
                if self.ctx.url_source == "config"
                    && auto_update_ssl_mode_enabled()
                    && let Some(config_path) = &self.ctx.config_path
                {
                    let _ = update_ssl_mode(config_path, &self.ctx.profile_name, SslMode::Require);
                }
                Ok(messages)
            }
            Err(error) => Err(error),
        }
    }

    async fn run_once(&self, url: &str, sql: &str) -> Result<Vec<SimpleQueryMessage>> {
        if self.ctx.ssl_mode == SslMode::Require
            || url.contains("sslmode=require")
            || url.contains("sslmode=verify")
        {
            let mut roots = rustls::RootCertStore::empty();
            let certs = rustls_native_certs::load_native_certs();
            for cert in certs.certs {
                let _ = roots.add(cert);
            }
            let tls = rustls::ClientConfig::builder()
                .with_root_certificates(roots)
                .with_no_client_auth();
            let connector = MakeRustlsConnect::new(tls);
            let (client, connection) = connect_client(url, connector).await?;
            tokio::spawn(async move {
                let _ = connection.await;
            });
            apply_session_settings(&client, &self.ctx.application_name).await?;
            client
                .simple_query(sql)
                .await
                .with_context(|| "Failed to execute SQL query".to_string())
        } else {
            let (client, connection) = connect_client(url, NoTls).await?;
            tokio::spawn(async move {
                let _ = connection.await;
            });
            apply_session_settings(&client, &self.ctx.application_name).await?;
            client
                .simple_query(sql)
                .await
                .with_context(|| "Failed to execute SQL query".to_string())
        }
    }
}

fn auto_update_ssl_mode_enabled() -> bool {
    ["DB_AUTO_UPDATE_SSL_MODE", "DB_AUTO_UPDATE_SSLMODE"]
        .iter()
        .any(|key| std::env::var(key).ok().as_deref() == Some("1"))
}

async fn connect_client<T>(url: &str, tls: T) -> Result<(Client, Connection<Socket, T::Stream>)>
where
    T: MakeTlsConnect<Socket>,
{
    let timeout = connect_timeout()?;
    let mut config: tokio_postgres::Config = url
        .parse()
        .map_err(|error| anyhow!("Invalid connection URL: {error}"))?;
    config.connect_timeout(timeout);
    tokio::time::timeout(timeout, config.connect(tls))
        .await
        .map_err(|_| {
            anyhow!(
                "timed out connecting to PostgreSQL after {}ms",
                timeout.as_millis()
            )
        })?
        .map_err(Into::into)
}

fn connect_timeout() -> Result<Duration> {
    parse_connect_timeout_ms(std::env::var("DB_CONNECT_TIMEOUT_MS").ok().as_deref())
}

pub fn parse_connect_timeout_ms(value: Option<&str>) -> Result<Duration> {
    let Some(value) = value.map(str::trim).filter(|value| !value.is_empty()) else {
        return Ok(Duration::from_millis(DEFAULT_CONNECT_TIMEOUT_MS));
    };
    let millis: u64 = value
        .parse()
        .with_context(|| "DB_CONNECT_TIMEOUT_MS must be a positive integer.".to_string())?;
    if millis == 0 || millis > MAX_CONNECT_TIMEOUT_MS {
        bail!("DB_CONNECT_TIMEOUT_MS must be between 1 and {MAX_CONNECT_TIMEOUT_MS}.");
    }
    Ok(Duration::from_millis(millis))
}

pub fn with_row_limit(sql: &str, limit: Option<u32>) -> String {
    let sql = sql.trim();
    let sql = sql.strip_suffix(';').unwrap_or(sql).trim_end();
    match limit {
        Some(limit) => format!("{sql} limit {limit};"),
        None => format!("{sql};"),
    }
}

async fn apply_session_settings(
    client: &tokio_postgres::Client,
    application_name: &str,
) -> Result<()> {
    let mut settings = Vec::new();
    if let Ok(ms) = std::env::var("DB_STATEMENT_TIMEOUT_MS")
        && !ms.trim().is_empty()
    {
        settings.push(format!(
            "SET statement_timeout = '{}';",
            escape_literal(&ms)
        ));
    }
    if let Ok(ms) = std::env::var("DB_LOCK_TIMEOUT_MS")
        && !ms.trim().is_empty()
    {
        settings.push(format!("SET lock_timeout = '{}';", escape_literal(&ms)));
    }
    settings.push(format!(
        "SET application_name = '{}';",
        escape_literal(application_name)
    ));
    if !settings.is_empty() {
        client.batch_execute(&settings.join("\n")).await?;
    }
    Ok(())
}

pub fn table_to_json(table: &QueryTable) -> Result<Value> {
    let rows = table
        .rows
        .iter()
        .map(|row| {
            let mut map = Map::new();
            for (index, column) in table.columns.iter().enumerate() {
                if map.contains_key(column) {
                    bail!(
                        "Duplicate JSON column name '{column}'. Rename the selected columns so JSON object keys are unique."
                    );
                }
                map.insert(
                    column.clone(),
                    row.get(index)
                        .cloned()
                        .flatten()
                        .map(Value::String)
                        .unwrap_or(Value::Null),
                );
            }
            Ok(Value::Object(map))
        })
        .collect::<Result<Vec<_>>>()?;
    Ok(json!({
        "columns": table.columns,
        "rows": rows,
    }))
}

pub fn execution_to_json(execution: &QueryExecution) -> Result<Value> {
    let mut statements = Vec::new();
    for statement in &execution.statements {
        statements.push(json!({
            "statement": statement.statement,
            "row_count": statement.row_count,
            "result": table_to_json(&QueryTable {
                columns: statement.columns.clone(),
                rows: statement.rows.clone(),
            })?,
        }));
    }
    Ok(json!({
        "statements": statements,
    }))
}

pub fn escape_literal(value: &str) -> String {
    value.replace('\'', "''")
}

pub fn set_sslmode(url: &str, sslmode: &str) -> Result<String> {
    let mut parsed = url::Url::parse(url).context("Invalid connection URL")?;
    let mut pairs = parsed.query_pairs().into_owned().collect::<Vec<_>>();
    pairs.retain(|(key, _)| key != "sslmode");
    pairs.push(("sslmode".to_string(), sslmode.to_string()));
    parsed.query_pairs_mut().clear().extend_pairs(pairs);
    Ok(parsed.to_string())
}

fn looks_like_ssl_failure(message: &str) -> bool {
    let lowered = message.to_ascii_lowercase();
    lowered.contains("ssl")
        || lowered.contains("tls")
        || lowered.contains("requires encryption")
        || lowered.contains("requires ssl")
        || lowered.contains("certificate")
}

pub fn expect_non_empty(table: &QueryTable, message: &str) -> Result<()> {
    if table.rows.is_empty() {
        return Err(anyhow!(message.to_string()));
    }
    Ok(())
}

fn query_execution_from_messages(messages: Vec<SimpleQueryMessage>) -> QueryExecution {
    let mut statements = Vec::new();
    let mut columns = Vec::new();
    let mut rows = Vec::new();

    for message in messages {
        match message {
            SimpleQueryMessage::RowDescription(description) => {
                columns = description
                    .iter()
                    .map(|column| column.name().to_string())
                    .collect();
            }
            SimpleQueryMessage::Row(row) => {
                if columns.is_empty() {
                    columns = row
                        .columns()
                        .iter()
                        .map(|column| column.name().to_string())
                        .collect();
                }
                let values = row
                    .columns()
                    .iter()
                    .enumerate()
                    .map(|(index, _)| row.get(index).map(|value| value.to_string()))
                    .collect();
                rows.push(values);
            }
            SimpleQueryMessage::CommandComplete(row_count) => {
                statements.push(QueryStatement {
                    statement: statements.len() + 1,
                    row_count,
                    columns: std::mem::take(&mut columns),
                    rows: std::mem::take(&mut rows),
                });
            }
            _ => {}
        }
    }

    QueryExecution { statements }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn execution_tracks_write_only_statement_counts() {
        let execution = query_execution_from_messages(vec![
            SimpleQueryMessage::CommandComplete(0),
            SimpleQueryMessage::CommandComplete(2),
        ]);

        assert_eq!(execution.statements.len(), 2);
        assert_eq!(execution.statements[0].statement, 1);
        assert_eq!(execution.statements[0].row_count, 0);
        assert!(execution.statements[0].columns.is_empty());
        assert!(execution.statements[0].rows.is_empty());
        assert_eq!(execution.statements[1].statement, 2);
        assert_eq!(execution.statements[1].row_count, 2);
    }

    #[test]
    fn table_json_rejects_duplicate_column_names() {
        let unique = QueryTable {
            columns: vec!["id".to_string(), "name".to_string()],
            rows: vec![vec![Some("1".to_string()), Some("a".to_string())]],
        };
        let json = table_to_json(&unique).unwrap();
        assert_eq!(json["rows"][0]["id"], "1");
        assert_eq!(json["rows"][0]["name"], "a");

        let duplicate = QueryTable {
            columns: vec!["id".to_string(), "id".to_string()],
            rows: vec![vec![Some("1".to_string()), Some("2".to_string())]],
        };
        let error = table_to_json(&duplicate).unwrap_err();
        assert!(format!("{error:#}").contains("Duplicate JSON column name 'id'"));
    }

    #[test]
    fn connect_timeout_defaults_and_validates() {
        assert_eq!(
            parse_connect_timeout_ms(None).unwrap(),
            Duration::from_millis(10_000)
        );
        assert_eq!(
            parse_connect_timeout_ms(Some(" 1500 ")).unwrap(),
            Duration::from_millis(1500)
        );
        assert!(parse_connect_timeout_ms(Some("0")).is_err());
        assert!(parse_connect_timeout_ms(Some("bad")).is_err());
    }

    #[test]
    fn row_limit_appends_or_preserves_sql() {
        assert_eq!(with_row_limit("select 1;", Some(5)), "select 1 limit 5;");
        assert_eq!(with_row_limit("select 1", None), "select 1;");
    }
}
