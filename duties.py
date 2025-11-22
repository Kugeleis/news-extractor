from duty import duty


@duty
def test(ctx):
    """Run pytest (via uv)."""
    ctx.run("uv run pytest", title="Run tests")


@duty
def lint(ctx):
    """Run ruff lint checks."""
    ctx.run("uv run ruff check .", title="Run ruff")


@duty
def format(ctx):
    """Format code with ruff."""
    ctx.run("uv run ruff format .", title="Format with ruff")


@duty
def typecheck(ctx):
    """Run mypy type checks (requires mypy in dev deps)."""
    ctx.run("python -m mypy src/", title="Typecheck with mypy")


@duty
def sync(ctx):
    """Sync project dependencies with uv."""
    ctx.run("uv sync", title="Sync dependencies")


@duty
def run(ctx):
    """Run the project CLI entrypoint."""
    ctx.run("uv run news-extractor", title="Run CLI")


@duty
def bump(ctx, part: str = "patch"):
    """Bump project version using bump-my-version.

    `part` is the version component to bump (major/minor/patch).
    Example: `duty bump --part=minor` or `duty bump minor`.
    """
    # run without committing or tagging by default; user can run bump-my-version directly
    ctx.run(f"bump-my-version bump {part}", title=f"Bump version ({part})")
