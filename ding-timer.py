#!/usr/bin/env python3
"""
A simple CLI stopwatch that dings at regular intervals.
Usage: python ding-timer.py <seconds>
"""

import sys
import time
import argparse
import subprocess
import platform
import threading


def play_ding():
    """Play a system ding sound in a non-blocking way."""
    def _play():
        system = platform.system()
        try:
            if system == "Darwin":  # macOS
                subprocess.Popen(["afplay", "/System/Library/Sounds/Glass.aiff"],
                               stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL)
            elif system == "Linux":
                subprocess.Popen(["paplay", "/usr/share/sounds/freedesktop/stereo/bell.oga"],
                               stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL)
            elif system == "Windows":
                import winsound
                winsound.Beep(1000, 200)
        except Exception:
            # Fallback to terminal bell
            print("\a", end="", flush=True)

    # Play sound in a separate thread to avoid blocking
    threading.Thread(target=_play, daemon=True).start()


def format_time(seconds):
    """Format seconds as HH:MM:SS."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 10)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis}"


def get_terminal_width():
    """Get terminal width, default to 80 if unable to determine."""
    try:
        import shutil
        return shutil.get_terminal_size().columns
    except Exception:
        return 80


def run_stopwatch(interval):
    """Run the stopwatch with ding intervals."""
    term_width = get_terminal_width()

    # Print header
    print("\n" + "═" * min(term_width, 60))
    print(f"{'⏱️  STOPWATCH':^{min(term_width, 60)}}")
    print(f"{'Ding every ' + str(interval) + ' seconds':^{min(term_width, 60)}}")
    print("═" * min(term_width, 60))
    print(f"\n{'Press Ctrl+C to stop':^{min(term_width, 60)}}\n")

    start_time = time.time()
    last_ding = 0
    ding_flash = 0

    try:
        while True:
            elapsed = time.time() - start_time

            # Check if it's time to ding
            current_interval = int(elapsed // interval)
            if current_interval > last_ding:
                play_ding()
                last_ding = current_interval
                ding_flash = 5  # Flash for 5 iterations (~0.5 seconds)

            # Build display
            time_str = format_time(elapsed)

            # Create progress bar for interval
            next_ding = (last_ding + 1) * interval
            progress = (elapsed % interval) / interval
            bar_width = 30
            filled = int(bar_width * progress)
            bar = "█" * filled + "░" * (bar_width - filled)

            # Show ding indicator
            if ding_flash > 0:
                ding_indicator = "🔔 DING! 🔔"
                ding_flash -= 1
            else:
                ding_indicator = f"Next ding in {int(next_ding - elapsed)}s"

            # Format output
            output = f"\r  ┃ {time_str} ┃  [{bar}]  {ding_indicator}  "

            print(output, end="", flush=True)
            time.sleep(0.1)

    except KeyboardInterrupt:
        elapsed = time.time() - start_time
        print("\n\n" + "─" * min(term_width, 60))
        print(f"{'⏹️  STOPPED':^{min(term_width, 60)}}")
        print("─" * min(term_width, 60))
        print(f"\n  Final time: {format_time(elapsed)}")
        print(f"  Total dings: {last_ding}")
        print(f"  Average interval: {elapsed/last_ding:.1f}s\n" if last_ding > 0 else "")


def main():
    parser = argparse.ArgumentParser(
        description="A stopwatch that dings at regular intervals.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Example: python ding-timer.py 30  # Dings every 30 seconds"
    )
    parser.add_argument(
        "interval",
        type=int,
        help="Interval in seconds between each ding"
    )

    args = parser.parse_args()

    if args.interval <= 0:
        print("Error: Interval must be a positive number.", file=sys.stderr)
        sys.exit(1)

    run_stopwatch(args.interval)


if __name__ == "__main__":
    main()
