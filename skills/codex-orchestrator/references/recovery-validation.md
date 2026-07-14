# Recovery Validation

Load this reference only when resuming from a ledger Recovery Packet. It
validates the compact projection before any mutation or dispatch; the ledger,
source items, canonical options, authority, and gates remain authoritative.
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
   For each checkpoint with `scope_transfer_ref=issue:<NN>`, re-read that
   generated issue's current `## Orchestrator Handoff`
   `delivery_source_evidence` and `issue_mutation_authority_evidence`. When the
   handoff selects `explicit-direct-mutation`, preserve its independent owner
   evidence while requiring matching scope, target, branch, and transfer
   tokens. Trim only outer whitespace, encode a literal `|` as `%7C`, and hash
   each evidence value independently with SHA-256. Require the live values to
   match `delivery_evidence_fingerprint` and
   `issue_mutation_evidence_fingerprint`; require each fingerprint to be
   `not-applicable` exactly when its corresponding transfer ref is
   `not-applicable`. Reject
   an issue ref that is not the checkpoint's registered source item.
5. Require packet repo checkpoint realpaths to equal the complete canonical
   in-scope/claimed repo set from `## Scope` and `## Active Root`; reject
   missing or extra repos. Then recompute every HEAD, branch, and
   `git status --short` fingerprint and verify the root claim plus active-worker
   state still match. Parse the authoritative `Active workers` rows, reject
   duplicate worker IDs or malformed surfaces, and require their exact ID set
   to match the packet. Require every listed `workstream_ids` assignment to
   exist in the authoritative active workstream bucket and to match that
   workstream's `worker=<id>` and `actual_workstream_surface` evidence; reject
   duplicate, stale, missing, or cross-worker assignments. Count all
   `cli-subagent` and `codex-app-thread` workers
   against `worker_limit`, count `codex-app-thread` workers against
   `app_thread_limit`, and reject a fresh packet whose live worker state exceeds
   either canonical limit or exists without its required delegation/consent.
6. If every check matches, mark the packet `fresh`. Load the packet's exact
   session and scoped `## Option Resolution` row IDs, recompute their canonical
   rows fingerprint, and require it to match `rows_fingerprint`. Before hashing,
   derive discovery-source scope IDs from every authoritative
   `## Discovery Sources` row and workstream scope IDs directly from every
   authoritative `## Workstreams` entry. Prefix stable IDs with `source:` or
   `workstream:` as they appear in the option table. Registered source-item
   checkpoints are freshness evidence, not separate option scopes. Reject a
   duplicate discovery-source or workstream stable ID before constructing the
   scope set; do not collapse duplicates. Require the
   packet row IDs to equal the exact Session Registry field set plus
   `worker_limit` and `app_thread_limit`, the exact Discovery Source Registry
   field set for every discovery source, and the exact Per-Workstream Registry
   field set plus the `branch_name`, `scope_transfer_ref`, and
   `issue_mutation_transfer_ref` data rows for every workstream.
   Validate canonical row IDs, values, sources, required evidence,
   and cross-field constraints from `options.md`; reject omitted, extra,
   duplicate, invalid, or out-of-scope rows. Session and scoped option tables
   use the same six columns. Cells must not contain a
   literal `|`; encode that character as `%7C` in evidence data. A pipe-prefixed
   Markdown row must therefore have exactly eight AWK fields: two empty framing
   fields plus the six contract cells. Validate that count before recognizing
   a header, separator, or data row. Serialize all
   and only the unique row IDs referenced by the packet as tab-separated
   `row_id,scope_id,field,value,source,evidence`, trim outer whitespace and one
   pair of wrapping backticks from each cell, sort bytewise by `row_id`, and
   hash the resulting lines:

   ```bash
   OPTION_ROW_IDS='<comma-separated union of packet session_rows and scoped_rows>'
   set -o pipefail
   OPTION_SOURCE_SCOPE_IDS="$(
     awk -F '|' '
       function norm(value) {
         gsub(/^[[:space:]]+|[[:space:]]+$/, "", value)
         return value
       }
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
         id=$0
         sub(/^#### /, "", id)
         sub(/: .*/, "", id)
         print "workstream:" id
       }
       workstreams && /^- workstream_id=[A-Za-z0-9:_-]+;/ {
         id=$0
         sub(/^- workstream_id=/, "", id)
         sub(/;.*/, "", id)
         print "workstream:" id
       }
     ' "$ledger" | LC_ALL=C sort | awk 'seen[$0]++ { exit 52 } { print }' | paste -sd, -
   )" || exit 52
   OPTION_SCOPE_IDS="$OPTION_SOURCE_SCOPE_IDS${OPTION_SOURCE_SCOPE_IDS:+${OPTION_WORKSTREAM_SCOPE_IDS:+,}}$OPTION_WORKSTREAM_SCOPE_IDS"
   ACTIVE_WORKER_ROWS="$(
     awk '
       /^Active workers:$/ { workers=1; next }
       /^Takeover history:$/ { exit }
       workers && /^- none$/ { next }
       workers && /^- worker_id=[A-Za-z0-9:_-]+; actual_workstream_surface=(cli-subagent|codex-app-thread); workstream_ids=[A-Za-z0-9,:_-]+$/ {
         line=$0
         sub(/^- worker_id=/, "", line)
         split(line, parts, "; ")
         id=parts[1]
         surface=parts[2]
         sub(/^actual_workstream_surface=/, "", surface)
         assignments=parts[3]
         sub(/^workstream_ids=/, "", assignments)
         print id "\t" surface "\t" assignments
         next
       }
       workers && /^-/ { exit 53 }
     ' "$ledger" | LC_ALL=C sort | awk -F '\t' 'seen[$1]++ { exit 53 } { print }'
   )" || exit 53
   PACKET_ACTIVE_WORKER_IDS="$(
     awk '
       function norm(value) {
         gsub(/^[[:space:]]+|[[:space:]]+$/, "", value)
         return value
       }
       /^## Recovery Packet$/ { packet=1; next }
       /^## Worker And Delivery References$/ { exit }
       packet && /^Root: / {
         roots++
         count=split($0, parts, ";")
         workers=""
         for (i=1; i <= count; i++) {
           item=norm(parts[i])
           if (item ~ /^active_workers=/) {
             workers=item
             sub(/^active_workers=/, "", workers)
           }
         }
         if (workers == "none") next
         if (workers == "") exit 55
         worker_count=split(workers, ids, ",")
         for (i=1; i <= worker_count; i++) {
           id=norm(ids[i])
           if (id !~ /^[A-Za-z0-9:_-]+$/) exit 55
           print id
         }
       }
       END { if (roots != 1) exit 55 }
     ' "$ledger" | LC_ALL=C sort | awk 'seen[$0]++ { exit 55 } { print }' | paste -sd, -
   )" || exit 55
   PACKET_OPTION_ROWS_FINGERPRINT="$(
     awk '
       function norm(value) {
         gsub(/^[[:space:]]+|[[:space:]]+$/, "", value)
         return value
       }
       /^## Recovery Packet$/ { packet=1; next }
       /^## Worker And Delivery References$/ { exit }
       packet && /^Option resolution refs: / {
         refs++
         count=split($0, parts, ";")
         fingerprint=""
         for (i=1; i <= count; i++) {
           item=norm(parts[i])
           if (item ~ /^rows_fingerprint=/) {
             fingerprint=item
             sub(/^rows_fingerprint=/, "", fingerprint)
           }
         }
         if (fingerprint !~ /^[0-9a-f]{64}$/) exit 56
         print fingerprint
       }
       END { if (refs != 1) exit 56 }
     ' "$ledger"
   )" || exit 56
   ACTIVE_WORKER_IDS="$(printf '%s\n' "$ACTIVE_WORKER_ROWS" | awk -F '\t' 'NF { print $1 }' | LC_ALL=C sort | paste -sd, -)"
   [ "$PACKET_ACTIVE_WORKER_IDS" = "$ACTIVE_WORKER_IDS" ] || exit 55
   ACTIVE_WORKSTREAM_ROWS="$(
     awk -F '|' '
       function norm(value) {
         gsub(/^[[:space:]]+|[[:space:]]+$/, "", value)
         return value
       }
       function token_value(value, key, count, parts, i, item, prefix) {
         count=split(value, parts, ";")
         prefix=key "="
         for (i=1; i <= count; i++) {
           item=norm(parts[i])
           if (substr(item, 1, length(prefix)) == prefix)
             return substr(item, length(prefix) + 1)
         }
         return ""
       }
       /^## Workstreams$/ { workstreams=1; next }
       workstreams && /^### active$/ { active=1; next }
       active && /^### / { exit }
       active && /^#### [A-Za-z0-9:_-]+: / {
         workstream=$0
         sub(/^#### /, "", workstream)
         sub(/: .*/, "", workstream)
         worker=""
         next
       }
       active && /^\| Repo \/ surface \|/ {
         worker=token_value(norm($3), "worker")
         next
       }
       active && /^\| Worker evidence \|/ {
         surface=token_value(norm($3), "actual_workstream_surface")
         if (workstream == "" || worker !~ /^[A-Za-z0-9:_-]+$/ || surface !~ /^(root-thread|cli-subagent|codex-app-thread)$/) exit 54
         print workstream "\t" worker "\t" surface
       }
     ' "$ledger" | LC_ALL=C sort -t $'\t' -k1,1
   )" || exit 54
   {
     printf '%s\n' "$ACTIVE_WORKER_ROWS" | awk -F '\t' 'NF { print "worker\t" $0 }'
     printf '%s\n' "$ACTIVE_WORKSTREAM_ROWS" | awk -F '\t' 'NF { print "workstream\t" $0 }'
   } | awk -F '\t' '
     $1 == "worker" {
       worker=$2
       surface=$3
       count=split($4, workstreams, ",")
       if (count < 1) exit 54
       for (i=1; i <= count; i++) {
         workstream=workstreams[i]
         if (workstream !~ /^[A-Za-z0-9:_-]+$/ || assigned[workstream]++) exit 54
         assigned_worker[workstream]=worker
         assigned_surface[workstream]=surface
       }
       next
     }
     $1 == "workstream" {
       workstream=$2
       if (authoritative[workstream]++) exit 54
       authoritative_worker[workstream]=$3
       authoritative_surface[workstream]=$4
     }
     END {
       for (workstream in assigned)
         if (!(workstream in authoritative) || assigned_worker[workstream] != authoritative_worker[workstream] || assigned_surface[workstream] != authoritative_surface[workstream]) exit 54
       for (workstream in authoritative) {
         if (authoritative_surface[workstream] ~ /^(cli-subagent|codex-app-thread)$/ && !(workstream in assigned)) exit 54
         if (authoritative_surface[workstream] == "root-thread" && workstream in assigned) exit 54
       }
     }
   ' || exit 54
   ACTIVE_DELEGATED_WORKER_COUNT="$(printf '%s\n' "$ACTIVE_WORKER_ROWS" | awk 'NF { count++ } END { print count + 0 }')"
   ACTIVE_APP_WORKER_COUNT="$(printf '%s\n' "$ACTIVE_WORKER_ROWS" | awk -F '\t' '$2 == "codex-app-thread" { count++ } END { print count + 0 }')"
   OPTION_BRANCH_NAMES="$(
     awk -F '|' -v scopes="$OPTION_SCOPE_IDS" '
       BEGIN {
         count=split(scopes, ids, ",")
         for (i=1; i <= count; i++)
           if (ids[i] != "") applicable_scope[ids[i]]=1
       }
       function norm(value) {
         gsub(/^[[:space:]]+|[[:space:]]+$/, "", value)
         if (length(value) >= 2 && substr(value, 1, 1) == "`" && substr(value, length(value), 1) == "`")
           value=substr(value, 2, length(value) - 2)
         return value
       }
       /^## Option Resolution$/ { options=1; next }
       /^## Discovery Sources$/ { exit }
       options && /^\|/ && norm($4) == "branch_name" && norm($3) in applicable_scope { print norm($5) }
     ' "$ledger"
   )"
   while IFS= read -r branch_name; do
     [ -z "$branch_name" ] && continue
     [ "$branch_name" = "not-applicable" ] || git check-ref-format --branch "$branch_name" >/dev/null 2>&1 || exit 50
   done < <(printf '%s\n' "$OPTION_BRANCH_NAMES")
   set -o pipefail
   COMPUTED_OPTION_ROWS_FINGERPRINT="$(
   awk -F '|' -v wanted="$OPTION_ROW_IDS" -v scopes="$OPTION_SCOPE_IDS" -v active_delegated_count="$ACTIVE_DELEGATED_WORKER_COUNT" -v active_app_count="$ACTIVE_APP_WORKER_COUNT" '
     BEGIN {
       split("delegation_mode worker_surface worker_limit app_thread_consent app_thread_limit raw_worktree_fallback active_root_takeover_policy", fields, " ")
       for (i in fields) expected_session[fields[i]]=1
       expected_source["source_mutation_authority"]=1
       split("source_mutation_authority publication_authority issue_mutation_authority merge_authority merge_policy caller_checkout_policy automation_authority temporary_source_execution completion_proof_policy delivery_mode delivery_source branch_name current_pr_ref scope_transfer_ref issue_mutation_transfer_ref pr_closeout codex_review_policy pr_shape closeout_mode integration_mode", fields, " ")
       for (i in fields) expected_workstream[fields[i]]=1
       count=split(wanted, ids, ",")
       for (i=1; i <= count; i++) {
         if (ids[i] == "") continue
         requested[ids[i]]++
         selected[ids[i]]=1
       }
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
       if (length(value) >= 2 && substr(value, 1, 1) == "`" && substr(value, length(value), 1) == "`")
         value=substr(value, 2, length(value) - 2)
       return value
     }
     function matches(value, choices) {
       return value ~ ("^(" choices ")$")
     }
     function token_value(evidence, key, count, parts, i, prefix) {
       count=split(evidence, parts, ";")
       prefix=key "="
       for (i=1; i <= count; i++)
         if (substr(parts[i], 1, length(prefix)) == prefix)
           return substr(parts[i], length(prefix) + 1)
       return ""
     }
     function authority_value(field, value) {
       if (field == "app_thread_consent" && value == "granted") return 1
       if (field == "raw_worktree_fallback" && value == "owner-approved") return 1
       if (field == "active_root_takeover_policy" && value == "stale-ledger-check") return 1
       if (field == "source_mutation_authority" && matches(value, "propose|write")) return 1
       if (field == "publication_authority" && value == "explicit-owner-authorization") return 1
       if (field == "issue_mutation_authority" && value == "explicit-direct-mutation") return 1
       if (field == "merge_authority" && value == "explicit-owner-authorization") return 1
       if (field == "merge_policy" && value == "automatic-after-gates") return 1
       if (field == "caller_checkout_policy" && value == "caller-checkout-approved") return 1
       if (field == "automation_authority" && value == "explicit-owner-authorization") return 1
       if (field == "temporary_source_execution" && value == "owner-approved") return 1
       if (field == "completion_proof_policy" && value == "synthetic-accepted") return 1
       if (field == "delegation_mode" && value == "bounded") return 1
       if (field == "delivery_mode" && value == "direct-commit") return 1
       if (field == "delivery_source" && matches(value, "issue-level-override|owner-instruction")) return 1
       if (field == "pr_closeout" && value == "draft-only") return 1
       if (field == "codex_review_policy" && value == "skip") return 1
       return 0
     }
     function allowed_value(field, value) {
       if (field == "delegation_mode") return matches(value, "auto|disabled|bounded")
       if (field == "worker_surface") return matches(value, "auto|root-thread|cli-subagent|codex-app-thread")
       if (field == "worker_limit") return matches(value, "unbounded|[1-9][0-9]*")
       if (field == "app_thread_consent") return matches(value, "not-requested|granted|denied")
       if (field == "app_thread_limit") return matches(value, "unspecified|[1-9][0-9]*")
       if (field == "raw_worktree_fallback") return matches(value, "forbidden|owner-approved")
       if (field == "active_root_takeover_policy") return matches(value, "owner-approval|stale-ledger-check")
       if (field == "source_mutation_authority") return matches(value, "none|propose|write")
       if (field == "publication_authority") return matches(value, "none|explicit-owner-authorization|spec-backed-pull-request|blocked")
       if (field == "issue_mutation_authority") return matches(value, "none|pr-body-closeout-only|explicit-direct-mutation")
       if (field == "merge_authority") return matches(value, "none|explicit-owner-authorization")
       if (field == "merge_policy") return matches(value, "owner-approval|automatic-after-gates")
       if (field == "caller_checkout_policy") return matches(value, "preserve-current-branch|caller-checkout-approved|not-applicable")
       if (field == "automation_authority") return matches(value, "none|explicit-owner-authorization")
       if (field == "temporary_source_execution") return matches(value, "forbidden|owner-approved")
       if (field == "completion_proof_policy") return matches(value, "live-required|synthetic-accepted")
       if (field == "delivery_mode") return matches(value, "local-only|pull-request|direct-commit")
       if (field == "delivery_source") return matches(value, "runtime-default|feature-level-inherited|issue-level-override|owner-instruction")
       if (field == "branch_name") return value != "" && value != "none"
       if (field == "current_pr_ref") return matches(value, "not-applicable|pending|[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+#[1-9][0-9]*")
       if (field == "scope_transfer_ref") return matches(value, "not-applicable|issue:[A-Za-z0-9:_-]+")
       if (field == "issue_mutation_transfer_ref") return matches(value, "not-applicable|issue:[A-Za-z0-9:_-]+")
       if (field == "pr_closeout") return matches(value, "merge-ready|draft-only|not-applicable")
       if (field == "codex_review_policy") return matches(value, "required|skip|not-applicable")
       if (field == "pr_shape") return matches(value, "single-pr|per-repo-pr|none")
       if (field == "closeout_mode") return matches(value, "feature-pr-closes-issue|repo-pr-closes-issue|direct-commit-closes-issue|local-done-move-after-proof|not-applicable")
       if (field == "integration_mode") return matches(value, "single-repo-pr|repo-pr|direct-commit|not-applicable")
       return 0
     }
     function allowed_source(field, value, source) {
       if (field == "worker_limit") return value == "unbounded" ? matches(source, "default|owner-instruction|legacy-migration") : matches(source, "owner-instruction|legacy-migration")
       if (field == "app_thread_limit") return value == "unspecified" ? matches(source, "default|owner-instruction|legacy-migration") : matches(source, "owner-instruction|legacy-migration")
       if (field == "delegation_mode") return value == "auto" ? matches(source, "default|owner-instruction|legacy-migration") : matches(source, "owner-instruction|legacy-migration")
       if (field == "worker_surface") {
         if (value == "auto") return matches(source, "default|owner-instruction|legacy-migration")
         if (value == "root-thread") return matches(source, "owner-instruction|runtime-capability|legacy-migration")
         return matches(source, "owner-instruction|legacy-migration")
       }
       if (field == "app_thread_consent") return value == "not-requested" ? matches(source, "default|owner-instruction|legacy-migration") : matches(source, "owner-instruction|legacy-migration")
       if (field == "raw_worktree_fallback") return value == "forbidden" ? matches(source, "default|owner-instruction|legacy-migration") : source == "owner-instruction"
       if (field == "active_root_takeover_policy") return value == "owner-approval" ? matches(source, "default|owner-instruction|legacy-migration") : source == "owner-instruction"
       if (field == "source_mutation_authority") return value == "none" ? matches(source, "default|runtime-capability|legacy-migration") : matches(source, "owner-instruction|legacy-migration")
       if (field == "publication_authority") {
         if (matches(value, "none|blocked")) return matches(source, "default|runtime-capability|owner-instruction")
         if (value == "spec-backed-pull-request") return matches(source, "source-contract|legacy-migration")
         return matches(source, "owner-instruction|source-contract")
       }
       if (field == "issue_mutation_authority") {
         if (value == "none") return matches(source, "default|runtime-capability")
         if (value == "pr-body-closeout-only") return source == "source-contract"
         return matches(source, "owner-instruction|source-contract")
       }
       if (field == "merge_authority") return value == "none" ? matches(source, "default|runtime-capability|legacy-migration") : matches(source, "owner-instruction|legacy-migration")
       if (field == "merge_policy") return value == "owner-approval" ? matches(source, "default|legacy-migration") : matches(source, "owner-instruction|legacy-migration")
       if (field == "caller_checkout_policy") return value == "caller-checkout-approved" ? source == "owner-instruction" : matches(source, "default|runtime-derived")
       if (field == "automation_authority") return value == "none" ? matches(source, "default|runtime-capability") : source == "owner-instruction"
       if (field == "temporary_source_execution") return value == "forbidden" ? matches(source, "default|runtime-capability|source-contract") : source == "owner-instruction"
       if (field == "completion_proof_policy") return value == "live-required" ? matches(source, "default|source-contract") : source == "owner-instruction"
       if (field == "delivery_mode") return value == "local-only" ? matches(source, "default|runtime-derived") : matches(source, "source-contract|owner-instruction")
       if (field == "delivery_source") return value == "runtime-default" ? matches(source, "default|runtime-derived") : (value == "feature-level-inherited" ? source == "source-contract" : matches(source, "source-contract|owner-instruction"))
       if (field == "branch_name") return value == "not-applicable" ? matches(source, "default|runtime-derived") : matches(source, "source-contract|owner-instruction|runtime-derived|legacy-migration")
       if (field == "current_pr_ref") return source == "runtime-derived"
       if (field == "scope_transfer_ref") return value == "not-applicable" ? matches(source, "default|runtime-derived") : source == "source-contract"
       if (field == "issue_mutation_transfer_ref") return value == "not-applicable" ? matches(source, "default|runtime-derived") : source == "source-contract"
       if (field == "pr_closeout") {
         if (value == "merge-ready") return matches(source, "default|source-contract|legacy-migration")
         if (value == "draft-only") return matches(source, "source-contract|owner-instruction|legacy-migration")
         return matches(source, "runtime-derived|legacy-migration")
       }
       if (field == "codex_review_policy") {
         if (value == "required") return matches(source, "default|legacy-migration")
         if (value == "skip") return source == "owner-instruction"
         return matches(source, "runtime-derived|legacy-migration")
       }
       if (field == "pr_shape" || field == "closeout_mode" || field == "integration_mode") return matches(source, "source-contract|runtime-derived|legacy-migration")
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
       scope_id=norm($3)
       field=norm($4)
       value=norm($5)
       source=norm($6)
       evidence=norm($7)
       is_applicable=(scope_id == "session" || scope_id in applicable_scope)
       if (is_applicable) {
         applicable[row_id]++
         expected_id=(scope_id == "session" ? "session:" field : scope_id ":" field)
         if (row_id != expected_id) invalid=45
         if (scope_id == "session" && !(field in expected_session)) invalid=45
         if (scope_id in applicable_source_scope && !(field in expected_source)) invalid=45
         if (scope_id in applicable_workstream_scope && !(field in expected_workstream)) invalid=45
         if (!allowed_value(field, value) || !allowed_source(field, value, source)) invalid=46
         if (matches(source, "owner-instruction|source-contract|runtime-capability|legacy-migration") && (evidence == "" || evidence == "none")) invalid=47
         if (authority_value(field, value) && (token_value(evidence, "owner-ref") == "" || token_value(evidence, "scope-ref") != scope_id || token_value(evidence, "target-ref") == "")) invalid=49
         present[scope_id SUBSEP field]++
         resolved[scope_id SUBSEP field]=value
         row_evidence[scope_id SUBSEP field]=evidence
         row_source[scope_id SUBSEP field]=source
       }
       if (!is_applicable) out_of_scope[row_id]=1
       if (!(row_id in selected)) next
       seen[row_id]++
       print row_id "\t" scope_id "\t" field "\t" value "\t" source "\t" evidence
     }
     END {
       if (invalid) exit invalid
       for (row_id in requested)
         if (requested[row_id] != 1) exit 41
       for (row_id in selected)
         if (seen[row_id] != 1) exit 42
       for (row_id in applicable)
         if (applicable[row_id] != 1 || !(row_id in selected)) exit 43
       for (row_id in out_of_scope)
         exit 44
       for (field in expected_session)
         if (present["session" SUBSEP field] != 1) exit 45
       for (scope_id in applicable_source_scope)
         for (field in expected_source)
           if (present[scope_id SUBSEP field] != 1) exit 45
       for (scope_id in applicable_workstream_scope)
         for (field in expected_workstream)
           if (present[scope_id SUBSEP field] != 1) exit 45
       if (resolved["session" SUBSEP "delegation_mode"] == "disabled" && resolved["session" SUBSEP "worker_surface"] != "root-thread") exit 48
       if (resolved["session" SUBSEP "delegation_mode"] == "disabled" && active_delegated_count != 0) exit 48
       if (resolved["session" SUBSEP "worker_surface"] == "root-thread" && active_delegated_count != 0) exit 48
       if (resolved["session" SUBSEP "worker_surface"] == "cli-subagent" && active_app_count != 0) exit 48
       if (resolved["session" SUBSEP "worker_surface"] == "codex-app-thread" && active_delegated_count != active_app_count) exit 48
       if (resolved["session" SUBSEP "delegation_mode"] != "bounded" && resolved["session" SUBSEP "worker_limit"] != "unbounded") exit 48
       if (resolved["session" SUBSEP "delegation_mode"] == "bounded") {
         delegation_evidence=row_evidence["session" SUBSEP "delegation_mode"]
         worker_limit_evidence=row_evidence["session" SUBSEP "worker_limit"]
         if (resolved["session" SUBSEP "worker_limit"] !~ /^[1-9][0-9]*$/ || token_value(worker_limit_evidence, "owner-ref") == "" || token_value(worker_limit_evidence, "owner-ref") != token_value(delegation_evidence, "owner-ref") || token_value(worker_limit_evidence, "scope-ref") != "session" || token_value(worker_limit_evidence, "target-ref") != token_value(delegation_evidence, "target-ref")) exit 48
         if (active_delegated_count > resolved["session" SUBSEP "worker_limit"] + 0) exit 48
       }
       if (resolved["session" SUBSEP "app_thread_consent"] != "granted" && resolved["session" SUBSEP "app_thread_limit"] != "unspecified") exit 48
       if (resolved["session" SUBSEP "app_thread_consent"] == "granted") {
         consent_evidence=row_evidence["session" SUBSEP "app_thread_consent"]
         app_limit_evidence=row_evidence["session" SUBSEP "app_thread_limit"]
         if (resolved["session" SUBSEP "app_thread_consent"] != "granted" || resolved["session" SUBSEP "app_thread_limit"] !~ /^[1-9][0-9]*$/ || token_value(app_limit_evidence, "owner-ref") == "" || token_value(app_limit_evidence, "owner-ref") != token_value(consent_evidence, "owner-ref") || token_value(app_limit_evidence, "scope-ref") != "session" || token_value(app_limit_evidence, "target-ref") != token_value(consent_evidence, "target-ref")) exit 48
         if (active_app_count > resolved["session" SUBSEP "app_thread_limit"] + 0) exit 48
       }
       if (resolved["session" SUBSEP "app_thread_consent"] != "granted" && active_app_count != 0) exit 48
       if (resolved["session" SUBSEP "worker_surface"] == "codex-app-thread" && resolved["session" SUBSEP "app_thread_consent"] != "granted") exit 48
       for (scope_id in applicable_workstream_scope) {
         delivery=resolved[scope_id SUBSEP "delivery_mode"]
         closeout=resolved[scope_id SUBSEP "closeout_mode"]
         shape=resolved[scope_id SUBSEP "pr_shape"]
         integration=resolved[scope_id SUBSEP "integration_mode"]
         branch_name=resolved[scope_id SUBSEP "branch_name"]
         current_pr_ref=resolved[scope_id SUBSEP "current_pr_ref"]
         scope_transfer_ref=resolved[scope_id SUBSEP "scope_transfer_ref"]
         issue_mutation_transfer_ref=resolved[scope_id SUBSEP "issue_mutation_transfer_ref"]
         pr_closeout=resolved[scope_id SUBSEP "pr_closeout"]
         codex_review_policy=resolved[scope_id SUBSEP "codex_review_policy"]
         if (resolved[scope_id SUBSEP "merge_policy"] == "automatic-after-gates" && resolved[scope_id SUBSEP "merge_authority"] != "explicit-owner-authorization") exit 48
         if (delivery == "local-only" && (resolved[scope_id SUBSEP "delivery_source"] != "runtime-default" || branch_name != "not-applicable" || current_pr_ref != "not-applicable" || scope_transfer_ref != "not-applicable" || issue_mutation_transfer_ref != "not-applicable" || pr_closeout != "not-applicable" || codex_review_policy != "not-applicable" || shape != "none" || closeout != "not-applicable" || integration != "not-applicable")) exit 48
         if (delivery == "pull-request" && (!matches(resolved[scope_id SUBSEP "delivery_source"], "feature-level-inherited|issue-level-override|owner-instruction") || branch_name == "not-applicable" || current_pr_ref == "not-applicable" || scope_transfer_ref != "not-applicable" || issue_mutation_transfer_ref != "not-applicable" || !matches(pr_closeout, "merge-ready|draft-only") || !matches(shape, "single-pr|per-repo-pr") || !matches(closeout, "feature-pr-closes-issue|repo-pr-closes-issue|local-done-move-after-proof") || !matches(integration, "single-repo-pr|repo-pr|not-applicable"))) exit 48
         if (delivery == "pull-request" && pr_closeout == "merge-ready" && !matches(codex_review_policy, "required|skip")) exit 48
         if (delivery == "pull-request" && pr_closeout == "draft-only" && codex_review_policy != "not-applicable") exit 48
         if (codex_review_policy == "skip") {
           review_evidence=row_evidence[scope_id SUBSEP "codex_review_policy"]
           review_pr_ref=token_value(review_evidence, "pr-ref")
           if (row_source[scope_id SUBSEP "codex_review_policy"] != "owner-instruction" || token_value(review_evidence, "owner-ref") == "" || token_value(review_evidence, "scope-ref") != scope_id || token_value(review_evidence, "target-ref") != scope_id || review_pr_ref == "" || (review_pr_ref != "not-applicable" && review_pr_ref != current_pr_ref)) exit 48
         }
         if (delivery == "direct-commit") {
           delivery_evidence=row_evidence[scope_id SUBSEP "delivery_mode"]
           delivery_source=resolved[scope_id SUBSEP "delivery_source"]
           delivery_source_evidence=row_evidence[scope_id SUBSEP "delivery_source"]
           branch_evidence=row_evidence[scope_id SUBSEP "branch_name"]
           publication_evidence=row_evidence[scope_id SUBSEP "publication_authority"]
           issue_mutation_evidence=row_evidence[scope_id SUBSEP "issue_mutation_authority"]
           transfer_evidence=row_evidence[scope_id SUBSEP "scope_transfer_ref"]
           issue_mutation_transfer_evidence=row_evidence[scope_id SUBSEP "issue_mutation_transfer_ref"]
           owner_ref=token_value(delivery_evidence, "owner-ref")
           branch_owner_ref=token_value(branch_evidence, "owner-ref")
           target_ref=token_value(delivery_evidence, "target-ref")
           if (!matches(delivery_source, "feature-level-inherited|issue-level-override|owner-instruction")) exit 48
           transfer_token=token_value(delivery_evidence, "scope-transfer-ref")
           if (resolved[scope_id SUBSEP "publication_authority"] != "explicit-owner-authorization" || token_value(publication_evidence, "owner-ref") != owner_ref || token_value(publication_evidence, "scope-ref") != scope_id || token_value(publication_evidence, "target-ref") != target_ref || token_value(publication_evidence, "target-branch") != branch_name || token_value(publication_evidence, "scope-transfer-ref") != transfer_token || branch_name == "not-applicable" || current_pr_ref != "not-applicable" || !matches(row_source[scope_id SUBSEP "branch_name"], "owner-instruction|source-contract") || owner_ref == "" || branch_owner_ref != owner_ref || target_ref == "" || token_value(branch_evidence, "target-ref") != target_ref || token_value(delivery_evidence, "scope-ref") != scope_id || token_value(branch_evidence, "scope-ref") != scope_id || token_value(delivery_evidence, "target-branch") != branch_name || token_value(branch_evidence, "target-branch") != branch_name || token_value(branch_evidence, "scope-transfer-ref") != transfer_token || token_value(delivery_source_evidence, "owner-ref") != owner_ref || token_value(delivery_source_evidence, "scope-ref") != scope_id || token_value(delivery_source_evidence, "target-ref") != target_ref || token_value(delivery_source_evidence, "target-branch") != branch_name || token_value(delivery_source_evidence, "scope-transfer-ref") != transfer_token || pr_closeout != "not-applicable" || codex_review_policy != "not-applicable" || shape != "none" || !matches(closeout, "direct-commit-closes-issue|local-done-move-after-proof") || !matches(integration, "direct-commit|not-applicable")) exit 48
           issue_mutation_transfer_token=token_value(issue_mutation_evidence, "scope-transfer-ref")
           if (closeout == "direct-commit-closes-issue" && (resolved[scope_id SUBSEP "issue_mutation_authority"] != "explicit-direct-mutation" || token_value(issue_mutation_evidence, "owner-ref") == "" || token_value(issue_mutation_evidence, "scope-ref") != scope_id || token_value(issue_mutation_evidence, "target-ref") != target_ref || token_value(issue_mutation_evidence, "target-branch") != branch_name || (issue_mutation_transfer_ref == "not-applicable" ? issue_mutation_transfer_token != "" : issue_mutation_transfer_token != issue_mutation_transfer_ref))) exit 48
           if (matches(delivery_source, "feature-level-inherited|issue-level-override")) {
             if (scope_transfer_ref == "not-applicable" || row_source[scope_id SUBSEP "scope_transfer_ref"] != "source-contract" || token_value(delivery_evidence, "scope-transfer-ref") != scope_transfer_ref || token_value(transfer_evidence, "scope-ref") != scope_transfer_ref || token_value(transfer_evidence, "owner-ref") != owner_ref || token_value(transfer_evidence, "target-ref") != target_ref || token_value(transfer_evidence, "target-branch") != branch_name) exit 48
             if (closeout == "direct-commit-closes-issue" && (issue_mutation_transfer_ref != scope_transfer_ref || row_source[scope_id SUBSEP "issue_mutation_transfer_ref"] != "source-contract" || token_value(issue_mutation_transfer_evidence, "scope-ref") != issue_mutation_transfer_ref || token_value(issue_mutation_transfer_evidence, "owner-ref") != token_value(issue_mutation_evidence, "owner-ref") || token_value(issue_mutation_transfer_evidence, "target-ref") != target_ref || token_value(issue_mutation_transfer_evidence, "target-branch") != branch_name)) exit 48
             if (closeout != "direct-commit-closes-issue" && issue_mutation_transfer_ref != "not-applicable") exit 48
             if (delivery_source == "feature-level-inherited" && token_value(transfer_evidence, "scope-transfer-ref") != "run") exit 48
             if (delivery_source == "feature-level-inherited" && closeout == "direct-commit-closes-issue" && token_value(issue_mutation_transfer_evidence, "scope-transfer-ref") != "run") exit 48
           } else if (delivery_source == "owner-instruction" && (scope_transfer_ref != "not-applicable" || issue_mutation_transfer_ref != "not-applicable")) exit 48
         }
       }
     }
   ' "$ledger" | LC_ALL=C sort -t $'\t' -k1,1 | shasum -a 256 | awk '{ print $1 }'
   )" || exit 56
   [ "$COMPUTED_OPTION_ROWS_FINGERPRINT" = "$PACKET_OPTION_ROWS_FINGERPRINT" ] || exit 56
   printf '%s\n' "$COMPUTED_OPTION_ROWS_FINGERPRINT"
   ```

   For every non-`not-applicable` transfer, hash the normalized evidence cells
   of the workstream's `scope_transfer_ref` and
   `issue_mutation_transfer_ref` rows and require them to equal the
   checkpoint's separately live-verified delivery and mutation fingerprints.
   Then load
   only the packet's named workstream rows, gate rows, sources,
   proofs, and other references. Do not dispatch or mutate when an option row
   is missing, extra, mismatched, or scoped to another source/workstream.
7. If any check differs, mark it `stale` or `invalid`; do not mutate or dispatch
   from it. Read the authoritative ledger sections, reconcile all in-scope
   sources, and replace the packet.

Refresh the packet after each wave, source mutation, and planned pause using
this order: derive every packet field from authoritative state; compute and
write the packet Content fingerprint to both the packet and Active Root;
compute the Projection fingerprint, which now binds that content fingerprint;
then write it to the packet. Packet freshness never bypasses claims,
capabilities, authority, dependencies, gates, or final reconciliation.
