# AI PR Reviewer Setup Checklist

## Required inputs

- GitHub token placeholder only: `GITHUB_TOKEN`
- LLM provider key placeholder only: `GEMINI_API_KEY`

Do not commit real values. Store them in local environment variables or an ignored `.env` file.

## Permission review

- No repository write access is required for the reviewer itself
- No auto-merge or auto-approve permissions
- No push permissions
- If this is ever wrapped in a workflow, keep permissions minimal and comment-only

## Manual run

1. Create and activate a local virtual environment.
2. Install the reviewer app dependencies in the external project only.
3. Set the placeholder environment variables locally.
4. Start the reviewer backend.
5. Submit a pull request URL to the review endpoint or CLI.
6. Read the generated review as advisory feedback only.

## How to disable

- Unset the local environment variables
- Stop the local reviewer process
- Remove any optional wrapper script or workflow reference

## First-run checks

- Confirm the tool only comments and never approves or merges
- Confirm it does not request trading advice
- Confirm it does not mention live trading enablement
- Confirm it does not expose tokens, account IDs, or webhook URLs
- Confirm the review focuses on safety, tests, scope, and execution risk

## Rollback

1. Remove the optional docs links or example config.
2. Delete any local environment variables used only for the reviewer.
3. Keep the MellyTrade repo on the existing safety posture.
4. Re-run the safety checks in this repository.

