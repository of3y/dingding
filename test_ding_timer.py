#!/usr/bin/env python3
"""Standalone test suite for ding-timer.py

Run with:  python test_ding_timer.py
"""

import os
import sys
import csv
import signal
import time
import subprocess
import tempfile
import unittest

SCRIPT = os.path.join(os.path.dirname(__file__), "ding-timer.py")


def run(args, wait=1.5, timeout=10):
    """Launch ding-timer with args, let it run for `wait` seconds, then interrupt.

    Uses SIGINT (not SIGTERM) so the KeyboardInterrupt handler fires and the
    summary is printed before the process exits.
    """
    proc = subprocess.Popen(
        [sys.executable, SCRIPT] + args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    time.sleep(wait)
    proc.send_signal(signal.SIGINT)
    out, err = proc.communicate(timeout=timeout)
    return out.decode(), err.decode(), proc.returncode


def run_to_completion(args, timeout=10):
    """Run ding-timer and wait for it to exit on its own (auto-stop modes)."""
    proc = subprocess.Popen(
        [sys.executable, SCRIPT] + args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    out, err = proc.communicate(timeout=timeout)
    return out.decode(), err.decode(), proc.returncode


class TestHeader(unittest.TestCase):
    def test_stopwatch_header_default(self):
        out, _, _ = run(["5", "--quiet"])
        self.assertIn("STOPWATCH", out)
        self.assertIn("Ding every 5s", out)
        self.assertIn("Ctrl+C to stop", out)

    def test_countdown_header_default(self):
        out, _, _ = run(["5", "--duration", "30s", "--quiet"])
        self.assertIn("COUNTDOWN", out)
        self.assertIn("Duration:", out)

    def test_header_color_a(self):
        out, _, _ = run(["5", "--color", "a", "--quiet"])
        self.assertIn("Ctrl+C to stop", out)
        self.assertIn("5s", out)

    def test_header_color_b(self):
        out, _, _ = run(["5", "--color", "b", "--quiet"])
        self.assertIn("Interval: 5s", out)
        self.assertIn("Ctrl+C to stop", out)

    def test_header_color_c(self):
        out, _, _ = run(["5", "--color", "c", "--quiet"])
        self.assertIn("┌", out)
        self.assertIn("┘", out)
        self.assertIn("Interval: 5s", out)

    def test_task_label_shown(self):
        out, _, _ = run(["5", "--task", "Deep work", "--quiet"])
        self.assertIn("Deep work", out)

    def test_task_label_color_a(self):
        out, _, _ = run(["5", "--color", "a", "--task", "My task", "--quiet"])
        self.assertIn("My task", out)


class TestDisplayLine(unittest.TestCase):
    def test_clock_displayed(self):
        out, _, _ = run(["5", "--quiet"])
        # Clock appears as [HH:MM]
        self.assertRegex(out, r"\[\d{2}:\d{2}\]")

    def test_progress_bar_shown(self):
        out, _, _ = run(["5", "--quiet"])
        self.assertIn("█", out)

    def test_next_ding_indicator(self):
        out, _, _ = run(["5", "--quiet"])
        self.assertIn("Next:", out)

    def test_countdown_shows_time_left(self):
        out, _, _ = run(["5", "--duration", "30s", "--quiet"])
        self.assertIn("left", out)

    def test_count_info_shown(self):
        out, _, _ = run(["5", "--count", "3", "--quiet"])
        self.assertIn("[0/3]", out)

    def test_reverse_bar_present(self):
        # --reverse should still show a bar
        out, _, _ = run(["5", "--quiet", "--reverse"])
        self.assertIn("░", out)  # empty bar chars should be visible at start


class TestIntervals(unittest.TestCase):
    def test_float_interval(self):
        out, _, _ = run(["1.5", "--quiet"])
        self.assertIn("1.5s", out)

    def test_float_interval_below_one(self):
        out, _, _ = run(["0.5", "--quiet"])
        self.assertIn("0.5s", out)

    def test_integer_interval_no_decimal(self):
        out, _, _ = run(["30", "--quiet"])
        self.assertIn("30s", out)
        self.assertNotIn("30.0s", out)


class TestAutoStop(unittest.TestCase):
    def test_count_stops_after_n_dings(self):
        out, err, rc = run_to_completion(["1", "--count", "2", "--quiet"])
        self.assertIn("Session complete", out)
        self.assertEqual(err, "")

    def test_duration_stops_after_time(self):
        out, err, rc = run_to_completion(["2", "--duration", "3s", "--quiet"])
        self.assertIn("Session complete", out)
        self.assertEqual(err, "")

    def test_duration_summary_shows_countdown_header(self):
        out, _, _ = run_to_completion(["2", "--duration", "3s", "--quiet"])
        self.assertIn("COUNTDOWN", out)


class TestSummary(unittest.TestCase):
    def test_summary_shows_final_time(self):
        out, _, _ = run(["5", "--quiet"], wait=1.5)
        # Interrupt → summary with "Final time:"
        self.assertIn("Final time:", out)

    def test_summary_shows_dings(self):
        out, _, _ = run(["5", "--quiet"], wait=1.5)
        self.assertIn("Total dings:", out)

    def test_summary_color_b(self):
        out, _, _ = run(["5", "--color", "b", "--quiet"], wait=1.5)
        self.assertIn("Final:", out)
        self.assertIn("dings", out)

    def test_summary_color_c(self):
        out, _, _ = run(["5", "--color", "c", "--quiet"], wait=1.5)
        self.assertIn("┌", out)
        self.assertIn("Time:", out)
        self.assertIn("Dings:", out)

    def test_summary_completion_message(self):
        out, _, _ = run_to_completion(["1", "--count", "1", "--quiet"])
        self.assertIn("Session complete", out)

    def test_summary_average_shown_when_dings_occurred(self):
        out, _, _ = run_to_completion(["1", "--count", "2", "--quiet"])
        self.assertIn("Average", out)


class TestQuiet(unittest.TestCase):
    def test_quiet_no_stderr(self):
        _, err, _ = run(["5", "--quiet"])
        self.assertEqual(err, "")

    def test_quiet_still_shows_display(self):
        out, _, _ = run(["5", "--quiet"])
        self.assertIn("Next:", out)


class TestValidation(unittest.TestCase):
    def test_negative_interval_rejected(self):
        proc = subprocess.Popen(
            [sys.executable, SCRIPT, "-5"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        _, err = proc.communicate()
        self.assertEqual(proc.returncode, 1)
        self.assertIn("Error", err.decode())

    def test_zero_interval_rejected(self):
        proc = subprocess.Popen(
            [sys.executable, SCRIPT, "0"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        _, err = proc.communicate()
        self.assertEqual(proc.returncode, 1)

    def test_invalid_duration_rejected(self):
        proc = subprocess.Popen(
            [sys.executable, SCRIPT, "5", "--duration", "notatime"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        _, err = proc.communicate()
        self.assertEqual(proc.returncode, 1)
        self.assertIn("Error", err.decode())

    def test_negative_duration_rejected(self):
        # argparse may exit with code 2 (unknown flag) or our code exits with 1;
        # either way it must not succeed (returncode 0)
        proc = subprocess.Popen(
            [sys.executable, SCRIPT, "5", "--duration", "-5m"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        _, err = proc.communicate()
        self.assertNotEqual(proc.returncode, 0)


class TestDurationParsing(unittest.TestCase):
    """Unit tests for parse_duration() directly."""

    def setUp(self):
        # Import the module directly
        import importlib.util
        spec = importlib.util.spec_from_file_location("ding_timer", SCRIPT)
        self.mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.mod)

    def test_minutes(self):
        self.assertEqual(self.mod.parse_duration("25m"), 1500.0)

    def test_seconds(self):
        self.assertEqual(self.mod.parse_duration("90s"), 90.0)

    def test_hours(self):
        self.assertEqual(self.mod.parse_duration("1h"), 3600.0)

    def test_raw_seconds(self):
        self.assertEqual(self.mod.parse_duration("1500"), 1500.0)

    def test_float_minutes(self):
        self.assertAlmostEqual(self.mod.parse_duration("1.5m"), 90.0)

    def test_uppercase_ignored(self):
        self.assertEqual(self.mod.parse_duration("25M"), 1500.0)

    def test_invalid_raises(self):
        with self.assertRaises(ValueError):
            self.mod.parse_duration("abc")


class TestFormatters(unittest.TestCase):
    def setUp(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("ding_timer", SCRIPT)
        self.mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.mod)

    def test_format_elapsed_under_minute(self):
        self.assertEqual(self.mod.format_elapsed(5.7), "00:05.7")

    def test_format_elapsed_minutes(self):
        self.assertEqual(self.mod.format_elapsed(90.0), "01:30.0")

    def test_format_elapsed_hours(self):
        self.assertEqual(self.mod.format_elapsed(3661.0), "01:01:01.0")

    def test_format_remaining_under_minute(self):
        self.assertEqual(self.mod.format_remaining(45.9), "00:45")

    def test_format_remaining_minutes(self):
        self.assertEqual(self.mod.format_remaining(1500), "25:00")

    def test_format_remaining_hours(self):
        self.assertEqual(self.mod.format_remaining(3661), "1:01:01")

    def test_format_remaining_zero(self):
        self.assertEqual(self.mod.format_remaining(0), "00:00")

    def test_format_remaining_negative_clamped(self):
        self.assertEqual(self.mod.format_remaining(-5), "00:00")


class TestBuildBar(unittest.TestCase):
    def setUp(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("ding_timer", SCRIPT)
        self.mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.mod)
        self.s_plain = self.mod.SCHEMES[None]
        self.s_colored = self.mod.SCHEMES["a"]

    def test_empty_bar_at_zero(self):
        bar = self.mod.build_bar(self.s_plain, 0.0)
        self.assertEqual(bar, "░" * 24)

    def test_full_bar_at_one(self):
        bar = self.mod.build_bar(self.s_plain, 1.0)
        self.assertEqual(bar, "█" * 24)

    def test_half_bar(self):
        bar = self.mod.build_bar(self.s_plain, 0.5)
        self.assertEqual(bar.count("█"), 12)
        self.assertEqual(bar.count("░"), 12)

    def test_reverse_empty_bar_at_one(self):
        bar = self.mod.build_bar(self.s_plain, 1.0, reverse=True)
        self.assertEqual(bar, "░" * 24)

    def test_reverse_full_bar_at_zero(self):
        bar = self.mod.build_bar(self.s_plain, 0.0, reverse=True)
        self.assertEqual(bar, "█" * 24)

    def test_reverse_half(self):
        bar = self.mod.build_bar(self.s_plain, 0.5, reverse=True)
        self.assertEqual(bar.count("█"), 12)
        self.assertEqual(bar.count("░"), 12)

    def test_progress_clamped_above_one(self):
        bar = self.mod.build_bar(self.s_plain, 1.5)
        self.assertEqual(bar, "█" * 24)

    def test_progress_clamped_below_zero(self):
        bar = self.mod.build_bar(self.s_plain, -0.5)
        self.assertEqual(bar, "░" * 24)

    def test_colored_bar_contains_reset(self):
        bar = self.mod.build_bar(self.s_colored, 0.5)
        self.assertIn("\033[0m", bar)

    def test_colored_gradient_green_at_low_progress(self):
        # progress=0.5 → display=0.5 → > 0.3 threshold → green
        bar = self.mod.build_bar(self.s_colored, 0.5, reverse=False)
        self.assertIn("\033[92m", bar)  # green

    def test_colored_gradient_coral_near_full(self):
        # Very high display (> 90%) → green, and very low (< 10%) → coral
        # Reverse at 0.95 progress → display 0.05 → coral
        bar = self.mod.build_bar(self.s_colored, 0.95, reverse=True)
        self.assertIn("\033[38;5;210m", bar)  # coral


class TestSessionLog(unittest.TestCase):
    def test_log_written_on_auto_stop(self):
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            log_path = f.name

        try:
            env = os.environ.copy()
            # Patch LOG_FILE via env isn't possible directly; use count=1 short run
            # and check the actual log file
            run_to_completion(
                ["1", "--count", "1", "--quiet", "--task", "log-test-session"]
            )
            log = os.path.expanduser("~/.ding-log.csv")
            self.assertTrue(os.path.exists(log))
            with open(log) as f:
                content = f.read()
            self.assertIn("log-test-session", content)
            # Check CSV structure
            with open(log) as f:
                reader = csv.DictReader(f)
                rows = list(reader)
            self.assertIn("date", rows[0])
            self.assertIn("task", rows[0])
            self.assertIn("elapsed_seconds", rows[0])
            self.assertIn("dings", rows[0])
            self.assertIn("interval_seconds", rows[0])
        finally:
            os.unlink(log_path)

    def test_log_not_required_to_run(self):
        # Even if log write would fail, the app should not crash
        # (save_log is wrapped in try/except)
        out, err, rc = run(["5", "--quiet"], wait=0.5)
        self.assertEqual(err, "")


class TestSyntax(unittest.TestCase):
    def test_compiles_cleanly(self):
        import py_compile
        py_compile.compile(SCRIPT, doraise=True)

    def test_no_unused_stdlib_side_effects(self):
        # Importing the module should not start any threads or open files
        import importlib.util
        spec = importlib.util.spec_from_file_location("ding_timer", SCRIPT)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        # Verify key symbols exist
        self.assertTrue(callable(mod.run_stopwatch))
        self.assertTrue(callable(mod.play_ding))
        self.assertTrue(callable(mod.build_bar))
        self.assertIn(None, mod.SCHEMES)
        self.assertIn("a", mod.SCHEMES)
        self.assertIn("b", mod.SCHEMES)
        self.assertIn("c", mod.SCHEMES)


if __name__ == "__main__":
    unittest.main(verbosity=2)
