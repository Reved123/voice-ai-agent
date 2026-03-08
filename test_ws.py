import websocket

ws = websocket.WebSocket()
ws.connect("ws://127.0.0.1:8000/ws/voice")

with open("test.wav", "rb") as f:
    ws.send_binary(f.read())

result = ws.recv()
print(result)