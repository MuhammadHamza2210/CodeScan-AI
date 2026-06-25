# CodeScan AI 🔍

A code plagiarism / similarity detector built with **Python + Streamlit**. It
compares programs using several engines — AST structure, ML classification,
control-flow graphs, winnowing fingerprints and tree edit distance — to score
real similarity rather than just matching text.

> 👥 Built as a **group project** together with a teammate.
> Maintained here by **Muhammad Hamza**.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Notes

- The heavy CodeBERT engine (PyTorch / Transformers) is **optional** — the app
  detects whether those libraries are installed and gracefully runs the other
  engines without them. The hosted demo runs the lightweight engines so it fits
  free-tier limits.
- The SQLite database (`codescan.db`) is created automatically on first run and
  is intentionally not committed.
