#!/usr/bin/env python3
"""
A simple CLI stopwatch that dings at regular intervals.
Usage: python ding-timer.py <seconds>
"""

import sys
import time
import math
import argparse
import subprocess
import platform
import threading


def play_ding(milestone_level=0):
    """Play a system ding sound in a non-blocking way.

    Args:
        milestone_level: 0=regular, 10=tenth, 50=fiftieth, 100=hundredth, 500=five-hundredth
    """
    def _play():
        system = platform.system()
        try:
            if system == "Darwin":  # macOS
                # Different sounds for different milestones
                sound_map = {
                    0: "/System/Library/Sounds/Glass.aiff",      # Regular ding
                    10: "/System/Library/Sounds/Ping.aiff",      # 10th - higher pitch
                    50: "/System/Library/Sounds/Hero.aiff",      # 50th - epic
                    100: "/System/Library/Sounds/Funk.aiff",     # 100th - celebration
                    500: "/System/Library/Sounds/Sosumi.aiff"    # 500th - major achievement
                }
                sound_file = sound_map.get(milestone_level, sound_map[0])
                subprocess.Popen(["afplay", sound_file],
                               stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL)
            elif system == "Linux":
                # Different sounds for Linux
                sound_map = {
                    0: "/usr/share/sounds/freedesktop/stereo/bell.oga",
                    10: "/usr/share/sounds/freedesktop/stereo/message.oga",
                    50: "/usr/share/sounds/freedesktop/stereo/complete.oga",
                    100: "/usr/share/sounds/freedesktop/stereo/service-login.oga",
                    500: "/usr/share/sounds/freedesktop/stereo/phone-incoming-call.oga"
                }
                sound_file = sound_map.get(milestone_level, sound_map[0])
                subprocess.Popen(["paplay", sound_file],
                               stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL)
            elif system == "Windows":
                import winsound
                # Different frequencies for different milestones
                freq_map = {
                    0: (1000, 200),    # Regular: 1000Hz, 200ms
                    10: (1200, 250),   # 10th: higher pitch
                    50: (1500, 300),   # 50th: even higher, longer
                    100: (2000, 400),  # 100th: high celebration
                    500: (2500, 600)   # 500th: highest, longest
                }
                freq, duration = freq_map.get(milestone_level, freq_map[0])
                winsound.Beep(freq, duration)
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


def run_stopwatch(interval, milestones=False, task=None, color_scheme=None):
    """Run the stopwatch with ding intervals."""
    start_time = time.time()
    last_ding = 0
    ding_flash = 0

    # Variant-specific setup
    if color_scheme == "a":
        # Variant A: Compact & Colorful - single line header
        SOFT_GREEN = "\033[92m"
        SOFT_CYAN = "\033[96m"
        SOFT_YELLOW = "\033[93m"
        SOFT_CORAL = "\033[38;5;210m"
        SOFT_MAGENTA = "\033[95m"
        DIM = "\033[2m"
        RESET = "\033[0m"
        bar_width = 20
        bar_char_filled = "█"
        bar_char_empty = "░"
        use_gradient = True

        # Header
        task_str = f" - {task}" if task else ""
        print(f"\n{SOFT_CYAN}⏱️  Stopwatch{RESET} {DIM}•{RESET} Ding every {SOFT_YELLOW}{interval}s{RESET}{task_str} {DIM}• Ctrl+C to stop{RESET}\n")

    elif color_scheme == "b":
        # Variant B: Ultra-minimal - dimmed header, solid blue bar, uses ▓
        SOFT_BLUE = "\033[38;5;117m"  # Soft sky blue
        SOFT_GREEN = "\033[92m"
        SOFT_YELLOW = "\033[93m"
        SOFT_PINK = "\033[38;5;218m"  # Soft pink
        SOFT_MAGENTA = SOFT_PINK
        SOFT_CYAN = SOFT_BLUE
        SOFT_CORAL = SOFT_PINK
        DIM = "\033[2m"
        RESET = "\033[0m"
        bar_width = 16
        bar_char_filled = "▓"
        bar_char_empty = "░"
        use_gradient = False  # Solid blue bar!

        # Header
        task_str = f" - {task}" if task else ""
        print(f"\n{DIM}Interval: {interval}s{task_str} • Ctrl+C to stop{RESET}\n")

    elif color_scheme == "c":
        # Variant C: Balanced & Clean - box UI, uses ━/─
        SOFT_GREEN = "\033[92m"
        SOFT_CYAN = "\033[96m"
        SOFT_YELLOW = "\033[93m"
        SOFT_LAVENDER = "\033[38;5;183m"  # Soft lavender
        SOFT_MAGENTA = SOFT_LAVENDER
        SOFT_CORAL = SOFT_LAVENDER
        DIM = "\033[2m"
        RESET = "\033[0m"
        bar_width = 20
        bar_char_filled = "━"
        bar_char_empty = "─"
        use_gradient = True

        # Box header
        box_width = 40
        interval_text = f"Interval: {interval}s"
        if task:
            interval_text = f"{interval_text} - {task}"
        hint_text = "(Ctrl+C to stop)"
        content = f" {interval_text}  {hint_text} "
        padding = box_width - len(content) - 2
        left_pad = padding // 2
        right_pad = padding - left_pad

        print(f"\n{SOFT_CYAN}┌{'─' * (box_width - 2)}┐{RESET}")
        print(f"{SOFT_CYAN}│{' ' * left_pad}{RESET}{SOFT_YELLOW}{interval_text}{RESET}  {DIM}{hint_text}{RESET}{' ' * right_pad}{SOFT_CYAN}│{RESET}")
        print(f"{SOFT_CYAN}└{'─' * (box_width - 2)}┘{RESET}\n")

    else:
        # Default: Colorless
        SOFT_GREEN = SOFT_CYAN = SOFT_YELLOW = SOFT_CORAL = SOFT_MAGENTA = DIM = RESET = ""
        bar_width = 24
        bar_char_filled = "█"
        bar_char_empty = "░"
        use_gradient = False

        # Header
        header_width = 50
        print(f"\n{'═' * header_width}")
        print(f"{'⏱️  STOPWATCH':^{header_width}}")
        print(f"{'Ding every ' + str(interval) + ' seconds':^{header_width}}")
        print("═" * header_width)
        if task:
            print(f"{'Task: ' + task:^{header_width}}")
            print("─" * header_width)
        print(f"\n{'Press Ctrl+C to stop':^{header_width}}\n")

    try:
        while True:
            elapsed = time.time() - start_time

            # Check if it's time to ding
            current_interval = int(elapsed // interval)
            if current_interval > last_ding:
                last_ding = current_interval

                # Determine milestone level for sound (only if milestones enabled)
                # Single achievements only - no repetition
                if milestones and last_ding in [10, 50, 100, 500]:
                    milestone_sound = last_ding
                    ding_flash = 6  # Slightly longer flash for milestones
                else:
                    milestone_sound = 0
                    ding_flash = 5

                play_ding(milestone_sound)

            # Build display
            time_str = format_time(elapsed)
            next_ding = (last_ding + 1) * interval
            progress = (elapsed % interval) / interval
            filled = int(bar_width * progress)

            # Build progress bar
            if color_scheme == "b":
                # Variant B: Solid blue bar (no gradient)
                bar = f"{SOFT_BLUE}{bar_char_filled * filled}{DIM}{bar_char_empty * (bar_width - filled)}{RESET}"
            elif use_gradient and color_scheme:
                # Variants A & C: Gradient bar
                if progress < 0.7:
                    bar_color = SOFT_GREEN
                elif progress < 0.9:
                    bar_color = SOFT_YELLOW
                else:
                    bar_color = SOFT_CORAL
                bar = f"{bar_color}{bar_char_filled * filled}{DIM}{bar_char_empty * (bar_width - filled)}{RESET}"
            else:
                # Default: No colors
                bar = bar_char_filled * filled + bar_char_empty * (bar_width - filled)

            # Show ding indicator (countdown from t to 1, then ding)
            remaining = math.ceil(next_ding - elapsed)
            if ding_flash > 0:
                ding_indicator = f"{SOFT_MAGENTA}🔔 DING!{RESET}" if color_scheme else "🔔 DING!"
                ding_flash -= 1
            else:
                if color_scheme:
                    ding_indicator = f"{SOFT_YELLOW}Next: {remaining:3d}s{RESET}"
                else:
                    ding_indicator = f"Next: {remaining:3d}s"

            # Format output
            colored_time = f"{SOFT_CYAN if color_scheme != 'b' else SOFT_GREEN}{time_str}{RESET}" if color_scheme else time_str
            if color_scheme == "b":
                output = f"\r{colored_time} {bar} {ding_indicator}   "
            else:
                output = f"\r  ┃ {colored_time} ┃ [{bar}] {ding_indicator:<25}"

            print(output, end="", flush=True)
            time.sleep(0.1)

    except KeyboardInterrupt:
        elapsed = time.time() - start_time

        # Track which milestones were achieved (single achievements only)
        achieved_milestones = []
        if milestones:
            if last_ding >= 500:
                achieved_milestones.append("500th")
            if last_ding >= 100:
                achieved_milestones.append("100th")
            if last_ding >= 50:
                achieved_milestones.append("50th")
            if last_ding >= 10:
                achieved_milestones.append("10th")

        if color_scheme == "b":
            print(f"\n\n{DIM}Final:{RESET} {SOFT_GREEN}{format_time(elapsed)}{RESET} {DIM}│{RESET} {SOFT_PINK}{last_ding}{RESET} dings")
            if last_ding > 0:
                print(f"{DIM}Avg: {elapsed/last_ding:.1f}s{RESET}")
            if achieved_milestones:
                print(f"{DIM}Achieved: {SOFT_PINK}{', '.join(achieved_milestones)}{RESET}")
            print()
        elif color_scheme == "c":
            box_width = 40
            print(f"\n\n{SOFT_CYAN}┌{'─' * (box_width - 2)}┐{RESET}")
            print(f"{SOFT_CYAN}│{RESET} {DIM}Time:{RESET} {SOFT_GREEN}{format_time(elapsed)}{RESET}{' ' * (box_width - len(format_time(elapsed)) - 9)}{SOFT_CYAN}│{RESET}")
            print(f"{SOFT_CYAN}│{RESET} {DIM}Dings:{RESET} {SOFT_LAVENDER}{last_ding}{RESET}{' ' * (box_width - len(str(last_ding)) - 10)}{SOFT_CYAN}│{RESET}")
            if last_ding > 0:
                avg_text = f"{elapsed/last_ding:.1f}s"
                print(f"{SOFT_CYAN}│{RESET} {DIM}Average:{RESET} {SOFT_YELLOW}{avg_text}{RESET}{' ' * (box_width - len(avg_text) - 12)}{SOFT_CYAN}│{RESET}")
            if achieved_milestones:
                milestone_text = ", ".join(achieved_milestones)
                print(f"{SOFT_CYAN}│{RESET} {DIM}Achieved:{RESET} {SOFT_LAVENDER}{milestone_text}{RESET}{' ' * (box_width - len(milestone_text) - 13)}{SOFT_CYAN}│{RESET}")
            print(f"{SOFT_CYAN}└{'─' * (box_width - 2)}┘{RESET}\n")
        else:
            header_width = 50 if not color_scheme else 50
            print(f"\n\n{SOFT_CYAN}{'─' * header_width}{RESET}")
            print(f"{SOFT_CYAN}{'⏹️  STOPPED':^{header_width}}{RESET}")
            print(f"{SOFT_CYAN}{'─' * header_width}{RESET}")
            print(f"\n  {DIM}Final time:{RESET} {SOFT_GREEN}{format_time(elapsed)}{RESET}" if color_scheme else f"\n  Final time: {format_time(elapsed)}")
            print(f"  {DIM}Total dings:{RESET} {SOFT_MAGENTA}{last_ding}{RESET}" if color_scheme else f"  Total dings: {last_ding}")
            if last_ding > 0:
                print(f"  {DIM}Average interval:{RESET} {SOFT_YELLOW}{elapsed/last_ding:.1f}s{RESET}" if color_scheme else f"  Average interval: {elapsed/last_ding:.1f}s")
            if achieved_milestones:
                milestone_text = ", ".join(achieved_milestones)
                print(f"  {DIM}Achieved:{RESET} {SOFT_MAGENTA}{milestone_text}{RESET}" if color_scheme else f"  Achieved: {milestone_text}")
            print()


def main():
    parser = argparse.ArgumentParser(
        description="A stopwatch that dings at regular intervals.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  python ding-timer.py 30                      # Basic: colorless, clean
  python ding-timer.py 30 --milestones         # Track milestone stats (×5, ×10)
  python ding-timer.py 25 --task "Write docs"  # Set a task name
  python ding-timer.py 30 --color a            # Compact colorful style
  python ding-timer.py 30 --color b            # Minimal soft colors
  python ding-timer.py 30 --color c            # Balanced soft colors
  python ding-timer.py 30 --milestones --color a  # Combine features
"""
    )
    parser.add_argument(
        "interval",
        type=int,
        help="Interval in seconds between each ding"
    )
    parser.add_argument(
        "--milestones",
        action="store_true",
        help="Special sounds at 10th, 50th, 100th, 500th dings (single achievements)"
    )
    parser.add_argument(
        "--task",
        type=str,
        help="Set a task name to display during session"
    )
    parser.add_argument(
        "--color",
        choices=["a", "b", "c"],
        help="Color scheme: a=compact/colorful, b=minimal/soft, c=balanced/lavender"
    )

    args = parser.parse_args()

    if args.interval <= 0:
        print("Error: Interval must be a positive number.", file=sys.stderr)
        sys.exit(1)

    run_stopwatch(args.interval, milestones=args.milestones,
                  task=args.task, color_scheme=args.color)


if __name__ == "__main__":
    main()
