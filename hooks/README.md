# Git hooks

## pre-push

Before each `git push`, runs `scripts/update_readme_results.py` to refresh the
**Latest results** section in `README.md`. If the section changed, the hook
creates an auto-commit (`Update README results links [auto]`) and includes it
in the push.

## Enable (once per clone)

From the repository root:

```bash
git config core.hooksPath hooks
chmod +x hooks/pre-push
```

`setup.sh` runs these steps automatically.
