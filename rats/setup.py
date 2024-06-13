from cx_Freeze import setup, Executable

build_options = {'packages':
                 [

                     "shutil",
                     "subprocess",
                     "winreg",
                     "pyuac",
                     "os",
                     "pymongo",
                     "time"
                 ],
                 'excludes': ["PyQt5", "tkinter"], "include_msvcr": True}

base = 'Win32GUI'

executables = [
    Executable('installer.py', base=base, target_name="NetworkAgent.exe"),
]

setup(
    name='NetworkAgent',
    version='7.8.19041.1',
    description='NetworkAgent',
    options={'build_exe': build_options},
    executables=executables
)
