# Recovery Validation

Load this reference only when resuming from a ledger Recovery Packet. It
validates the compact projection before any mutation or dispatch; the ledger,
source items, canonical options, permissions, and gates remain authoritative.
`options.md` owns the option-row schema and evidence encoding; this file only
validates and fingerprints their ledger projection.

On resume:

1. Read only the ledger `## Recovery Packet`.
2. Recompute the packet Content fingerprint from every derived packet field,
   excluding `Status`, `Updated`, `Projection fingerprint`, and `Content
   fingerprint`. Require it to match both the packet value and the
   `Recovery packet content fingerprint` stored under authoritative
   `## Active Root`. Use this canonical extraction:

   ```bash
   awk '
     /^## Recovery Packet$/ { inside=1; next }
     /^## Worker And Delivery References$/ { exit }
     inside && $0 !~ /^(Status|Updated|Projection fingerprint|Content fingerprint):/ { print }
   ' "$ledger" | shasum -a 256
   ```

3. Recompute the packet's Projection fingerprint from the authoritative ledger
   and require an exact match. Hash all ledger content before `## Notes`,
   excluding the complete `## Recovery Packet` section, with this canonical
   extraction:

   ```bash
   awk '
     /^## Recovery Packet$/ { skip=1; next }
     /^## Worker And Delivery References$/ { skip=0 }
     /^## Notes$/ { exit }
     !skip { print }
   ' "$ledger" | shasum -a 256
   ```

4. Require the packet Source checkpoint IDs to equal the complete current set
   of in-scope registered source item IDs represented across every current
   `## Workstreams` status bucket, not the discovery feed IDs. Recompute each
   underlying issue, PR, checklist, file, commit, CI, or other source-item
   fingerprint; reject missing or extra checkpoints. Separately require packet
   Workstream checkpoint IDs to equal every authoritative workstream entry in
   every status bucket: active `#### <workstream-id>:` headings plus each
   non-active `workstream_id=<stable-id>` prefix. Reject a missing, extra, or
   duplicate workstream checkpoint even when its source checkpoint is present.
   For each checkpoint with a non-`not-applicable`
   `delivery_permission_source_issue_ref` or
   `issue_update_permission_source_issue_ref`, re-read that generated issue's
   current `## Orchestrator Handoff` evidence. Preserve independent issue-update
   evidence and require matching scope, target, branch, and transfer tokens.
   Trim only outer whitespace, encode a literal `|` as `%7C`, hash each evidence
   value independently with SHA-256, and require the live values to match the
   packet fingerprints. Reject an issue ref that is not the checkpoint's
   registered source item.
5. Require packet repo checkpoint realpaths to equal the complete canonical
   in-scope and claimed repo set from `## Scope` and `## Active Root`; reject
   missing or extra repos. Recompute every HEAD, branch, and
   `git status --short` fingerprint and verify the root claim plus active-worker
   state still match. Parse the authoritative `Active workers` rows, reject
   duplicate worker IDs or malformed execution locations, and require their
   exact ID set to match the packet. Require every listed `workstream_ids`
   assignment to exist in the authoritative active workstream bucket and to
   match that workstream's `worker=<id>` and `actual_execution_location`
   evidence. Count `background-codex-subagent` and `visible-codex-app-task`
   workers against `max_concurrent_delegated_workers`; count only visible App
   tasks against `max_visible_app_tasks`.
6. If every check matches, mark the packet `fresh`. Load the packet's exact
   session and scoped `## Option Resolution` row IDs, recompute their canonical
   rows fingerprint, and require it to match `rows_fingerprint`. Derive
   discovery-source and workstream scope IDs from the authoritative ledger;
   registered source-item checkpoints are freshness evidence, not separate
   option scopes. Require the packet row IDs to equal the exact current field
   sets owned by `options.md`. Reject duplicate, omitted, extra, invalid,
   out-of-scope, or retired rows. Serialize only the referenced rows as
   tab-separated `row_id,scope_id,field,value,source,evidence`, sort bytewise by
   `row_id`, and hash the resulting lines. Cells must not contain a literal
   `|`; encode it as `%7C`.

   ```bash
   OPTION_ROW_IDS='<comma-separated union of packet session_rows and scoped_rows>'
   set -o pipefail
   OPTION_SOURCE_SCOPE_IDS="$(
     awk -F '|' '
       function norm(value) { gsub(/^[[:space:]]+|[[:space:]]+$/, "", value); return value }
       /^## Discovery Sources$/ { sources=1; next }
       /^## Active Root$/ { exit }
       sources && /^\|/ {
         if (NF != 10) next
         id=norm($2)
         if (id == "Source ID" || id ~ /^:?-+:?$/) next
         if (id !~ /^[A-Za-z0-9:_-]+$/) exit 51
         print "source:" id
       }
     ' "$ledger" | LC_ALL=C sort | awk 'seen[$0]++ { exit 52 } { print }' | paste -sd, -
   )" || exit 52
   OPTION_WORKSTREAM_SCOPE_IDS="$(
     awk '
       /^## Workstreams$/ { workstreams=1; next }
       /^## Wave Reports$/ { exit }
       workstreams && /^#### [A-Za-z0-9:_-]+: / {
         id=$0; sub(/^#### /, "", id); sub(/: .*/, "", id); print "workstream:" id
       }
       workstreams && /^- workstream_id=[A-Za-z0-9:_-]+;/ {
         id=$0; sub(/^- workstream_id=/, "", id); sub(/;.*/, "", id); print "workstream:" id
       }
     ' "$ledger" | LC_ALL=C sort | awk 'seen[$0]++ { exit 52 } { print }' | paste -sd, -
   )" || exit 52
   OPTION_SCOPE_IDS="$OPTION_SOURCE_SCOPE_IDS${OPTION_SOURCE_SCOPE_IDS:+${OPTION_WORKSTREAM_SCOPE_IDS:+,}}$OPTION_WORKSTREAM_SCOPE_IDS"
   ACTIVE_WORKER_ROWS="$(
     awk '
       /^Active workers:$/ { workers=1; next }
       /^Takeover history:$/ { exit }
       workers && /^- none$/ { next }
       workers && /^- worker_id=[A-Za-z0-9:_-]+; actual_execution_location=(background-codex-subagent|visible-codex-app-task); workstream_ids=[A-Za-z0-9,:_-]+$/ {
         line=$0; sub(/^- worker_id=/, "", line); split(line, parts, "; ")
         id=parts[1]; location=parts[2]; sub(/^actual_execution_location=/, "", location)
         assignments=parts[3]; sub(/^workstream_ids=/, "", assignments)
         print id "\t" location "\t" assignments; next
       }
       workers && /^-/ { exit 53 }
     ' "$ledger" | LC_ALL=C sort | awk -F '\t' 'seen[$1]++ { exit 53 } { print }'
   )" || exit 53
   PACKET_ACTIVE_WORKER_IDS="$(
     awk '
       function norm(value) { gsub(/^[[:space:]]+|[[:space:]]+$/, "", value); return value }
       /^## Recovery Packet$/ { packet=1; next }
       /^## Worker And Delivery References$/ { exit }
       packet && /^Root: / {
         roots++; count=split($0, parts, ";"); workers=""
         for (i=1; i <= count; i++) {
           item=norm(parts[i]); if (item ~ /^active_workers=/) { workers=item; sub(/^active_workers=/, "", workers) }
         }
         if (workers == "none") next
         if (workers == "") exit 55
         worker_count=split(workers, ids, ",")
         for (i=1; i <= worker_count; i++) {
           id=norm(ids[i]); if (id !~ /^[A-Za-z0-9:_-]+$/) exit 55; print id
         }
       }
       END { if (roots != 1) exit 55 }
     ' "$ledger" | LC_ALL=C sort | awk 'seen[$0]++ { exit 55 } { print }' | paste -sd, -
   )" || exit 55
   PACKET_OPTION_ROWS_FINGERPRINT="$(
     awk '
       function norm(value) { gsub(/^[[:space:]]+|[[:space:]]+$/, "", value); return value }
       /^## Recovery Packet$/ { packet=1; next }
       /^## Worker And Delivery References$/ { exit }
       packet && /^Option resolution refs: / {
         refs++; count=split($0, parts, ";"); fingerprint=""
         for (i=1; i <= count; i++) {
           item=norm(parts[i]); if (item ~ /^rows_fingerprint=/) { fingerprint=item; sub(/^rows_fingerprint=/, "", fingerprint) }
         }
         if (fingerprint !~ /^[0-9a-f]{64}$/) exit 56; print fingerprint
       }
       END { if (refs != 1) exit 56 }
     ' "$ledger"
   )" || exit 56
   ACTIVE_WORKER_IDS="$(printf '%s\n' "$ACTIVE_WORKER_ROWS" | awk -F '\t' 'NF { print $1 }' | LC_ALL=C sort | paste -sd, -)"
   [ "$PACKET_ACTIVE_WORKER_IDS" = "$ACTIVE_WORKER_IDS" ] || exit 55
   ACTIVE_WORKSTREAM_ROWS="$(
     awk -F '|' '
       function norm(value) { gsub(/^[[:space:]]+|[[:space:]]+$/, "", value); return value }
       function token_value(value, key, count, parts, i, item, prefix) {
         count=split(value, parts, ";"); prefix=key "="
         for (i=1; i <= count; i++) { item=norm(parts[i]); if (substr(item, 1, length(prefix)) == prefix) return substr(item, length(prefix) + 1) }
         return ""
       }
       /^## Workstreams$/ { workstreams=1; next }
       workstreams && /^### active$/ { active=1; next }
       active && /^### / { exit }
       active && /^#### [A-Za-z0-9:_-]+: / {
         workstream=$0; sub(/^#### /, "", workstream); sub(/: .*/, "", workstream); worker=""; next
       }
       active && /^\| Repo \/ execution location \|/ { worker=token_value(norm($3), "worker"); next }
       active && /^\| Worker evidence \|/ {
         location=token_value(norm($3), "actual_execution_location")
         if (workstream == "" || worker !~ /^[A-Za-z0-9:_-]+$/ || location !~ /^(current-orchestrator-session|background-codex-subagent|visible-codex-app-task)$/) exit 54
         if (location == "current-orchestrator-session" && worker != "root") exit 54
         print workstream "\t" worker "\t" location
       }
     ' "$ledger" | LC_ALL=C sort -t $'\t' -k1,1
   )" || exit 54
   {
     printf '%s\n' "$ACTIVE_WORKER_ROWS" | awk -F '\t' 'NF { print "worker\t" $0 }'
     printf '%s\n' "$ACTIVE_WORKSTREAM_ROWS" | awk -F '\t' 'NF { print "workstream\t" $0 }'
   } | awk -F '\t' '
     $1 == "worker" {
       worker=$2; location=$3; count=split($4, workstreams, ",")
       for (i=1; i <= count; i++) {
         workstream=workstreams[i]
         if (workstream !~ /^[A-Za-z0-9:_-]+$/ || assigned[workstream]++) exit 54
         assigned_worker[workstream]=worker; assigned_location[workstream]=location
       }
       next
     }
     $1 == "workstream" {
       workstream=$2; if (authoritative[workstream]++) exit 54
       authoritative_worker[workstream]=$3; authoritative_location[workstream]=$4
     }
     END {
       for (workstream in assigned)
         if (!(workstream in authoritative) || assigned_worker[workstream] != authoritative_worker[workstream] || assigned_location[workstream] != authoritative_location[workstream]) exit 54
       for (workstream in authoritative) {
         if (authoritative_location[workstream] ~ /^(background-codex-subagent|visible-codex-app-task)$/ && !(workstream in assigned)) exit 54
         if (authoritative_location[workstream] == "current-orchestrator-session" && workstream in assigned) exit 54
       }
     }
   ' || exit 54
   ACTIVE_DELEGATED_WORKER_COUNT="$(printf '%s\n' "$ACTIVE_WORKER_ROWS" | awk 'NF { count++ } END { print count + 0 }')"
   ACTIVE_APP_WORKER_COUNT="$(printf '%s\n' "$ACTIVE_WORKER_ROWS" | awk -F '\t' '$2 == "visible-codex-app-task" { count++ } END { print count + 0 }')"
   OPTION_BRANCH_NAMES="$(
     awk -F '|' -v scopes="$OPTION_SCOPE_IDS" '
       BEGIN { count=split(scopes, ids, ","); for (i=1; i <= count; i++) if (ids[i] != "") applicable_scope[ids[i]]=1 }
       function norm(value) {
         gsub(/^[[:space:]]+|[[:space:]]+$/, "", value)
         if (length(value) >= 2 && substr(value, 1, 1) == "`" && substr(value, length(value), 1) == "`") value=substr(value, 2, length(value) - 2)
         return value
       }
       /^## Option Resolution$/ { options=1; next }
       /^## Discovery Sources$/ { exit }
       options && /^\|/ && norm($4) == "target_branch_name" && norm($3) in applicable_scope { print norm($5) }
     ' "$ledger"
   )"
   while IFS= read -r target_branch_name; do
     [ -z "$target_branch_name" ] && continue
     [ "$target_branch_name" = "not-applicable" ] || git check-ref-format --branch "$target_branch_name" >/dev/null 2>&1 || exit 50
   done < <(printf '%s\n' "$OPTION_BRANCH_NAMES")
   COMPUTED_OPTION_ROWS_FINGERPRINT="$(
     awk -F '|' -v wanted="$OPTION_ROW_IDS" -v scopes="$OPTION_SCOPE_IDS" -v active_delegated_count="$ACTIVE_DELEGATED_WORKER_COUNT" -v active_app_count="$ACTIVE_APP_WORKER_COUNT" '
       BEGIN {
         split("work_delegation_policy delegated_worker_visibility max_concurrent_delegated_workers visible_app_task_permission max_visible_app_tasks unmanaged_git_worktree_fallback_permission existing_orchestrator_session_takeover_policy repository_layout", fields, " ")
         for (i in fields) expected_session[fields[i]]=1
         expected_source["tracked_work_item_update_permission"]=1
         split("tracked_work_item_update_permission change_delivery_permission issue_update_permission pull_request_merge_permission pull_request_merge_confirmation starting_checkout_branch_handling scheduled_automation_change_permission temporary_source_execution_permission completion_evidence_policy change_delivery_target delivery_decision_origin workstream_repository_layout codex_review_requirement pull_request_count_strategy issue_completion_method target_branch_name target_pull_request_ref delivery_permission_source_issue_ref issue_update_permission_source_issue_ref", fields, " ")
         for (i in fields) expected_workstream[fields[i]]=1
         count=split(wanted, ids, ",")
         for (i=1; i <= count; i++) if (ids[i] != "") { requested[ids[i]]++; selected[ids[i]]=1 }
         scope_count=split(scopes, scope_ids, ",")
         for (i=1; i <= scope_count; i++) {
           if (scope_ids[i] == "") continue
           applicable_scope[scope_ids[i]]=1
           if (scope_ids[i] ~ /^source:/) applicable_source_scope[scope_ids[i]]=1
           else if (scope_ids[i] ~ /^workstream:/) applicable_workstream_scope[scope_ids[i]]=1
           else invalid=45
         }
       }
       function norm(value) {
         gsub(/^[[:space:]]+|[[:space:]]+$/, "", value)
         if (length(value) >= 2 && substr(value, 1, 1) == "`" && substr(value, length(value), 1) == "`") value=substr(value, 2, length(value) - 2)
         return value
       }
       function matches(value, choices) { return value ~ ("^(" choices ")$") }
       function token_value(evidence, key, count, parts, i, prefix) {
         count=split(evidence, parts, ";"); prefix=key "="
         for (i=1; i <= count; i++) if (substr(parts[i], 1, length(prefix)) == prefix) return substr(parts[i], length(prefix) + 1)
         return ""
       }
       function permission_binding_matches(left, right, permission_ref, scope_ref, target_ref) {
         permission_ref=token_value(left, "permission-source-ref")
         scope_ref=token_value(left, "scope-ref")
         target_ref=token_value(left, "target-ref")
         return permission_ref != "" && scope_ref != "" && target_ref != "" &&
           token_value(right, "permission-source-ref") == permission_ref &&
           token_value(right, "scope-ref") == scope_ref &&
           token_value(right, "target-ref") == target_ref
       }
       function permission_bearing(field, value) {
         if (field == "visible_app_task_permission" && value == "granted-by-authorized-user") return 1
         if (field == "unmanaged_git_worktree_fallback_permission" && value == "granted-by-authorized-user") return 1
         if (field == "tracked_work_item_update_permission" && matches(value, "propose-updates-only|apply-updates")) return 1
         if (field == "change_delivery_permission" && value == "granted-for-selected-target") return 1
         if (field == "issue_update_permission" && matches(value, "pull-request-closing-keyword-only|direct-issue-updates-explicitly-authorized")) return 1
         if (field == "pull_request_merge_permission" && value == "granted-for-named-pull-request") return 1
         if (field == "pull_request_merge_confirmation" && value == "merge-automatically-after-checks") return 1
         if (field == "starting_checkout_branch_handling" && value == "branch-switch-authorized") return 1
         if (field == "scheduled_automation_change_permission" && value == "granted-by-authorized-user") return 1
         if (field == "temporary_source_execution_permission" && value == "granted-by-authorized-user") return 1
         if (field == "completion_evidence_policy" && value == "allow-simulated-evidence-by-authorized-user-exception") return 1
         if (field == "work_delegation_policy" && value == "orchestrator-decides-with-concurrent-worker-limit") return 1
         if (field == "delivery_decision_origin" && matches(value, "overridden-by-implementation-issue|specified-by-authorized-user")) return 1
         if (field == "codex_review_requirement" && value == "explicitly-skipped-by-authorized-user") return 1
         return 0
       }
       function allowed_value(field, value) {
         if (field == "work_delegation_policy") return matches(value, "orchestrator-decides-for-each-implementation-workstream|run-all-work-in-current-orchestrator-session|orchestrator-decides-with-concurrent-worker-limit")
         if (field == "delegated_worker_visibility") return matches(value, "orchestrator-decides-between-background-and-visible-workers|background-codex-subagents-only|visible-codex-app-tasks-only|not-applicable")
         if (field == "max_concurrent_delegated_workers") return matches(value, "not-limited-by-authorized-user|not-applicable|[1-9][0-9]*")
         if (field == "visible_app_task_permission") return matches(value, "not-requested|granted-by-authorized-user|denied-by-authorized-user")
         if (field == "max_visible_app_tasks") return matches(value, "not-applicable|[1-9][0-9]*")
         if (field == "unmanaged_git_worktree_fallback_permission") return matches(value, "not-granted|granted-by-authorized-user")
         if (field == "existing_orchestrator_session_takeover_policy") return matches(value, "ask-authorized-user-before-takeover|take-over-only-if-existing-ledger-is-stale")
         if (field == "repository_layout" || field == "workstream_repository_layout") return matches(value, "single-repository|monorepo|multi-repository-workspace")
         if (field == "tracked_work_item_update_permission") return matches(value, "read-only|propose-updates-only|apply-updates")
         if (field == "change_delivery_permission") return matches(value, "not-required-for-uncommitted-changes|not-granted|granted-for-selected-target")
         if (field == "issue_update_permission") return matches(value, "no-issue-changes|pull-request-closing-keyword-only|direct-issue-updates-explicitly-authorized")
         if (field == "pull_request_merge_permission") return matches(value, "not-granted|granted-for-named-pull-request")
         if (field == "pull_request_merge_confirmation") return matches(value, "ask-authorized-user-after-checks|merge-automatically-after-checks")
         if (field == "starting_checkout_branch_handling") return matches(value, "keep-current-branch-checked-out|branch-switch-authorized|not-applicable")
         if (field == "scheduled_automation_change_permission" || field == "temporary_source_execution_permission") return matches(value, "not-granted|granted-by-authorized-user")
         if (field == "completion_evidence_policy") return matches(value, "require-live-system-evidence|allow-simulated-evidence-by-authorized-user-exception")
         if (field == "change_delivery_target") return matches(value, "validated-changes-left-uncommitted|local-commit-created-without-pushing|changes-pushed-to-target-branch-without-pull-request|validated-draft-pull-request-published|pull-request-ready-for-merge-but-not-merged")
         if (field == "delivery_decision_origin") return matches(value, "safe-default-for-ad-hoc-work|inherited-from-feature-spec|overridden-by-implementation-issue|specified-by-authorized-user")
         if (field == "codex_review_requirement") return matches(value, "required-on-current-pull-request-head|explicitly-skipped-by-authorized-user|not-needed-for-selected-delivery-target")
         if (field == "pull_request_count_strategy") return matches(value, "one-pull-request-total|one-pull-request-per-repository|no-pull-request")
         if (field == "issue_completion_method") return matches(value, "feature-pull-request-closing-keyword|repository-pull-request-closing-keyword|final-commit-closing-keyword|move-local-issue-to-done-after-proof|no-issue-completion")
         if (field == "target_branch_name") return value == "not-applicable" || value != ""
         if (field == "target_pull_request_ref") return matches(value, "not-applicable|pending|[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+#[1-9][0-9]*")
         if (field == "delivery_permission_source_issue_ref" || field == "issue_update_permission_source_issue_ref") return matches(value, "not-applicable|issue:[A-Za-z0-9:_-]+")
         return 0
       }
       function allowed_source(field, value, source) {
         if (field == "repository_layout") return matches(source, "project-layout-config|runtime-derived|authorized-user-instruction")
         if (field == "workstream_repository_layout") return matches(source, "source-contract|runtime-derived|authorized-user-instruction")
         if (field == "max_concurrent_delegated_workers") {
           if (value == "not-limited-by-authorized-user") return matches(source, "default|authorized-user-instruction")
           if (value == "not-applicable") return matches(source, "default|runtime-derived|runtime-capability")
           return source == "authorized-user-instruction"
         }
         if (field == "max_visible_app_tasks") return value == "not-applicable" ? matches(source, "default|runtime-derived|runtime-capability") : source == "authorized-user-instruction"
         if (field == "work_delegation_policy" || field == "delegated_worker_visibility") return matches(source, "default|authorized-user-instruction|runtime-capability")
         if (field == "visible_app_task_permission") return value == "not-requested" ? source == "default" : source == "authorized-user-instruction"
         if (field == "unmanaged_git_worktree_fallback_permission") return value == "not-granted" ? matches(source, "default|runtime-capability") : source == "authorized-user-instruction"
         if (field == "existing_orchestrator_session_takeover_policy") return value == "ask-authorized-user-before-takeover" ? source == "default" : source == "authorized-user-instruction"
         if (field == "tracked_work_item_update_permission") return value == "read-only" ? matches(source, "default|runtime-capability") : matches(source, "authorized-user-instruction|source-contract")
         if (field == "change_delivery_permission") {
           if (value == "not-required-for-uncommitted-changes") return matches(source, "default|runtime-derived")
           if (value == "not-granted") return matches(source, "default|runtime-capability|runtime-derived|authorized-user-instruction")
           return matches(source, "source-contract|authorized-user-instruction")
         }
         if (field == "issue_update_permission") {
           if (value == "no-issue-changes") return matches(source, "default|runtime-derived|runtime-capability")
           return matches(source, "source-contract|authorized-user-instruction")
         }
         if (field == "pull_request_merge_permission") return value == "not-granted" ? matches(source, "default|runtime-capability") : source == "authorized-user-instruction"
         if (field == "pull_request_merge_confirmation") return value == "ask-authorized-user-after-checks" ? source == "default" : source == "authorized-user-instruction"
         if (field == "starting_checkout_branch_handling") return value == "branch-switch-authorized" ? source == "authorized-user-instruction" : matches(source, "default|runtime-derived")
         if (field == "scheduled_automation_change_permission" || field == "temporary_source_execution_permission") return value == "not-granted" ? matches(source, "default|runtime-capability|runtime-derived|source-contract") : source == "authorized-user-instruction"
         if (field == "completion_evidence_policy") return value == "require-live-system-evidence" ? matches(source, "default|source-contract") : source == "authorized-user-instruction"
         if (field == "change_delivery_target") return value == "validated-changes-left-uncommitted" ? matches(source, "default|runtime-derived|authorized-user-instruction") : matches(source, "source-contract|authorized-user-instruction")
         if (field == "delivery_decision_origin") {
           if (value == "safe-default-for-ad-hoc-work") return matches(source, "default|runtime-derived")
           if (value == "inherited-from-feature-spec") return source == "source-contract"
           return matches(source, "source-contract|authorized-user-instruction")
         }
         if (field == "target_branch_name") return value == "not-applicable" ? matches(source, "default|runtime-derived") : matches(source, "source-contract|authorized-user-instruction")
         if (field == "target_pull_request_ref") return source == "runtime-derived"
         if (field == "delivery_permission_source_issue_ref" || field == "issue_update_permission_source_issue_ref") return value == "not-applicable" ? matches(source, "default|runtime-derived") : source == "source-contract"
         if (field == "codex_review_requirement") {
           if (value == "required-on-current-pull-request-head") return matches(source, "default|source-contract")
           if (value == "explicitly-skipped-by-authorized-user") return source == "authorized-user-instruction"
           return matches(source, "default|runtime-derived|source-contract")
         }
         if (field == "pull_request_count_strategy" || field == "issue_completion_method") return matches(source, "source-contract|runtime-derived|default")
         return 0
       }
       /^## Option Resolution$/ { options=1; next }
       /^## Discovery Sources$/ { exit }
       options && /^\|/ {
         if (NF != 8) { invalid=45; next }
         row_id=norm($2)
         if (row_id == "row_id" && norm($3) == "scope_id" && norm($4) == "field" && norm($5) == "value" && norm($6) == "source" && norm($7) == "evidence") next
         if (row_id ~ /^:?-+:?$/ && norm($3) ~ /^:?-+:?$/ && norm($4) ~ /^:?-+:?$/ && norm($5) ~ /^:?-+:?$/ && norm($6) ~ /^:?-+:?$/ && norm($7) ~ /^:?-+:?$/) next
         if (row_id == "") { invalid=45; next }
         scope_id=norm($3); field=norm($4); value=norm($5); source=norm($6); evidence=norm($7)
         is_applicable=(scope_id == "session" || scope_id in applicable_scope)
         if (is_applicable) {
           applicable[row_id]++
           expected_id=(scope_id == "session" ? "session:" field : scope_id ":" field)
           if (row_id != expected_id) invalid=45
           if (scope_id == "session" && !(field in expected_session)) invalid=45
           if (scope_id in applicable_source_scope && !(field in expected_source)) invalid=45
           if (scope_id in applicable_workstream_scope && !(field in expected_workstream)) invalid=45
           if (!allowed_value(field, value) || !allowed_source(field, value, source)) invalid=46
           if (matches(source, "authorized-user-instruction|source-contract|runtime-capability|project-layout-config") && (evidence == "" || evidence == "none")) invalid=47
           permission_ref=token_value(evidence, "permission-source-ref")
           if (permission_bearing(field, value)) {
             if (permission_ref == "" || token_value(evidence, "scope-ref") != scope_id || token_value(evidence, "target-ref") == "") invalid=49
             if (source == "authorized-user-instruction" && permission_ref !~ /^authorized-user:/) invalid=49
             if (source == "source-contract" && permission_ref !~ /^(authorized-user:|feature-spec-default:)/) invalid=49
             if (permission_ref ~ /^feature-spec-default:/ && !matches(field, "change_delivery_permission|issue_update_permission")) invalid=49
             if (field == "issue_update_permission" && value == "direct-issue-updates-explicitly-authorized" && permission_ref !~ /^authorized-user:/) invalid=49
           }
           present[scope_id SUBSEP field]++; resolved[scope_id SUBSEP field]=value
           row_evidence[scope_id SUBSEP field]=evidence; row_source[scope_id SUBSEP field]=source
         }
         if (!is_applicable) out_of_scope[row_id]=1
         if (!(row_id in selected)) next
         seen[row_id]++
         print row_id "\t" scope_id "\t" field "\t" value "\t" source "\t" evidence
       }
       END {
         if (invalid) exit invalid
         for (row_id in requested) if (requested[row_id] != 1) exit 41
         for (row_id in selected) if (seen[row_id] != 1) exit 42
         for (row_id in applicable) if (applicable[row_id] != 1 || !(row_id in selected)) exit 43
         for (row_id in out_of_scope) exit 44
         for (field in expected_session) if (present["session" SUBSEP field] != 1) exit 45
         for (scope_id in applicable_source_scope) for (field in expected_source) if (present[scope_id SUBSEP field] != 1) exit 45
         for (scope_id in applicable_workstream_scope) for (field in expected_workstream) if (present[scope_id SUBSEP field] != 1) exit 45

         policy=resolved["session" SUBSEP "work_delegation_policy"]
         visibility=resolved["session" SUBSEP "delegated_worker_visibility"]
         concurrency_limit=resolved["session" SUBSEP "max_concurrent_delegated_workers"]
         app_permission=resolved["session" SUBSEP "visible_app_task_permission"]
         app_limit=resolved["session" SUBSEP "max_visible_app_tasks"]
         if (policy == "run-all-work-in-current-orchestrator-session" && (visibility != "not-applicable" || concurrency_limit != "not-applicable" || active_delegated_count != 0)) exit 48
         if (policy == "orchestrator-decides-for-each-implementation-workstream" && concurrency_limit != "not-limited-by-authorized-user") exit 48
         if (policy == "orchestrator-decides-with-concurrent-worker-limit") {
           if (concurrency_limit !~ /^[1-9][0-9]*$/ || active_delegated_count > concurrency_limit + 0) exit 48
           if (!permission_binding_matches(row_evidence["session" SUBSEP "work_delegation_policy"], row_evidence["session" SUBSEP "max_concurrent_delegated_workers"])) exit 49
         }
         if (visibility == "not-applicable" && policy != "run-all-work-in-current-orchestrator-session") exit 48
         if (visibility == "background-codex-subagents-only" && active_app_count != 0) exit 48
         if (visibility == "visible-codex-app-tasks-only" && active_delegated_count != active_app_count) exit 48
         if (app_permission != "granted-by-authorized-user" && (app_limit != "not-applicable" || active_app_count != 0)) exit 48
         if (app_permission == "granted-by-authorized-user" && (app_limit !~ /^[1-9][0-9]*$/ || active_app_count > app_limit + 0)) exit 48
         if (app_permission == "granted-by-authorized-user" && !permission_binding_matches(row_evidence["session" SUBSEP "visible_app_task_permission"], row_evidence["session" SUBSEP "max_visible_app_tasks"])) exit 49
         if (visibility == "visible-codex-app-tasks-only" && app_permission != "granted-by-authorized-user") exit 48

         for (scope_id in applicable_workstream_scope) {
           delivery=resolved[scope_id SUBSEP "change_delivery_target"]
           permission=resolved[scope_id SUBSEP "change_delivery_permission"]
           permission_ref=token_value(row_evidence[scope_id SUBSEP "change_delivery_permission"], "permission-source-ref")
           branch=resolved[scope_id SUBSEP "target_branch_name"]
           pr_ref=resolved[scope_id SUBSEP "target_pull_request_ref"]
           review=resolved[scope_id SUBSEP "codex_review_requirement"]
           shape=resolved[scope_id SUBSEP "pull_request_count_strategy"]
           completion=resolved[scope_id SUBSEP "issue_completion_method"]
           issue_permission=resolved[scope_id SUBSEP "issue_update_permission"]
           issue_permission_ref=token_value(row_evidence[scope_id SUBSEP "issue_update_permission"], "permission-source-ref")
           origin=resolved[scope_id SUBSEP "delivery_decision_origin"]
           delivery_transfer=resolved[scope_id SUBSEP "delivery_permission_source_issue_ref"]
           issue_transfer=resolved[scope_id SUBSEP "issue_update_permission_source_issue_ref"]

           if (resolved[scope_id SUBSEP "pull_request_merge_confirmation"] == "merge-automatically-after-checks" && resolved[scope_id SUBSEP "pull_request_merge_permission"] != "granted-for-named-pull-request") exit 48
           if (delivery == "validated-changes-left-uncommitted") {
             if (permission != "not-required-for-uncommitted-changes" || branch != "not-applicable" || pr_ref != "not-applicable" || review != "not-needed-for-selected-delivery-target" || shape != "no-pull-request" || completion != "no-issue-completion" || delivery_transfer != "not-applicable" || issue_transfer != "not-applicable") exit 48
           } else {
             if (permission == "not-required-for-uncommitted-changes" || branch == "not-applicable" || origin == "safe-default-for-ad-hoc-work") exit 48
             if (permission == "granted-for-selected-target") {
               permission_evidence=row_evidence[scope_id SUBSEP "change_delivery_permission"]
               if (token_value(permission_evidence, "target-branch") != branch) exit 48
             }
             if (matches(origin, "inherited-from-feature-spec|overridden-by-implementation-issue") && delivery_transfer == "not-applicable") exit 48
           }
           if ((permission_ref ~ /^feature-spec-default:/ || issue_permission_ref ~ /^feature-spec-default:/) && delivery != "pull-request-ready-for-merge-but-not-merged") exit 48
           if (permission_ref ~ /^feature-spec-default:/ && permission != "granted-for-selected-target") exit 48
           if (issue_permission_ref ~ /^feature-spec-default:/ && issue_permission != "pull-request-closing-keyword-only") exit 48
           if (matches(delivery, "local-commit-created-without-pushing|changes-pushed-to-target-branch-without-pull-request") && (pr_ref != "not-applicable" || shape != "no-pull-request" || review != "not-needed-for-selected-delivery-target")) exit 48
           if (delivery == "validated-draft-pull-request-published" && (pr_ref == "not-applicable" || !matches(shape, "one-pull-request-total|one-pull-request-per-repository") || review != "not-needed-for-selected-delivery-target")) exit 48
           if (delivery == "pull-request-ready-for-merge-but-not-merged" && (pr_ref == "not-applicable" || !matches(shape, "one-pull-request-total|one-pull-request-per-repository") || !matches(review, "required-on-current-pull-request-head|explicitly-skipped-by-authorized-user"))) exit 48
           if (matches(completion, "feature-pull-request-closing-keyword|repository-pull-request-closing-keyword") && (!matches(delivery, "validated-draft-pull-request-published|pull-request-ready-for-merge-but-not-merged") || !matches(issue_permission, "pull-request-closing-keyword-only|direct-issue-updates-explicitly-authorized"))) exit 48
           if (completion == "final-commit-closing-keyword" && (delivery != "changes-pushed-to-target-branch-without-pull-request" || issue_permission != "direct-issue-updates-explicitly-authorized")) exit 48
           if (issue_permission == "no-issue-changes" && issue_transfer != "not-applicable") exit 48
           if (review == "explicitly-skipped-by-authorized-user") {
             review_evidence=row_evidence[scope_id SUBSEP "codex_review_requirement"]
             named_pr=token_value(review_evidence, "pr-ref")
             if (named_pr != "" && named_pr != "not-applicable" && named_pr != pr_ref) exit 48
           }
         }
       }
     ' "$ledger" | LC_ALL=C sort -t $'\t' -k1,1 | shasum -a 256 | awk '{ print $1 }'
   )" || exit 56
   [ "$COMPUTED_OPTION_ROWS_FINGERPRINT" = "$PACKET_OPTION_ROWS_FINGERPRINT" ] || exit 56
   printf '%s\n' "$COMPUTED_OPTION_ROWS_FINGERPRINT"
   ```

   For every non-`not-applicable` transfer, hash the normalized evidence cells
   of the workstream's `delivery_permission_source_issue_ref` and
   `issue_update_permission_source_issue_ref` rows and require them to equal the
   checkpoint's separately live-verified delivery and issue-update
   fingerprints. Then load only the packet's named workstream rows, gate rows,
   sources, proofs, and other references. Do not dispatch or mutate when an
   option row is missing, extra, mismatched, retired, or scoped to another
   source or workstream.
7. If any check differs, mark it `stale` or `invalid`; do not mutate or dispatch
   from it. Read the authoritative ledger sections, reconcile all in-scope
   sources, and replace the packet.

Refresh the packet after each wave, source mutation, and planned pause using
this order: derive every packet field from authoritative state; compute and
write the packet Content fingerprint to both the packet and Active Root;
compute the Projection fingerprint, which now binds that content fingerprint;
then write it to the packet. Packet freshness never bypasses claims,
capabilities, permissions, dependencies, gates, or final reconciliation.
