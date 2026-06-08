# CLI Workflows

Use the Homebrew `chrome-devtools` command for shell-friendly browser control.
State persists across commands through its background server. Do not run
`start`, `status`, or `stop` before every normal command; reserve them for setup
or cleanup.

## Basic checks

```sh
chrome-devtools --version
chrome-devtools status
chrome-devtools list_pages
chrome-devtools new_page "https://example.com"
chrome-devtools take_snapshot
```

## Navigation

```sh
chrome-devtools list_pages
chrome-devtools select_page 1 --bringToFront true
chrome-devtools navigate_page --url "https://example.com"
chrome-devtools navigate_page --type reload --ignoreCache true
chrome-devtools new_page "https://example.com" --background true
chrome-devtools close_page 1
```

## Input automation

Take a fresh snapshot first and use the returned element `uid`s:

```sh
chrome-devtools take_snapshot
chrome-devtools click "1_4" --includeSnapshot true
chrome-devtools fill "1_7" "hello"
chrome-devtools press_key "Enter"
chrome-devtools type_text "hello" --submitKey "Enter"
chrome-devtools upload_file "1_9" "/path/to/file.txt"
```

If an element is not found, take a new snapshot. The page may have re-rendered
and changed the `uid`s.

## Inspection

```sh
chrome-devtools evaluate_script "() => document.title"
chrome-devtools evaluate_script "(el) => el.innerText" --args "1_4"
chrome-devtools list_console_messages --pageSize 50
chrome-devtools get_console_message 1
chrome-devtools list_network_requests --pageSize 50
chrome-devtools get_network_request --reqid 3 --requestFilePath req.md --responseFilePath res.md
chrome-devtools take_screenshot --filePath page.png
chrome-devtools take_snapshot --verbose true --filePath snapshot.txt
```

Prefer `take_snapshot` for automation and `take_screenshot` for visual evidence.
Use file path arguments for large outputs.

## Emulation and performance

```sh
chrome-devtools emulate --viewport "390x844" --colorScheme dark
chrome-devtools emulate --networkConditions "Fast 3G" --cpuThrottlingRate 4
chrome-devtools resize_page 1280 720
chrome-devtools lighthouse_audit --mode navigation --outputDirPath ./lighthouse
chrome-devtools performance_start_trace --reload true --autoStop true --filePath trace.json
chrome-devtools performance_analyze_insight "1" "LCPBreakdown"
```

## Extensions and experimental tools

Extension commands require the MCP server category flag:

```sh
chrome-devtools list_extensions
chrome-devtools install_extension "/path/to/unpacked-extension"
chrome-devtools trigger_extension_action "extension_id"
```

If extension tools are missing, restart the underlying MCP server with
`--categoryExtensions=true`. Some extension workflows cannot use `--autoConnect`
on older Chrome versions.
