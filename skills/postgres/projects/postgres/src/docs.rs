use anyhow::{Context, Result, bail};
use regex::Regex;
use serde::Serialize;

#[derive(Debug, Clone, Serialize)]
pub struct DocsSearchResult {
    pub title: String,
    pub url: String,
    pub snippet: String,
}

pub async fn search(query: &str, limit: usize) -> Result<Vec<DocsSearchResult>> {
    if query.trim().is_empty() {
        bail!("Query must not be empty.");
    }
    if limit == 0 || limit > 20 {
        bail!("Limit must be between 1 and 20.");
    }

    let search_url = std::env::var("DB_DOCS_SEARCH_URL")
        .unwrap_or_else(|_| "https://www.postgresql.org/search/".to_string());
    let max_time = std::env::var("DB_DOCS_SEARCH_MAX_TIME")
        .ok()
        .and_then(|value| value.parse::<u64>().ok())
        .unwrap_or(30);

    let client = reqwest::Client::builder()
        .brotli(true)
        .gzip(true)
        .deflate(true)
        .timeout(std::time::Duration::from_secs(max_time))
        .build()
        .context("Failed to initialize HTTP client")?;

    let response = client
        .get(search_url)
        .query(&[("q", query), ("u", "/docs/current/")])
        .send()
        .await
        .context("Failed to query postgresql.org search endpoint")?
        .error_for_status()
        .context("PostgreSQL docs search request failed")?
        .text()
        .await
        .context("Failed to read PostgreSQL docs search response")?;

    parse_results(&response, limit)
}

fn parse_results(html: &str, limit: usize) -> Result<Vec<DocsSearchResult>> {
    let matcher = Regex::new(
        r#"(?s)\d+\.\s*<a href="(https://www\.postgresql\.org/docs/current/[^"]+)">(.+?)</a>.*?\[.*?\]\s*<br/>\s*<div>(.*?)</div>"#,
    )
    .unwrap();
    let tag_regex = Regex::new(r"<[^>]+>").unwrap();
    let mut results = Vec::new();

    for capture in matcher.captures_iter(html) {
        let url = capture.get(1).map(|m| m.as_str()).unwrap_or_default();
        let title = clean_html(
            tag_regex
                .replace_all(capture.get(2).map(|m| m.as_str()).unwrap_or_default(), "")
                .as_ref(),
        );
        let snippet = clean_html(
            tag_regex
                .replace_all(capture.get(3).map(|m| m.as_str()).unwrap_or_default(), "")
                .as_ref(),
        );
        if title.is_empty()
            || results
                .iter()
                .any(|existing: &DocsSearchResult| existing.url == url)
        {
            continue;
        }
        results.push(DocsSearchResult {
            title,
            url: url.to_string(),
            snippet: if snippet.is_empty() {
                "(no snippet)".to_string()
            } else {
                snippet
            },
        });
        if results.len() >= limit {
            break;
        }
    }

    Ok(results)
}

fn clean_html(value: &str) -> String {
    decode_html_entities(value)
        .split_whitespace()
        .collect::<Vec<_>>()
        .join(" ")
}

fn decode_html_entities(value: &str) -> String {
    let mut decoded = String::with_capacity(value.len());
    let mut remaining = value;
    while let Some(start) = remaining.find('&') {
        decoded.push_str(&remaining[..start]);
        let after_amp = &remaining[start + 1..];
        let Some(end) = after_amp.find(';') else {
            decoded.push('&');
            remaining = after_amp;
            continue;
        };
        let entity = &after_amp[..end];
        if let Some(replacement) = decode_html_entity(entity) {
            decoded.push_str(&replacement);
            remaining = &after_amp[end + 1..];
        } else {
            decoded.push('&');
            remaining = after_amp;
        }
    }
    decoded.push_str(remaining);
    decoded
}

fn decode_html_entity(entity: &str) -> Option<String> {
    match entity {
        "amp" => Some("&".to_string()),
        "lt" => Some("<".to_string()),
        "gt" => Some(">".to_string()),
        "quot" => Some("\"".to_string()),
        "apos" => Some("'".to_string()),
        "nbsp" => Some(" ".to_string()),
        "copy" => Some("©".to_string()),
        other if other.starts_with('#') => decode_numeric_entity(&other[1..]),
        _ => None,
    }
}

fn decode_numeric_entity(value: &str) -> Option<String> {
    let code = if let Some(hex) = value.strip_prefix('x').or_else(|| value.strip_prefix('X')) {
        u32::from_str_radix(hex, 16).ok()?
    } else {
        value.parse().ok()?
    };
    char::from_u32(code).map(String::from)
}

#[cfg(test)]
mod tests {
    use super::{clean_html, parse_results};

    const CURRENT_SEARCH_HTML: &str = include_str!("../tests/fixtures/docs-search-current.html");

    #[test]
    fn parses_multiline_postgresql_search_results() {
        let results = parse_results(CURRENT_SEARCH_HTML, 5).unwrap();
        assert_eq!(results.len(), 3);
        assert_eq!(
            results[0].title,
            "PostgreSQL: Documentation: 18: 13.2. Transaction Isolation"
        );
        assert_eq!(
            results[0].url,
            "https://www.postgresql.org/docs/current/transaction-iso.html"
        );
        assert!(results[0].snippet.contains("Transaction Isolation"));
        assert_eq!(
            results[1].title,
            "PostgreSQL: Documentation: 18: SET TRANSACTION"
        );
        assert!(results[1].snippet.contains("serializable transaction"));
        assert_eq!(results[2].snippet, "Quotes \" and apostrophes ' plus &.");
    }

    #[test]
    fn respects_result_limit() {
        let results = parse_results(CURRENT_SEARCH_HTML, 1).unwrap();
        assert_eq!(results.len(), 1);
        assert_eq!(
            results[0].url,
            "https://www.postgresql.org/docs/current/transaction-iso.html"
        );
    }

    #[test]
    fn decodes_standard_html_entities() {
        assert_eq!(
            clean_html("A&nbsp;&amp;&nbsp;B &quot;quoted&quot; &#39;ok&#39; &#x3C;tag&#x3E;"),
            "A & B \"quoted\" 'ok' <tag>"
        );
    }
}
