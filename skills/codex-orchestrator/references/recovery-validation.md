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
   Re-read each workstream's source/handoff and require its canonical
   `feature_spec_ref` plus transport-encoded `feature_spec_title` to match the
   checkpoint and scoped option rows; use `not-applicable` for both on ad-hoc
   work. Never infer Feature Spec backing from generic delivery- or
   issue-permission transfer refs.
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
   evidence. Require explicit visible-App-task permission whenever any active worker uses
   `visible-codex-app-task`. When that permission is granted, also validate the
   complete `## Feature Spec Task Registry`: every implementation-eligible
   Feature Spec dispatched in the current active wave has exactly one row and
   one active visible task; the live
   task title equals the exact Feature Spec title after decoding the ledger
   title transport defined in `ledger-template.md`; every active child
   workstream, repository, and PR for that Spec maps to that task; one task
   never maps to multiple Specs; and neither root nor a background-only worker
   owns implementation or review. Require root-readable task Goal evidence,
   reject any non-`created` row whose Goal is still pending, and require an
   exact objective plus missing-tool evidence for the unavailable fallback.
   Reject `root-owned-fallback` for implementation or review. Task
   scheduling is otherwise derived from dependencies and live runtime capacity
   rather than ledger limits.
   Require `Next Root Check: action=<value>; target=<value>; due_at=<value>`
   under Active Root to match the Recovery Packet `next_action`, `next_target`,
   and `next_due_at` exactly and to satisfy `ledger.md`'s action predicate
   against the current task registry.
   Independently validate every `## Codex Review Wait Registry` row against all
   mapped active-workstream projections: one row per PR head, exact deadline,
   wait state, observation fingerprint, and transition timestamp, with no
   terminal/non-terminal contradiction. Elapsed wall time and poll attempts
   are not persisted state and cannot make a packet fresh.
   Before running the shell validation below, use the current Codex App
   `list_threads`/`read_thread` equivalents for every active visible task,
   including visible ad-hoc workers. Reject a
   missing, archived, unreadable, or replaced id; require the live title,
   project/worktree repository set, latest reported PR set, and reported Goal
   objective/state to match the registry and active workstreams. Build
   `LIVE_TASK_EVIDENCE_ROWS` only from
   those current tool results, never from ledger values, with one tab-separated
   row per task:

   ```text
   <task-id>\t<transport-encoded-live-title>\tactive\t<comma-separated-repo-refs>\t<comma-separated-pr-refs>\t<task-goal-mode>\t<task-goal-status>\t<task-goal-reported-objective-sha256-or-pending>\t<task-goal-evidence>\t<task-goal-missing-tool>\t<tool-result-ref/fingerprint>
   ```

   If the live task inspection surface is unavailable, the packet cannot be
   `fresh`; stop before resumed mutation or dispatch.
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
       function encoded_title(value, transport) {
         transport=value; gsub(/%(25|7C|3B|3D)/, "", transport)
         return transport !~ /[%|;=]/
       }
       function valid_hash(value) { return length(value) == 64 && value ~ /^[0-9a-f]+$/ }
       function valid_goal(mode, status, dispatch_hash, reported_hash, evidence, missing_tool, allow_terminal) {
         if (!valid_hash(dispatch_hash) || evidence == "" || evidence == "none" || evidence == "not-applicable") return 0
         if (mode == "pending") return status == "pending" && reported_hash == "pending" && missing_tool == "not-applicable" && evidence ~ /^(thread-message|goal-create-message):/
         if (!valid_hash(reported_hash) || reported_hash != dispatch_hash) return 0
         if (mode == "active") {
           if (missing_tool != "not-applicable") return 0
           return allow_terminal ? status ~ /^(active|complete|blocked)$/ : status == "active"
         }
         if (mode == "unavailable") return status == "not-applicable" && missing_tool == "runtime-goal-tool" && evidence ~ /^thread-read:/
         return 0
       }
       function emit_workstream() {
         if (workstream == "") return
         if (worker !~ /^[A-Za-z0-9:_-]+$/ || location !~ /^(current-orchestrator-session|background-codex-subagent|visible-codex-app-task)$/ || repo_ref == "" || pr_ref == "") exit 54
         if (location == "current-orchestrator-session" && worker != "root") exit 54
         if (location == "visible-codex-app-task") {
           if (!valid_goal(goal_mode, goal_status, goal_dispatch_objective_sha256, goal_reported_objective_sha256, goal_evidence, goal_missing_tool, task_assignment == "required")) exit 57
         } else if (goal_mode != "not-applicable" || goal_status != "not-applicable" || goal_dispatch_objective_sha256 != "not-applicable" || goal_reported_objective_sha256 != "not-applicable" || goal_evidence != "not-applicable" || goal_missing_tool != "not-applicable") exit 57
         print workstream "\t" worker "\t" location "\t" feature_spec_ref "\t" feature_spec_title "\t" task_assignment "\t" repo_ref "\t" pr_ref "\t" goal_mode "\t" goal_status "\t" goal_dispatch_objective_sha256 "\t" goal_reported_objective_sha256 "\t" goal_evidence "\t" goal_missing_tool
         workstream=""
       }
       /^## Workstreams$/ { workstreams=1; next }
       workstreams && /^### active$/ { active=1; next }
       active && /^### / { emit_workstream(); exit }
       active && /^#### [A-Za-z0-9:_-]+: / {
         emit_workstream()
         workstream=$0; sub(/^#### /, "", workstream); sub(/: .*/, "", workstream)
         worker=""; location=""; repo_ref=""; pr_ref=""; feature_spec_ref=""; feature_spec_title=""; task_assignment=""; goal_mode=""; goal_status=""; goal_dispatch_objective_sha256=""; goal_reported_objective_sha256=""; goal_evidence=""; goal_missing_tool=""; next
       }
       active && /^\| Feature Spec task \|/ {
         value=norm($3)
         feature_spec_ref=token_value(value, "feature_spec_ref")
         feature_spec_title=token_value(value, "feature_spec_title")
         task_assignment=token_value(value, "feature_spec_task_assignment")
         goal_mode=token_value(value, "task_goal_mode")
         goal_status=token_value(value, "task_goal_status")
         goal_dispatch_objective_sha256=token_value(value, "task_goal_dispatch_objective_sha256")
         goal_reported_objective_sha256=token_value(value, "task_goal_reported_objective_sha256")
         goal_evidence=token_value(value, "task_goal_evidence")
         goal_missing_tool=token_value(value, "task_goal_missing_tool")
         if (feature_spec_title != "" && feature_spec_title != "not-applicable" && !encoded_title(feature_spec_title)) exit 57
         next
       }
       active && /^\| Repo \/ execution location \|/ {
         value=norm($3); worker=token_value(value, "worker")
         split(value, repo_parts, ";"); repo_ref=norm(repo_parts[1]); next
       }
       active && /^\| Worker evidence \|/ {
         location=token_value(norm($3), "actual_execution_location")
         next
       }
       active && /^\| Delivery \|/ { pr_ref=token_value(norm($3), "target_pull_request_ref"); next }
       END { emit_workstream() }
     ' "$ledger" | LC_ALL=C sort -t $'\t' -k1,1
   )" || exit 54
   ACTIVE_WORKSTREAM_IDS="$(
     awk '
       /^## Workstreams$/ { workstreams=1; next }
       workstreams && /^### active$/ { active=1; next }
       active && /^### / { exit }
       active && /^#### [A-Za-z0-9:_-]+: / {
         id=$0; sub(/^#### /, "", id); sub(/: .*/, "", id); print id
       }
     ' "$ledger" | LC_ALL=C sort | awk 'seen[$0]++ { exit 54 } { print }' | paste -sd, -
   )" || exit 54
   PARSED_ACTIVE_WORKSTREAM_IDS="$(printf '%s\n' "$ACTIVE_WORKSTREAM_ROWS" | awk -F '\t' 'NF { print $1 }' | LC_ALL=C sort | paste -sd, -)"
   [ "$ACTIVE_WORKSTREAM_IDS" = "$PARSED_ACTIVE_WORKSTREAM_IDS" ] || exit 54
   FEATURE_SPEC_TASK_ROWS="$(
     awk -F '|' '
       function norm(value) {
         gsub(/^[[:space:]]+|[[:space:]]+$/, "", value)
         if (length(value) >= 2 && substr(value, 1, 1) == "`" && substr(value, length(value), 1) == "`") value=substr(value, 2, length(value) - 2)
         return value
       }
       function encoded_title(value, transport) {
         transport=value; gsub(/%(25|7C|3B|3D)/, "", transport)
         return transport !~ /[%|;=]/
       }
       function valid_hash(value) { return length(value) == 64 && value ~ /^[0-9a-f]+$/ }
       /^## Feature Spec Task Registry$/ { registry=1; next }
       registry && /^## / { exit }
       registry && /^\|/ {
         if (NF != 22) exit 57
         ref=norm($2); title=norm($3); task=norm($4); live_title=norm($5)
         workstreams=norm($6); repos=norm($7); prs=norm($8); lifecycle=norm($9); poll_owner=norm($10)
         state=norm($11); drift=norm($13); task_evidence=norm($15)
         goal_mode=norm($16); goal_status=norm($17); goal_dispatch_objective_sha256=norm($18); goal_reported_objective_sha256=norm($19); goal_evidence=norm($20); goal_missing_tool=norm($21)
         if (ref == "feature_spec_ref") next
         if (ref ~ /^:?-+:?$/) next
         if (ref == "" || title == "" || !encoded_title(title) || !encoded_title(live_title) || task !~ /^[A-Za-z0-9:_-]+$/ || live_title != title || workstreams == "" || repos == "" || prs == "" || lifecycle != "visible-feature-spec-task" || poll_owner != "visible-feature-spec-task" || task_evidence == "" || task_evidence == "none" || goal_evidence == "" || goal_evidence == "none" || goal_evidence == "not-applicable" || !valid_hash(goal_dispatch_objective_sha256)) exit 57
         if (state !~ /^(created|implementing|validating|draft-pr|review-polling|fixing-review|ci|marking-ready|merge-ready|target-complete|blocked|needs-owner|replaced)$/ || drift == "") exit 57
         if (goal_mode !~ /^(pending|active|unavailable)$/ || goal_status !~ /^(pending|active|complete|blocked|not-applicable)$/) exit 57
         if (goal_mode == "pending" && (goal_status != "pending" || state != "created" || goal_reported_objective_sha256 != "pending" || goal_missing_tool != "not-applicable" || goal_evidence !~ /^(thread-message|goal-create-message):/)) exit 57
         if (goal_mode != "pending" && (!valid_hash(goal_reported_objective_sha256) || goal_reported_objective_sha256 != goal_dispatch_objective_sha256)) exit 57
         if (goal_mode == "active" && (goal_status !~ /^(active|complete|blocked)$/ || goal_missing_tool != "not-applicable")) exit 57
         if (goal_mode == "unavailable" && (goal_status != "not-applicable" || goal_missing_tool != "runtime-goal-tool" || goal_evidence !~ /^thread-read:/)) exit 57
         if (goal_status == "complete" && state !~ /^(merge-ready|target-complete)$/) exit 57
         if (state ~ /^(merge-ready|target-complete)$/ && goal_mode == "active" && goal_status != "complete") exit 57
         if (goal_status == "blocked" && state !~ /^(blocked|needs-owner)$/) exit 57
         print task "\t" ref "\t" title "\t" workstreams "\t" repos "\t" prs "\t" state "\t" drift "\t" task_evidence "\t" goal_mode "\t" goal_status "\t" goal_dispatch_objective_sha256 "\t" goal_reported_objective_sha256 "\t" goal_evidence "\t" goal_missing_tool
       }
     ' "$ledger" | LC_ALL=C sort -t $'\t' -k1,1
   )" || exit 57
   {
     printf '%s\n' "$ACTIVE_WORKER_ROWS" | awk -F '\t' 'NF { print "worker\t" $0 }'
     printf '%s\n' "$ACTIVE_WORKSTREAM_ROWS" | awk -F '\t' 'NF { print "workstream\t" $0 }'
     printf '%s\n' "$FEATURE_SPEC_TASK_ROWS" | awk -F '\t' 'NF { print "registry\t" $0 }'
     printf '%s\n' "$LIVE_TASK_EVIDENCE_ROWS" | awk -F '\t' 'NF { print "live\t" $0 }'
   } | awk -F '\t' '
     $1 == "worker" {
       worker=$2; location=$3; count=split($4, workstreams, ",")
       if (location == "visible-codex-app-task") active_visible_worker[worker]=1
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
       authoritative_spec_ref[workstream]=$5; authoritative_spec_title[workstream]=$6; authoritative_task_assignment[workstream]=$7
       authoritative_repo[workstream]=$8; authoritative_pr[workstream]=$9
       authoritative_goal_mode[workstream]=$10; authoritative_goal_status[workstream]=$11; authoritative_goal_dispatch_objective_sha256[workstream]=$12; authoritative_goal_reported_objective_sha256[workstream]=$13; authoritative_goal_evidence[workstream]=$14; authoritative_goal_missing_tool[workstream]=$15
       next
     }
     $1 == "registry" {
       task=$2; ref=$3; title=$4
       if (registry_task[task]++ || registry_ref[ref]++) exit 57
       registry_task_ref[task]=ref; registry_task_title[task]=title
       registry_task_state[task]=$8; registry_task_drift[task]=$9; registry_task_evidence[task]=$10
       registry_task_goal_mode[task]=$11; registry_task_goal_status[task]=$12; registry_task_goal_dispatch_objective_sha256[task]=$13; registry_task_goal_reported_objective_sha256[task]=$14; registry_task_goal_evidence[task]=$15; registry_task_goal_missing_tool[task]=$16
       count=split($5, workstreams, ",")
       for (i=1; i <= count; i++) {
         workstream=workstreams[i]
         if (workstream !~ /^[A-Za-z0-9:_-]+$/ || registry_workstream[workstream]++) exit 57
         registry_worker_for_workstream[workstream]=task
         registry_ref_for_workstream[workstream]=ref
         registry_title_for_workstream[workstream]=title
       }
       count=split($6, repos, ",")
       for (i=1; i <= count; i++) {
         repo=repos[i]; if (repo == "" || registry_repo[task SUBSEP repo]++) exit 57
       }
       count=split($7, prs, ",")
       for (i=1; i <= count; i++) {
         pr=prs[i]; if (pr == "" || registry_pr[task SUBSEP pr]++) exit 57
       }
       next
     }
     $1 == "live" {
       task=$2; title=$3; state=$4
       reported_hash=$9
       if (live_task[task]++ || task !~ /^[A-Za-z0-9:_-]+$/ || title == "" || state != "active" || $5 == "" || $6 == "" || $7 == "" || $8 == "" || $10 == "" || $11 == "" || $12 == "") exit 58
       if (($7 == "pending" && reported_hash != "pending") || ($7 != "pending" && (length(reported_hash) != 64 || reported_hash !~ /^[0-9a-f]+$/))) exit 58
       live_title[task]=title; live_goal_mode[task]=$7; live_goal_status[task]=$8; live_goal_reported_objective_sha256[task]=reported_hash; live_goal_evidence[task]=$10; live_goal_missing_tool[task]=$11; live_evidence[task]=$12
       count=split($5, repos, ",")
       for (i=1; i <= count; i++) { repo=repos[i]; if (repo == "" || live_repo[task SUBSEP repo]++) exit 58 }
       count=split($6, prs, ",")
       for (i=1; i <= count; i++) { pr=prs[i]; if (pr == "" || live_pr[task SUBSEP pr]++) exit 58 }
       next
     }
     END {
       for (workstream in assigned)
         if (!(workstream in authoritative) || assigned_worker[workstream] != authoritative_worker[workstream] || assigned_location[workstream] != authoritative_location[workstream]) exit 54
       for (workstream in authoritative) {
         if (authoritative_location[workstream] ~ /^(background-codex-subagent|visible-codex-app-task)$/ && !(workstream in assigned)) exit 54
         if (authoritative_location[workstream] == "current-orchestrator-session" && workstream in assigned) exit 54
         if (authoritative_task_assignment[workstream] == "required") {
           if (authoritative_location[workstream] != "visible-codex-app-task" || !(workstream in registry_workstream)) exit 57
           if (authoritative_worker[workstream] != registry_worker_for_workstream[workstream] || authoritative_spec_ref[workstream] != registry_ref_for_workstream[workstream] || authoritative_spec_title[workstream] != registry_title_for_workstream[workstream]) exit 57
           task=authoritative_worker[workstream]
           if (authoritative_goal_mode[workstream] != registry_task_goal_mode[task] || authoritative_goal_status[workstream] != registry_task_goal_status[task] || authoritative_goal_dispatch_objective_sha256[workstream] != registry_task_goal_dispatch_objective_sha256[task] || authoritative_goal_reported_objective_sha256[workstream] != registry_task_goal_reported_objective_sha256[task] || authoritative_goal_evidence[workstream] != registry_task_goal_evidence[task] || authoritative_goal_missing_tool[workstream] != registry_task_goal_missing_tool[task]) exit 57
         } else if (workstream in registry_workstream) exit 57
         if (authoritative_location[workstream] == "visible-codex-app-task") {
           task=authoritative_worker[workstream]
           if (live_goal_mode[task] != authoritative_goal_mode[workstream] || live_goal_status[task] != authoritative_goal_status[workstream] || live_goal_reported_objective_sha256[task] != authoritative_goal_reported_objective_sha256[workstream] || live_goal_evidence[task] != authoritative_goal_evidence[workstream] || live_goal_missing_tool[task] != authoritative_goal_missing_tool[workstream]) exit 58
           active_visible_repo[task SUBSEP authoritative_repo[workstream]]=1
           active_visible_pr[task SUBSEP authoritative_pr[workstream]]=1
         }
       }
       for (workstream in registry_workstream)
         if (!(workstream in authoritative) || assigned_worker[workstream] != registry_worker_for_workstream[workstream] || assigned_location[workstream] != "visible-codex-app-task") exit 57
         else {
           task=registry_worker_for_workstream[workstream]
           repo_key=task SUBSEP authoritative_repo[workstream]
           pr_key=task SUBSEP authoritative_pr[workstream]
           if (!(repo_key in registry_repo) || !(pr_key in registry_pr)) exit 57
           active_registry_repo[repo_key]=1; active_registry_pr[pr_key]=1
         }
       for (key in registry_repo) if (!(key in active_registry_repo) || !(key in live_repo)) exit 57
       for (key in registry_pr) if (!(key in active_registry_pr) || !(key in live_pr)) exit 57
       for (task in registry_task)
         if (!(task in live_task) || live_title[task] != registry_task_title[task] || live_evidence[task] != registry_task_evidence[task] || live_goal_mode[task] != registry_task_goal_mode[task] || live_goal_status[task] != registry_task_goal_status[task] || live_goal_reported_objective_sha256[task] != registry_task_goal_reported_objective_sha256[task] || live_goal_evidence[task] != registry_task_goal_evidence[task] || live_goal_missing_tool[task] != registry_task_goal_missing_tool[task]) exit 58
       for (task in active_visible_worker) if (!(task in live_task)) exit 58
       for (task in live_task) if (!(task in active_visible_worker)) exit 58
       for (key in active_visible_repo) if (!(key in live_repo)) exit 58
       for (key in live_repo) if (!(key in active_visible_repo)) exit 58
       for (key in active_visible_pr) if (!(key in live_pr)) exit 58
       for (key in live_pr) if (!(key in active_visible_pr)) exit 58
     }
   ' || exit $?
   ROOT_NEXT_ACTION="$(
     awk '
       /^## Active Root$/ { root=1; next }
       /^## Codex Review Wait Registry$/ { exit }
       root && /^Next Root Check: / {
         rows++
         value=$0; sub(/^Next Root Check: /, "", value)
         count=split(value, parts, "; "); action=""; target=""; due=""
         for (i=1; i <= count; i++) {
           if (parts[i] ~ /^action=/) { action=parts[i]; sub(/^action=/, "", action) }
           if (parts[i] ~ /^target=/) { target=parts[i]; sub(/^target=/, "", target) }
           if (parts[i] ~ /^due_at=/) { due=parts[i]; sub(/^due_at=/, "", due) }
         }
         if (action !~ /^(monitor-task|send-correction|dispatch-feature-spec|reconcile-feature-spec|owner-action|none)$/ || target !~ /^([A-Za-z0-9:_.#\/@-]+|none)$/ || due !~ /^([A-Za-z0-9:_.+\/@-]+|none)$/) exit 59
         print action "\t" target "\t" due
       }
       END { if (rows != 1) exit 59 }
     ' "$ledger"
   )" || exit 59
   PACKET_NEXT_ACTION="$(
     awk '
       function norm(value) { gsub(/^[[:space:]]+|[[:space:]]+$/, "", value); return value }
       /^## Recovery Packet$/ { packet=1; next }
       /^## Worker And Delivery References$/ { exit }
       packet && /^Current wave: / {
         rows++; count=split($0, parts, ";"); action=""; target=""; due=""
         for (i=1; i <= count; i++) {
           item=norm(parts[i])
           if (item ~ /^next_action=/) { action=item; sub(/^next_action=/, "", action) }
           if (item ~ /^next_target=/) { target=item; sub(/^next_target=/, "", target) }
           if (item ~ /^next_due_at=/) { due=item; sub(/^next_due_at=/, "", due) }
         }
         if (action == "" || target == "" || due == "") exit 59
         print action "\t" target "\t" due
       }
       END { if (rows != 1) exit 59 }
     ' "$ledger"
   )" || exit 59
   [ "$ROOT_NEXT_ACTION" = "$PACKET_NEXT_ACTION" ] || exit 59
   IFS=$'\t' read -r ROOT_NEXT_ACTION_NAME ROOT_NEXT_ACTION_TARGET ROOT_NEXT_ACTION_DUE <<< "$ROOT_NEXT_ACTION"
   {
     printf '%s\n' "$FEATURE_SPEC_TASK_ROWS" | awk -F '\t' 'NF { print "registry\t" $1 "\t" $2 "\t" $7 "\t" $8 "\t" $10 }'
     printf '%s\n' "$ACTIVE_WORKSTREAM_ROWS" | awk -F '\t' '$3 == "visible-codex-app-task" { print "visible\t" $2 "\tnot-applicable\tactive\tnone\t" $9 }'
   } | awk -F '\t' -v action="$ROOT_NEXT_ACTION_NAME" -v target="$ROOT_NEXT_ACTION_TARGET" -v due="$ROOT_NEXT_ACTION_DUE" '
     $1 == "registry" {
       task[$2]=1; ref[$3]=1; state[$2]=$4; drift[$2]=$5
       if ($6 == "pending") pending[$2]=1
       next
     }
     $1 == "visible" {
       visible[$2]=1
       if ($6 == "pending") pending[$2]=1
       next
     }
     END {
       if (action == "none") {
         for (id in pending) exit 59
         exit target == "none" && due == "none" ? 0 : 59
       }
       if (target == "none" || due == "none") exit 59
       if (action == "monitor-task") {
         if (!(target in visible) || (target in task && (drift[target] != "none" || state[target] ~ /^(merge-ready|target-complete|blocked|needs-owner|replaced)$/))) exit 59
         exit 0
       }
       if (action == "send-correction") {
         if (!(target in task) || drift[target] == "none" || state[target] ~ /^(merge-ready|blocked|needs-owner|replaced)$/) exit 59
         exit 0
       }
       if (action == "dispatch-feature-spec") exit target in ref ? 59 : 0
       if (action == "reconcile-feature-spec") exit target in ref ? 0 : 59
       if (action == "owner-action") exit 0
       exit 59
     }
   ' || exit 59
   REVIEW_WAIT_ROWS="$(
     awk -F '|' '
       function norm(value) {
         gsub(/^[[:space:]]+|[[:space:]]+$/, "", value)
         if (length(value) >= 2 && substr(value, 1, 1) == "`" && substr(value, length(value), 1) == "`") value=substr(value, 2, length(value) - 2)
         return value
       }
       /^## Codex Review Wait Registry$/ { waits=1; next }
       waits && /^## / { exit }
       waits && /^\|/ {
         if (NF != 13) exit 60
         record=norm($2); pr=norm($3); head=norm($4); request=norm($5); profile=norm($6); budget=norm($7)
         started=norm($8); deadline=norm($9); state=norm($10); fingerprint=norm($11); transitioned=norm($12)
         if (record == "wait_record" || record ~ /^:?-+:?$/) next
         if (record == "" || pr == "" || head == "" || request == "" || profile !~ /^(standard|extended)$/ || budget !~ /^(15|30)$/ || started == "" || deadline == "" || state !~ /^(active|monitoring-required|terminal)$/ || fingerprint !~ /^[0-9a-f]{64}$/ || transitioned == "") exit 60
         print record "\t" pr "\t" head "\t" request "\t" profile "\t" budget "\t" started "\t" deadline "\t" state "\t" fingerprint "\t" transitioned
       }
     ' "$ledger" | LC_ALL=C sort -t $'\t' -k1,1 | awk -F '\t' 'seen[$1]++ { exit 60 } { print }'
   )" || exit 60
   ACTIVE_REVIEW_PROJECTIONS="$(
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
       active && /^#### [A-Za-z0-9:_-]+: / { workstream=$0; sub(/^#### /, "", workstream); sub(/: .*/, "", workstream); next }
       active && /^\| Codex review evidence \|/ {
         value=norm($3)
         print workstream "\t" token_value(value, "wait_record") "\t" token_value(value, "wait_profile_pr") "\t" token_value(value, "request_head") "\t" token_value(value, "request_object") "\t" token_value(value, "wait_profile") "\t" token_value(value, "wait_budget_minutes") "\t" token_value(value, "wait_started_at") "\t" token_value(value, "wait_deadline") "\t" token_value(value, "wait_state") "\t" token_value(value, "observation_fingerprint") "\t" token_value(value, "last_transition_at") "\t" token_value(value, "checker_status") "\t" token_value(value, "terminal")
       }
     ' "$ledger"
   )" || exit 60
   {
     printf '%s\n' "$REVIEW_WAIT_ROWS" | awk -F '\t' 'NF { print "wait\t" $0 }'
     printf '%s\n' "$ACTIVE_REVIEW_PROJECTIONS" | awk -F '\t' 'NF { print "projection\t" $0 }'
   } | awk -F '\t' '
     $1 == "wait" {
       record=$2; wait_seen[record]++
       wait_pr[record]=$3; wait_head[record]=$4; wait_request[record]=$5; wait_profile[record]=$6; wait_budget[record]=$7
       wait_started[record]=$8; wait_deadline[record]=$9; wait_state[record]=$10; wait_fingerprint[record]=$11; wait_transition[record]=$12
       next
     }
     $1 == "projection" {
       workstream=$2; record=$3; pr=$4; head=$5; request=$6; profile=$7; budget=$8; started=$9; deadline=$10
       state=$11; fingerprint=$12; transition=$13; checker=$14; terminal=$15
       if (record == "none" || record == "not-applicable" || record == "") next
       if (!(record in wait_seen) || pr != wait_pr[record] || head != wait_head[record] || request != wait_request[record] || profile != wait_profile[record] || budget != wait_budget[record] || started != wait_started[record] || deadline != wait_deadline[record] || state != wait_state[record] || fingerprint != wait_fingerprint[record] || transition != wait_transition[record]) exit 60
       if (wait_state[record] == "terminal") {
         if (checker !~ /^(clean|findings|error)$/ || terminal != checker) exit 60
       } else if (checker !~ /^(acknowledged|pending)$/ || terminal != "none") exit 60
       referenced_wait[record]++
       next
     }
     END { for (record in wait_seen) if (!(record in referenced_wait)) exit 60 }
   ' || exit 60
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
     awk -F '|' -v wanted="$OPTION_ROW_IDS" -v scopes="$OPTION_SCOPE_IDS" -v active_app_count="$ACTIVE_APP_WORKER_COUNT" -v active_workstreams="$ACTIVE_WORKSTREAM_ROWS" '
       BEGIN {
         split("visible_app_task_permission unmanaged_git_worktree_fallback_permission existing_orchestrator_session_takeover_policy repository_layout", fields, " ")
         for (i in fields) expected_session[fields[i]]=1
         expected_source["tracked_work_item_update_permission"]=1
         split("tracked_work_item_update_permission change_delivery_permission issue_update_permission pull_request_merge_permission pull_request_merge_confirmation starting_checkout_branch_handling scheduled_automation_change_permission temporary_source_execution_permission completion_evidence_policy change_delivery_target delivery_decision_origin workstream_repository_layout codex_review_requirement pull_request_count_strategy issue_completion_method feature_spec_ref feature_spec_title target_branch_name target_pull_request_ref delivery_permission_source_issue_ref issue_update_permission_source_issue_ref", fields, " ")
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
         active_count=split(active_workstreams, active_lines, "\n")
         for (i=1; i <= active_count; i++) {
           if (active_lines[i] == "") continue
           field_count=split(active_lines[i], active_fields, "\t")
           if (field_count < 8) { invalid=57; continue }
           active_scope="workstream:" active_fields[1]
           active_location[active_scope]=active_fields[3]
           active_spec_ref[active_scope]=active_fields[4]
           active_spec_title[active_scope]=active_fields[5]
           active_task_assignment[active_scope]=active_fields[6]
         }
       }
       function norm(value) {
         gsub(/^[[:space:]]+|[[:space:]]+$/, "", value)
         if (length(value) >= 2 && substr(value, 1, 1) == "`" && substr(value, length(value), 1) == "`") value=substr(value, 2, length(value) - 2)
         return value
       }
       function matches(value, choices) { return value ~ ("^(" choices ")$") }
       function encoded_title(value, transport) {
         transport=value; gsub(/%(25|7C|3B|3D)/, "", transport)
         return transport !~ /[%|;=]/
       }
       function token_value(evidence, key, count, parts, i, prefix) {
         count=split(evidence, parts, ";"); prefix=key "="
         for (i=1; i <= count; i++) if (substr(parts[i], 1, length(prefix)) == prefix) return substr(parts[i], length(prefix) + 1)
         return ""
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
         if (field == "delivery_decision_origin" && matches(value, "overridden-by-implementation-issue|specified-by-authorized-user")) return 1
         if (field == "codex_review_requirement" && value == "explicitly-skipped-by-authorized-user") return 1
         return 0
       }
       function allowed_value(field, value) {
         if (field == "visible_app_task_permission") return matches(value, "not-requested|granted-by-authorized-user|denied-by-authorized-user")
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
         if (field == "feature_spec_ref") return value == "not-applicable" || value != ""
         if (field == "feature_spec_title") return value == "not-applicable" || (value != "" && encoded_title(value))
         if (field == "target_branch_name") return value == "not-applicable" || value != ""
         if (field == "target_pull_request_ref") return matches(value, "not-applicable|pending|[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+#[1-9][0-9]*")
         if (field == "delivery_permission_source_issue_ref" || field == "issue_update_permission_source_issue_ref") return matches(value, "not-applicable|issue:[A-Za-z0-9:_-]+")
         return 0
       }
       function allowed_source(field, value, source) {
         if (field == "repository_layout") return matches(source, "project-layout-config|runtime-derived|authorized-user-instruction")
         if (field == "workstream_repository_layout") return matches(source, "source-contract|runtime-derived|authorized-user-instruction")
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
         if (field == "feature_spec_ref" || field == "feature_spec_title") return value == "not-applicable" ? matches(source, "default|runtime-derived") : source == "source-contract"
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

         app_permission=resolved["session" SUBSEP "visible_app_task_permission"]
         if (app_permission != "granted-by-authorized-user" && active_app_count != 0) exit 48

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
           canonical_spec_ref=resolved[scope_id SUBSEP "feature_spec_ref"]
           canonical_spec_title=resolved[scope_id SUBSEP "feature_spec_title"]

           if ((canonical_spec_ref == "not-applicable") != (canonical_spec_title == "not-applicable")) exit 57
           if (scope_id in active_location && (active_spec_ref[scope_id] != canonical_spec_ref || active_spec_title[scope_id] != canonical_spec_title)) exit 57
           feature_spec_backed=(canonical_spec_ref != "not-applicable")
           if (app_permission == "granted-by-authorized-user" && feature_spec_backed && scope_id in active_location) {
             if (active_location[scope_id] != "visible-codex-app-task" || active_task_assignment[scope_id] != "required" || active_spec_ref[scope_id] == "" || active_spec_ref[scope_id] == "not-applicable" || active_spec_title[scope_id] == "" || active_spec_title[scope_id] == "not-applicable") exit 57
           }

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
