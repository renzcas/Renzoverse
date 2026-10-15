import argparse
import base64
import hashlib
import json
import socketserver
import time


SAMPLE_STATES = (
    {
        "threat": 24,
        "cta": 18,
        "corruption": 12.5,
        "ctaBoss": "Telemetry Mock",
        "directive": "Observe the cave",
        "creatures": [
            {
                "name": "TunnelRat",
                "health": 85,
                "aggression": 20,
                "hunger": 35,
                "x": -8,
                "y": 4,
                "corruptionExposure": 3,
                "isAfraid": False,
            },
            {
                "name": "StoneCrawler",
                "health": 42,
                "aggression": 75,
                "hunger": 80,
                "x": 7,
                "y": -5,
                "corruptionExposure": 18,
                "isAfraid": True,
            },
        ],
        "corruptionGrid": [],
    },
    {
        "threat": 68,
        "cta": 74,
        "corruption": 56.0,
        "ctaBoss": "Telemetry Mock",
        "directive": "High threat sample",
        "creatures": [
            {
                "name": "TunnelRat",
                "health": 64,
                "aggression": 45,
                "hunger": 70,
                "x": -3,
                "y": 8,
                "corruptionExposure": 24,
                "isAfraid": True,
            },
            {
                "name": "GlowMoth",
                "health": 91,
                "aggression": 10,
                "hunger": 15,
                "x": 5,
                "y": 2,
                "corruptionExposure": 2,
                "isAfraid": False,
            },
        ],
        "corruptionGrid": [],
    },
)


class TelemetryHandler(socketserver.BaseRequestHandler):
    def handle(self):
        request_line = self._read_line()
        request_parts = request_line.split(b" ") if request_line else []
        if len(request_parts) < 2 or request_parts[1] != b"/telemetry/":
            self.request.sendall(b"HTTP/1.1 404 Not Found\r\nConnection: close\r\n\r\n")
            return

        headers = {}
        while True:
            line = self._read_line()
            if not line:
                return
            if line == b"\r\n":
                break
            name, value = line.decode("latin-1").split(":", 1)
            headers[name.strip().lower()] = value.strip()

        key = headers.get("sec-websocket-key")
        if headers.get("upgrade", "").lower() != "websocket" or not key:
            self.request.sendall(b"HTTP/1.1 400 Bad Request\r\nConnection: close\r\n\r\n")
            return

        accept = base64.b64encode(
            hashlib.sha1(
                (key + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11").encode("ascii")
            ).digest()
        )
        self.request.sendall(
            b"HTTP/1.1 101 Switching Protocols\r\n"
            b"Upgrade: websocket\r\n"
            b"Connection: Upgrade\r\n"
            b"Sec-WebSocket-Accept: "
            + accept
            + b"\r\n\r\n"
        )
        print(f"Browser connected from {self.client_address[0]}", flush=True)

        index = 0
        try:
            while True:
                payload = json.dumps(SAMPLE_STATES[index % len(SAMPLE_STATES)]).encode("utf-8")
                self.request.sendall(self._text_frame(payload))
                index += 1
                time.sleep(self.server.interval)
        except (BrokenPipeError, ConnectionResetError):
            pass
        finally:
            print("Browser disconnected", flush=True)

    def _read_line(self):
        line = bytearray()
        while len(line) <= 8192:
            char = self.request.recv(1)
            if not char:
                return None
            line.extend(char)
            if line.endswith(b"\r\n"):
                return bytes(line)
        return None

    @staticmethod
    def _text_frame(payload):
        length = len(payload)
        if length < 126:
            header = bytes((0x81, length))
        elif length < 65536:
            header = bytes((0x81, 126)) + length.to_bytes(2, "big")
        else:
            header = bytes((0x81, 127)) + length.to_bytes(8, "big")
        return header + payload


class TelemetryServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True

    def __init__(self, address, interval):
        self.interval = interval
        super().__init__(address, TelemetryHandler)


def main():
    parser = argparse.ArgumentParser(description="Mock the CaveSharp telemetry WebSocket.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8181)
    parser.add_argument("--interval", type=float, default=1.0)
    args = parser.parse_args()

    if args.interval <= 0:
        parser.error("--interval must be greater than zero")

    with TelemetryServer((args.host, args.port), args.interval) as server:
        print(f"Mock telemetry listening at ws://{args.host}:{args.port}/telemetry/", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nStopping mock telemetry server.", flush=True)


if __name__ == "__main__":
    main()
