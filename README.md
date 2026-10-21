# brainflex

Brain federated learning experiment.

## Development

This project uses [uv](https://docs.astral.sh/uv/).

```bash
uv sync                  # create .venv and install brainflex + dev dependencies
uv run prek install      # set up git hooks for linting/formatting
uv run prek run -a       # run linting/formatting on all files
uv run pytest            # run tests
```
