From QOL 3.1 to release 4.0:

Additions:
- Major:
  - Added a wiki (https://github.com/Tiger-Tom/RunServerDotPy/wiki)
  - Added mod reloader command
  - Added commands to display links to go to RS.PY's Github page and Wiki
  - Added a web interface. This interface shows everything that is outputted to users, as well as the results of any ChatCommands that it uses

- Minor:
  - Added protections for "speedtest" command failing
  - TPS test command now actually shows something when it can't be run due to being ran to recently, before it just did nothing

Changes:
- Major:
  - ChatCommands are "selected" in a different way - using the new "case-match" system in Python 3.10
  - A lot of ChatCommands were also rewritten and maybe optimized
  - ~~Cleaned up modloader function a bit~~ Completely overhauled the modloading system
  - Modding can now have custom runtimes - functions that run at certain times. Current times are firstStart, everyStart, lastStop, and everyStop
  - Help text version checker now fingerprints both the current version and the (potentially newer) online version and compares them, instead of relying on cached help version data
  - You can now change where RunServerDotPy checks for updates (it still has to be a GitHub repository), and where it checks for and downloads new help texts (which can be any JSON file)
  - The queue.Queue for inputQueue (used for "injecting" ChatCommands synchronously from the console) has been replaced with the more efficient collections.deque
- Minor:
  - Uptime command now shows in seconds, minutes, hours, days, and weeks format
  - Cleaned up imports section & grouped similar imports further

Removals:
- Major:
  - Removed the antivirus scan command and the update/upgrade command
- Minor:
  - Removed some chat and console spam
  - Removed some unusable features
  - Removed battery sensor for sysinfo command

Bugfixes:
- Major:
  - Emoticon page menu now suggests text to run command instead of running a "/tag" command to set a flag, as this doesn't actually work without OP
  - Tellraw functions fixed ("safeTellRaw" function specifically)
  - Fixed an issue with the time calculations for "uptime" by replacing time.monotonic() with time.time()
  - Fixed an issue where modules would be installed in the wrong version if "pip3" didn't correspond to the correct Python version
  - Fixed an issue where "requests" module wasn't in the "non-standard" group that would be automatically installed if they were missing (I thought that that was build-in...)

- Minor:
  - Fixed a bug which would cause the "sysinfo" command to still check for battery(when it still existed)/temperature, even if these don't actually exist, therefore causing an exception
  - Fixed an issue where an exception would be displayed in console if ";sudo" or ";root" was entered without any commands
  - Fixed an issue where some outputs of the sysinfo command were being broadcast to all user and some weren't. Now all of them just go to the target user

- Typo/misspelling:
  - Fixed a misspelling that caused a log's start time to be "Y%" instead of STRFTimed "%Y"
  - Fixed an issue where the help menu for sudo commands would show ";sudo[command]" without spacing upon hovering over or inserting a command, instead of ";sudo [command]"

---

From release 3.0 to QOL 3.1:

Changes:
- Replaced "getDTime" function with faster STRFTime function
- Changed default date format from "month-day-year" to "year-month-day"

Bugfixes:
- Restart counter now updates correctly

---

From bugfix 2.3 to release 3.0:

Additions:
- Added mods, which can add custom ChatCommands and help strings, or modify already existing commands and help strings

Changes:
- Changed the "refresh" ChatCommand help to reflect that it also reloads mods

Bugfixes:
- Fixed a bug where the program wouldn't boot on Windows, because removing the "update" command returned an error as it was using an outdated name

---

From QOL 2.2 to bugfix 2.3:

Bugfixes:
- Darn errors! (Making the script that updates the help file into a function made it so that the "chatCommandsHelp" (and the admin and root variations) variable weren't actually written

---

From QOL 2.1 to QOL 2.2:

Additions:
- Help file is automatically refreshed whenever the MC server restarts, instead of whenever the main script restarts

---

From release 2.0 to QOL 2.1:

Additions:
- Help file will now no longer be updated if the newer version is for a newer version of the program
- Antimalware scan command, using Windows Defender on Windows, and ClamAV on Linux

Changes:
- "AutoClean" subcommand of the upgrade command now also runs "sudo apt-get autoremove"

Removals:
- Removed "PIP" subcommand of the upgrade command, because it wasn't useful or needed

---

From bugfix 1.1 to release 2.0:

Additions:
- Added various comments for documentation
- The script can now automatically update itself on startup (the user only has to answer y/n questions)
- Users can now click on a ChatCommand in the help page to have it written (or "suggested") on their chat
- The user join message is now a configurable setting
- If the EULA hasn't been marked "true", then the Mojang EULA page will be opened in the user's default web browser, and the user will have the option to mark the EULA as "true" through the program

Changes:
- Compacted single-line if statements
- Help text is now cached in a file, instead of just being in the program, and checks GitHub to see if a newer version is availiable
- The copy- and paste-able emoticons are now shown by "page", and can now also be inserted into the user's chat by shift-clicking
- The time between users being able to use ChatCommands has been changed from 10 seconds down to 1 second
- Changed auto-restart countdown to 3 seconds, down from 5 seconds

Optimizations:
- Optimized the pad0s function's "round" function
- Some configurations (emoticons and user join messages) now have the defaults stored on GitHub intead of in the code
- Optimized the profanity checker so that it only checks chat messages, instead of wasting time checking everything
- If a user leaves the games, they will be removed from the dictionary containing when users last used a ChatCommand

Bugfixes:
- Fixed a logging bug
- Fixed a bug where user join messages wouldn't be shown
- Fixed a bug where console commands entered by users would be saved as /say messages in logs
- Fixed a bug where the ChatCommand spam protection wouldn't work, because it checked if the last time the user used a command was "-1" to see if they were an admin, and the default value is set to "-1"
- Fixed a bug where ChatCommand help would not show properly if executed from the console
- Fixed a bug where the server couldn't start if there was no server properties file
