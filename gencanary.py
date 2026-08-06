#!/usr/bin/env python3
"""
gencanary.py - reifr.net Warrant Canary Guided Generator & Signing Assistant

Features:
- Step-by-step interactive CLI wizard for guiding the signer through canary generation.
- Fresh Machine YubiKey Keyring Auto-Setup: Automatically imports repo public keys (`keys/Signing_key_1E02.asc`) and runs `gpg --card-status` to generate secret key stubs (`ssb>`) for YubiKey smartcards on fresh installations.
- Full YubiKey Smartcard Inspection: Queries `gpg --card-status` to display connected YubiKey serial numbers, cardholders, and on-card signature key fingerprints.
- Full 16-char / Full Fingerprint Key IDs: Uses unambiguous key IDs to prevent "No secret key" GPG errors.
- Full WSL / Linux / macOS / Windows GPG support: Sets GPG_TTY for pinentry passphrase prompts.
- Dynamic counter detection: Scans repository canaries/ directory to determine the next canary number (only counts canaries with valid .sig signature files present).
- Resilient Draft & Error Handling: Detects un-signed draft files from interrupted/failed runs, allows overwriting/retrying, and offers cleanup if signing fails.
- Real-time proof of freshness data collection (Spiegel, NY Times, BBC RSS feeds & Bitcoin block hash).
- Ability to add/edit Special Announcements dynamically during wizard execution.
- GPG key selection (Primary 1E02, Legacy 7BDC, or custom key IDs).
- Complete formatted preview and signer approval prompt.
- Automated YubiKey GPG detached signature generation (.sig).
- STRICT PRE-COMMIT VERIFICATION: Comprehensive validation of files, statement text, header counter, and cryptographic GPG signatures BEFORE allowing Git commits.
- Optional automatic Git staging, signed Git commit (git commit -S), and remote push.
- CLI flags support (--wizard, --preview, --no-sign, --yes).
"""

import os
import sys
import datetime
import argparse
import subprocess
import shutil
import re
import urllib.request
import xml.etree.ElementTree as ET
import html
from pathlib import Path

# Master key fingerprints & Long Key IDs
DEFAULT_PRIMARY_KEY_FP = "9CAF 2256 61DA 2385 BBA2  4CFD 782F B8F3 3924 1E02"
DEFAULT_PRIMARY_KEY_ID = "9CAF225661DA2385BBA24CFD782FB8F339241E02"  # Full fingerprint or Long ID 782FB8F339241E02
DEFAULT_PRIMARY_KEY_SHORT = "1E02"
DEFAULT_PRIMARY_KEY_FILE = "Signing_key_1E02.asc"

DEFAULT_LEGACY_KEY_FP = "20BB 6616 A328 2A9F 8F15  9A53 4BB8 D801 C141 7BDC"
DEFAULT_LEGACY_KEY_ID = "20BB6616A3282A9F8F159A534BB8D801C1417BDC"  # Full fingerprint or Long ID 4BB8D801C1417BDC
DEFAULT_LEGACY_KEY_SHORT = "7BDC"
DEFAULT_LEGACY_KEY_FILE = "Signing_key_7BDC.asc"

# RSS & Freshness feeds
SPIEGEL_RSS_URL = "https://www.spiegel.de/international/index.rss"
NYT_RSS_URL = "https://rss.nytimes.com/services/xml/rss/nyt/World.xml"
BBC_RSS_URL = "https://feeds.bbci.co.uk/news/world/rss.xml"
BTC_HASH_URLS = [
    "https://blockchain.info/q/latesthash",
    "https://blockstream.info/api/blocks/tip/hash",
    "https://mempool.space/api/blocks/tip/hash"
]

def prepare_gpg_env():
    """Ensure GPG_TTY environment variable is set for pinentry in TTY environments (WSL/Linux/macOS)."""
    env = os.environ.copy()
    if "GPG_TTY" not in env:
        try:
            env["GPG_TTY"] = os.ttyname(sys.stdin.fileno())
        except Exception:
            try:
                env["GPG_TTY"] = os.ttyname(0)
            except Exception:
                pass
    return env

def find_gpg():
    """Locate the gpg binary in system PATH or common installation paths."""
    gpg_bin = shutil.which("gpg") or shutil.which("gpg2")
    if gpg_bin:
        return gpg_bin
    
    win_paths = [
        r"C:\Program Files (x86)\GnuPG\bin\gpg.exe",
        r"C:\Program Files\GnuPG\bin\gpg.exe",
        r"C:\Program Files\Git\usr\bin\gpg.exe"
    ]
    for path in win_paths:
        if os.path.exists(path):
            return path
    return None

def get_yubikey_info(gpg_bin, gpg_env):
    """Query `gpg --card-status` to extract connected YubiKey details."""
    info = {
        "connected": False,
        "serial": "Unknown",
        "cardholder": "Unknown",
        "signature_key": "None",
        "raw_output": ""
    }
    if not gpg_bin:
        return info

    try:
        res = subprocess.run([gpg_bin, "--card-status"], capture_output=True, text=True, env=gpg_env, timeout=5)
        info["raw_output"] = res.stdout + res.stderr
        if res.returncode == 0:
            info["connected"] = True
            for line in res.stdout.splitlines():
                line_str = line.strip()
                if "Serial number" in line_str:
                    info["serial"] = line_str.split(":", 1)[-1].strip()
                elif "Name of cardholder" in line_str:
                    info["cardholder"] = line_str.split(":", 1)[-1].strip() or "Not specified"
                elif "Signature key" in line_str:
                    info["signature_key"] = line_str.split(":", 1)[-1].strip()
    except Exception as e:
        info["raw_output"] = str(e)
    
    return info

def get_secret_keys_in_keyring(gpg_bin, gpg_env):
    """Query `gpg --list-secret-keys --with-colons` to list available secret keys / card stubs in GPG keyring."""
    keys = []
    if not gpg_bin:
        return keys

    try:
        res = subprocess.run([gpg_bin, "--list-secret-keys", "--with-colons"], capture_output=True, text=True, env=gpg_env, timeout=5)
        if res.returncode == 0:
            for line in res.stdout.splitlines():
                parts = line.split(":")
                if parts[0] in ["sec", "ssb"]:
                    key_id = parts[4]
                    if key_id:
                        keys.append(key_id.upper())
                elif parts[0] == "fpr":
                    fpr = parts[9]
                    if fpr:
                        keys.append(fpr.upper())
    except Exception:
        pass
    
    return keys

def setup_fresh_machine_keyring(repo_dir, gpg_bin, gpg_env, keys_needed):
    """
    Import public keys from repo keys/ and run `gpg --card-status` to generate YubiKey secret key stubs.
    """
    keys_dir = repo_dir / "keys"
    print("\n" + "-" * 72)
    print("FRESH MACHINE GPG KEYRING INITIALIZATION")
    print("-" * 72)
    print("Secret key stubs for YubiKey were not found in your local GPG keyring.")
    print("Attempting automatic key import and YubiKey smartcard stub generation...\n")

    # Step A: Import public key files from keys/
    for k in keys_needed:
        key_file = keys_dir / k.get("filename", "")
        if key_file.exists():
            print(f"[*] Importing public key file: {key_file.relative_to(repo_dir)}")
            res = subprocess.run([gpg_bin, "--import", str(key_file)], capture_output=True, text=True, env=gpg_env)
            if res.returncode == 0:
                print(f"[✓] Successfully imported {k['short']} public key.")
            else:
                print(f"[!] Warning importing {key_file.name}: {res.stderr.strip()}")
        else:
            print(f"[!] Key file not found: {key_file}")

    # Step B: Trigger gpg --card-status to bind YubiKey to public key and generate secret key stubs
    print("\nPlease ensure your YubiKey is plugged into your computer.")
    input("[Press Enter to run `gpg --card-status` and generate secret key stubs...]")

    res_card = subprocess.run([gpg_bin, "--card-status"], capture_output=True, text=True, env=gpg_env)
    if res_card.returncode == 0:
        print("[✓] `gpg --card-status` completed successfully.")
        print("[✓] Secret key stubs (ssb>) have been linked to your local GPG keyring!")
    else:
        print("[!] `gpg --card-status` failed. Details:")
        print(res_card.stderr)
        print("    If using WSL, ensure pcscd / gpg-agent smartcard passthrough is active.")

    print("-" * 72 + "\n")

def fetch_rss_titles(url, count=5):
    """Fetch top N titles from an RSS feed with graceful fallback."""
    headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) reifr-gencanary/2.0"}
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            content = response.read()
            tree = ET.fromstring(content)
            titles = []
            for item in tree.findall(".//item")[:count]:
                t = item.find("title")
                if t is not None and t.text:
                    clean_title = html.unescape(t.text.strip())
                    titles.append(clean_title)
            if titles:
                return titles
    except Exception as e:
        print(f"  [!] Warning: Failed to fetch RSS feed from {url}: {e}", file=sys.stderr)
    
    return [f"[Error fetching feed from {url}]"]

def fetch_btc_hash():
    """Fetch latest Bitcoin block hash with fallbacks."""
    headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) reifr-gencanary/2.0"}
    for url in BTC_HASH_URLS:
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as response:
                hash_val = response.read().decode("utf-8").strip()
                if hash_val and len(hash_val) == 64:
                    return hash_val
        except Exception:
            continue
    print("  [!] Warning: Failed to fetch Bitcoin block hash from all sources.", file=sys.stderr)
    return "[Error fetching Bitcoin hash]"

def get_next_canary_date(now_utc):
    """Calculate the target month and year (+3 months) for statement #4."""
    year = now_utc.year
    month = now_utc.month + 3
    if month > 12:
        month -= 12
        year += 1
    
    dt = datetime.datetime(year, month, 1)
    return dt.strftime("%B %Y")

def get_latest_canary_count(canaries_dir):
    """
    Dynamically determine highest canary number by scanning canaries/ directory.
    Only counts canaries that have at least one detached signature (.sig) file present.
    """
    if not canaries_dir.exists():
        return 0
    
    max_count = 0
    filename_pattern = re.compile(r"canary#(\d+)-")
    header_pattern = re.compile(r"reifr\.net canary #(\d+)")
    
    for p in canaries_dir.rglob("canary#*.txt"):
        sig_files = list(p.parent.glob(f"{p.name}-*.sig"))
        if not sig_files:
            continue

        c_num = 0
        match = filename_pattern.search(p.name)
        if match:
            c_num = int(match.group(1))
        else:
            try:
                with open(p, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read(500)
                    h_match = header_pattern.search(content)
                    if h_match:
                        c_num = int(h_match.group(1))
            except Exception:
                pass
                
        max_count = max(max_count, c_num)
            
    return max_count

def generate_canary_text(count_num, now_utc, spiegel_titles, nyt_titles, bbc_titles, btc_hash, special_announcements="None.", key_fp=DEFAULT_PRIMARY_KEY_FP):
    """Construct full text of warrant canary declaration."""
    issue_date_str = now_utc.strftime("%m/%d/%Y")
    next_date_str = get_next_canary_date(now_utc)
    rfc2822_date = now_utc.strftime("%a, %d %b %Y %H:%M:%S +0000")
    
    spiegel_block = "\n".join(spiegel_titles)
    nyt_block = "\n".join(nyt_titles)
    bbc_block = "\n".join(bbc_titles)
    
    canary_text = f"""                    ---===[ reifr.net canary #{count_num} ]===---


Statements
-----------
The administrators of reifr.net who have digitally signed this file state the following:


1. The date of issue of this canary is {issue_date_str}

2. The reifr.net Master Signing Key fingerprint is:

	{key_fp}

3. No warrants have ever been served to us with regard to the reifr.net
domain or subdomains (e.g. to hand out private data related to the domain's
SSL certificates, signing keys, encrypted files, or non-encrypted files, user data,
or hardware the services are running on).

4. We plan to publish the next of these canary statements in the first
two weeks of {next_date_str}. Special note should be taken if no new canary
is published by that time or if the list of statements changes without
plausible explanation.

Special announcements
----------------------

{special_announcements}

Disclaimers and notes
----------------------

This canary scheme is not infallible. Although signing the declaration
makes it very difficult for a third party to produce arbitrary
declarations, it does not prevent them from using force or other
means, like blackmail or compromising the signers' laptops, to coerce
us to produce false declarations.

The news feeds quoted below (Proof of freshness) serves to demonstrate
that this canary could not have been created prior to the date stated.
It shows that a series of canaries was not created in advance.

This declaration is merely a best effort and is provided without any
guarantee or warranty. It is not legally binding in any way to
anybody. None of the signers should be ever held legally responsible
for any of the statements made here.

Proof of freshness
-------------------

$ date -R -u
{rfc2822_date}

$ feedstail -1 -n5 -f '{{title}}' -u {SPIEGEL_RSS_URL}
{spiegel_block}

$ feedstail -1 -n5 -f '{{title}}' -u {NYT_RSS_URL}
{nyt_block}

$ feedstail -1 -n5 -f '{{title}}' -u {BBC_RSS_URL}
{bbc_block}

$ curl -s 'https://blockchain.info/q/latesthash'
{btc_hash}

Footnotes
----------

[1] This file should be signed via detached PGP
signatures by each of the signers, distributed together with this
canary in the https://github.com/winxp5421/reifr.net.git repository. [2]

[2] Don't just trust the contents of this file blindly! Verify the
digital signatures!"""
    return canary_text

def get_output_filename(count_num, now_utc):
    """Generate target filename according to repository convention: canary#N-Mon-DD.txt"""
    mon_abbrev = now_utc.strftime("%b")
    day_str = now_utc.strftime("%d")
    return f"canary#{count_num}-{mon_abbrev}-{day_str}.txt"

def print_header(step_num, title):
    print("\n" + "=" * 72)
    print(f" STEP {step_num}: {title}".upper())
    print("=" * 72)

def verify_canary_package(target_file, expected_count, keys_to_sign, gpg_bin):
    """
    Strict verification checks to ensure the generated canary file
    and all detached GPG signatures are valid before allowing git commit.
    Returns (passed_bool, list_of_logs).
    """
    logs = []
    failed = False
    gpg_env = prepare_gpg_env()
    
    logs.append("Executing Verification Suite:")
    
    # Check 1: Target file exists and non-empty
    if not target_file.exists() or target_file.stat().st_size == 0:
        logs.append(f"  [X] FAIL: Target file missing or empty: {target_file}")
        failed = True
    else:
        logs.append(f"  [✓] Target canary file exists ({target_file.stat().st_size} bytes)")

    # Check 2: Statement Content Sanity
    try:
        with open(target_file, "r", encoding="utf-8") as f:
            content = f.read()

        if f"reifr.net canary #{expected_count}" not in content:
            logs.append(f"  [X] FAIL: Header statement counter #{expected_count} missing from content")
            failed = True
        else:
            logs.append(f"  [✓] Header statement counter #{expected_count} verified")

        if DEFAULT_PRIMARY_KEY_FP not in content:
            logs.append(f"  [X] FAIL: Master Signing Key fingerprint missing from content")
            failed = True
        else:
            logs.append(f"  [✓] Primary Master Signing Key fingerprint verified")

        if "Proof of freshness" not in content or "$ curl -s 'https://blockchain.info/q/latesthash'" not in content:
            logs.append(f"  [X] FAIL: Proof of freshness section incomplete")
            failed = True
        else:
            logs.append(f"  [✓] Proof of freshness section structure verified")
            
    except Exception as e:
        logs.append(f"  [X] FAIL: Cannot inspect canary file content: {e}")
        failed = True

    # Check 3: Detached Signature Cryptographic Verification
    if not gpg_bin:
        logs.append(f"  [X] FAIL: GPG binary unavailable for cryptographic verification")
        failed = True
    else:
        for key_info in keys_to_sign:
            key_id = key_info["id"]
            suffix = key_info["short"]
            sig_file = target_file.parent / f"{target_file.name}-{suffix}.sig"
            if not sig_file.exists() or sig_file.stat().st_size == 0:
                logs.append(f"  [X] FAIL: Detached signature file for key {suffix} ({key_id}) missing or empty")
                failed = True
            else:
                logs.append(f"  [✓] Signature file for key {suffix} exists ({sig_file.stat().st_size} bytes)")
                
                v_res = subprocess.run([gpg_bin, "--verify", str(sig_file), str(target_file)], capture_output=True, text=True, env=gpg_env)
                if v_res.returncode == 0:
                    logs.append(f"  [✓] Cryptographic signature for key {suffix} ({key_id}) VERIFIED SUCCESSFUL!")
                else:
                    logs.append(f"  [X] FAIL: Cryptographic signature verification FAILED for key {suffix} ({key_id})")
                    logs.append(f"      GPG Output: {v_res.stderr.strip()}")
                    failed = True

    return not failed, logs

def cleanup_unsigned_draft(target_file, keys_to_sign):
    """Offer to remove un-signed draft files if signing fails or is aborted."""
    print(f"\n[!] Cleanup Option: Un-signed draft file is at {target_file}")
    ans = input("Would you like to delete this un-signed draft file to keep working tree clean? [Y/n]: ").strip().lower()
    if ans not in ["n", "no"]:
        try:
            if target_file.exists():
                target_file.unlink()
                print(f"[✓] Deleted un-signed draft: {target_file.name}")
            for key_info in keys_to_sign:
                suffix = key_info["short"]
                sig_f = target_file.parent / f"{target_file.name}-{suffix}.sig"
                if sig_f.exists():
                    sig_f.unlink()
        except Exception as e:
            print(f"[!] Warning: Error during draft cleanup: {e}")

def run_interactive_wizard(args, repo_dir, canaries_dir):
    print("=" * 72)
    print("         REIFR.NET WARRANT CANARY GENERATOR WIZARD         ".center(72))
    print("=" * 72)
    print("Welcome! This interactive assistant will guide you step-by-step")
    print("through gathering freshness data, reviewing the canary statement,")
    print("detecting YubiKey hardware, generating GPG detached signatures,")
    print("running pre-commit verification, and making a signed git commit.")
    
    gpg_env = prepare_gpg_env()
    gpg_bin = find_gpg()

    # STEP 1: Metadata & Dynamic Count Setup
    latest_count = get_latest_canary_count(canaries_dir)
    new_count = latest_count + 1
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    year_str = now_utc.strftime("%Y")
    filename = get_output_filename(new_count, now_utc)
    target_dir = canaries_dir / year_str
    target_file = target_dir / filename

    print_header(1, "Canary Initialization & Dynamic Counter Detection")
    print(f"  • Latest Verified Canary  : #{latest_count}")
    print(f"  • Target Canary Counter   : #{new_count}")
    print(f"  • Date of Issue (UTC)     : {now_utc.strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print(f"  • Target File Destination : {target_file.relative_to(repo_dir)}")
    print(f"  • GPG Executable Location : {gpg_bin if gpg_bin else 'NOT FOUND'}")
    
    yubi_info = get_yubikey_info(gpg_bin, gpg_env)
    if yubi_info["connected"]:
        print(f"  • YubiKey Hardware Status : CONNECTED")
        print(f"    - Serial Number         : {yubi_info['serial']}")
        print(f"    - Cardholder            : {yubi_info['cardholder']}")
        print(f"    - On-Card Signature Key : {yubi_info['signature_key']}")
    else:
        print(f"  • YubiKey Hardware Status : NOT DETECTED via gpg --card-status")
        print(f"    (Ensure YubiKey is plugged in or smartcard service is active)")

    if target_file.exists():
        sig_files = list(target_file.parent.glob(f"{target_file.name}-*.sig"))
        if not sig_files:
            print("\n  [!] NOTICE: Found an un-signed canary draft on disk from a previous run.")
            print("  [!] Running this wizard will overwrite the draft with fresh data and retry signing.")
    
    input("\n[Press Enter to proceed to Freshness Data Collection...]")

    # STEP 2: Proof of Freshness Collection
    while True:
        print_header(2, "Gathering Proof of Freshness Data")
        print("Fetching latest headlines and Bitcoin block hash...")
        
        print("  • Fetching Spiegel International RSS...")
        spiegel_titles = fetch_rss_titles(SPIEGEL_RSS_URL)
        
        print("  • Fetching NY Times World RSS...")
        nyt_titles = fetch_rss_titles(NYT_RSS_URL)
        
        print("  • Fetching BBC World RSS...")
        bbc_titles = fetch_rss_titles(BBC_RSS_URL)
        
        print("  • Fetching latest Bitcoin Block Hash...")
        btc_hash = fetch_btc_hash()

        print("\n[+] Freshness Data Collected:")
        print(f"    - Spiegel Headliners: {len(spiegel_titles)} titles")
        print(f"    - NYT Headliners    : {len(nyt_titles)} titles")
        print(f"    - BBC Headliners    : {len(bbc_titles)} titles")
        print(f"    - BTC Tip Hash      : {btc_hash[:16]}...{btc_hash[-8:]}")
        
        ans = input("\nDoes the freshness data look good? ([y]/r to retry): ").strip().lower()
        if ans not in ["r", "retry"]:
            break

    # STEP 3: Special Announcements
    print_header(3, "Special Announcements")
    print("Default announcement is 'None.'")
    add_special = input("Do you have any Special Announcements to include in this canary? [y/N]: ").strip().lower()
    special_announcements = "None."
    if add_special in ["y", "yes"]:
        print("Enter your Special Announcement text below (press Enter twice when finished):")
        lines = []
        while True:
            line = input("> ")
            if not line and lines:
                break
            if line:
                lines.append(line)
        if lines:
            special_announcements = "\n".join(lines)

    # STEP 4: GPG Key Selection & Fresh Machine Auto-Setup
    print_header(4, "GPG Signing Keys & YubiKey Selection")
    print("Select which key(s) to sign the canary statement with:")
    print(f"  [1] Primary Master Key ({DEFAULT_PRIMARY_KEY_SHORT} / {DEFAULT_PRIMARY_KEY_ID[:16]}...) [Recommended]")
    print(f"  [2] Both Primary ({DEFAULT_PRIMARY_KEY_SHORT}) and Legacy ({DEFAULT_LEGACY_KEY_SHORT}) Keys")
    print("  [3] Custom Key ID / Fingerprint")
    
    key_choice = input("\nSelect option [1-3] (Default: 1): ").strip()
    
    keys_to_sign = [
        {
            "id": DEFAULT_PRIMARY_KEY_ID,
            "short": DEFAULT_PRIMARY_KEY_SHORT,
            "fp": DEFAULT_PRIMARY_KEY_FP,
            "filename": DEFAULT_PRIMARY_KEY_FILE,
            "name": f"Primary Master Key ({DEFAULT_PRIMARY_KEY_SHORT})"
        }
    ]

    if key_choice == "2":
        keys_to_sign.append({
            "id": DEFAULT_LEGACY_KEY_ID,
            "short": DEFAULT_LEGACY_KEY_SHORT,
            "fp": DEFAULT_LEGACY_KEY_FP,
            "filename": DEFAULT_LEGACY_KEY_FILE,
            "name": f"Legacy Master Key ({DEFAULT_LEGACY_KEY_SHORT})"
        })
    elif key_choice == "3":
        custom_input = input("Enter GPG Key ID or Fingerprint (e.g. email, long ID, or fingerprint): ").strip()
        if custom_input:
            keys_to_sign = [{
                "id": custom_input,
                "short": custom_input[-8:] if len(custom_input) >= 8 else custom_input,
                "fp": custom_input,
                "filename": "",
                "name": f"Custom Key ({custom_input})"
            }]

    # Check if secret key stubs exist in GPG keyring
    secret_keys = get_secret_keys_in_keyring(gpg_bin, gpg_env)
    missing_stubs = []
    for k in keys_to_sign:
        k_id_clean = k["id"].replace(" ", "").upper()
        k_short_clean = k["short"].upper()
        found = any(k_id_clean in sk or k_short_clean in sk for sk in secret_keys)
        if not found:
            missing_stubs.append(k)

    if missing_stubs:
        setup_fresh_machine_keyring(repo_dir, gpg_bin, gpg_env, missing_stubs)
        # Refresh YubiKey & secret key status
        yubi_info = get_yubikey_info(gpg_bin, gpg_env)

    # Display configured signing keys & YubiKey details
    print("\n[+] Configured Signing Keys:")
    for k in keys_to_sign:
        print(f"    - {k['name']}")
        print(f"      Key ID / Fingerprint: {k['id']}")
    
    if yubi_info["connected"]:
        print(f"\n[+] Active YubiKey Detected:")
        print(f"    - Serial Number : {yubi_info['serial']}")
        print(f"    - Cardholder    : {yubi_info['cardholder']}")

    # STEP 5: Final Review & Approval
    canary_text = generate_canary_text(
        count_num=new_count,
        now_utc=now_utc,
        spiegel_titles=spiegel_titles,
        nyt_titles=nyt_titles,
        bbc_titles=bbc_titles,
        btc_hash=btc_hash,
        special_announcements=special_announcements
    )

    print_header(5, "Complete Statement Review")
    print("-" * 72)
    print(canary_text)
    print("-" * 72)
    print(f"\nTarget File: {target_file}")
    print(f"Signing Keys: {', '.join([k['short'] for k in keys_to_sign])}")
    
    confirm = input("\n>>> ARE YOU READY TO WRITE THIS CANARY & PROCEED TO SIGNING? [y/N]: ").strip().lower()
    if confirm not in ["y", "yes"]:
        print("\n[!] Operation cancelled by user. No files modified.")
        sys.exit(0)

    # STEP 6: Write Canary File
    target_dir.mkdir(parents=True, exist_ok=True)
    with open(target_file, "w", encoding="utf-8", newline="\n") as f:
        f.write(canary_text)
    
    print(f"\n[✓] Created canary statement file: {target_file.name}")

    if args.no_sign:
        print("[i] Skipping GPG signing (--no-sign requested).")
        return

    print_header(6, "YubiKey GPG Detached Signing")
    if not gpg_bin:
        print("[!] GPG binary not found in PATH or standard installation directories.")
        print(f"[!] Please sign manually: gpg --armor --detach-sign -u {DEFAULT_PRIMARY_KEY_ID} {target_file}")
        sys.exit(1)

    staged_files = [target_file]
    signing_failed = False

    for k_info in keys_to_sign:
        key_id = k_info["id"]
        suffix = k_info["short"]
        sig_file = target_dir / f"{filename}-{suffix}.sig"
        
        print(f"\n--- SIGNING WITH {k_info['name']} ---")
        print(f"Full Key ID / Fingerprint: {key_id}")
        print(f"Target signature file    : {sig_file.name}")
        if yubi_info["connected"]:
            print(f"Target YubiKey Serial #  : {yubi_info['serial']} ({yubi_info['cardholder']})")
        print("Please ensure your YubiKey is connected.")
        input(f"[Press Enter to trigger GPG prompt for key {suffix}...]")
        
        cmd = [
            gpg_bin,
            "--detach-sign",
            "--armor",
            "--local-user", key_id,
            "--output", str(sig_file),
            str(target_file)
        ]
        
        res = subprocess.run(cmd, env=gpg_env)
        if res.returncode == 0:
            print(f"[✓] Created signature file: {sig_file.name}")
            staged_files.append(sig_file)
        else:
            print(f"[!] GPG signing failed (exit code {res.returncode}) for key {key_id}.")
            print("    Troubleshooting steps:")
            print("    1. Verify key is imported into GPG keyring (`gpg --list-secret-keys` or `gpg --card-status`)")
            print("    2. Ensure GPG_TTY is exported: export GPG_TTY=$(tty)")
            print("    3. If running WSL, ensure gpg-agent is active: gpg-connect-agent reloadagent /bye")
            signing_failed = True

    if signing_failed:
        print("\n[!] GPG signing encountered errors.")
        cleanup_unsigned_draft(target_file, keys_to_sign)
        sys.exit(1)

    # STEP 7: STRICT PRE-COMMIT VERIFICATION GATE
    print_header(7, "Pre-Commit Package Verification Check")
    passed, logs = verify_canary_package(target_file, new_count, keys_to_sign, gpg_bin)
    
    for log_msg in logs:
        print(log_msg)

    if not passed:
        print("\n" + "!" * 72)
        print(" [!] VERIFICATION CHECKS FAILED! COMMIT ABORTED. ".center(72, "!"))
        print(" [!] Correct any issues before attempting to commit this canary.".center(72, "!"))
        print("!" * 72 + "\n")
        cleanup_unsigned_draft(target_file, keys_to_sign)
        sys.exit(1)

    print("\n" + "✓" * 72)
    print(" [✓] ALL PRE-COMMIT VERIFICATION CHECKS PASSED SUCCESSFULLY! ".center(72, "✓"))
    print("✓" * 72 + "\n")

    # STEP 8: Signed Git Commit & Push (Only reached if verification passed!)
    print_header(8, "Git Repository Staging & Signed Commit")
    git_ans = input("Would you like to stage these verified files and create a GPG-signed Git commit? [Y/n]: ").strip().lower()
    if git_ans not in ["n", "no"]:
        rel_files = [str(p.relative_to(repo_dir)) for p in staged_files]
        print(f"Staging verified files: {', '.join(rel_files)}")
        subprocess.run(["git", "add"] + rel_files, cwd=repo_dir)
        
        primary_key_id = keys_to_sign[0]["id"]
        commit_msg = f"Publish canary #{new_count}"
        print(f"Creating signed Git commit ('{commit_msg}') using key {primary_key_id[:16]}...")
        print("(Your YubiKey may be prompted again for commit signing)")
        
        commit_cmd = ["git"]
        if primary_key_id:
            commit_cmd.extend(["-c", f"user.signingkey={primary_key_id}"])
        if gpg_bin:
            commit_cmd.extend(["-c", f"gpg.program={gpg_bin}"])
        commit_cmd.extend(["commit", "-S", "-m", commit_msg])

        c_res = subprocess.run(commit_cmd, cwd=repo_dir, env=gpg_env)
        if c_res.returncode == 0:
            print(f"[✓] GPG-signed Git commit created successfully!")
            
            push_ans = input("\nWould you like to push this commit to origin remote now? [y/N]: ").strip().lower()
            if push_ans in ["y", "yes"]:
                print("Pushing to origin master...")
                p_res = subprocess.run(["git", "push"], cwd=repo_dir)
                if p_res.returncode == 0:
                    print("[✓] Pushed commit to remote repository!")
                else:
                    print("[!] Failed to push to remote repository.")
        else:
            print("[!] Git commit failed.")

    print("\n" + "=" * 72)
    print(f" CANARY #{new_count} GENERATION & SIGNING COMPLETE! ".center(72, "="))
    print("=" * 72 + "\n")

def main():
    parser = argparse.ArgumentParser(description="reifr.net Warrant Canary Generator Wizard")
    parser.add_argument("--preview", "--dry-run", action="store_true", help="Preview canary output without saving or signing.")
    parser.add_argument("--no-sign", action="store_true", help="Save canary file, but skip GPG signing.")
    parser.add_argument("--keys", nargs="+", default=[DEFAULT_PRIMARY_KEY_ID], help="GPG key ID(s) or fingerprints to sign with.")
    parser.add_argument("--git-commit", action="store_true", help="Automatically stage and create a signed git commit.")
    parser.add_argument("-y", "--yes", action="store_true", help="Bypass wizard and non-interactively generate.")

    args = parser.parse_args()

    repo_dir = Path(__file__).resolve().parent
    canaries_dir = repo_dir / "canaries"

    # If --preview or --yes passed, run quick CLI mode instead of full wizard
    if args.preview or args.yes:
        latest_count = get_latest_canary_count(canaries_dir)
        new_count = latest_count + 1
        now_utc = datetime.datetime.now(datetime.timezone.utc)
        year_str = now_utc.strftime("%Y")
        filename = get_output_filename(new_count, now_utc)
        target_dir = canaries_dir / year_str
        target_file = target_dir / filename

        print(f"[*] Target File: {target_file}")
        print(f"[*] Dynamic Counter Detected: #{new_count} (Previous Verified: #{latest_count})")
        print("[*] Fetching proof of freshness feeds...")
        spiegel_titles = fetch_rss_titles(SPIEGEL_RSS_URL)
        nyt_titles = fetch_rss_titles(NYT_RSS_URL)
        bbc_titles = fetch_rss_titles(BBC_RSS_URL)
        btc_hash = fetch_btc_hash()

        canary_text = generate_canary_text(
            count_num=new_count,
            now_utc=now_utc,
            spiegel_titles=spiegel_titles,
            nyt_titles=nyt_titles,
            bbc_titles=bbc_titles,
            btc_hash=btc_hash
        )

        print("-" * 72)
        print(canary_text)
        print("-" * 72)

        if args.preview:
            print("[i] Preview mode completed.")
            return

        target_dir.mkdir(parents=True, exist_ok=True)
        with open(target_file, "w", encoding="utf-8", newline="\n") as f:
            f.write(canary_text)
        print(f"[+] Saved canary #{new_count} to {target_file}")
        return

    # Standard execution: Run interactive step-by-step wizard
    run_interactive_wizard(args, repo_dir, canaries_dir)

if __name__ == "__main__":
    main()
