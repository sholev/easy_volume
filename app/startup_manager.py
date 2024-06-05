"""
Manages start on login for an application by using the Windows registry.
"""

import os
import sys
import winreg


class StartupManager:
    def __init__(self, app_name, app_file):
        self.app_name = app_name
        self.user_path = winreg.HKEY_CURRENT_USER
        self.app_file = app_file
        self.registry_path = r'Software\Microsoft\Windows\CurrentVersion\Run'
        self.executable_path = self.get_executable_path()

    """
    Returns the path to the executable based on the current environment
    """
    def get_executable_path(self):
        if getattr(sys, 'frozen', False):  # It is compiled. AKA 'frozen'
            return sys.executable

        # Not compiled, run script with the current python environment
        executable = sys.executable.replace('python.exe', 'pythonw.exe')
        return f'"{executable}" {os.path.abspath(self.app_file)}"'

    """
    Checks if the self.app_name exists in the registry
    """
    def is_startup_enabled(self):
        key = winreg.OpenKey(
            self.user_path, self.registry_path, 0, winreg.KEY_READ
        )
        try:
            winreg.QueryValueEx(key, self.app_name)
            return True
        except FileNotFoundError:
            return False
        finally:
            key.Close()

    """
    Adds the self.app_name to the registry to start on login
    """
    def enable_startup(self):
        key = winreg.OpenKey(
            self.user_path, self.registry_path, 0, winreg.KEY_WRITE
        )
        winreg.SetValueEx(
            key, self.app_name, 0, winreg.REG_SZ, self.executable_path
        )
        key.Close()

    """
    Looks for the self.app_name in the registry and removes it if it exists
    """
    def disable_startup(self):
        key = winreg.OpenKey(
            self.user_path, self.registry_path, 0, winreg.KEY_WRITE
        )
        try:
            winreg.DeleteValue(key, self.app_name)
        except FileNotFoundError:
            pass
        key.Close()
