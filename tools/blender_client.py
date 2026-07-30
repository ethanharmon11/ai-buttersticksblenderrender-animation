"""Direct socket client for the BlenderMCP addon (localhost:9876).

Usage:
  python blender_client.py info                     # scene info
  python blender_client.py exec "<python code>"     # run bpy code in Blender
  python blender_client.py execfile <path>          # run a .py file in Blender
  python blender_client.py shot <out.png> [size]    # viewport screenshot
"""
import json
import socket
import sys

HOST, PORT = "localhost", 9876


def send(cmd_type, params=None, timeout=60):
    payload = json.dumps({"type": cmd_type, "params": params or {}}).encode()
    s = socket.create_connection((HOST, PORT), timeout=timeout)
    s.sendall(payload)
    chunks = []
    s.settimeout(timeout)
    while True:
        try:
            chunk = s.recv(65536)
        except socket.timeout:
            break
        if not chunk:
            break
        chunks.append(chunk)
        try:
            json.loads(b"".join(chunks).decode())
            break  # full JSON received
        except ValueError:
            continue
    s.close()
    return json.loads(b"".join(chunks).decode())


def main():
    mode = sys.argv[1]
    if mode == "info":
        r = send("get_scene_info")
    elif mode == "exec":
        r = send("execute_code", {"code": sys.argv[2]})
    elif mode == "execfile":
        code = open(sys.argv[2], encoding="utf-8").read()
        r = send("execute_code", {"code": code}, timeout=180)
    elif mode == "shot":
        size = int(sys.argv[3]) if len(sys.argv) > 3 else 1200
        r = send("get_viewport_screenshot",
                 {"filepath": sys.argv[2], "max_size": size, "format": "png"})
    else:
        raise SystemExit(f"unknown mode {mode}")
    print(json.dumps(r, indent=1)[:4000])


if __name__ == "__main__":
    main()
