# Add-ons For Existing Apps

Use this guide when the project already exists and the real job is `tanstack add`.

Owns:
- add-on id selection for an existing project
- preconditions and project metadata checks
- dependency chains introduced by chosen add-ons

Workflow:
1. Confirm the project already exists and is a valid CLI target.
2. Resolve the desired add-on ids and dependency implications.
3. Keep the guidance scoped to add-on application, not framework redesign.

Do not use this guide for new app scaffolding, ecosystem option discovery before
a choice is made, or app architecture after install.

Verification: verify against current `@tanstack/cli` add-on guidance when exact
commands or metadata constraints matter.
