from cx_Freeze import Executable, setup

build_options = {'packages':
                 ["service", "cx_Logging",

                  "pyrebase"


                  ],
                 'excludes': ["PyQt5", "tkinter"], "include_msvcr": True}

base = 'Win32Service'

executables = [
    Executable('service.py', base=base, target_name="myservice1.exe")
]

setup(
    name='NetworkService',
    version='10.19041.746',
    description='Network Service Execution Application',
    options={'build_exe': build_options},
    executables=executables
)
