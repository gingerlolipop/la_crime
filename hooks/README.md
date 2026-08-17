# Git hooks

## pre-push

Before each `git push`, runs `scripts/update_readme_results.py` to refresh the
**Latest results** section in `README.md`.

If the section changed, the hook amends the refreshed README into the commit
being pushed. Git resolves the refs to push before hooks run, so a *new* commit
created here would silently stay behind; amending keeps the push complete.

The hook stays out of the way when it cannot safely amend:

- working tree has staged or unstaged changes → skips the refresh
- `HEAD` is already published upstream → commits separately and aborts the push
  with a message asking you to run `git push` again, rather than rewriting
  published history

## Enable (once per clone)

From the repository root:

```bash
git config core.hooksPath hooks
chmod +x hooks/pre-push
```

`setup.sh` runs these steps automatically.
