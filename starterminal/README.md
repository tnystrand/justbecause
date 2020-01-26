# Bash stars
Simple, not-very-productionized python script that prints dots in the terminal. The dots are printed in random locations and with psudo-random colors. Thus the 'star' aspect.

## Installation
Only tested on iTerm2 on MacOS
Setup python version `3.8.1` or larger - pyenv, pipenv (or miniconda) recommended

E.g.
First remove other python version from `.profile`, `.bash_profile` and `.bashrc`.

```bash
brew install pyenv
pyenv install 3.8.1
```

Add the line below to `~/.bash_profile` (if using bash or `~/.profile` depending on system setup)
```bash
eval "$(pyenv init -)"
```

Set global python version
```bash
pyenv global 3.8.1
```

If using iTerm, for full program functionality configure 'allow blink' (by default iTerm does not allow this escape sequence). This should be configurable for other emulators as well. Mac's default terminator allows it without changing any settings for instance.

## Running
```bash
python star.py
```

## Configuration
Open `star.py` and change the following settings:
* `nstars = 40` to desirable number of stars
* `allow_loop = True` to either False if desired (will only use blink escape codes to avoid an infinity `while True` loop (at the expense of better blinkin).
* `ticker_time` for faster or slower 'fastest' blinking (slower blinking is still possible due to random dot behavior)

## Backlog
- [ ] Install script using `Pipfile`
- [ ] Use argparse/yaml loading for configuration
- [ ] Split script into reasonable modular code
- [ ] Migrate to `tput` for portability
