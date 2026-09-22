#!/usr/bin/env python3
"""Sinh sha256sums.txt, files.json, manifest.json và tools/release-commands.sh từ releases/ và tools/files.txt.

Chạy sau tools/fetch.sh. Đối chiếu danh mục gốc của GameNative (manifest.json trong cây app) để giữ nguyên
id/variant/arch của từng mục, chỉ đổi URL sang release trên GitHub.

Dùng: tools/make-manifest.py [--upstream <manifest.json gốc>]
"""
import argparse
import datetime as dt
import hashlib
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = "MinhLuongNeo/wof_fly_components"
SOURCE_BASE = "https://downloads.gamenative.app"
RELEASE_BASE = f"https://github.com/{REPO}/releases/download"


def read_list(path):
    rows = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line or line.startswith("#"):
                continue
            tag, src = line.split("\t", 1)
            source = src if src.startswith(("http://", "https://")) else f"{SOURCE_BASE}/{src}"
            rows.append((tag, source, src.rsplit("/", 1)[-1]))
    return rows


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--upstream", default=os.path.join(ROOT, "tools", "upstream-manifest.json"))
    args = ap.parse_args()

    rows = read_list(os.path.join(ROOT, "tools", "files.txt"))
    files = []
    missing = []
    for tag, src, name in rows:
        local = os.path.join(ROOT, "releases", tag, name)
        if not os.path.isfile(local):
            missing.append(f"{tag}/{name}")
            continue
        files.append({
            "tag": tag,
            "name": name,
            "size": os.path.getsize(local),
            "sha256": sha256(local),
            "source": src,
            "url": f"{RELEASE_BASE}/{tag}/{name}",
        })
        print(f"{files[-1]['sha256'][:12]}  {tag}/{name}  {files[-1]['size']:>11,d}", file=sys.stderr)
    if missing:
        print("THIẾU trong releases/: " + ", ".join(missing), file=sys.stderr)
        sys.exit(1)

    today = dt.date.today().isoformat()
    by_source = {f["source"]: f for f in files}

    with open(os.path.join(ROOT, "sha256sums.txt"), "w", encoding="utf-8") as out:
        for f in files:
            out.write(f"{f['sha256']}  {f['tag']}/{f['name']}\n")

    with open(os.path.join(ROOT, "files.json"), "w", encoding="utf-8") as out:
        json.dump({"updatedAt": today, "releaseBase": RELEASE_BASE, "files": files}, out, ensure_ascii=False, indent=2)
        out.write("\n")

    # manifest.json theo đúng schema app đọc (ManifestData: version, updatedAt, items{loại: [id, name, url, variant, arch]}).
    # App chỉ tải từ kho này (quyết định 2026-09-22), nên danh mục CHỈ giữ mục có file trong kho — URL đổi sang GitHub;
    # mục chưa có trong kho bị bỏ (muốn có thì thêm dòng vào tools/files.txt).
    items = {}
    kept = dropped = 0
    if os.path.isfile(args.upstream):
        with open(args.upstream, encoding="utf-8") as f:
            upstream = json.load(f)
        for kind, entries in upstream.get("items", {}).items():
            for e in entries:
                url = e.get("url", "")
                if url in by_source:
                    items.setdefault(kind, []).append(dict(e, url=by_source[url]["url"]))
                    kept += 1
                else:
                    dropped += 1
    else:
        print(f"Không thấy danh mục gốc ở {args.upstream}", file=sys.stderr)
        sys.exit(1)
    with open(os.path.join(ROOT, "manifest.json"), "w", encoding="utf-8") as out:
        json.dump({"version": 1, "updatedAt": today, "items": items}, out, ensure_ascii=False, indent=2)
        out.write("\n")
    print(f"manifest.json: giữ {kept} mục có trong kho, bỏ {dropped} mục", file=sys.stderr)

    # Hai chỉ mục phẳng {tên hiển thị: tên file} cho hộp thoại Wine/Proton manager (component-manifest.json, file ở tag
    # root, tên bắt đầu bằng proton/wine) và Driver manager (drivers-manifest.json, file ở tag drivers). Cùng định dạng
    # với chỉ mục gốc của GameNative; app ghép tên file vào kho (root/… hay drivers/…).
    component = {f["name"].rsplit(".", 1)[0]: f["name"] for f in files
                 if f["tag"] == "root" and f["name"].lower().startswith(("proton", "wine")) and f["name"].endswith(".wcp")}
    drivers = {f["name"].rsplit(".", 1)[0]: f["name"] for f in files if f["tag"] == "drivers"}
    for name, data in (("component-manifest.json", component), ("drivers-manifest.json", drivers)):
        with open(os.path.join(ROOT, name), "w", encoding="utf-8") as out:
            json.dump(data, out, ensure_ascii=False, indent=2)
            out.write("\n")
        print(f"{name}: {len(data)} mục", file=sys.stderr)

    tags = []
    for f in files:
        if f["tag"] not in tags:
            tags.append(f["tag"])
    with open(os.path.join(ROOT, "tools", "release-commands.sh"), "w", encoding="utf-8") as out:
        out.write("#!/usr/bin/env bash\n")
        out.write("# Sinh bởi tools/make-manifest.py. Chạy trong thư mục repo sau khi `gh auth login`.\n")
        out.write("# Mỗi tag một release; tên tag trùng thư mục trên máy chủ GameNative cũ, file gốc vào tag root.\n")
        out.write("# Release chưa có thì tạo kèm mọi file; có rồi thì chỉ tải lên file CHƯA có trên GitHub (so theo tên).\n")
        out.write("# Muốn thay một file đã có (đổi nội dung mà giữ tên — không nên): xoá asset trên GitHub rồi chạy lại.\n")
        out.write('set -euo pipefail\ncd "$(dirname "$0")/.."\n\n')
        out.write("upload_tag() {\n")
        out.write("  local tag=\"$1\"; shift\n")
        out.write("  local existing\n")
        out.write("  if existing=$(gh release view \"$tag\" --json assets --jq '.assets[].name' 2>/dev/null); then\n")
        out.write("    local missing=()\n")
        out.write("    for f in \"$@\"; do grep -qxF \"$(basename \"$f\")\" <<<\"$existing\" || missing+=(\"$f\"); done\n")
        out.write("    if [ ${#missing[@]} -eq 0 ]; then echo \"$tag: đủ $# file, không tải gì\"; return; fi\n")
        out.write("    echo \"$tag: tải lên ${#missing[@]} file còn thiếu\"\n")
        out.write("    gh release upload \"$tag\" \"${missing[@]}\"\n")
        out.write("  else\n")
        out.write("    echo \"$tag: tạo release với $# file\"\n")
        out.write("    gh release create \"$tag\" \"$@\" --title \"$tag\" --notes \"Gói của WOF Fly, nguồn gốc từng file xem files.json, kiểm bằng sha256sums.txt\"\n")
        out.write("  fi\n")
        out.write("}\n\n")
        for tag in tags:
            names = " ".join(f"releases/{tag}/{f['name']}" for f in files if f["tag"] == tag)
            out.write(f'upload_tag "{tag}" {names}\n\n')
    os.chmod(os.path.join(ROOT, "tools", "release-commands.sh"), 0o755)
    total = sum(f["size"] for f in files)
    print(f"{len(files)} file, {total / 2**20:,.1f} MB, {len(tags)} tag", file=sys.stderr)


if __name__ == "__main__":
    main()
