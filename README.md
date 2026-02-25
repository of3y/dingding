# Ding Timer ⏱️🔔

A CLI stopwatch and countdown timer that dings at regular intervals.

```
════════════════════════════════════════════════════
                   ⏱️  STOPWATCH
                   Ding every 30s
════════════════════════════════════════════════════

                Press Ctrl+C to stop

  ┃ 00:01:23.4 ┃ [████████████░░░░░░░░░░░░] Next:   7s               [14:22]
```

```
════════════════════════════════════════════════════
                   ⏱️  COUNTDOWN
                   Ding every 30s
                  Duration: 25:00
════════════════════════════════════════════════════

                Press Ctrl+C to stop

  ┃ 23:41 left ┃ [█████████████████░░░░░░░] Next:  12s               [14:22]
```

## Usage

```bash
python ding-timer.py <interval> [options]
```

### Stopwatch (infinite)

```bash
python ding-timer.py 30                        # Ding every 30s, run forever
python ding-timer.py 1.5                       # Float intervals supported
python ding-timer.py 30 --reverse              # Bar drains toward next ding
```

### Countdown (auto-stop)

```bash
python ding-timer.py 30 --duration 25m        # 25-minute session
python ding-timer.py 30 --duration 90s        # 90-second session
python ding-timer.py 30 --duration 1h         # 1-hour session
python ding-timer.py 25 --count 8             # Stop after 8 dings
```

Countdown mode uses a reverse bar by default — it starts full and drains to
zero as the session time is consumed. Pass `--reverse` explicitly to get the
same effect in stopwatch mode.

### Labels & sound

```bash
python ding-timer.py 30 --task "Deep work"    # Label the session
python ding-timer.py 30 --quiet               # Visual only, no sounds
python ding-timer.py 30 --milestones          # Special sounds at 10/50/100/500 dings
```

### Color schemes

```bash
python ding-timer.py 30 --color a             # Compact & colorful (gradient bar)
python ding-timer.py 30 --color b             # Minimal (sky blue / pink)
python ding-timer.py 30 --color c             # Balanced (lavender accents, box UI)
```

Combine anything:

```bash
python ding-timer.py 25 --duration 50m --task "Writing" --color a --milestones
```

## Features

- **Stopwatch & countdown** — run forever or auto-stop after a duration or ding count
- **Reverse progress bar** — bar drains toward the next ding; default in countdown mode
- **Wall clock** — current time `[HH:MM]` on every line (helps with time blindness)
- **Visual progress bar** — fills (or drains) toward next ding
- **Non-blocking sounds** — system audio in a background thread, never delays the display
- **Float intervals** — `0.5`, `1.5`, `2.5` — any positive number works
- **Session log** — every session is silently appended to `~/.ding-log.csv`
- **Summary on exit** — total time, ding count, average interval
- **Cross-platform** — macOS (`afplay`), Linux (`paplay`), Windows (`winsound`), terminal bell fallback
- **Zero dependencies** — Python 3 stdlib only

### Milestone sounds (`--milestones`)

Special one-time sounds at landmark ding counts:

| Ding | macOS sound |
|------|-------------|
| 10th | Ping |
| 50th | Hero |
| 100th | Funk |
| 500th | Sosumi |

### Session log (`~/.ding-log.csv`)

Every session writes one row:

```
date,task,elapsed_seconds,dings,interval_seconds
2026-02-25 14:22,Deep work,1500.0,50,30
```

## Requirements

Python 3 — no additional dependencies.

## Quick setup

```bash
# Add to ~/.zshrc or ~/.bashrc
alias ding='python /path/to/ding-timer.py'
```

## Running the tests

```bash
python test_ding_timer.py
```

61 tests covering all features, formatters, bar logic, auto-stop, and validation.
