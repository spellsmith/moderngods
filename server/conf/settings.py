"""
Evennia settings file.

The available options are found in the default settings file found
here:

/home/pi/moderngods/evennia/evennia/settings_default.py

Remember:

Don't copy more from the default file than you actually intend to
change; this will make sure that you don't overload upstream updates
unnecessarily.

When changing a setting requiring a file system path (like
path/to/actual/file.py), use GAME_DIR and EVENNIA_DIR to reference
your game folder and the Evennia library folders respectively. Python
paths (path.to.module) should be given relative to the game's root
folder (typeclasses.foo) whereas paths within the Evennia library
needs to be given explicitly (evennia.foo).

If you want to share your game dir, including its settings, you can
put secret game- or server-specific settings in secret_settings.py.

"""

# Use the defaults from Evennia unless explicitly overridden
from evennia.settings_default import *

######################################################################
# Evennia base server config
######################################################################

# This is the name of your game. Make it catchy!
SERVERNAME = "Modern Gods"

# Server ports. If enabled and marked as "visible", the port
# should be visible to the outside world on a production server.
# Note that there are many more options available beyond these.

# Telnet ports. Visible.
TELNET_ENABLED = True
TELNET_PORTS = [4000]
# (proxy, internal). Only proxy should be visible.
WEBSERVER_ENABLED = True
WEBSERVER_PORTS = [(4001, 4002)]
# Telnet+SSL ports, for supporting clients. Visible.
SSL_ENABLED = False
SSL_PORTS = [4003]
# SSH client ports. Requires crypto lib. Visible.
SSH_ENABLED = False
SSH_PORTS = [4004]
# Websocket-client port. Visible.
WEBSOCKET_CLIENT_ENABLED = True
WEBSOCKET_CLIENT_PORT = 4005
# Internal Server-Portal port. Not visible.
AMP_PORT = 4006


# This is a security setting protecting against host poisoning
# attacks.
ALLOWED_HOSTS = ["*"]

# Idle timeout for users (in seconds).
# 600 = 10 min; 900 = 15 min; 1800 = 30 min.
# Set to <=0 to deactive the idle time out completely.
IDLE_TIMEOUT = 900

# Maximum length of string to be sent to the server.
MAX_CHAR_LIMIT = 1200

# The 'too long' warning text.
MAX_CHAR_LIMIT_WARNING = "Your text was too long.  Please limit your input to 1200 characters or less."

# In-Game errors.  Turn off for production.
IN_GAME_ERRORS = True

# Default start location.  #2 is Limbo.
START_LOCATION = "#2"

# Time flow factor.  Higher is faster. '1' is real-world.
TIME_FACTOR = 1.0

# Starting point of game-time in UNIX epoch.
# 0 is Jan 1 1979
TIME_GAME_EPOCH = 1517838400

# Multisession mode
MULTISESSION_MODE = 2

# Max number of characters per account.
MAX_NR_CHARACTERS = 4

# Log in with friendly menu
CMDSET_UNLOGGEDIN = "contrib.menu_login.UnloggedinCmdSet"


# Web Admins
ADMINS = [('Spellsmith','spellsmithtsw@gmail.com')]


# Default Channels
DEFAULT_CHANNELS = [
    # public channel
    {"key": "OOC",
     "aliases": "",
     "desc": "Game-Wide OOC discussion",
     "locks": "control:perm(Admin);listen:all();send:all()"},
    # connection/mud info
    {"key": "MudInfo",
     "aliases": "",
     "desc": "Connection log",
     "locks": "control:perm(Developer);listen:perm(Admin);send:false()"}
]

# Default commands override for game/commands/command.py
COMMAND_DEFAULT_CLASS = "commands.command.MuxCommand"


######################################################################
# Settings given in secret_settings.py override those in this file.
######################################################################
try:
    from server.conf.secret_settings import *
except ImportError:
    print "secret_settings.py file not found or failed to import."
