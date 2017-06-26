# BackdoorLnkMacroStager

A custom stager that generates an office macro, which when ran will backdoor .lnk files on the user's desktop with a powershell stub that in turn calls launcher code stored in the registry at an operator-defined location.

NOTE:  This is a very early iteration of this tool and is for testing purposes only, as such it has been hardcoded with several default .lnk files it will attempt to modify (iexplore.lnk on the user's desktop and Internet Explorer.lnk in the user's Quicklaunch Taskbar)

Usage:  Drop backdoorLnkMacro.py into *rootEmpireFolder*/lib/stagers/windows and start empire, the stager should now show up in your stagers list (usestager windows/backdoorLnkMacro.py)
