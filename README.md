# Ding Timer ⏱️🔔

A simple, colorless CLI stopwatch that dings at regular intervals.

```
══════════════════════════════════════════════════
                  ⏱️  STOPWATCH
              Ding every 30 seconds
══════════════════════════════════════════════════

            Press Ctrl+C to stop

  ┃ 00:01:23.4 ┃ [████████████░░░░░░░░░░░░] Next:   7s
```

## Usage

```bash
python ding-timer.py <seconds> [options]
```

**Basic Examples:**
- `python ding-timer.py 30` - Ding every 30 seconds
- `python ding-timer.py 300` - Ding every 5 minutes
- `python ding-timer.py 60` - Ding every minute

**With Optional Features:**
- `python ding-timer.py 30 --milestones` - Special sounds at 10th, 50th, 100th, 500th
- `python ding-timer.py 25 --task "Write docs"` - Set a task name
- `python ding-timer.py 30 --milestones --task "Deep work"` - Combine features

**With Color Schemes:**
- `python ding-timer.py 30 --color a` - Compact & colorful (gradient progress)
- `python ding-timer.py 30 --color b` - Minimal & soft (sky blue/pink)
- `python ding-timer.py 30 --color c` - Balanced & lavender (elegant)
- `python ding-timer.py 30 --color a --milestones` - Colors + milestones!

## Features

- ⏱️ Clean, colorless display by default (simplicity is beauty)
- 📊 Visual progress bar until next ding
- 🔔 Non-blocking system sound notifications
- 🖥️ Cross-platform (macOS, Linux, Windows)
- 📈 Summary stats when stopped (total time, dings, average)

**Optional Enhancements:**
- 🎵 **Milestones** - Special sounds at single achievements (`--milestones`)
  - 10th ding: Higher pitch (one time)
  - 50th ding: Epic sound (one time)
  - 100th ding: Celebration sound (one time)
  - 500th ding: Major achievement sound (one time)
  - Regular dings: Standard sound
- 📝 **Task naming** - Display your task (`--task "name"`)
- 🎨 **Color schemes** - Three soft color palettes (`--color a/b/c`)
  - **a**: Compact & colorful with gradient progress
  - **b**: Minimal with soft sky blue/pink tones
  - **c**: Balanced with elegant lavender accents

## Requirements

Python 3 - No additional dependencies!

## Quick Setup

Make it accessible anywhere:

```bash
# Add to ~/.zshrc or ~/.bashrc
alias ding='python /path/to/ding-timer.py'
```
