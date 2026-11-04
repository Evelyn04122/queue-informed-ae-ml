"""Download the current official NHS Artificial HES A&E sample for schema/EDA work.

The NHS describes this release as a pipeline-development resource: fields are
generated independently, so it must not be used for predictive-model claims.
This script downloads and extracts the official 10,000-row sample only.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from zipfile import ZipFile

import requests

URL = ("https://files.digital.nhs.uk/assets/Services/Artificial%20data/"
       "Artificial%20HES%20final/artificial_hes_ae_202302_v1_sample.zip")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, required=True)
    args = parser.parse_args()
    raw_dir = args.data_dir / "nhs_artificial_hes_ae"
    raw_dir.mkdir(parents=True, exist_ok=True)
    archive = raw_dir / "artificial_hes_ae_sample.zip"

    if not archive.exists():
        print("Downloading official NHS Artificial HES A&E sample...")
        with requests.get(URL, stream=True, timeout=120) as response:
            response.raise_for_status()
            with archive.open("wb") as file:
                for block in response.iter_content(chunk_size=1024 * 1024):
                    if block:
                        file.write(block)

    with ZipFile(archive) as source:
        source.extractall(raw_dir)
        print("Extracted files:")
        for name in source.namelist():
            print(" -", name)
    print("Use these files for schema inspection and EDA only; do not train a predictive model on them.")

if __name__ == "__main__":
    main()
