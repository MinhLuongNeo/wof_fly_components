#!/usr/bin/env python3
"""Rà mọi tên gói mà mã app có thể xin theo tên, đối chiếu với kho.

Nguồn tên: (1) năm file assets/*_download.json của app (thư mục/tên), (2) mọi chuỗi literal trong mã Kotlin/Java trông
như tên file gói (.tzst .txz .tar.xz .wcp .zip .pem .exe). Tên nào máy chủ GameNative có (HEAD 200) mà tools/files.txt
chưa có thì in ra dạng dòng files.txt để chép vào. Dùng: tools/audit-names.py [--app <cây app>] [--apply]
"""
import argparse, glob, json, os, re, subprocess, sys, concurrent.futures as cf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE_BASE = "https://downloads.gamenative.app"
EXT = r"\.(?:tzst|txz|tar\.xz|wcp|zip|pem|exe)"

def head_ok(path):
    out = subprocess.run(["curl", "-sIL", "--max-time", "40", f"{SOURCE_BASE}/{path}"], capture_output=True, text=True).stdout
    code = None
    for line in out.replace("\r", "").splitlines():
        if line.startswith("HTTP/"):
            code = line.split()[1]
    return path, code == "200"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--app", default=os.path.join(ROOT, "..", "wof_droid", "game_native_source_code", "app", "src", "main"))
    ap.add_argument("--apply", action="store_true", help="ghi thẳng các dòng thiếu vào tools/files.txt")
    a = ap.parse_args()

    names = set()
    for f in glob.glob(os.path.join(a.app, "assets", "*_download.json")):
        folder = os.path.basename(f).replace("_download.json", "")
        for c in json.load(open(f, encoding="utf-8"))["components"]:
            rel = c["url"].split("downloads.gamenative.app/", 1)[1] if "downloads.gamenative.app/" in c["url"] else f"{folder}/{c['name']}"
            names.add(rel)
    lit = re.compile(r'"([A-Za-z0-9][A-Za-z0-9_./+-]*' + EXT + r')"')
    for dirpath, _, files in os.walk(os.path.join(a.app, "java")):
        for fn in files:
            if fn.endswith((".kt", ".java")):
                for m in lit.finditer(open(os.path.join(dirpath, fn), encoding="utf-8", errors="ignore").read()):
                    n = m.group(1)
                    if n.startswith(("fexcore/", "box86_64/", "wowbox64/", "dxwrapper/cnc", "inputcontrols/")):
                        continue  # asset trong APK
                    names.add(n)

    have = set()
    for line in open(os.path.join(ROOT, "tools", "files.txt"), encoding="utf-8"):
        if "\t" in line and not line.startswith("#"):
            have.add(line.rstrip("\n").split("\t", 1)[1])
    candidates = sorted(n for n in names if n not in have and not n.startswith("http"))
    with cf.ThreadPoolExecutor(12) as ex:
        results = list(ex.map(head_ok, candidates))
    missing = [p for p, ok in results if ok]
    absent = [p for p, ok in results if not ok]
    print(f"tên trong mã/JSON: {len(names)}; đã có trong kho: {len(names & have)}; máy chủ có mà kho thiếu: {len(missing)}; "
          f"tên không có trên máy chủ (asset trong APK hay tên động): {len(absent)}", file=sys.stderr)
    lines = []
    for p in missing:
        tag = p.split("/", 1)[0] if "/" in p else "root"
        lines.append(f"{tag}\t{p}")
    print("\n".join(lines))
    if a.apply and lines:
        with open(os.path.join(ROOT, "tools", "files.txt"), "a", encoding="utf-8") as out:
            out.write("\n".join(lines) + "\n")
        print(f"đã thêm {len(lines)} dòng vào tools/files.txt", file=sys.stderr)
    if absent:
        print("-- không có trên máy chủ: " + ", ".join(absent), file=sys.stderr)

if __name__ == "__main__":
    main()
