[app]

title = MAC ULTRA
package.name = macultra
package.domain = org.morpheus

source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,json,mp3,wav,ogg,dat
source.include_patterns = assets/*,*.png,*.mp3

version = 1.0.0

icon.filename = mac-ultra-icon.png

requirements = python3,kivy,android,httpx,httpcore,anyio,sniffio,h11,certifi,idna

orientation = portrait
fullscreen = 1

android.archs = arm64-v8a

p4a.bootstrap = sdl2

android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,MANAGE_EXTERNAL_STORAGE,READ_MEDIA_IMAGES,READ_MEDIA_VIDEO,READ_MEDIA_AUDIO
android.wakelock = True

android.api = 34
android.minapi = 21
android.ndk = 25b
android.build_tools_version = 33.0.2
android.accept_sdk_license = True

[buildozer]

log_level = 2
warn_on_root = 1
