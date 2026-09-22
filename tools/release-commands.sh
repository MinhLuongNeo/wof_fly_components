#!/usr/bin/env bash
# Sinh bởi tools/make-manifest.py. Chạy trong thư mục repo sau khi `gh auth login`.
# Mỗi tag một release; tên tag trùng thư mục trên server GameNative, file gốc vào tag root.
# Release đã có thì `gh release upload --clobber` để cập nhật file.
set -euo pipefail
cd "$(dirname "$0")/.."

if gh release view "root" >/dev/null 2>&1; then
  gh release upload "root" releases/root/imagefs_bionic.txz releases/root/experimental-drm-20260116.tzst releases/root/steam.tzst releases/root/proton-10.0-arm64ec.wcp releases/root/proton-10.0-4-arm64ec.wcp releases/root/proton-11.0-1-arm64ec.wcp releases/root/lsteamclient-arm64ec-proton10.tzst releases/root/lsteamclient-arm64ec-proton11.tzst releases/root/steam-token.tzst releases/root/steamclient-dlls-20260619.tzst releases/root/steam.exe releases/root/steam-proton11.exe releases/root/cacert.pem --clobber
else
  gh release create "root" releases/root/imagefs_bionic.txz releases/root/experimental-drm-20260116.tzst releases/root/steam.tzst releases/root/proton-10.0-arm64ec.wcp releases/root/proton-10.0-4-arm64ec.wcp releases/root/proton-11.0-1-arm64ec.wcp releases/root/lsteamclient-arm64ec-proton10.tzst releases/root/lsteamclient-arm64ec-proton11.tzst releases/root/steam-token.tzst releases/root/steamclient-dlls-20260619.tzst releases/root/steam.exe releases/root/steam-proton11.exe releases/root/cacert.pem --title "root" --notes "Gói lấy từ https://downloads.gamenative.app/ — xem sha256sums.txt"
fi

if gh release view "container_files" >/dev/null 2>&1; then
  gh release upload "container_files" releases/container_files/extras.tzst releases/container_files/container_pattern_common_20260821.tzst releases/container_files/container_pattern_gamenative.tzst --clobber
else
  gh release create "container_files" releases/container_files/extras.tzst releases/container_files/container_pattern_common_20260821.tzst releases/container_files/container_pattern_gamenative.tzst --title "container_files" --notes "Gói lấy từ https://downloads.gamenative.app/container_files — xem sha256sums.txt"
fi

if gh release view "graphics_driver" >/dev/null 2>&1; then
  gh release upload "graphics_driver" releases/graphics_driver/vortek-2.1.tzst releases/graphics_driver/zink-22.2.5.tzst releases/graphics_driver/turnip-25.2.0.tzst releases/graphics_driver/turnip-25.3.0.tzst releases/graphics_driver/wrapper-gamenative-20260724.tzst releases/graphics_driver/libvulkan_wrapper.tar.xz releases/graphics_driver/extra_libs.tzst --clobber
else
  gh release create "graphics_driver" releases/graphics_driver/vortek-2.1.tzst releases/graphics_driver/zink-22.2.5.tzst releases/graphics_driver/turnip-25.2.0.tzst releases/graphics_driver/turnip-25.3.0.tzst releases/graphics_driver/wrapper-gamenative-20260724.tzst releases/graphics_driver/libvulkan_wrapper.tar.xz releases/graphics_driver/extra_libs.tzst --title "graphics_driver" --notes "Gói lấy từ https://downloads.gamenative.app/graphics_driver — xem sha256sums.txt"
fi

if gh release view "dxwrapper" >/dev/null 2>&1; then
  gh release upload "dxwrapper" releases/dxwrapper/dxvk-2.7.1.tzst releases/dxwrapper/vkd3d-3.0b.tzst --clobber
else
  gh release create "dxwrapper" releases/dxwrapper/dxvk-2.7.1.tzst releases/dxwrapper/vkd3d-3.0b.tzst --title "dxwrapper" --notes "Gói lấy từ https://downloads.gamenative.app/dxwrapper — xem sha256sums.txt"
fi

if gh release view "wincomponents" >/dev/null 2>&1; then
  gh release upload "wincomponents" releases/wincomponents/direct3d.tzst releases/wincomponents/directsound.tzst releases/wincomponents/directmusic.tzst releases/wincomponents/directshow.tzst releases/wincomponents/directplay.tzst releases/wincomponents/vcrun2010.tzst releases/wincomponents/wmdecoder.tzst releases/wincomponents/opengl.tzst releases/wincomponents/openal.tzst releases/wincomponents/xaudio.tzst releases/wincomponents/ddraw.tzst --clobber
else
  gh release create "wincomponents" releases/wincomponents/direct3d.tzst releases/wincomponents/directsound.tzst releases/wincomponents/directmusic.tzst releases/wincomponents/directshow.tzst releases/wincomponents/directplay.tzst releases/wincomponents/vcrun2010.tzst releases/wincomponents/wmdecoder.tzst releases/wincomponents/opengl.tzst releases/wincomponents/openal.tzst releases/wincomponents/xaudio.tzst releases/wincomponents/ddraw.tzst --title "wincomponents" --notes "Gói lấy từ https://downloads.gamenative.app/wincomponents — xem sha256sums.txt"
fi

if gh release view "core_drivers" >/dev/null 2>&1; then
  gh release upload "core_drivers" releases/core_drivers/SD8Elite_800.51.zip releases/core_drivers/SD8Elite_2-842.6.zip --clobber
else
  gh release create "core_drivers" releases/core_drivers/SD8Elite_800.51.zip releases/core_drivers/SD8Elite_2-842.6.zip --title "core_drivers" --notes "Gói lấy từ https://downloads.gamenative.app/core_drivers — xem sha256sums.txt"
fi

