---
paths:
  - "**/*.py"
  - "**/pyproject.toml"
  - "**/requirements*.txt"
  - "**/uv.lock"
description: "Python 環境ルール（uv 優先）"
---

## Python 環境ルール

Python 関係のツールは `uv` を優先して使うこと（pip / venv / pyenv より優先）。

例:

- `uv run`
- `uv pip install`
- `uv init`
- `uv add`
