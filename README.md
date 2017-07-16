# BackdoorLnkMacroStager

This is a two-step attack vector, the initial macro that a user runs will configure a shortcut on their desktop to run powershell.  The second step occurs when the user clicks on the shortcut, the powershell download stub that runs will attempt to download & execute empire launcher code from an xml file hosted at a pre-defined location, which will in turn give you a shell back.  This is done to defeat application-aware security measures that flag on launches of powershell from unexpected programs, such as a direct launch from office applications.  As the macro is pure vba and does not leverage powershell it is less likely to be detected by these types of tools.

NOTE:  This is a very early iteration of this tool and is for testing purposes only, as such it has been hardcoded with several default .lnk files it will attempt to modify (iexplore.lnk on the user's desktop and Internet Explorer.lnk in the user's Quicklaunch Taskbar)

Usage:  Drop backdoorLnkMacro.py into *rootEmpireFolder*/lib/stagers/windows and start empire, the stager should now show up in your stagers list (usestager windows/backdoorLnkMacro.py)  
		Upon execution of the stager a macro file and an xml file will be generated, ensure the xml is located on the webserver configured during setup of the stager and that this is a location accessible on the remote system.
