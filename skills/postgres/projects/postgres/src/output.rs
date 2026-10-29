use crate::db::QueryTable;
use anyhow::Result;
use comfy_table::{Cell, ContentArrangement, Table, presets::UTF8_FULL};
use serde::Serialize;
use serde_json::{Map, Value};
use std::sync::OnceLock;

static COMMAND: OnceLock<String> = OnceLock::new();

/// Names the running command, such as `query run`, for every JSON envelope.
pub fn set_command(name: String) {
    let _ = COMMAND.set(name);
}

pub fn command_name() -> &'static str {
    COMMAND.get().map(String::as_str).unwrap_or("parse")
}

/// Prints a success payload. An object without `ok` gets the standard
/// `ok: true` and `command` envelope fields.
pub fn print_json<T: Serialize>(value: &T) -> Result<()> {
    let value = match serde_json::to_value(value)? {
        Value::Object(fields) if !fields.contains_key("ok") => {
            let mut envelope = Map::new();
            envelope.insert("ok".to_string(), Value::Bool(true));
            envelope.insert("command".to_string(), Value::String(command_name().to_string()));
            envelope.extend(fields);
            Value::Object(envelope)
        }
        other => other,
    };
    println!("{}", serde_json::to_string_pretty(&value)?);
    Ok(())
}

pub fn render_table(table: &QueryTable, title: Option<&str>) -> String {
    let mut output = String::new();
    if let Some(title) = title {
        output.push_str(title);
        output.push('\n');
    }

    let mut pretty = Table::new();
    pretty.load_style(UTF8_FULL);
    pretty.set_content_arrangement(ContentArrangement::Dynamic);
    pretty.set_header(table.columns.iter().map(Cell::new));
    for row in &table.rows {
        pretty.add_row(
            row.iter()
                .map(|value| Cell::new(value.clone().unwrap_or_else(|| "(null)".to_string())))
                .collect::<Vec<_>>(),
        );
    }
    output.push_str(&pretty.to_string());
    output
}
