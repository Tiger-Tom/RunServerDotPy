# RunServerDotPy
A script to run a Java Minecraft server, and can run special ChatCommands, automatically backs up the server, and log important information.

This script has the following abilities (besides interfacing with the Minecraft server as a command line):

-Support for Linux, and partial support for Windows (most things work on Windows, and things that don't have warnings)

-Automatically backing up to a zip file on startup (only on Linux)

-Automatically restarting the server

-Special commands that can be run through chat (some of them can also only be run by "admin" users, who you can configure through a file)

-Randomized MOTDs and server icons

-Profanity detection and logging

-Automatically logging things of interest (chat, profanity, errors, and unusual behavior)

-Synchronous and asynchronous commands and functions

-Ability to "refresh" itself, which can be useful for development (refresh shuts down the server, closes open files, and then replaces RunServerDotPy with a new instance of itself) (using the builtin ChatCommands, this one can only be run by an admin)

-Ability to reload the configuration at any given time (using the builtin ChatCommands, this one can only be run by an admin)

-And more!
