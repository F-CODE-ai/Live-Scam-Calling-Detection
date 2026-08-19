"""
live_bridge.py

Captures your real microphone audio, runs it through the real ASR model,
and sends the resulting text to your backend over the same session your
browser is watching.

Run it like this (get the session id from your browser screen first):
    python -m app.live_bridge sess_xxxxxxxxxx
"""
import asyncio
import json
import sys
import websockets

from app.audio.recorder import AudioRecorder
from app.asr.sherpa import ASRService


async def main():
    if len(sys.argv) < 2:
        print("You forgot the session id.")
        print("Usage: python -m app.live_bridge <session_id>")
        print("Get it from your browser screen after clicking 'Start Live Call Shield'.")
        return

    session_id = sys.argv[1]
    ws_url = f"ws://localhost:8000/ws/live/{session_id}"

    print("Loading ASR model... (takes a few seconds)")
    asr = ASRService()
    print("Model loaded.")

    recorder = AudioRecorder()

    async with websockets.connect(ws_url) as ws:
        print("Connected. Speak now.")
        print("Press CTRL+C to stop.")

        previous_text = ""
        for chunk in recorder.stream():
            transcript = asr.process_audio(chunk)
            if transcript and transcript != previous_text:
                previous_text = transcript
                print(f"You said: {transcript}")
                await ws.send(json.dumps({"transcript": transcript}))


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nStopped.")