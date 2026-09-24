import argparse
import json
import os
import re
import zipfile
from pathlib import Path

MODULE_MARKERS = {
    "ember": ["Ember/main.py", "AMBER/main.py"],
    "exo": ["EXO_Wolf_AI_Desktop_Full_v2.0/main.py", "EXO_Wolf/index.html"],
    "aster": ["ASTER_Agent_v0.2/main.py"],
    "infinity": ["Infinity-OS-V7-REBORN-BEYOND/main.py", "Infinity-OS-Pulsar-AI-Mark-LII-Unified/START-INFINITY-OS.bat"],
    "pulsar": ["Pulsar-AI-ALL-FUSION-v1.6/desktop/"],
    "mark-liv": ["Mark-LIV-main/main.py", "Mark-LIV-main/core/"],
}

BLOCKED = {
    ".env", ".env.local", "provider_secrets.json", "providers.local.json",
    "secrets.json", "credentials.json", "google-services.json", "keystore.properties"
}

SECRET_LINE = re.compile(r"(?i)^([^\n]*(?:api[_-]?key|secret|token|password)[^:=\n]*[:=]\s*)(.+)$")

def normalize(name):
    return name.replace("\\", "/").strip("/")

def blocked(path):
    name = Path(path).name.lower()
    return name in BLOCKED or "__pycache__" in path or path.endswith(".pyc")

def detect_module(names):
    for module, markers in MODULE_MARKERS.items():
        for marker in markers:
            if any(name.lower().startswith(marker.lower()) for name in names):
                return module
    return None

def sanitize(text):
    lines = []
    for line in text.splitlines():
        match = SECRET_LINE.match(line)
        if match:
            lines.append(match.group(1) + "REDACTED")
        else:
            lines.append(line)
    return "\n".join(lines)

def import_zip(zip_path, destination):
    imported = 0
    with zipfile.ZipFile(zip_path) as archive:
        names = [normalize(n) for n in archive.namelist() if not n.endswith("/")]
        module = detect_module(names)
        if not module:
            return None, 0
        root = Path(destination) / module
        root.mkdir(parents=True, exist_ok=True)
        first = names[0].split("/")[0] if names else ""
        for name in names:
            if blocked(name):
                continue
            raw = archive.read(name)
            rel = name[len(first):].lstrip("/") if first and name.startswith(first) else name
            out = root / rel
            out.parent.mkdir(parents=True, exist_ok=True)
            try:
                out.write_text(sanitize(raw.decode("utf-8")), encoding="utf-8")
            except UnicodeDecodeError:
                out.write_bytes(raw)
            imported += 1
        return module, imported

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("zips", nargs="+")
    parser.add_argument("--dest", default="desktop/vendor")
    args = parser.parse_args()
    results = {}
    for item in args.zips:
        module, count = import_zip(item, args.dest)
        if module:
            results[module] = results.get(module, 0) + count
    manifest = {
        "modules": {
            "Pulsar AI": ["vendor/pulsar/main.py", "vendor/pulsar/desktop/main.py"],
            "Infinity OS": ["vendor/infinity/main.py", "vendor/infinity/START-INFINITY-OS.bat"],
            "EXO": ["vendor/exo/main.py"],
            "Ember": ["vendor/ember/main.py"],
            "AEGIS / ASTER": ["vendor/aster/main.py"],
            "Mark LIV": ["vendor/mark-liv/main.py"]
        },
        "imports": results
    }
    dest = Path(args.dest)
    dest.mkdir(parents=True, exist_ok=True)
    (dest / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main()
