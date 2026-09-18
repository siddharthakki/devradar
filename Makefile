.PHONY: test lint ingest feeds digest run

test:
pytest tests/ -v

lint:
python -m py_compile engine/analyzer.py engine/store.py engine/rss.py

ingest:
python engine/analyzer.py

feeds:
python engine/rss.py

digest:
python engine/digest.py

run:
python -m http.server 8000
