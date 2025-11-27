# 👋 THIS REPOSITORY HAS MOVED! 👋

**This repository is no longer actively maintained on GitHub.**

Please update your bookmarks and remotes to the new home on Codeberg:

➡️ **[https://codeberg.org/alexeygumirov/tmux-session-manager](https://codeberg.org/alexeygumirov/tmux-session-manager)** ⬅️

Thank you for your understanding!

# Tmux session manager

Simple Tmux session manager in Python.

Version: v2.2

## Motivation

I use Tmux quite extensively in my job and needed some tool which allowed me to manage my Tmux sessions efficiently:

1. Create sessions:
    - With necessary number of windows
    - Given window names
    - Given root folder for each window
        - Handle root folders with special charaters and spaces, e.g. `~/Downloads/Project {1} - Test (1)`
2. Restore/repair sessions if I accidentially mess it up.
3. Switch between sessions.

**New features added**:

1. Actions menu.
2. Ability to save running session.
3. Ability to deleted session file.

## Dependencies

- [fzf](https://github.com/junegunn/fzf)

## How it works

- You need Tmux and FZF installed
- By default the folder for your session config files is `~/.config/tmux-project-sessions`, but you can change in the script `main()` function by setting `config_path` variable.
- Session file name is a session name
- Session file format:

Each entry is `window name = root folder` pair. If one is empty - default value defined by Tmux config is going to be used.

```config
# Example Tmux Session

= ~/
config = ~/.config
down = ~/Downloads
project = ~/Projects/my awesome project
```

## Script parameters

Script accepts following parameters:
- `menu`: Script starts with actions selection menu: Open/Restore/Save/Delete. You first select the action and then script calls sessions list to apply action to.
- `open`: Opens selected session or attaches client to it if session already running.
- `restore`: Restores/repairs selected session. Use this option if you messed up your windows (qantity, order, names, root folders) and you want to go reset session back to the state described in the session file.
- `save`: Allows to save current session into the new file in the `~/.config/tmux-project-sessions` directory. File name will be `TIME_STAMP_session_name`. TIME_STAMP is in the format of `%Y-%m-%d_%H-%M-%S`. `session_name` part of the file name is created from the actual session name where all non-alphanumerical symbols are replaced with `-`.
- `delete`: Delete selected session file.
    - **Important**: This command just deletes session file. Hence, if session with this name is currently running in the TMUX - it will keep running until you will kill it, or save it again.

`tmux-sessions-manager.py` without parameters is equivalent to `tmux-sessions-manager.py open`. So, it will go into selection of session to open.

## Integration with ZSH (example)

I assigned key bindings in my `.zshrc` file:

```bash
bindkey -s '^gt' 'tmux-session-manager.py^M'
bindkey -s '^gr' 'tmux-session-manager.py restore^M'
bindkey -s '^gm' 'tmux-session-manager.py menu^M'
bindkey -s '^gs' 'tmux-session-manager.py save^M'
```

## Screenshot

![screenshot](screenshot.png)

## Why Python?

Initially I had a very simple shell script doing almost all job but by some reason I could not make it work with paths containing special characters like spaces, brackets, etc. E.g. shell script was not able to process path like one above: `~/Downloads/Project {1} - Test (1)`. I know, it is an extreme example, but I wanted my script being able to cope with any path.

I tried to write a wrapper in Python and it turned to be working quite well.

