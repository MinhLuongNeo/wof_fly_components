#!/usr/bin/env bash
# Tải các gói trong tools/files.txt từ downloads.gamenative.app vào releases/<tag>/<tên file>.
# Chạy lại bao nhiêu lần cũng được: file đã đủ kích thước thì bỏ qua, file dở thì tải tiếp (-C -).
# Dùng: tools/fetch.sh [danh-sách]   (mặc định tools/files.txt)
set -u
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LIST="${1:-$ROOT/tools/files.txt}"
BASE="https://downloads.gamenative.app"
fail=0
while IFS=$'\t' read -r tag path; do
  [[ -z "${tag:-}" || "$tag" == \#* ]] && continue
  name="${path##*/}"
  dir="$ROOT/releases/$tag"
  dest="$dir/$name"
  mkdir -p "$dir"
  expected="$(curl -sIL --max-time 30 "$BASE/$path" | tr -d '\r' | awk 'BEGIN{IGNORECASE=1} /^content-length:/{len=$2} END{print len}')"
  if [[ -z "$expected" ]]; then
    echo "LỖI  $tag/$name: server không trả kích thước"; fail=1; continue
  fi
  if [[ -f "$dest" && "$(stat -f %z "$dest")" == "$expected" ]]; then
    echo "CÓ   $tag/$name ($expected byte)"; continue
  fi
  echo "TẢI  $tag/$name ($expected byte)"
  if curl -sS -L --fail --retry 5 --retry-delay 3 -C - -o "$dest" "$BASE/$path"; then
    actual="$(stat -f %z "$dest")"
    if [[ "$actual" != "$expected" ]]; then
      echo "LỖI  $tag/$name: có $actual byte, server nói $expected"; fail=1
    else
      echo "XONG $tag/$name ($actual byte)"
    fi
  else
    echo "LỖI  $tag/$name: curl thất bại"; fail=1
  fi
done < "$LIST"
echo "--- hết danh sách, lỗi=$fail"
exit $fail
