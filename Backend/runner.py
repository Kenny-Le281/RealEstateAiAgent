"""Run the full pipeline:
1) Fetch API data (API.py)
2) Consolidate / select fields (consolidation.py)
3) Run web scraper on the selected JSON (web-scraper.py)

This is intentionally implemented as a small orchestrator script (subprocess calls),
so it works even without treating Backend/ as a Python package.
"""

import subprocess
import sys
from pathlib import Path


def run_script(script_path: Path):
    print(f"\n=== Running: {script_path.name} ===")
    subprocess.run([sys.executable, str(script_path)], check=True)


def main():
    repo_root = Path(__file__).resolve().parents[1]

    api_script = repo_root / "Backend" / "API" / "api_property_response.py"
    consolidation_script = repo_root / "Backend" / "API" / "consolidation.py"
    webscraper_script = repo_root / "Backend" / "web-scraping" / "web-scraper.py"

    run_script(api_script)
    run_script(consolidation_script)
    run_script(webscraper_script)


if __name__ == "__main__":
    main()
