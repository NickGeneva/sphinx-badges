# Development guidelines

## Package / environment management

Use **uv** for all Python environment and dependency management in this repo.

```bash
# Create / activate the virtual environment
uv venv
source .venv/bin/activate

# Install the package in editable mode with dev extras
uv pip install -e ".[dev]"

# Add a dependency
uv add <package>

# Run a command inside the venv without activating
uv run <command>
```

Do **not** use `pip`, `python -m venv`, or `conda` directly.
