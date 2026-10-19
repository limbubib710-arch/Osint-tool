#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
  ██╗  ██╗███████╗██╗   ██╗███████╗ ██████╗ ██████╗  ██████╗ ███████╗
  ██║ ██╔╝██╔════╝██║   ██║██╔════╝██╔═══██╗██╔══██╗██╔════╝ ██╔════╝
  █████╔╝ █████╗  ██║   ██║███████╗██║   ██║██████╔╝██║  ███╗█████╗
  ██╔═██╗ ██╔══╝  ╚██╗ ██╔╝╚════██║██║   ██║██╔══██╗██║   ██║██╔══╝
  ██║  ██╗███████╗ ╚████╔╝ ███████║╚██████╔╝██║  ██║╚██████╔╝███████╗
  ╚═╝  ╚═╝╚══════╝  ╚═══╝  ╚══════╝ ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚══════╝
        UNLIMITED API KEY GENERATOR  v2.0  [ Termux Edition ]
"""

import os, sys, uuid, secrets, string, base64, hashlib, time, json

# ---------------- config ----------------
STYLES = {
    "1": ("UUID4",            lambda: str(uuid.uuid4())),
    "2": ("UUID4 Uppercase",  lambda: str(uuid.uuid4()).upper()),
    "3": ("Hex (32)",         lambda: secrets.token_hex(16)),
    "4": ("Hex (64)",         lambda: secrets.token_hex(32)),
    "5": ("Base64 URL-Safe",  lambda: base64.urlsafe_b64encode(secrets.token_bytes(32)).decode().rstrip("=")),
    "6": ("OpenAI Style",     lambda: "sk-" + "".join(secrets.choice(string.ascii_letters + string.digits) for _ in range(48))),
    "7": ("Stripe Style",     lambda: "sk_live_" + "".join(secrets.choice(string.ascii_letters + string.digits) for _ in range(24))),
    "8": ("AWS Style",        lambda: "AKIA" + "".join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(16))),
    "9": ("GitHub Token",     lambda: "ghp_" + "".join(secrets.choice(string.ascii_letters + string.digits) for _ in range(36))),
    "10":("Segmented (XXXX-XXXX-XXXX-XXXX)",
          lambda: "-".join("".join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(4)) for _ in range(4))),
    "11":("Hash SHA-256",     lambda: hashlib.sha256(secrets.token_bytes(32)).hexdigest()),
    "12":("Custom Prefix",    None),  # handled interactively
}

SAVE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "generated_keys.json")

def safe_input(prompt, default=""):
    """Input that never crashes (EOFError/KeyboardInterrupt-safe)."""
    try:
        return input(prompt).strip() or default
    except (EOFError, KeyboardInterrupt):
        print()
        return default

def generate(style_id, count):
    keys = []
    name, fn = STYLES[style_id]
    if style_id == "12":
        prefix = safe_input("  Enter prefix (e.g. myapp_): ", "key_")
        length = safe_input("  Length [default 32]: ", "32")
        try: length = max(8, int(length))
        except ValueError: length = 32
        alphabet = string.ascii_letters + string.digits
        fn = lambda: prefix + "".join(secrets.choice(alphabet) for _ in range(length))
    for _ in range(count):
        keys.append(fn())
    return name, keys

def save_keys(keys, style_name):
    data = []
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE) as f: data = json.load(f)
        except Exception: data = []
    data.append({"style": style_name, "time": time.strftime("%Y-%m-%d %H:%M:%S"), "keys": keys})
    with open(SAVE_FILE, "w") as f:
        json.dump(data, f, indent=2)

def show_menu():
    print("\033[95m" + __doc__ + "\033[0m")
    print("  \033[92m─── KEY STYLES ───\033[0m")
    for k, (name, _) in sorted(STYLES.items(), key=lambda x: int(x[0])):
        print(f"   \033[93m[{k:>2}]\033[0m {name}")
    print(f"   \033[93m[ q]\033[0m Quit   \033[93m[ s]\033[0m Show saved keys")

def main():
    while True:
        show_menu()
        choice = safe_input("\n  \033[96mSelect style ➜ \033[0m", "q").lower()
        if choice == "q":
            print("\033[92m[*] Keys saved to " + SAVE_FILE + " — bye!\033[0m")
            break
        if choice == "s":
            if os.path.exists(SAVE_FILE):
                with open(SAVE_FILE) as f:
                    print(json.dumps(json.load(f), indent=2))
            else:
                print("  No saved keys yet.")
            continue
        if choice not in STYLES:
            print("  \033[91m[!] Invalid choice, try again.\033[0m")
            continue
        count_raw = safe_input("  How many keys? [default 1]: ", "1")
        try: count = max(1, int(count_raw))
        except ValueError: count = 1

        name, keys = generate(choice, count)
        print(f"\n  \033[92m[+] Generated {len(keys)} key(s) — {name}:\033[0m\n")
        for k in keys:
            print(f"    \033[96m{k}\033[0m")
        save_keys(keys, name)
        print(f"\n  \033[90m[*] Auto-saved to {SAVE_FILE}\033[0m")
        safe_input("\n  Press Enter to continue...")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\033[91m[!] Unexpected error: {e}\033[0m")
        sys.exit(1)
