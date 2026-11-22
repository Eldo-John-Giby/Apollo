"""Reassemble and authenticate the split Apollo stable-release archive."""
import hashlib
import json
from pathlib import Path


def main():
    root = Path(__file__).resolve().parent
    manifest = json.loads((root / "release-assets.json").read_text())
    archive = manifest["submission_archive"]
    target = root / archive["filename"]
    if target.exists():
        raise SystemExit(f"Output already exists: {target}")
    temporary = target.with_suffix(".zip.partial")
    total = hashlib.sha256()
    with temporary.open("xb") as output:
        for part in archive["parts"]:
            digest = hashlib.sha256()
            size = 0
            with (root / part["filename"]).open("rb") as source:
                while chunk := source.read(8 * 1024 * 1024):
                    output.write(chunk)
                    total.update(chunk)
                    digest.update(chunk)
                    size += len(chunk)
            if size != part["bytes"] or digest.hexdigest() != part["sha256"]:
                raise SystemExit(f"Part verification failed: {part['filename']}")
    if temporary.stat().st_size != archive["bytes"] or total.hexdigest() != archive["sha256"]:
        raise SystemExit("Assembled archive verification failed")
    temporary.rename(target)
    print(f"Verified {target.name}: {total.hexdigest()}")


if __name__ == "__main__":
    main()
