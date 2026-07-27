# 🏡 File Haven

A modern, local-first desktop application for organizing and cleaning files safely.

File Haven helps users identify duplicate files, large files, and old files while providing powerful search, sorting, and safe cleanup tools—all without uploading data to the cloud.

> 🚧 This project is currently under active development.

---

## Features (Planned)

- 📂 Scan folders recursively
- 🔍 Detect duplicate files
- 📦 Find large files
- 🕒 Find old files
- 🔎 Instant file search
- ↕️ Sort by name, size, date, and type
- 🗑️ Safely move files to the Trash
- 📁 Reveal files in Finder (macOS)
- 💾 Store scan history in SQLite
- 🌙 Modern dark desktop interface

---

## Tech Stack

- Python 3.12+
- PySide6
- SQLite
- pytest
- Send2Trash

---

## Project Structure

```
file-haven/
│
├── src/
│   └── file_haven/
│       ├── domain/
│       ├── infrastructure/
│       ├── presentation/
│       ├── services/
│       └── app.py
│
├── tests/
├── README.md
├── pyproject.toml
└── .gitignore
```

---

## Running

```bash
pip install -e ".[dev]"
```

Run the application:

```bash
file-haven
```

or

```bash
python -m file_haven.app
```

---

## License

MIT (planned)