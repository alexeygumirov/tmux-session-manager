#!/bin/python3

"""
MIT License

Copyright (c) 2022 Alexey Gumirov

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import os
import subprocess
import sys
from datetime import datetime


def check_if_program_exists(program_name: str) -> bool:
    """
    Function checks if program is installed in the system.
    Args:
        program_name (str): Name of the program to check.
    Returns:
        True if program exists, False if not.
    """

    cmd = ["which", program_name]
    result = subprocess.call(cmd, stdout=subprocess.DEVNULL)
    if result == 0:
        return True
    else:
        return False


def get_session_params(file_path: str) -> list:
    """
    This function extracts session parameters from the file.
    Args:
        file_path (str): Path to the file with session parameters.
    Returns:
        session_params (list): List with session parameters.
    """

    session_params = []

    with open(os.path.expanduser(file_path), "r") as f:
        counter = 1
        for line in f:
            if line[0] != "#" and line.strip():
                window_name = line.split("=", 1)[0].strip().strip("\n")
                window_path = line.split("=", 1)[1].strip().strip("\n")
                session_params.append([str(counter), window_name, window_path])
                counter += 1

    return session_params


def make_new_session(session_name: str, session_params: list) -> str:
    """
    This function creates a new TMUX session based on the given parameters.
    Args:
        session_name (str): Name of the session to create.
        session_params (list): List with session parameters.
    Returns:
        result (str): Result of the command execution.
    """

    cmd = ["tmux", "new", "-d", "-s", session_name]
    result = str(subprocess.call(cmd))

    if session_params:
        for session in session_params:
            if session[1] and session[2]:
                cmd = [
                    "tmux",
                    "new-window",
                    "-k",
                    "-d",
                    "-c",
                    os.path.expanduser(session[2]),
                    "-n",
                    session[1],
                    "-t",
                    session_name + ":" + session[0],
                ]
            if session[1] and not session[2]:
                cmd = [
                    "tmux",
                    "new-window",
                    "-k",
                    "-d",
                    "-n",
                    session[1],
                    "-t",
                    session_name + ":" + session[0],
                ]
            if not session[1] and session[2]:
                cmd = [
                    "tmux",
                    "new-window",
                    "-k",
                    "-d",
                    "-c",
                    os.path.expanduser(session[2]),
                    "-t",
                    session_name + ":" + session[0],
                ]
            if not session[1] and not session[2]:
                cmd = [
                    "tmux",
                    "new-window",
                    "-k",
                    "-d",
                    "-t",
                    session_name + ":" + session[0],
                ]
            result = str(subprocess.call(cmd))

    return result


def get_session(
    fzf_header: str, config_path: str = "~/.config/tmux-project-sessions"
) -> str:
    """
    Lists all available sessions in the folder and allows to select one of them.
    Args:
        fzf_header (str): Header for FZF window.
        config_path (str): Path to the folder with session files.
    Returns:
        session_name (str): Name of the selected session.
    """

    session_name = ""
    ls_cmd = ["/usr/bin/ls", "-1", os.path.expanduser(config_path)]
    fzf_cmd = [
        "fzf",
        '--header="' + fzf_header + '"',
        "--border",
        "--height",
        "20%",
        "--reverse",
        "--cycle",
        "--no-multi",
    ]
    try:
        with subprocess.Popen(ls_cmd, stdout=subprocess.PIPE) as ls_process:
            session_name = (
                subprocess.check_output(fzf_cmd, stdin=ls_process.stdout)
                .decode("utf-8")
                .strip("\n")
            )
    except Exception:
        session_name = ""

    return session_name


def get_action() -> str:
    """
    Calls FZF and selects action to do first.
    Returns:
        action (str): Selected action.
    """
    action = ""
    actions_list = "Open\nRestore\nSave\nDelete"
    echo_cmd = ["echo", actions_list]
    try:
        with subprocess.Popen(echo_cmd, stdout=subprocess.PIPE) as echo_process:
            action = (
                subprocess.check_output(
                    [
                        "fzf",
                        '--header="Select action:"',
                        "--border",
                        "--height",
                        "20%",
                        "--reverse",
                        "--no-multi",
                    ],
                    stdin=echo_process.stdout,
                )
                .decode("utf-8")
                .strip("\n")
            )
    except Exception:
        action = ""

    return action


def tmux_session_detection(session_name: str) -> bool:
    """
    Function checks if session already exists.
    Args:
        session_name (str): Name of the session to check.
    Returns:
        True if session exists, False if not.
    """

    cmd = ["tmux", "list-sessions", "-F", "#S"]
    try:
        result = (
            subprocess.check_output(cmd, stderr=subprocess.DEVNULL)
            .decode("utf-8")
            .split("\n")
        )
        if session_name in result:
            return True
        else:
            return False
    except Exception:
        return False


def tmux_session_restore(session_name: str, session_params: list):
    """
    Restores current active session.
    Args:
        session_name (str): Name of the session to restore.
        session_params (list): List with session parameters.
    Returns:
        result (str): Result of the command execution.
    """

    cmd = ["tmux", "rename-session", session_name + "-old"]
    result = subprocess.call(cmd)
    make_new_session(session_name, session_params)
    cmd = ["tmux", "switch-client", "-t", session_name]
    result = subprocess.call(cmd)
    cmd = ["tmux", "kill-session", "-t", session_name + "-old"]
    result = subprocess.call(cmd)

    return result


def is_inside_session() -> bool:
    """
    Detect if currently is inside session.
    Returns:
        True if inside session, False if not.
    """

    try:
        os.environ["TMUX"]
        return True
    except Exception:
        return False


def get_current_session_name() -> str:
    """
    Get name of the TMUX session we are in.
    Returns:
        session_name (str): Name of the current session.
    """

    if is_inside_session():
        cmd = ["tmux", "display-message", "-p", "#S"]
        result = (
            subprocess.check_output(cmd, stderr=subprocess.DEVNULL)
            .decode("utf-8")
            .rstrip()
        )
        return result
    else:
        return ""


def save_session_to_file(config_path: str) -> None:
    """
    Function to save current TMUX session into the session file.
    Args:
        config_path (str): Path to the folder with session files.
    """

    if not is_inside_session():
        sys.exit("Cannot save, you are not inside TMUX session.")

    session_name_raw = get_current_session_name()
    window_list: list[str] = []
    cmd = ["tmux", "list-windows", "-F", "#I==#W==#{pane_current_path}"]
    output = (
        subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode("utf-8").rstrip()
    )
    for window in output.split("\n"):
        window_list.append(str(window.split("==")))

    session_name = ""
    for char in session_name_raw:
        if char == " " or char == "-":
            session_name += "-"
        elif char.isalnum():
            session_name += char

    file_name = datetime.now().strftime("%Y-%m-%d_%H-%M-%S_") + session_name
    with open(os.path.expanduser(config_path + "/" + file_name), "w") as f:
        f.write(f"# Session parameters for session: {session_name}\n")
        f.write("\n")
        for window in window_list:
            if window[1] in ["zsh", "bash", "fish"]:
                f.write(f" = {window[2]}\n")
            else:
                f.write(f"{window[1]} = {window[2]}\n")

    print(f"\nCurrent Tmux session was saved in the file:\n{file_name}\n")


def delete_session(config_path: str, file_name: str) -> None:
    """
    Deletes selected session file.
    Args:
        config_path (str): Path to the folder with session files.
        file_name (str): Name of the session file to delete.
    """

    os.remove(os.path.expanduser(config_path + "/" + file_name))
    print(f"\n Tmux session file `{file_name}` was removed.\n")


def main():
    """
    Main function which creates, switches or restores sessions
    """

    config_path = "~/.config/tmux-project-sessions"
    result = ""

    if not check_if_program_exists("tmux"):
        sys.exit("Error: Tmux is not installed.")

    if not check_if_program_exists("fzf"):
        sys.exit("Error: FZF is not installed.")

    # action = get_action()
    # if not action:
    #     sys.exit()

    action = ""
    if len((sys.argv)) == 1:
        action = "Open"
    elif len((sys.argv)) > 1:
        mode = str(sys.argv[1])
        if mode == "menu":
            action = get_action()
        if mode == "open":
            action = "Open"
        if mode == "restore":
            action = "Restore"
        if mode == "save":
            action = "Save"
        if mode == "delete":
            action = "Delete"

    if action == "Open":
        session_name = get_session("Open session:", config_path)
        if not session_name:
            sys.exit()

        if tmux_session_detection(session_name):
            if not is_inside_session():
                cmd = ["tmux", "attach", "-d", "-t", session_name]
                result = subprocess.call(cmd)
            else:
                if session_name != get_current_session_name():
                    cmd = ["tmux", "detach-client", "-s", session_name]
                    result = subprocess.call(cmd)
                    cmd = ["tmux", "switch-client", "-t", session_name]
                    result = subprocess.call(cmd)
                else:
                    sys.exit()
        else:
            session_params = get_session_params(config_path + "/" + session_name)
            make_new_session(session_name, session_params)
            if not is_inside_session():
                cmd = ["tmux", "attach", "-d", "-t", session_name]
                result = subprocess.call(cmd)
            else:
                cmd = ["tmux", "switch-client", "-t", session_name]
                result = subprocess.call(cmd)

    if action == "Restore":
        session_name = get_session("Repair session:", config_path)
        if session_name:
            session_params = get_session_params(config_path + "/" + session_name)
            tmux_session_restore(session_name, session_params)
        else:
            sys.exit("No session was selected.")

    if action == "Save":
        save_session_to_file(config_path)

    if action == "Delete":
        session_name = get_session("Delete session:", config_path)
        if not session_name:
            sys.exit()
        else:
            delete_session(config_path, session_name)

    else:
        sys.exit()

    return result


if __name__ == "__main__":
    main()
