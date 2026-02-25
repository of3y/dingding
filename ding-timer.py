#!/usr/bin/env python3
"""CLI stopwatch/countdown timer that dings at regular intervals.
Usage: python ding-timer.py <seconds> [options]
"""

import sys
import csv
import os
import time
import math
import argparse
import subprocess
import platform
import threading
from datetime import datetime

LOG_FILE = os.path.expanduser("~/.ding-log.csv")

# ---------------------------------------------------------------------------
# Color schemes
# ---------------------------------------------------------------------------
SCHEMES = {
    None: {
        "green": "", "cyan": "", "yellow": "", "coral": "",
        "magenta": "", "blue": "", "pink": "", "dim": "", "reset": "",
        "bar_width": 24, "filled": "█", "empty": "░", "gradient": False,
    },
    "a": {
        "green": "\033[92m", "cyan": "\033[96m", "yellow": "\033[93m",
        "coral": "\033[38;5;210m", "magenta": "\033[95m",
        "blue": "\033[96m", "pink": "\033[95m", "dim": "\033[2m", "reset": "\033[0m",
        "bar_width": 20, "filled": "█", "empty": "░", "gradient": True,
    },
    "b": {
        "green": "\033[92m", "cyan": "\033[38;5;117m", "yellow": "\033[93m",
        "coral": "\033[38;5;218m", "magenta": "\033[38;5;218m",
        "blue": "\033[38;5;117m", "pink": "\033[38;5;218m", "dim": "\033[2m", "reset": "\033[0m",
        "bar_width": 16, "filled": "▓", "empty": "░", "gradient": False,
    },
    "c": {
        "green": "\033[92m", "cyan": "\033[96m", "yellow": "\033[93m",
        "coral": "\033[38;5;183m", "magenta": "\033[38;5;183m",
        "blue": "\033[38;5;183m", "pink": "\033[38;5;183m", "dim": "\033[2m", "reset": "\033[0m",
        "bar_width": 20, "filled": "━", "empty": "─", "gradient": True,
    },
}


# ---------------------------------------------------------------------------
# Sound
# ---------------------------------------------------------------------------
def play_ding(milestone_level=0, quiet=False):
    """Play a system ding. milestone_level=-1 means session complete."""
    if quiet:
        return

    def _play():
        system = platform.system()
        try:
            if system == "Darwin":
                sound_map = {
                    0:    "/System/Library/Sounds/Glass.aiff",
                    10:   "/System/Library/Sounds/Ping.aiff",
                    50:   "/System/Library/Sounds/Hero.aiff",
                    100:  "/System/Library/Sounds/Funk.aiff",
                    500:  "/System/Library/Sounds/Sosumi.aiff",
                    -1:   "/System/Library/Sounds/Hero.aiff",
                }
                subprocess.Popen(
                    ["afplay", sound_map.get(milestone_level, sound_map[0])],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                )
            elif system == "Linux":
                sound_map = {
                    0:    "/usr/share/sounds/freedesktop/stereo/bell.oga",
                    10:   "/usr/share/sounds/freedesktop/stereo/message.oga",
                    50:   "/usr/share/sounds/freedesktop/stereo/complete.oga",
                    100:  "/usr/share/sounds/freedesktop/stereo/service-login.oga",
                    500:  "/usr/share/sounds/freedesktop/stereo/phone-incoming-call.oga",
                    -1:   "/usr/share/sounds/freedesktop/stereo/complete.oga",
                }
                subprocess.Popen(
                    ["paplay", sound_map.get(milestone_level, sound_map[0])],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                )
            elif system == "Windows":
                import winsound
                freq_map = {
                    0:   (1000, 200),
                    10:  (1200, 250),
                    50:  (1500, 300),
                    100: (2000, 400),
                    500: (2500, 600),
                    -1:  (2000, 600),
                }
                freq, dur = freq_map.get(milestone_level, freq_map[0])
                winsound.Beep(freq, dur)
        except Exception:
            print("\a", end="", flush=True)

    threading.Thread(target=_play, daemon=True).start()


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------
def format_elapsed(seconds):
    """HH:MM:SS.d or MM:SS.d"""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    t = int((seconds % 1) * 10)
    if h > 0:
        return f"{h:02d}:{m:02d}:{s:02d}.{t}"
    return f"{m:02d}:{s:02d}.{t}"


def format_remaining(seconds):
    """H:MM:SS or MM:SS (no suffix — caller adds it)."""
    seconds = max(0.0, seconds)
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    if h > 0:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"


def parse_duration(s):
    """Parse '25m', '90s', '1h', or raw seconds as float."""
    s = s.strip().lower()
    if s.endswith("h"):
        return float(s[:-1]) * 3600
    if s.endswith("m"):
        return float(s[:-1]) * 60
    if s.endswith("s"):
        return float(s[:-1])
    return float(s)


# ---------------------------------------------------------------------------
# Progress bar
# ---------------------------------------------------------------------------
def build_bar(s, progress, reverse=False):
    """Build a progress bar string. progress in [0.0, 1.0].

    reverse=True: bar drains (full → empty) as progress increases.
    Gradient color is keyed on the display fill level so it signals urgency
    correctly in both directions.
    """
    bar_width = s["bar_width"]
    display = max(0.0, min(1.0, (1.0 - progress) if reverse else progress))
    filled = int(bar_width * display)

    if not s["reset"]:
        return s["filled"] * filled + s["empty"] * (bar_width - filled)

    if s["gradient"]:
        if display > 0.3:
            color = s["green"]
        elif display > 0.1:
            color = s["yellow"]
        else:
            color = s["coral"]
    else:
        color = s["blue"]

    return (
        f"{color}{s['filled'] * filled}"
        f"{s['dim']}{s['empty'] * (bar_width - filled)}{s['reset']}"
    )


# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
def print_header(interval, task, duration, s, cs):
    """Print the session start header. cs = color_scheme key."""
    interval_str = f"{interval:g}s"
    task_str = f" - {task}" if task else ""

    if cs == "b":
        dur_part = f" | Duration: {format_remaining(duration)}" if duration else ""
        print(
            f"\n{s['dim']}Interval: {interval_str}{task_str}{dur_part}"
            f" • Ctrl+C to stop{s['reset']}\n"
        )

    elif cs == "c":
        bw = 44
        parts = [f"Interval: {interval_str}"]
        if duration:
            parts.append(f"Duration: {format_remaining(duration)}")
        if task:
            parts.append(task)
        content = "  ".join(parts)
        hint = "(Ctrl+C to stop)"
        pad = max(0, bw - 2 - 1 - len(content) - 2 - len(hint) - 1)
        print(f"\n{s['cyan']}┌{'─' * (bw - 2)}┐{s['reset']}")
        print(
            f"{s['cyan']}│{s['reset']} "
            f"{s['yellow']}{content}{s['reset']}  "
            f"{s['dim']}{hint}{s['reset']}"
            f"{' ' * pad}{s['cyan']}│{s['reset']}"
        )
        print(f"{s['cyan']}└{'─' * (bw - 2)}┘{s['reset']}\n")

    elif cs == "a":
        dur_part = (
            f" {s['dim']}|{s['reset']} {s['green']}{format_remaining(duration)}{s['reset']}"
            if duration else ""
        )
        print(
            f"\n{s['cyan']}⏱️  Stopwatch{s['reset']} {s['dim']}•{s['reset']} "
            f"Ding every {s['yellow']}{interval_str}{s['reset']}{task_str}"
            f"{dur_part} {s['dim']}• Ctrl+C to stop{s['reset']}\n"
        )

    else:
        hw = 52
        mode = "COUNTDOWN" if duration else "STOPWATCH"
        print(f"\n{'═' * hw}")
        print(f"{'⏱️  ' + mode:^{hw}}")
        print(f"{'Ding every ' + interval_str:^{hw}}")
        if duration:
            print(f"{'Duration: ' + format_remaining(duration):^{hw}}")
        print("═" * hw)
        if task:
            print(f"{'Task: ' + task:^{hw}}")
            print("─" * hw)
        print(f"\n{'Press Ctrl+C to stop':^{hw}}\n")


# ---------------------------------------------------------------------------
# Live display line
# ---------------------------------------------------------------------------
def render_line(elapsed, interval, last_ding, ding_flash_until,
                duration, reverse, max_dings, s, cs):
    """Return the overwriting status line string."""

    # --- Time display ---
    if duration:
        time_str = format_remaining(duration - elapsed) + " left"
    else:
        time_str = format_elapsed(elapsed)

    # --- Progress bar ---
    if duration:
        # Session-level reverse bar: starts full, drains to zero at end
        bar = build_bar(s, min(1.0, elapsed / duration), reverse=True)
    else:
        # Interval-level bar (forward by default, reverse with --reverse)
        bar = build_bar(s, (elapsed % interval) / interval, reverse=reverse)

    # --- Ding indicator ---
    secs_to_next = math.ceil((last_ding + 1) * interval - elapsed)
    if time.time() < ding_flash_until:
        ding_part = f"{s['magenta']}🔔 DING!{s['reset']}" if cs else "🔔 DING!"
    else:
        if cs:
            count_info = f" {s['dim']}[{last_ding}/{max_dings}]{s['reset']}" if max_dings else ""
            ding_part = f"{s['yellow']}Next: {secs_to_next:3d}s{s['reset']}{count_info}"
        else:
            count_info = f" [{last_ding}/{max_dings}]" if max_dings else ""
            ding_part = f"Next: {secs_to_next:3d}s{count_info}"

    # --- Wall clock ---
    clock_str = datetime.now().strftime("%H:%M")
    clock = f"{s['dim']}[{clock_str}]{s['reset']}" if cs else f"[{clock_str}]"

    # --- Compose ---
    colored_time = f"{s['cyan']}{time_str}{s['reset']}" if cs else time_str
    if cs == "b":
        return f"\r{colored_time} {bar} {ding_part}  {clock}   "
    return f"\r  ┃ {colored_time} ┃ [{bar}] {ding_part:<25}{clock}   "


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
def print_summary(elapsed, last_ding, achieved, s, cs, session_complete=False):
    """Print end-of-session summary. Call after the live loop ends."""
    print()  # newline to end the live display line

    if session_complete:
        msg = (
            f"{s['green']}✅ Session complete!{s['reset']}" if cs
            else "✅ Session complete!"
        )
        print(f"\n{msg}")

    elapsed_str = format_elapsed(elapsed)
    avg_str = f"{elapsed / last_ding:.1f}s" if last_ding > 0 else "—"

    if cs == "b":
        print(
            f"\n{s['dim']}Final:{s['reset']} "
            f"{s['green']}{elapsed_str}{s['reset']} "
            f"{s['dim']}│{s['reset']} "
            f"{s['pink']}{last_ding}{s['reset']} dings"
        )
        if last_ding > 0:
            print(f"{s['dim']}Avg: {avg_str}{s['reset']}")
        if achieved:
            print(f"{s['dim']}Achieved: {s['pink']}{', '.join(achieved)}{s['reset']}")
        print()

    elif cs == "c":
        bw = 40
        rows = [("Time:", elapsed_str, s["green"])]
        rows.append(("Dings:", str(last_ding), s["magenta"]))
        if last_ding > 0:
            rows.append(("Average:", avg_str, s["yellow"]))
        if achieved:
            rows.append(("Achieved:", ", ".join(achieved), s["magenta"]))
        print(f"\n{s['cyan']}┌{'─' * (bw - 2)}┐{s['reset']}")
        for label, value, color in rows:
            pad = max(0, bw - 2 - 1 - len(label) - 1 - len(value) - 1)
            print(
                f"{s['cyan']}│{s['reset']} "
                f"{s['dim']}{label}{s['reset']} "
                f"{color}{value}{s['reset']}"
                f"{' ' * pad}{s['cyan']}│{s['reset']}"
            )
        print(f"{s['cyan']}└{'─' * (bw - 2)}┘{s['reset']}\n")

    else:
        hw = 52
        print(f"\n{s['cyan']}{'─' * hw}{s['reset']}")
        print(f"{s['cyan']}{'⏹️  STOPPED':^{hw}}{s['reset']}")
        print(f"{s['cyan']}{'─' * hw}{s['reset']}")
        if cs:
            print(f"\n  {s['dim']}Final time:{s['reset']} {s['green']}{elapsed_str}{s['reset']}")
            print(f"  {s['dim']}Total dings:{s['reset']} {s['magenta']}{last_ding}{s['reset']}")
            if last_ding > 0:
                print(f"  {s['dim']}Average interval:{s['reset']} {s['yellow']}{avg_str}{s['reset']}")
            if achieved:
                print(f"  {s['dim']}Achieved:{s['reset']} {s['magenta']}{', '.join(achieved)}{s['reset']}")
        else:
            print(f"\n  Final time: {elapsed_str}")
            print(f"  Total dings: {last_ding}")
            if last_ding > 0:
                print(f"  Average interval: {avg_str}")
            if achieved:
                print(f"  Achieved: {', '.join(achieved)}")
        print()


# ---------------------------------------------------------------------------
# Log
# ---------------------------------------------------------------------------
def save_log(task, elapsed, last_ding, interval):
    """Silently append session record to ~/.ding-log.csv."""
    try:
        exists = os.path.exists(LOG_FILE)
        with open(LOG_FILE, "a", newline="") as f:
            w = csv.writer(f)
            if not exists:
                w.writerow(["date", "task", "elapsed_seconds", "dings", "interval_seconds"])
            w.writerow([
                datetime.now().strftime("%Y-%m-%d %H:%M"),
                task or "",
                f"{elapsed:.1f}",
                last_ding,
                f"{interval:g}",
            ])
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------
def run_stopwatch(interval, milestones=False, task=None, color_scheme=None,
                  quiet=False, duration=None, max_dings=None, reverse=False):
    s = SCHEMES.get(color_scheme, SCHEMES[None])

    # Reverse bar is default for countdown mode
    if duration and not reverse:
        reverse = True

    start_time = time.time()
    last_ding = 0
    ding_flash_until = 0.0
    session_complete = False

    print_header(interval, task, duration, s, color_scheme)

    try:
        while True:
            elapsed = time.time() - start_time

            # Auto-stop: duration elapsed
            if duration and elapsed >= duration:
                play_ding(-1, quiet=quiet)
                session_complete = True
                break

            # Auto-stop: max dings reached
            if max_dings and last_ding >= max_dings:
                play_ding(-1, quiet=quiet)
                session_complete = True
                break

            # Interval ding check
            current_interval = int(elapsed // interval)
            if current_interval > last_ding:
                last_ding = current_interval
                milestone = last_ding if (milestones and last_ding in {10, 50, 100, 500}) else 0
                play_ding(milestone, quiet=quiet)
                ding_flash_until = time.time() + 0.5  # time-based flash

            line = render_line(
                elapsed, interval, last_ding, ding_flash_until,
                duration, reverse, max_dings, s, color_scheme,
            )
            print(line, end="", flush=True)
            time.sleep(0.1)

    except KeyboardInterrupt:
        pass

    elapsed = time.time() - start_time

    achieved = []
    if milestones:
        for m in [500, 100, 50, 10]:
            if last_ding >= m:
                achieved.append(f"{m}th")

    print_summary(elapsed, last_ding, achieved, s, color_scheme, session_complete)
    save_log(task, elapsed, last_ding, interval)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="CLI stopwatch/countdown timer that dings at regular intervals.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  python ding-timer.py 30                        # Stopwatch, ding every 30s
  python ding-timer.py 30 --duration 25m         # 25-minute countdown session
  python ding-timer.py 25 --count 8              # Stop after 8 dings
  python ding-timer.py 30 --quiet                # Silent (visual only)
  python ding-timer.py 30 --reverse              # Bar drains toward next ding
  python ding-timer.py 30 --task "Write docs"    # Label the session
  python ding-timer.py 30 --milestones           # Special sounds at 10/50/100/500
  python ding-timer.py 30 --color a              # Compact colorful style
  python ding-timer.py 30 --color b              # Minimal soft style
  python ding-timer.py 30 --color c              # Balanced lavender style
  python ding-timer.py 1.5 --color a             # Float intervals work too
""",
    )
    parser.add_argument(
        "interval", type=float,
        help="Interval in seconds between each ding (decimals supported)",
    )
    parser.add_argument(
        "--milestones", action="store_true",
        help="Special sounds at 10th, 50th, 100th, 500th dings",
    )
    parser.add_argument("--task", type=str, help="Session label to display")
    parser.add_argument(
        "--color", choices=["a", "b", "c"],
        help="Color scheme: a=compact/colorful, b=minimal/soft, c=balanced/lavender",
    )
    parser.add_argument("--quiet", action="store_true", help="Suppress all sounds")
    parser.add_argument(
        "--duration", type=str,
        help="Auto-stop after duration: '25m', '90s', '1h', or raw seconds",
    )
    parser.add_argument(
        "--count", type=int, dest="max_dings",
        help="Auto-stop after N dings",
    )
    parser.add_argument(
        "--reverse", action="store_true",
        help="Reverse bar: drains toward next ding (auto-enabled in countdown mode)",
    )

    args = parser.parse_args()

    if args.interval <= 0:
        print("Error: Interval must be positive.", file=sys.stderr)
        sys.exit(1)

    duration = None
    if args.duration:
        try:
            duration = parse_duration(args.duration)
        except ValueError:
            print(
                f"Error: Invalid duration '{args.duration}'. Use '25m', '90s', '1h', or seconds.",
                file=sys.stderr,
            )
            sys.exit(1)
        if duration <= 0:
            print("Error: Duration must be positive.", file=sys.stderr)
            sys.exit(1)

    run_stopwatch(
        args.interval,
        milestones=args.milestones,
        task=args.task,
        color_scheme=args.color,
        quiet=args.quiet,
        duration=duration,
        max_dings=args.max_dings,
        reverse=args.reverse,
    )


if __name__ == "__main__":
    main()
