# Contributing to GraphFusion AI

Thanks for considering contributing! This is a **proof-of-concept / learning project**, so contributions of all kinds are welcome — from bug fixes to major features.

## How to Contribute

### 1. Fork and Clone

```bash
git clone https://github.com/YOUR_USERNAME/GraphFusion_AI.git
cd GraphFusion_AI
```

### 2. Set Up Development Environment

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
# Edit .env with your test credentials
```

### 3. Make Your Changes

- Create a feature branch: `git checkout -b feature/your-feature-name`
- Follow existing code style (Python 3.12+ type hints, no `typing.List/Dict`)
- Keep changes focused and well-documented

### 4. Test Your Changes

```bash
# Run existing tests (when available)
pytest

# Manual testing:
# - Start the API: uvicorn src.api.main:app --reload
# - Start the UI: streamlit run src/ui/app.py
# - Verify your changes work
```

### 5. Submit a Pull Request

1. Commit your changes with a clear message
2. Push to your fork
3. Open a PR on GitHub describing:
   - What problem you're solving
   - What changes you made
   - How to test your changes

## Priority Areas for Contribution

These areas would most help move this POC forward:

| Area | What's Needed |
|------|---------------|
| **Tests** | Unit tests for intent detection, retrievers, API endpoints |
| **Evaluation** | Benchmark scripts comparing hybrid vs. single-store retrieval |
| **Fusion Improvements** | Reciprocal Rank Fusion (RRF), query-dependent weighting |
| **Documentation** | More examples, troubleshooting guides, deployment guides |
| **Bug Fixes** | Any broken functionality or edge cases |

## Code Style

- **Python 3.12+** — use built-in generics (`list[str]`, `dict[str, Any]`, `X | None`)
- **Type hints** — annotate function signatures
- **No hardcoded secrets** — use environment variables via `src/config.py`
- **Logging** — use `src/utils/logging.py` for consistent logging

## Questions?

Open an issue for discussion before starting large changes. Not sure if something fits the project scope? Ask!

---

By contributing, you agree your contributions are licensed under the MIT License (same as the project).
