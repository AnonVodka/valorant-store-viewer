import os
import sys
import asyncio

import main_discord as discord
import main_single as single

# possible args:
# --discord
# --single <region> <username> <password>

def main():
    args = sys.argv[1:]
    runAsBot = "--discord" in args
    runSingleAccount = "--single" in args

    if not runAsBot and not runSingleAccount:
        print("No command-line arguments found...")
        print("Possible arguments are:")
        print("\t--discord - to run the program as a discord bot")
        print("\t--single - to run the program for a single account which is specified in the config.json file")
        input("\npress enter to exit...")
        os._exit(1)

    if runAsBot and runSingleAccount:
        print("You can't run me in discord-mode and single-account-mode")
        input("\npress enter to exit...")
        os._exit(1)

    if runAsBot:
        print("Running program as discord bot..")
        discord.main()

    if runSingleAccount:
        print("Running program for a single account..")

        args = args[1:]

        if len(args) == 0:
            asyncio.run(single.main())

        elif len(args) == 3:
            region = args[0]
            username = args[1]
            password = args[2]

            asyncio.run(single.main(region, username, password))

        elif len(args) > 0 and len(args) != 3:
            print("Invalid command-line arguments passed to --single")
            print("Possible arguments are: ")
            print("\t--single - to run the program for a single account which is specified in the config.json file")
            print("\t--single <region> <username> <password> - to run the program for the given account details")

if __name__ == "__main__":
    main()