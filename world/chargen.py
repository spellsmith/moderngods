"""
Chargen EvMenu module.

Goes in game/world/chargen.py

The menu node functions defined in this module make up
the Ainneve character creation process, which is based
on a subset of Open Adventure rules.
"""
from evennia import spawn, TICKER_HANDLER as tickerhandler
from evennia.utils import fill, dedent
from evennia.utils.evtable import EvTable
from evennia.contrib import gendersub

def menunode_chargen_welcome(caller):
    char = caller.new_char
    """Starting page and gender listing."""
    text = dedent("""\
        |wWelcome to |cModern Gods|w, an |yEvennia|w-based RP MUSH.|n

        You are currently creating character |m%s|n.

        Select a gender below by number, or type |whelp|n
        at any time for more info.
    """ % char.key)
    help = fill("The gender of a character determines which pronouns are "
                "used in certain styles of emotes.  It has no other effect "
                "on the character, and does not limit any commands, abilities, "
                "or descriptive options.  You can change your gender at "
		"any time with the |m@gender|n command.")
    options = (
        {"desc": "Male (he, him, his)",
         "exec": lambda caller: \
                 char.attributes.add("gender","male"),
         "goto": "menunode_chargen_gender_speed"},
        {"desc": "Female (she, her, hers)",
         "exec": lambda caller: \
                 char.attributes.add("gender","female"),
         "goto": "menunode_chargen_gender_speed"},
        {"desc": "Neutral (it, its)",
         "exec": lambda caller: \
                 char.attributes.add("gender","neutral"),
         "goto": "menunode_chargen_gender_speed"},
        {"desc": "Ambiguous (they, them, their, theirs)",
         "exec": lambda caller: \
                 char.attributes.add("gender","ambiguous"),
         "goto": "menunode_chargen_gender_speed"})
    return (text, help), options


def menunode_chargen_gender_speed(caller, raw_string):
    """Gender confirmation; set speed"""
    char = caller.new_char
    text = dedent("""\
        Your gender has been set to |y%s|n.  You can change this later
        using the |w@gender|n command in-game.
		
        Now set your default |wspeed|n.  This is the rate at which you
        move from one area to another.
    """) % char.attributes.get("gender")
    help = fill("Movement takes time.  Any time you travel from one area "
                "to another, there is a small delay to account for this. "
                "You can change this in-game at any time using |m@setspeed|n.")
    options = (
	    {"desc": "Stroll (slowest)",
         "exec": lambda caller: \
                 char.attributes.add("move_speed","stroll"),
         "goto": "menunode_chargen_speed_sdesc"},
         {"desc": "Walk",
          "exec": lambda caller: \
                  char.attributes.add("move_speed","walk"),
          "goto": "menunode_chargen_speed_sdesc"},
         {"desc": "Run",
          "exec": lambda caller: \
                  char.attributes.add("move_speed","run"),
          "goto": "menunode_chargen_speed_sdesc"},
         {"desc": "Sprint (fastest)",
          "exec": lambda caller: \
                  char.attributes.add("move_speed","sprint"),
          "goto": "menunode_chargen_speed_sdesc"})
    return (text, help), options

def menunode_chargen_speed_sdesc(caller):
    """Confirm speed, call sdesc"""
    text = dedent("""\
        Your default speed has been set to |y%s|n.  You can change this
        later using the |w@setspeed|n command in-game.
        
        Now set a |wshort description|n for yourself.  A short description
        is what your character looks like at a glance when someone
        first sees them or doesn't recognize them.  For example, if your 
        short description is |c'A young Chinese man'|n, then people who 
        enter the room will see |w'A young Chinese man is reading a book'|n.
    """) % caller.new_char.attributes.get("move_speed")
    help = fill("You can only have one short description at a time, which you can change "
                "with the |m@sdesc|n command.  You can also set longer, "
                "more detailed descriptions.  The next few steps will tell you how, "
                "and also introduce |wposes|n, |wmasking|n and |wrecognition|n.")
    options = (
	    {"key": ("_default"),
         "goto": "menunode_chargen_sdesc_pose"})
    return (text, help), options

def menunode_chargen_sdesc_pose(caller, raw_input):
    string_input = raw_input.strip()
    if not string_input:
        text = "You have chosen not to set a short description yet.\n"
        text += "If you change your mind later, type |mhelp @sdesc|n.\n"
        text += dedent("""
            A |wpose|n is a short phrase that describes what your character is doing
            at a glance when someone enters the room. For example, if your pose 
            reads '|cis nursing a drink at the bar|n'.  When someone enters the room, 
            they will see |w'A young Chinese man is nursing a drink at the bar'|n\n
            Please type a pose for your character.  You can change it later.
        """)
        help = fill("You can only have one pose at a time, which you can change "
                "with the |m@pose|n command.  A pose is similar to an emote, but "
                "more static: it is more a 'description' of what you are doing, "
                "instead of an 'action'."
                " "
                "A pose might be '|wis drinking at the bar|n' "
                "while an emote might be '|wemote chugs down the shot of tequila and "
                "slams the shot glass down|n'.")
        options = (
            {"key": "_default",
             "goto": "menunode_chargen_desc"})
    else:
        caller.new_char.sdesc.add(string_input)
        text = "Your short description has been set to:\n\n"
        text += "|y%s|n\n\n" % caller.new_char.sdesc.get()
        text += "You can change this later using the |m@sdesc|n command.\n\n"
        text += dedent("""
            A |wpose|n is a short phrase that describes what your character is doing
            at a glance when someone enters the room.  For example, if your pose
            reads '|cis nursing a drink at the bar|n'.  When someone enters the room, 
            they will see |w'A young Chinese man is nursing a drink at the bar'|n\n
            Please type a pose for your character.  You can change it later.
        """)
        help = fill("You can only have one pose at a time, which you can change "
                "with the |m@pose|n command.  A pose is similar to an emote, but "
                "more static: it is more a 'description' of what you are doing, "
                "instead of an 'action'."
                " "
                "A pose might be '|wis drinking at the bar|n' "
                "while an emote might be '|wemote chugs down the shot of tequila and "
                "slams the shot glass down|n'.")
        options = (
            {"key": "_default",
             "goto": "menunode_chargen_desc"})
    return (text, help), options

def menunode_chargen_desc(caller, raw_input):
    string_input = raw_input.strip()
    char = caller.new_char.sdesc.get() if hasattr(caller.new_char, "sdesc") else caller.new_char.key
    if not string_input:
        text = "You have chosen not to set a pose at this time. If you\n"
        text += "change your mind later, type |mhelp @pose|n.\n\n"
        text += "Enter a more detailed description of your character's appearance. This will be\n"
        text += "displayed when others look at your character explicitly."
        help = fill("After character creation, your character's long description can be modified "
                    "using the |m@desc|n command.")
        options = (
	        {"key": "_default",
             "goto": "menunode_chargen_desc_confirm"})
    elif len(char) + len(string_input) > 60:
        text = "Your pose is too long.  Please try again.\n\n"
        text += "The combined length of your short description\n"
        text += "and your pose cannot be more than 60 characters."
        help = fill("After character creation, your character's long description can be modified"
                    "using the |m@desc|n command.")
        options = (
	        {"key": "_default",
             "goto": "menunode_chargen_desc"})
    else:
        caller.new_char.attributes.add("pose",string_input)
        text = "Your pose will display as:\n\n"
        text += "|y%s %s|n\n\n" % (char, caller.new_char.attributes.get("pose"))
        text += "You can change this later using the |m@sdesc|n and |m@pose|n commands.\n\n"
        text += "Enter a more detailed description of your character's appearance. This will be\n"
        text += "displayed when others look at your character explicitly."
        help = fill("After character creation, your character's long description can be modified "
                "using the |m@desc|n command.")
        options = (
	        {"key": "_default",
             "goto": "menunode_chargen_desc_confirm"})
    return (text, help), options

def menunode_chargen_desc_confirm(caller, raw_input):
    string_input = raw_input.strip()
    if not string_input:
        text = "You have chosen not to set a long description at this time. "
        text += "If you change your mind later, type |mhelp @desc|n.\n\n"
        text += "Press |gC|n to continue."
        help = fill("The |wdesc|n commands can be confusing!  |y@sdesc|n sets your "
                    "short description at a glance.  |y@desc|n sets your longer, "
                    "more detailed description when people look at you directly.  "
                    "|y+desc|n is a different command that lets you store and use "
                    "multiple different descriptions for different situations -- "
                    "very useful for roleplayers!  Use |mhelp <command>|n after "
                    "creating your character, to see more about each one.")
        options = (
            {"key": "_default",
             "goto": "menunode_chargen_mask_recog"})
    else:
        caller.new_char.attributes.add("desc", string_input)
        text = dedent("""\
            When people |wlook|n at your character directly, they will see:\n\n|c%s|n
            \n\nYou can change this later with the |mdesc|n command.\n\nPress |gC|n to continue.
        """) % caller.new_char.attributes.get("desc")
        help = fill("The |wdesc|n commands can be confusing!  |y@sdesc|n sets your "
                    "short description at a glance.  |y@desc|n sets your longer, "
                    "more detailed description when people look at you directly.  "
                    "|y+desc|n is a different command that lets you store and use "
                    "multiple different descriptions for different situations -- "
                    "very useful for roleplayers!  Use |mhelp <command>|n after "
                    "creating your character, to see more about each one.")
        options = (
            {"key": "_default",
             "goto": "menunode_chargen_mask_recog"})
    return (text, help), options

def menunode_chargen_mask_recog(caller):
    """Explain Masking and Recognition"""
    text = dedent("""\
        The |y@recog|n command lets you 'recognize' someone and assign a name to
        their short description.  That is, you can 'recognize' that 'A young Chinese
        man' is 'Dr. Wang' and use that in future instances after you learn his name.\n  
        Sometimes, though, you don't want to be recognized.  You can use the |ymask|n
        command to set a temporary, different short description (see |whelp @sdesc|n)
        on yourself to 'hide' who you are, or masquerade as someone else.  Think of a
        Halloween costume as an example.  While you are masked, other people's |wrecog|n
        keyed to you, will no longer work until you |yunmask|n yourself.\n
        Enter any key to continue.
    """)
    help = fill("After you exit character generation, type |mhelp @recog|n or |mhelp @mask|n "
                "for more information on recognition and masking.")
    options = (
        {"key": "_default",
         "goto": "menunode_chargen_ic_ooc"})
    return (text, help), options

def menunode_chargen_ic_ooc(caller):
    """Explaining IC and OOC"""
    text = dedent("""\
        After you log in to your account, you must use the |y@ic <CharName>|n command to
        log in to a specific character.  'IC' stands for 'in character'.  You can use
        |y@ooc|n to drop back out to 'OOC' (out of character), and then switch to a
        different character.  There is also an |yooc|n command (without the @) which
        will send a message to the server-wide OOC chat channel.\n
        Enter any key to continue.
    """)
    help = fill("After you exit character generation, type |mhelp @ic|n or |mhelp @ooc|n "
                "for more information.")
    options = (
        {"key": "_default",
         "goto": "menunode_chargen_end"})
    return (text, help), options

def menunode_chargen_end(caller):
    """Farewell message."""
    caller.new_char.db.chargen_complete = True
    text = dedent("""
        Congratulations!  Your character creation is complete.  Have fun!
        \nType |mhelp getting started|n for some last-minute advice.
    """)
    return text, None
