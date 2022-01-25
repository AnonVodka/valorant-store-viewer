import json
from io import TextIOWrapper
from json import JSONDecodeError
import os

# credits to: https://github.com/OwOHamper/VALORANT-rank-yoinker/blob/main/src/config.py

class Config:
    def __init__(self, inDiscordMode=False):
        if not os.path.exists("config.json"):
            with open("config.json", "w") as file:
                config = self.config_dialog(file, inDiscordMode)
            
        try:
            with open("config.json", "r") as file:
                config = json.load(file)
                if inDiscordMode:
                    if config.get("discord_token") is None:
                        config = self.config_dialog(file, inDiscordMode)
                else:
                    if config.get("username") is None:
                        config = self.config_dialog(file, inDiscordMode)
                
        except (JSONDecodeError):
            with open("config.json", "w") as file:
                config = self.config_dialog(file, inDiscordMode)
        finally:
            self.region = config.get("region")
            self.username = config.get("username")
            self.password = config.get("password")
            self.discord_token = config.get("discord_token")
            self.enc_key = config.get("encryption_key")
            self.dumpDataToFile = config.get("dumpDataToFile")

    def config_dialog(self, configFile: TextIOWrapper, inDiscordMode=False):
        region = "SET_ME"
        username = "SET_ME"
        password = "SET_ME"
        discord_token = "SET_ME"
        encryption_key = "SET_ME"
        dumpDataToFile = "false"

        if not inDiscordMode:
            region = input("Please enter your region: ")
            username = input("Please enter your username: ")
            password = input("Please enter your password: ")
        else:
            discord_token = input("Please enter your bot's discord token: ")
            encryption_key = input("Please enter a encryption key for the credentials file: ")

        dumpDataToFile = input("Should the requested data be saved to their files, yes or no?: ")

        jsonToWrite = {
            "region": region , 
            "username": username, 
            "password": password, 
            "discord_token": discord_token, 
            "encryption_key": encryption_key, 
            "dumpDataToFile": "True" if dumpDataToFile.lower() in ("yes", "true") else "False"
         }
        
        json.dump(jsonToWrite, configFile)
        print("\nSuccessfully wrote your values to the config file(config.json)")
        print("All values can be changed at any time\n")
        return jsonToWrite