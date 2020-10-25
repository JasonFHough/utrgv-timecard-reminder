# UTRGV Timecard Reminder

A Python automation script that reminds users when an upcoming timecard is due.

Users are notified by email and Slack integration.

## Installation

**Requires `Python 3.7.0` or later**

## Environment Setup (MacOS with Homebrew)

### Install `pyenv` and `pyenv-virtualenv`

```bash
brew install pyenv
brew install pyenv-virtualenv
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"
```

See [pyenv](https://github.com/pyenv/pyenv) and/or [pyenv-virtualenv](https://github.com/pyenv/pyenv-virtualenv) for more details.

### Create Virtual Environment using Python 3.7.0

```bash
pyenv virtualenv 3.7.0 utrgv-timecard
pyenv activate utrgv-timecard
```

See [pyenv](https://github.com/pyenv/pyenv) and/or [pyenv-virtualenv](https://github.com/pyenv/pyenv-virtualenv) for more details.

### Run `reminder.py`

```bash
python reminder.py
```
