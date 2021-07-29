# RunServerDotPy
A script to run a Java Minecraft server, and can run special ChatCommands, automatically backs up the server, and log important information.

> Incredible-best program I have ever used. 11/10 ⋆. _Note: I was paid to write this review_ - @Tiger-Tom 

This script has the following features (besides interfacing with the Minecraft server as a command line):

-Support for Linux, and partial support for Windows (most things work on Windows, and things that don't are either disabled or have warnings)

-Automatically backing up to a zip file every time the server starts (only on Linux)

-Automatically restarting the server if it stops or crashes for whatever reason

-Special commands that can be run through chat (some of them can also only be run by "admin" users, who you can configure through a file)

-Randomized MOTDs and server icons

-Profanity detection and logging

-Automatically logging things of interest (chat, profanity, errors, and unusual behavior)

-Synchronous and asynchronous commands and functions

-Ability to "refresh" itself, which can be useful for development (refresh shuts down the server, closes open files, and then replaces RunServerDotPy with a new instance of itself) (done using the builtin ChatCommands, although this one can only be run by an admin)

-Ability to reload the configuration at any given time (done using the builtin ChatCommands, although his one can only be run by an admin)

-And more!

Fun fact: the original RunServer.py script that I made was around 825 lines, and my goal for the new version (this one) was to make it more efficient, but I still ended up with more lines (hopefully the extra lines are just because of better commenting, better spacing, and more features being added)
