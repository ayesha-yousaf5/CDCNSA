"""TTS worker - runs edge_tts with text read from a file.

Called by voice_service.py to avoid Windows subprocess Unicode issues.
Usage: python _tts_worker.py --voice VOICE --text-file PATH --output PATH
"""
import argparse
import asyncio
import sys


async def _synthesize(text: str, voice: str, output: str):
    import edge_tts
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--voice", required=True)
    parser.add_argument("--text-file", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    with open(args.text_file, "r", encoding="utf-8") as f:
        text = f.read()

    if not text.strip():
        print("Error: empty text", file=sys.stderr)
        sys.exit(1)

    asyncio.run(_synthesize(text, args.voice, args.output))


if __name__ == "__main__":
    main()
