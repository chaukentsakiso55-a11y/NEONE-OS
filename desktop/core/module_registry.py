import json
import os
import subprocess
import sys

DEFAULT_MODULES = {
    "Pulsar AI": ["vendor/pulsar/main.py", "vendor/pulsar/desktop/main.py"],
    "Infinity OS": ["vendor/infinity/main.py", "vendor/infinity/START-INFINITY-OS.bat"],
    "EXO": ["vendor/exo/main.py"],
    "Ember": ["vendor/ember/main.py"],
    "AEGIS / ASTER": ["vendor/aster/main.py"],
}

class ModuleRegistry:
    def __init__(self, root):
        self.root = os.path.abspath(root)
        self.manifest_path = os.path.join(self.root, "vendor", "manifest.json")
        self.modules = dict(DEFAULT_MODULES)
        self._load_manifest()

    def _load_manifest(self):
        try:
            with open(self.manifest_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            for name, candidates in data.get("modules", {}).items():
                if isinstance(candidates, list):
                    self.modules[name] = candidates
        except Exception:
            pass

    def resolve(self, name):
        for candidate in self.modules.get(name, []):
            path = os.path.join(self.root, candidate.replace("/", os.sep))
            if os.path.isfile(path):
                return path
        return None

    def status(self, name):
        return "ready" if self.resolve(name) else "source not imported"

    def launch(self, name):
        path = self.resolve(name)
        if not path:
            raise FileNotFoundError(f"{name} source has not been imported into desktop/vendor yet")
        cwd = os.path.dirname(path)
        ext = os.path.splitext(path)[1].lower()
        if ext == ".py":
            return subprocess.Popen([sys.executable, path], cwd=cwd)
        if ext in {".bat", ".cmd"}:
            return subprocess.Popen(["cmd", "/c", path], cwd=cwd)
        if ext == ".exe":
            return subprocess.Popen([path], cwd=cwd)
        return subprocess.Popen([path], cwd=cwd, shell=True)
