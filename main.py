import zlib

with open("app_payload.dat", "rb") as f:
    compressed = f.read()

source = zlib.decompress(compressed).decode("utf-8")

exec(source)
