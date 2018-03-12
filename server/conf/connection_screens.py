# -*- coding: utf-8 -*-
"""
Connection screen

Texts in this module will be shown to the user at login-time.

Evennia will look at global string variables (variables defined
at the "outermost" scope of this module and use it as the
connection screen. If there are more than one, Evennia will
randomize which one it displays.

The commands available to the user when the connection screen is shown
are defined in commands.default_cmdsets. UnloggedinCmdSet and the
screen is read and displayed by the unlogged-in "look" command.

"""

from django.conf import settings
from evennia import utils

CONNECTION_SCREEN = """
|b==============================================================|n
 Welcome to |c{}|n!

|wAlton, Massachusetts:|n  a city that doesn't exist, populated by 
immortals who can either save the world or destroy it. Power games
and misdirection as secret societies vye for control of our mundane
world, or -- in theory -- work together to keep damnation at bay.

|cModern Gods|n is an experimental urban supernatural roleplay MUD, 
inspired by the stories of the |wCerberus Solutions|n roleplay group 
and various real world, literary, and original influences, including:

- |rCabbalistics, Inc.|n (Rebellion/2000AD)
- |rHellgate: London|n (Flagship Studios)
- |rThe Secret World|n & |rSecret World Legends|n (Funcom)
- |rResident Evil|n (Capcom)
- |rThe Dresden Files|n (Jim Butcher)
- |rBuffy the Vampire Slayer|n (Joss Whedon)

|b==============================================================|n""" \
    .format(settings.SERVERNAME, utils.get_evennia_version())
