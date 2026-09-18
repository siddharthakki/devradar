.PHONY: test lint ingest digest run

test:
pytest tests/ -v

lint:
python -m py_compile engine/analyzer.py engine/store.py

ingest:
python engine/analyzer.py

digest:
python engine/digest.py

run:
python -m http.server 8000
