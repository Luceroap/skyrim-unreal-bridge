"""Queue every unique Tamriel model from the generated full-world manifest.

This only writes the resumable asset-service queue and model index. It does not
modify Skyrim, Unreal assets, or source files.
"""
import json
import os

ROOT = os.path.dirname(os.path.abspath(__file__))
AREA = os.path.join(ROOT, "area2")
TAM = os.path.join(AREA, "tamriel")


def load_models(path):
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as f:
        value = json.load(f)
    if isinstance(value, dict):
        return value
    return {str(item[0]): str(item[1]) for item in value if isinstance(item, list) and len(item) >= 2}


def main():
    manifest = load_models(os.path.join(TAM, "models.json"))
    if not manifest:
        raise SystemExit("area2/tamriel/models.json is missing; run tamriel_world.py first")
    index_path = os.path.join(AREA, "models.json")
    index = load_models(index_path)
    index.update(manifest)
    with open(index_path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(index, f, indent=0, sort_keys=True)
    ready_path = os.path.join(AREA, "ready.txt")
    failed_path = os.path.join(AREA, "failed.txt")
    request_path = os.path.join(AREA, "requests.txt")
    ready = set(open(ready_path, encoding="utf-8", errors="replace").read().split()) if os.path.exists(ready_path) else set()
    failed = set(open(failed_path, encoding="utf-8", errors="replace").read().split()) if os.path.exists(failed_path) else set()
    existing = set(open(request_path, encoding="utf-8", errors="replace").read().split()) if os.path.exists(request_path) else set()
    pending = sorted(set(manifest) - ready - failed - existing)
    with open(request_path, "a", encoding="utf-8", newline="\n") as f:
        for name in pending:
            f.write(name + "\n")
    print("Tamriel models: %d" % len(manifest))
    print("Already ready: %d" % len(ready & set(manifest)))
    print("Already failed: %d" % len(failed & set(manifest)))
    print("Already queued: %d" % len(existing & set(manifest)))
    print("Newly queued: %d" % len(pending))


if __name__ == "__main__":
    main()
