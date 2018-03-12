"""
Account

The Account represents the game "account" and each login has only one
Account object. An Account is what chats on default channels but has no
other in-game-world existence. Rather the Account puppets Objects (such
as Characters) in order to actually participate in the game world.


Guest

Guest accounts are simple low-level accounts that are created/deleted
on the fly and allows users to test the game without the commitment
of a full registration. Guest accounts are deactivated by default; to
activate them, add the following line to your settings file:

    GUEST_ENABLED = True

You will also need to modify the connection screen to reflect the
possibility to connect with a guest account. The setting file accepts
several more options for customizing the Guest account system.

"""

from evennia import DefaultAccount, DefaultGuest
import time
from django.conf import settings
from django.utils import timezone
from evennia.typeclasses.models import TypeclassBase
from evennia.accounts.manager import AccountManager
from evennia.accounts.models import AccountDB
from evennia.objects.models import ObjectDB
from evennia.comms.models import ChannelDB
from evennia.commands import cmdhandler
from evennia.utils import logger
from evennia.utils.utils import (lazy_property, to_str,
                                 make_iter, to_unicode, is_iter,
                                 variable_from_module)
from evennia.typeclasses.attributes import NickHandler
from evennia.scripts.scripthandler import ScriptHandler
from evennia.commands.cmdsethandler import CmdSetHandler

from django.utils.translation import ugettext as _
from future.utils import with_metaclass

__all__ = ("DefaultAccount",)

_SESSIONS = None

_AT_SEARCH_RESULT = variable_from_module(*settings.SEARCH_AT_RESULT.rsplit('.', 1))
_MULTISESSION_MODE = settings.MULTISESSION_MODE
_MAX_NR_CHARACTERS = settings.MAX_NR_CHARACTERS
_CMDSET_ACCOUNT = settings.CMDSET_ACCOUNT
_CONNECT_CHANNEL = None


class Account(DefaultAccount):
    """
    This class describes the actual OOC account (i.e. the user connecting
    to the MUD). It does NOT have visual appearance in the game world (that
    is handled by the character which is connected to this). Comm channels
    are attended/joined using this object.

    It can be useful e.g. for storing configuration options for your game, but
    should generally not hold any character-related info (that's best handled
    on the character level).

    Can be set using BASE_ACCOUNT_TYPECLASS.


    * available properties

     key (string) - name of account
     name (string)- wrapper for user.username
     aliases (list of strings) - aliases to the object. Will be saved to database as AliasDB entries but returned as strings.
     dbref (int, read-only) - unique #id-number. Also "id" can be used.
     date_created (string) - time stamp of object creation
     permissions (list of strings) - list of permission strings

     user (User, read-only) - django User authorization object
     obj (Object) - game object controlled by account. 'character' can also be used.
     sessions (list of Sessions) - sessions connected to this account
     is_superuser (bool, read-only) - if the connected user is a superuser

    * Handlers

     locks - lock-handler: use locks.add() to add new lock strings
     db - attribute-handler: store/retrieve database attributes on this self.db.myattr=val, val=self.db.myattr
     ndb - non-persistent attribute handler: same as db but does not create a database entry when storing data
     scripts - script-handler. Add new scripts to object with scripts.add()
     cmdset - cmdset-handler. Use cmdset.add() to add new cmdsets to object
     nicks - nick-handler. New nicks with nicks.add().

    * Helper methods

     msg(text=None, **kwargs)
     swap_character(new_character, delete_old_character=False)
     execute_cmd(raw_string, session=None)
     search(ostring, global_search=False, attribute_name=None, use_nicks=False, location=None, ignore_errors=False, account=False)
     is_typeclass(typeclass, exact=False)
     swap_typeclass(new_typeclass, clean_attributes=False, no_default=True)
     access(accessing_obj, access_type='read', default=False)
     check_permstring(permstring)

    * Hook methods (when re-implementation, remember methods need to have self as first arg)

     basetype_setup()
     at_account_creation()

     - note that the following hooks are also found on Objects and are
       usually handled on the character level:

     at_init()
     at_cmdset_get(**kwargs)
     at_first_login()
     at_post_login(session=None)
     at_disconnect()
     at_message_receive()
     at_message_send()
     at_server_reload()
     at_server_shutdown()

    """
    def at_look(self, target=None, session=None, **kwargs):
        """
        Called when this object executes a look. It allows to customize
        just what this means.
        Args:
            target (Object or list, optional): An object or a list
                objects to inspect.
            session (Session, optional): The session doing this look.
            **kwargs (dict): Arbitrary, optional arguments for users
                overriding the call (unused by default).
        Returns:
            look_string (str): A prepared look string, ready to send
                off to any recipient (usually to ourselves)
        """

        if target and not is_iter(target):
            # single target - just show it
            return target.return_appearance(self)
        else:
            # list of targets - make list to disconnect from db
            characters = list(tar for tar in target if tar) if target else []
            sessions = self.sessions.all()
            is_su = self.is_superuser

            # text shown when looking in the ooc area
            result = ["|wWelcome, |g%s|n|w! (You are Out-of-Character)|n" % self.key]

            nsess = len(sessions)
            result.append(nsess == 1 and "\n\n|CConnected session:|n" or "\n\n|cConnected sessions (%i):|n" % nsess)
            for isess, sess in enumerate(sessions):
                csessid = sess.sessid
                addr = "%s (%s)" % (sess.protocol_key, isinstance(sess.address, tuple) and
                                    str(sess.address[0]) or str(sess.address))
                result.append("\n %s %s" % (session.sessid == csessid and "|w* %s|n" % (isess + 1) or
                                            "  %s" % (isess + 1), addr))
            result.append("\n\n|CAvailable commands:")
            result.append("\n |whelp|n - Show more commands")

            charmax = _MAX_NR_CHARACTERS if _MULTISESSION_MODE > 1 else 1

            if is_su or len(characters) < charmax:
                if not characters:
                    result.append("\n\n You don't have any characters yet. See |whelp @charcreate|n to create one.")
                else:
                    result.append("\n |w@charcreate <name>|n - Create a new character")
                    result.append("\n |w@chardelete <name>|n - Delete a character (cannot be undone!)")

            result.append("\n |wooc <message>|n - Talk to the OOC public chat channel")
            if characters:
                string_s_ending = len(characters) > 1 and "s" or ""
                result.append("\n |w@ic <character>|n - Enter the game as a character (use |w@ooc|n to get back here)")

                if is_su:
                    result.append("\n\n|CAvailable character%s|n (%i/unlimited):" % (string_s_ending, len(characters)))
                else:
                    result.append("\n\n|CAvailable character%s%s:|n"
                                  % (string_s_ending, charmax > 1 and " (%i/%i)" % (len(characters), charmax) or ""))

                for char in characters:
                    csessions = char.sessions.all()
                    if csessions:
                        for sess in csessions:
                            # character is already puppeted
                            sid = sess in sessions and sessions.index(sess) + 1
                            if sess and sid:
                                result.append("\n - |G%s|n [%s] (played by you in session %i)"
                                              % (char.key, ", ".join(char.permissions.all()), sid))
                            else:
                                result.append("\n - |R%s|n [%s] (played by someone else)"
                                              % (char.key, ", ".join(char.permissions.all())))
                    else:
                        # character is "free to puppet"
                        result.append("\n - %s [%s]" % (char.key, ", ".join(char.permissions.all())))
            look_string = ("-" * 68) + "\n" + "".join(result) + "\n" + ("-" * 68)
            return look_string

    pass


class Guest(DefaultGuest):
    """
    This class is used for guest logins. Unlike Accounts, Guests and their
    characters are deleted after disconnection.
    """
    pass
