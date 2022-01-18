#!/bin/python3

import os
import subprocess
import sys
from datetime import datetime


def check_if_program_exists(program_name: str) -> bool:
    """
        Function checks if program is installed in the system.
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
    """

    session_params = []

    with open(os.path.expanduser(file_path), 'r') as f:
        counter = 1
        for line in f:
            if line[0] != '#' and line.strip():
                window_name = line.split('=', 1)[0].strip().strip('\n')
                window_path = line.split('=', 1)[1].strip().strip('\n')
                session_params.append([str(counter), window_name, window_path])
                counter += 1

    return session_params


def make_new_session(session_name: str, session_params: list) -> str:
    """
    This function creates new TMUX session based on given parameters
    """

    cmd = ['tmux', 'new', '-d', '-s', session_name]
    result = subprocess.call(cmd)

    if session_params:
        for session in session_params:
            if session[1] and session[2]:
                cmd = ['tmux', 'new-window', '-k', '-d', '-c', os.path.expanduser(session[2]), '-n', session[1], '-t', session_name + ':' + session[0]]
            if session[1] and not session[2]:
                cmd = ['tmux', 'new-window', '-k', '-d', '-n', session[1], '-t', session_name + ':' + session[0]]
            if not session[1] and session[2]:
                cmd = ['tmux', 'new-window', '-k', '-d', '-c', os.path.expanduser(session[2]), '-t', session_name + ':' + session[0]]
            if not session[1] and not session[2]:
                cmd = ['tmux', 'new-window', '-k', '-d', '-t', session_name + ':' + session[0]]
            result = subprocess.call(cmd)

    return result


def get_session(fzf_header: str, config_path: str = '~/.config/tmux-project-sessions') -> str:
    """
    Lists all available sessions in the folder and allows to select one of them.
    Returns session name.
    """

    session_name = ""
    cmd = ['/usr/bin/ls', '-1', os.path.expanduser(config_path)]
    ls_process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    try:
        session_name = subprocess.check_output(['fzf', '--header="' + fzf_header + '"', '--border', '--height', '20%', '--reverse', '--cycle', '--no-multi'],
                                                stdin=ls_process.stdout).decode('utf-8').strip('\n')
    except Exception:
        session_name = ""

    return session_name


def get_action() -> str:
    """
        Calls FZF and selects action to do first.
    """
    action = ""
    actions_list = "Open\nRestore\nSave\nDelete"
    cmd = ['echo', actions_list]
    ls_process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    try:
        action = subprocess.check_output(['fzf', '--header="Select action:"', '--border', '--height', '20%', '--reverse', '--no-multi'],
                                                stdin=ls_process.stdout).decode('utf-8').strip('\n')
    except Exception:
        action = ""

    return action


def tmux_session_detection(session_name: str) -> bool:
    """
        Function checks if session already exists.
    """

    cmd = ['tmux', 'has-session', '-t', session_name]
    result = subprocess.call(cmd, stderr=subprocess.DEVNULL)
    if result == 0:
        return True
    else:
        return False


def tmux_session_restore(session_name: str, session_params: list):
    """
        Restores current active session.
    """

    cmd = ['tmux', 'rename-session', session_name + '-old']
    result = subprocess.call(cmd)
    make_new_session(session_name, session_params)
    cmd = ['tmux', 'switch-client', '-t', session_name]
    result = subprocess.call(cmd)
    cmd = ['tmux', 'kill-session', '-t', session_name + '-old']
    result = subprocess.call(cmd)

    return result


def is_inside_session() -> bool:
    """
        Detect if currently is inside session.
    """

    try:
        os.environ['TMUX']
        return True
    except Exception:
        return False


def get_current_session_name() -> str:
    """
        Get name of the TMUX session we are in.
    """

    if is_inside_session():
        cmd = ['tmux', 'display-message', '-p', '#S']
        result = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode('utf-8').rstrip()
        return result
    else:
        return ""


def save_session_to_file(config_path: str) -> None:
    """
        Function to save current TMUX session into the session file.
    """

    if not is_inside_session():
        sys.exit("Cannot save, you are not inside TMUX session.")

    session_name_raw = get_current_session_name()
    window_list = []
    cmd = ['tmux', 'list-windows', '-F', '#I==#W==#{pane_current_path}']
    output = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode('utf-8').rstrip()
    for window in output.split('\n'):
        window_list.append(window.split('=='))

    session_name = ""
    for char in session_name_raw:
        if char == ' ' or char == '-':
            session_name += '-'
        elif char.isalnum():
            session_name += char

    file_name = datetime.now().strftime("%Y-%m-%d_%H-%M-%S_") + session_name
    with open(os.path.expanduser(config_path + '/' + file_name), 'w') as f:
        f.write(f"# Session parameters for session: {session_name}\n")
        f.write("\n")
        for window in window_list:
            if window[1] in ['zsh', 'bash', 'fish']:
                f.write(f" = {window[2]}\n")
            else:
                f.write(f"{window[1]} = {window[2]}\n")

    print(f"\nCurrent Tmux session was saved in the file:\n{file_name}\n")


def delete_session(config_path: str, file_name: str) -> None:
    """
        Deletes selected session file.
    """

    os.remove(os.path.expanduser(config_path + '/' + file_name))
    print(f"\n Tmux session file `{file_name}` was removed.\n")




def main():
    """
    Main function which creates, switches or restores sessions
    """

    config_path = '~/.config/tmux-project-sessions'
    result = ""

    if not check_if_program_exists('tmux'):
        sys.exit('Error: Tmux is not installed.')

    if not check_if_program_exists('fzf'):
        sys.exit('Error: FZF is not installed.')

    # action = get_action()
    # if not action:
    #     sys.exit()

    action = ""
    if len((sys.argv)) == 1:
        action = "Open"
    elif len((sys.argv)) > 1:
        mode = str(sys.argv[1])
        if mode == 'menu':
            action = get_action()
        if mode == 'open':
            action = "Open"
        if mode == 'restore':
            action = "Restore"
        if mode == 'save':
            action = "Save"
        if mode == 'delete':
            action = "Delete"

    if action == 'Open':
        session_name = get_session("Open session:", config_path)
        if not session_name:
            sys.exit()

        if tmux_session_detection(session_name):
            if not is_inside_session():
                cmd = ['tmux', 'attach', '-d', '-t', session_name]
                result = subprocess.call(cmd)
            else:
                print(session_name)

                if session_name != get_current_session_name():
                    cmd = ['tmux', 'detach-client', '-s', session_name]
                    result = subprocess.call(cmd)
                    cmd = ['tmux', 'switch-client', '-t', session_name]
                    result = subprocess.call(cmd)
                else:
                    sys.exit()
        else:
            session_params = get_session_params(config_path + '/' + session_name)
            make_new_session(session_name, session_params)
            if not is_inside_session():
                cmd = ['tmux', 'attach', '-d', '-t', session_name]
                result = subprocess.call(cmd)
            else:
                cmd = ['tmux', 'switch-client', '-t', session_name]
                result = subprocess.call(cmd)

    if action == 'Restore':
        session_name = get_session("Repair session:", config_path)
        if session_name:
            session_params = get_session_params(config_path + '/' + session_name)
            tmux_session_restore(session_name, session_params)
        else:
            sys.exit("No session was selected.")

    if action == 'Save':
        save_session_to_file(config_path)

    if action == 'Delete':
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
