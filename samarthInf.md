# Samarth Project - Files and Folder Structure

```text
SAMARTHantigravity/
|-- .env
|-- .gitignore
|-- routes.txt
|-- samarthInfo
|-- start_samarth.bat
|-- test_llm.py
|-- test_out.txt
|-- test_out2.txt
|-- test_out3.txt
|-- .venv/                         (python virtual environment)
|
|-- backend/
|   |-- __init__.py
|   |-- config.py
|   |-- main.py
|   |-- requirements.txt
|   |-- samarth.db
|   |
|   |-- api/
|   |   |-- __init__.py
|   |   |-- models.py
|   |   |-- routes.py
|   |   |-- __pycache__/           (generated)
|   |
|   |-- core/
|   |   |-- __init__.py
|   |   |-- document_guidance.py
|   |   |-- eligibility_engine.py
|   |   |-- explanation.py
|   |   |-- orchestrator.py
|   |   |-- profile_manager.py
|   |   |-- pure_ai_assistant.py
|   |   |-- rag_engine.py
|   |   |-- retrieval.py
|   |   |-- scoring.py
|   |   |-- what_if.py
|   |   |-- __pycache__/           (generated)
|   |
|   |-- data/
|   |   |-- generate_schemes.py
|   |   |-- generate_schemes_batch2.py
|   |   |-- generate_schemes_batch3.py
|   |   |-- loader.py
|   |   |-- schemes.json
|   |   |-- __pycache__/           (generated)
|   |
|   |-- db/
|   |   |-- __init__.py
|   |   |-- database.py
|   |   |-- models.py
|   |   |-- __pycache__/           (generated)
|   |
|   |-- llm/
|   |   |-- __init__.py
|   |   |-- client.py
|   |   |-- prompts.py
|   |   |-- __pycache__/           (generated)
|   |
|   |-- __pycache__/               (generated)
|
|-- frontend/
|   |-- .gitignore
|   |-- eslint.config.mjs
|   |-- eslint_report.json
|   |-- next-env.d.ts
|   |-- next.config.ts
|   |-- package.json
|   |-- package-lock.json
|   |-- postcss.config.mjs
|   |-- README.md
|   |-- tsconfig.json
|   |
|   |-- public/
|   |   |-- favicon.ico
|   |   |-- file.svg
|   |   |-- globe.svg
|   |   |-- next.svg
|   |   |-- sitelogo.png
|   |   |-- smarth.png
|   |   |-- vercel.svg
|   |   |-- window.svg
|   |
|   |-- src/
|   |   |-- app/
|   |   |   |-- globals.css
|   |   |   |-- icon.png
|   |   |   |-- layout.tsx
|   |   |   |-- page.tsx
|   |   |   |
|   |   |   |-- ai/
|   |   |   |   |-- page.tsx
|   |   |   |
|   |   |   |-- chat/
|   |   |   |   |-- page.tsx
|   |   |   |
|   |   |   |-- explore/
|   |   |   |   |-- page.tsx
|   |   |   |   |
|   |   |   |   |-- [category]/
|   |   |   |   |   |-- page.tsx
|   |   |   |   |
|   |   |   |   |-- scheme/
|   |   |   |   |   |-- [id]/
|   |   |   |   |   |   |-- page.tsx
|   |   |
|   |   |-- components/
|   |   |   |-- CategoryCard.tsx
|   |   |   |-- ExploreSchemeCard.tsx
|   |   |   |-- Navbar.tsx
|   |   |   |-- SchemeCard.tsx
|   |   |
|   |   |-- context/
|   |       |-- LanguageContext.tsx
|   |
|   |-- .next/                     (generated)
|   |-- node_modules/              (generated)
```

## Notes
- `__pycache__`, `.next`, and `node_modules` are generated directories.
- `.venv` is your local Python environment directory.
- `backend/samarth.db` is the SQLite database used by the backend.
