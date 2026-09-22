# wof_fly_components

Kho gói runtime của app WOF Fly — **nguồn tải duy nhất của app** (quyết định 2026-09-22): gói chép lại từ máy chủ
GameNative (`downloads.gamenative.app`) và từ GitHub của Arihany (DXVK/wowbox64 dạng `.wcp`), để app không phụ thuộc
vào máy chủ nào ngoài repo này. Chỉ chứa gói nhị phân mã nguồn mở (Proton, Wine, DXVK, VKD3D, Turnip, Vortek, driver
Adreno, wincomponents) và bản dựng imagefs/container pattern của GameNative. App tải hỏng gói nào nghĩa là kho thiếu
gói đó: thêm vào `tools/files.txt`, không có đường lui.

## Bố cục

Gói nằm ở **GitHub Releases**, không nằm trong cây git (GitHub từ chối file trên 100 MB trong git).
Mỗi thư mục trên máy chủ GameNative là một release có tag trùng tên; file ở gốc máy chủ vào tag `root`:

| Trên máy chủ GameNative | Ở đây |
| --- | --- |
| `downloads.gamenative.app/imagefs_bionic.txz` | `releases/download/root/imagefs_bionic.txz` |
| `downloads.gamenative.app/container_files/extras.tzst` | `releases/download/container_files/extras.tzst` |
| `downloads.gamenative.app/wincomponents/xaudio.tzst` | `releases/download/wincomponents/xaudio.tzst` |
| `github.com/Arihany/WinlatorWCPHub/releases/download/DXVK/dxvk-2.7.1.wcp` | `releases/download/DXVK/dxvk-2.7.1.wcp` |

Nên URL đầy đủ là `https://github.com/MinhLuongNeo/wof_fly_components/releases/download/<tag>/<tên file>`,
và app chỉ cần đổi gốc URL, giữ nguyên đường dẫn tương đối, riêng file gốc thêm `root/`.

Tên file **giữ nguyên** như trên máy chủ GameNative: app coi cùng tên là cùng nội dung, muốn đổi nội dung
thì đổi tên.

## Trong cây git

- `files.json` — từng file: tag, tên, kích thước, SHA-256, URL nguồn và URL ở đây.
- `sha256sums.txt` — kiểm bằng `cd releases && shasum -a 256 -c ../sha256sums.txt`.
- `manifest.json` — danh mục theo đúng schema app đọc (`ManifestData`): **chỉ** những mục của danh mục gốc GameNative
  (`tools/upstream-manifest.json`) có file trong kho này, URL trỏ về đây. Mục chưa có trong kho bị bỏ.
- `component-manifest.json`, `drivers-manifest.json` — chỉ mục phẳng `{tên: file}` cho hộp thoại Wine/Proton manager
  (file ở tag `root`) và Driver manager (file ở tag `drivers`), cùng định dạng với chỉ mục gốc của GameNative.
- `tools/files.txt` — danh sách `tag<TAB>đường dẫn trên máy chủ GameNative` hoặc `tag<TAB>URL đầy đủ`. Thêm gói thì thêm dòng ở đây.
- `tools/fetch.sh` — tải mọi dòng trong `files.txt` vào `releases/<tag>/`, tải tiếp nếu dở, bỏ qua nếu đủ.
- `tools/make-manifest.py` — sinh ba file trên cùng `tools/release-commands.sh`.
- `tools/release-commands.sh` — lệnh `gh release create`/`upload` cho từng tag.

## Cập nhật kho

```bash
tools/fetch.sh
tools/make-manifest.py
tools/release-commands.sh      # cần `gh auth login` trước
git add -A && git commit -m "Cập nhật kho" && git push
```

## Giấy phép

Proton, Wine, DXVK, VKD3D, Mesa (Turnip, Zink), Box64, FEX theo giấy phép của từng dự án, giữ nguyên
trong gói. imagefs và container pattern là bản dựng của GameNative (https://gamenative.app).
