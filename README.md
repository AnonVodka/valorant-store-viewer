# valorant-store-viewer

This is a simple script to view your valorant store items without having to open the game

#

# Usage
Either clone the repository or download the precompiled binaries from the [release page](https://github.com/AnonVodka/valorant-store-viewer/releases)

<br></br>
If you've downloaded the precompiled binaries

run either "vsv-single.exe", if you want to check for a single account (account details set in the config or on first launch) 

or "vsv-discord.exe" if you want to run the program as a discord bot (bot token set in the config or on first launch)
<br></br>

"vsv.exe" is a simple "launcher" that can take command-line arguments:
- --single - runs in single account mode and uses the credentials saved in the config file
- --single "region" "username" "password" - same as above except that it uses the given arguments as credentials
- --discord - runs in discord bot mode
<br></br>

If you've cloned the repository execute any of the following commands:
- `python main.py` - to run the launcher, same command-line arguments as "vsv.exe"
- `python main_single.py` - to run it for a single account (account details set in the config or on first launch)
- `python main_discord.py` - to run it as a discord bot (bot token set in the config or on first launch)

#

## Bot commands
- .check_store "region" "username" "password" "save_credentials_to_file"
  - the bot will respond with a hash if "save_credentials_to_file" was set to true
  - this hash can be used in the same command and replaces the need to pass the credentials again
- .check_store "hash" -  only works if "save_credentials_to_file" was set to true

#

## Disclaimer
_May contain a lot of bad code_

#

## Credits
- [valorant-api.com](https://valorant-api.com)
- [OwOHamper](https://github.com/OwOHamper)