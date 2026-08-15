import unittest
from pathlib import Path


IMPLEMENT = Path(__file__).resolve().parents[1]
PLUGIN = IMPLEMENT.parents[1]
SKILL = IMPLEMENT / "SKILL.md"
PROFILE = IMPLEMENT / "references/task-profile.md"
ORCHESTRATION = IMPLEMENT / "references/orchestration.md"
REVIEW_DELIVERY = IMPLEMENT / "references/review-delivery.md"
PREFLIGHT = PLUGIN / "references/task-preflight.md"
HANDOFF = PLUGIN / "references/task-handoff.md"


def normalized(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").split())


class ApplicationTaskTopologyContractTests(unittest.TestCase):
    def test_explicit_invocation_authorizes_visible_project_tasks(self) -> None:
        skill = normalized(SKILL)
        profile = normalized(PROFILE)
        preflight = normalized(PREFLIGHT)

        self.assertIn(
            "`se:implement` invocation is the user's request and bounded authority",
            skill,
        )
        self.assertIn("do not ask for a second task-permission confirmation", skill)
        self.assertIn("grants `task_creation_authorization`", preflight)
        self.assertIn("do not ask for a second confirmation", preflight)
        self.assertIn("visible in the ChatGPT application project", profile)
        self.assertIn("the invoking project", profile)
        self.assertIn("the project for its target repository", profile)
        self.assertIn("For a fresh run, create exactly one new", skill)
        self.assertIn("one new Feature Worker task per selected Feature", skill)
        self.assertIn("A validated resume reuses only", skill)
        self.assertIn("missing or unverifiable retained identity blocks without", skill)
        self.assertIn("never create a replacement role task", profile)

    def test_required_roles_never_fall_back_to_delegation(self) -> None:
        contract = " ".join(
            normalized(path)
            for path in (SKILL, PROFILE, PREFLIGHT, HANDOFF, ORCHESTRATION)
        )

        for required in (
            "required application-task roles",
            "never satisfies or substitutes for either role",
            "never satisfies or substitutes for a required role",
            "cannot be promoted into the required handoff",
            "can never be promoted into either required role",
            "stop with `unsupported-runtime`",
            "do not switch topology",
        ):
            self.assertIn(required, contract)

        for forbidden_interface_name in (
            "create_thread",
            "spawn_agent",
            "wait_agent",
            "send_message",
            "list_agents",
        ):
            self.assertNotIn(forbidden_interface_name, contract)

    def test_recovery_retries_only_the_original_application_task_effect(self) -> None:
        preflight = normalized(PREFLIGHT)
        handoff = normalized(HANDOFF)

        self.assertIn(
            "Reconciliation may retry only the original application-task effect",
            preflight,
        )
        self.assertIn("after authoritative `not-applied` evidence", preflight)
        self.assertIn("never authorizes another execution topology", preflight)
        self.assertIn(
            "Reconciliation may repeat only the original application-task effect",
            handoff,
        )
        self.assertIn("never authorizes a different execution topology", handoff)

    def test_monitoring_is_change_driven_and_suppresses_no_op_control_traffic(self) -> None:
        handoff = normalized(HANDOFF)
        orchestration = normalized(ORCHESTRATION)
        review = normalized(REVIEW_DELIVERY)

        self.assertIn("Monitoring is change-driven", handoff)
        self.assertIn("status-only or \"continue\" message", handoff)
        self.assertIn("lengthen the interval after unchanged results", handoff)
        self.assertIn("An unchanged pending observation does not trigger", orchestration)
        self.assertIn("Every message is edge-triggered", orchestration)
        self.assertIn("Retain one delivery lineage per PR, exact HEAD", review)
        self.assertIn("does not cause a duplicate request, status message", review)
        self.assertIn("producing a status-only control message", review)

    def test_entrypoint_routes_details_instead_of_duplicating_them(self) -> None:
        skill = SKILL.read_text(encoding="utf-8")
        normalized_skill = " ".join(skill.split())

        for routed_detail in (
            "## Plan interpretation and orchestration",
            "## Feature Worker and review boundary",
            "### Optional Feature Worker support",
            "## Delivery topology",
            "## Ledger boundary",
        ):
            self.assertNotIn(routed_detail, skill)

        for route in (
            "Implement task profile",
            "shared task preflight",
            "shared task handoff",
            "Load orchestration",
            "Load review-delivery",
            "Load run-state",
        ):
            self.assertIn(route, normalized_skill)


if __name__ == "__main__":
    unittest.main()
