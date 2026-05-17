"""
sl_loop.py — Screenshot Loop (SL)
VKB Spin Doctor — Phase 2
-------------------------------
Takes a screenshot → sends to Gemma 4 in LM Studio → prints diagnosis.

HOW TO RUN:
  1. Make sure LM Studio is open with Gemma 4 loaded + server ON (port 1234)
  2. Open your game (War Thunder etc) on screen
  3. Run this script: python sl_loop.py
  4. It will screenshot, send to AI, print what it sees

STOP THE LOOP: Press Ctrl + C
"""

import mss
import mss.tools
import base64
import json
import urllib.request
import urllib.error
import time

# ── CONFIG ────────────────────────────────────────────────────────────────────
LM_STUDIO_URL  = "http://localhost:1234/v1/chat/completions"
MODELS_URL     = "http://localhost:1234/v1/models"
DELAY_SECONDS  = 5       # How many seconds between each screenshot loop
MAX_TOKENS     = 400     # How long the AI's reply can be

SYSTEM_PROMPT = (
    "You are a flight sim assistant helping a beginner joystick user. "
    "Look at the screenshot and describe what you see in plain English. "
    "Focus on: axis bindings, control settings, error messages, "
    "unmapped axes, the spin bug (X axis inverted or wrong). "
    "Be brief and helpful. If you see nothing unusual, say so."
)
# ─────────────────────────────────────────────────────────────────────────────


def get_loaded_model():
    """Ask LM Studio which model is currently loaded."""
    try:
        req = urllib.request.Request(MODELS_URL)
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            models = data.get("data", [])
            if models:
                model_id = models[0]["id"]
                print(f"[OK] Model detected: {model_id}")
                return model_id
            else:
                print("[WARN] No model loaded in LM Studio. Load Gemma 4 first.")
                return None
    except Exception as e:
        print(f"[ERROR] Can't reach LM Studio: {e}")
        print("        Is LM Studio open? Is the server ON? (port 1234)")
        return None


def take_screenshot():
    """Take a screenshot of the main monitor. Returns PNG bytes."""
    with mss.mss() as sct:
        monitor = sct.monitors[1]  # monitor 1 = main screen
        shot = sct.grab(monitor)
        png_bytes = mss.tools.to_png(shot.rgb, shot.size)
    return png_bytes


def ask_ai(model_id, png_bytes):
    """Send screenshot to Gemma 4 via LM Studio. Returns AI reply text."""
    img_b64 = base64.b64encode(png_bytes).decode("utf-8")

    payload = {
        "model": model_id,
        "max_tokens": MAX_TOKENS,
        "messages": [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{img_b64}"
                        }
                    },
                    {
                        "type": "text",
                        "text": "What do you see in this screenshot? Any joystick or axis issues?"
                    }
                ]
            }
        ]
    }

    req = urllib.request.Request(
        LM_STUDIO_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            return result["choices"][0]["message"]["content"]
    except urllib.error.URLError as e:
        return f"[ERROR] Network error: {e}"
    except KeyError:
        return "[ERROR] Unexpected response from LM Studio."


def main():
    print("=" * 60)
    print("  VKB Spin Doctor — Screenshot Loop (SL)")
    print("=" * 60)
    print()

    # Step 1: Check LM Studio is running and find the model
    model_id = get_loaded_model()
    if not model_id:
        input("\nFix the issue above, then press Enter to retry...")
        model_id = get_loaded_model()
        if not model_id:
            print("Giving up. Check LM Studio and try again.")
            return

    print()
    print(f"Loop will screenshot every {DELAY_SECONDS} seconds.")
    print("Press Ctrl + C to stop.\n")
    time.sleep(2)

    loop_count = 0

    while True:
        loop_count += 1
        print(f"── Screenshot #{loop_count} ──────────────────────────────────")

        # Step 2: Take screenshot
        print("  Taking screenshot...")
        png_bytes = take_screenshot()
        print(f"  Screenshot taken ({len(png_bytes) // 1024} KB)")

        # Step 3: Send to AI
        print("  Sending to Gemma 4... (may take 5-15 seconds)")
        reply = ask_ai(model_id, png_bytes)

        # Step 4: Print diagnosis
        print()
        print("  AI SAYS:")
        print("  " + reply.replace("\n", "\n  "))
        print()

        # Step 5: Wait before next loop
        print(f"  Waiting {DELAY_SECONDS} seconds... (Ctrl+C to stop)")
        time.sleep(DELAY_SECONDS)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nLoop stopped. Bye!")
