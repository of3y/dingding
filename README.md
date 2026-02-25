# Ding Timer ⏱️🔔

A beautiful CLI stopwatch that dings at regular intervals.

```
════════════════════════════════════════════════════════
                    ⏱️  STOPWATCH
                Ding every 30 seconds
════════════════════════════════════════════════════════

  ┃ 00:01:23.4 ┃  [███████████░░░░░░░░░░░░░░░░░░]  Next ding in 7s
```

## Usage

```bash
python ding-timer.py <seconds>
```

**Examples:**
- `python ding-timer.py 30` - Ding every 30 seconds
- `python ding-timer.py 300` - Ding every 5 minutes
- `python ding-timer.py 60` - Ding every minute

## Features

- ⏱️ Beautiful real-time display with milliseconds
- 📊 Visual progress bar until next ding
- 🔔 Non-blocking system sound notifications
- 🖥️ Cross-platform (macOS, Linux, Windows)
- 📈 Summary stats when stopped (total time, dings, average)

## Requirements

Python 3 - No additional dependencies!

## Quick Setup

Make it accessible anywhere:

```bash
# Add to ~/.zshrc or ~/.bashrc
alias ding='python /path/to/ding-timer.py'
```
