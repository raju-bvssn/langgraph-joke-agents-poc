# Repository Guidelines

## Project Structure & Module Organization
- `app/main.py` is the Streamlit entry; `app/agents/` holds performer/critic logic; `app/graph/workflow.py` orchestrates the LangGraph state machine; `app/utils/` stores settings, LLM factories, and TTS helpers.
- Root docs (`README.md`, `ARCHITECTURE.md`, `QUICKSTART.md`, deployment guides) explain flows; keep them updated when behavior changes.
- Tests sit at the repo root (`test_*.py`) and exercise the workflow, provider compatibility, and UI helpers; `verify_setup.py` is the preflight for Python, deps, and `.env` keys.

## Build, Test, and Development Commands
- Setup: `python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt`.
- Configure: `cp env.example .env`; set `OPENAI_API_KEY` or `GROQ_API_KEY`, `LANGCHAIN_API_KEY`, and optional `GOOGLE_API_KEY` for TTS.
- Preflight: `python verify_setup.py` to confirm environment before running.
- Run UI: `streamlit run app/main.py`.
- CLI workflow: `python test_workflow.py "topic" --performer-provider groq --critic-provider openai` to validate agents without the UI.

## Coding Style & Naming Conventions
- Python 3.10+, PEP8 (4-space indent); keep functions small, typed, and documented.
- snake_case for functions/vars, PascalCase for classes, uppercase for constants; keep agent code stateless and composable.
- Shared utilities belong in `app/utils`; prefer TypedDict/Pydantic models for structured state passed between components.

## Testing Guidelines
- Default suite: `python -m pytest` (covers workflow, provider, and model tests).
- Targeted checks: `python test_workflow.py "topic"` for end-to-end; `python test_all_providers.py` sweeps provider/model combos (needs valid keys and may spend quota).
- Export `LLM_PROVIDER` and API keys in `.env` before running; skip provider sweeps if keys or quotas are missing.
- Add tests beside related modules; name `test_<feature>.py`; keep prompts deterministic when possible.

## Commit & Pull Request Guidelines
- Follow conventional commits (`feat:`, `fix:`, `chore:`, `docs:`) as used in git history.
- Keep commits focused; update docs when UI/LLM behavior or defaults change.
- PRs should include a short summary, linked issues, commands/tests run, and screenshots/GIFs or LangSmith trace links for UI/agent changes.
- Note any new env vars, provider requirements, or migration steps.

## Security & Configuration Tips
- Never commit `.env` or API keys; rely on `env.example` placeholders and local secret storage.
- Keep `LANGCHAIN_TRACING_V2=true` for observability, but scrub sensitive inputs before sharing logs.
- Re-run `verify_setup.py` after dependency or config changes to catch setup drift early.
