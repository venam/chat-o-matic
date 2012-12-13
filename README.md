chat-o-matic
============

Very Simple python 2.x Chat with a simple salting for the logging system

[*]Dependencies:
    
    python2.x (any of the series)

    wxpython module (can be found on the repo of python main website)

    asyncore module if not found in the default library

[*]Concerning the Program:

    You need the server to be running before any user connects to it

    The Default password for the room is password

    You can easily generate a new password with the hashlib library:

    import hashlib

    hashlib.sha512("NEW_PASS_HERE").hexdigest()



[*]Wishlist:

    Encrypt the messages that the users send to the server

    Add a list-box with the user in the room

    Add multiple chat rooms

    Server act like an IRC bot and -block some users-do some special actions on certain commands

    Better connection handling

    Test on a real server



