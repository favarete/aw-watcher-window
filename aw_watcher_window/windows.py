import subprocess
from typing import Optional

import wmi
import win32gui
import win32process


c = wmi.WMI()

"""
Much of this derived from: http://stackoverflow.com/a/14973422/965332
More Documentation can be found here: https://docs.microsoft.com/en-us/windows/win32/cimwin32prov
"""


def get_app_pid(hwnd) -> Optional[str]:
    """Get application PID given hwnd."""
    _, pid = win32process.GetWindowThreadProcessId(hwnd)
    return pid


def get_app_description(hwnd) -> Optional[str]:
    """Get application description given hwnd."""
    description = None
    _, pid = win32process.GetWindowThreadProcessId(hwnd)
    for p in c.query('SELECT Description FROM Win32_Process WHERE ProcessId = %s' % str(pid)):
        description = p.Description
        break
    return description


def get_app_executable(hwnd) -> Optional[str]:
    """Get application executable given hwnd."""
    executable = None
    _, pid = win32process.GetWindowThreadProcessId(hwnd)
    for p in c.query('SELECT ExecutablePath FROM Win32_Process WHERE ProcessId = %s' % str(pid)):
        executable = p.ExecutablePath
        break
    return executable


def get_app_commandline(hwnd) -> Optional[str]:
    """Get application commandline given hwnd."""
    commandline = None
    _, pid = win32process.GetWindowThreadProcessId(hwnd)
    for p in c.query('SELECT CommandLine FROM Win32_Process WHERE ProcessId = %s' % str(pid)):
        commandline = p.CommandLine
        break
    return commandline


def get_app_version(hwnd) -> Optional[str]:
    """Get application version given hwnd."""
    version = None
    _, pid = win32process.GetWindowThreadProcessId(hwnd)
    for p in c.query('SELECT CreationDate FROM Win32_Process WHERE ProcessId = %s' % str(pid)):
        version = p.CreationDate
        break
    return version


def get_app_path(hwnd) -> Optional[str]:
    """Get application path given hwnd."""
    path = None
    _, pid = win32process.GetWindowThreadProcessId(hwnd)
    for p in c.query('SELECT ExecutablePath FROM Win32_Process WHERE ProcessId = %s' % str(pid)):
        path = p.ExecutablePath
        break
    return path


def get_username(hwnd) -> Optional[str]:
    """Get application username given hwnd."""
    username = None
    _, pid = win32process.GetWindowThreadProcessId(hwnd)
    for p in c.query('SELECT * FROM Win32_Process WHERE ProcessId = %s' % str(pid)):
        params = p.ExecMethod_('GetOwner')
        username = params.Properties_('User').Value
        break
    return username


def get_application_id(hwnd) -> Optional[str]:
    """Get application id given hwnd."""
    app_id = None
    _, pid = win32process.GetWindowThreadProcessId(hwnd)
    for p in c.query('SELECT * FROM Win32_Process WHERE ProcessId = %s' % str(pid)):
        app_id = p.Caption
        break
    return app_id


def get_app_name(hwnd) -> Optional[str]:
    """Get application filename given hwnd."""
    name = None
    _, pid = win32process.GetWindowThreadProcessId(hwnd)
    for p in c.query('SELECT Name FROM Win32_Process WHERE ProcessId = %s' % str(pid)):
        name = p.Name
        break
    return name


def get_env_vars(hwnd) -> Optional[str]:
    """Get application filename given hwnd."""
    _, pid = win32process.GetWindowThreadProcessId(hwnd)

    try:
        environment_variables = subprocess.check_output(['WindowsLocalVars.exe', str(pid)])
    except Exception as e:
        return e
    else:
        return environment_variables


def get_window_title(hwnd):
    return win32gui.GetWindowText(hwnd)


def get_active_window_handle():
    hwnd = win32gui.GetForegroundWindow()
    return hwnd


if __name__ == "__main__":
    hwnd = get_active_window_handle()
    print("App:", get_app_name(hwnd))
    print("Title:", get_window_title(hwnd))
    print("Application ID:", get_application_id(hwnd))
    print("Pid:", get_app_pid(hwnd))
    print("User:", get_username(hwnd))
    print("Process Description:", get_app_description(hwnd))
    print("Executable:", get_app_executable(hwnd))
    print("CommandLine:", get_app_commandline(hwnd))
    print("Version:", get_app_version(hwnd))
    print("Environment:", get_env_vars(hwnd))
