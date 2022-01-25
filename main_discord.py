import os
import discord
import hashlib
import json
import cryptocode as crypt
import valorant
from config import Config

cfg = None

# https://stackoverflow.com/a/5125636
def safe_list_get(l, idx):
    try:
        return l[idx]
    except IndexError:
        return None

async def save_credentials_to_file(region, username, password):

    # create hash from region, username and password
    hash = hashlib.sha1(f"{region}-{username}-{password}".encode()).hexdigest()

    # open credentials file and parse content
    with open("credentials.dat", "r") as f:
        content = f.read() # read file content
        content = crypt.decrypt(content, cfg.enc_key) # decrypt using encryption key
        content = json.loads(content) # parse content as json
        f.close() # close file

    if content.get(hash) is not None:
        print("Credentials are already safed to the file")
        return ["already_saved", hash]

    # TODO: maybe add discord id
    #       so person "A" cant check person "B"'s account
    #       just a wild thought, dont know if thats really useful 
    #       coz who cares if someone knows what items you have in your store

    # add our credentials to the table
    content[hash] = {
        "region": region,
        "username": username,
        "password": password
    }

    # save the table to the credentials file
    with open("credentials.dat", "w") as f:
        enc = crypt.encrypt(json.dumps(content), cfg.enc_key) # encrypt our credentials with our encryption key
        f.write(enc) # and save to file
        f.close() # close the file
    
    return ["successfully_saved", hash]

async def get_saved_credentials(hash):
    with open("credentials.dat", "r") as f:
        content = f.read() # read file content
        content = crypt.decrypt(content, cfg.enc_key) # decrypt using encryption key
        content = json.loads(content) # parse content as json
        f.close() # close file
    return content.get(hash) # return credentials or None if not found

async def run(send, region, username, password):

    data = await valorant.run(region, username, password, cfg.get("dumpDataToFile"))

    status = data[0]

    if status == "error":
        await send(f"An error happened when trying to check your store:\n\t{data[1]}")

    elif status == "ok":
        offers = data[1][0]
        bundle = data[1][1]
        
        msg = "```Current store items:\n"
        msg += f"\t- Bundle ({bundle.get('timeUntilRefresh')} until refresh): {bundle.get('name')}\n"

        bundle_content = bundle.get("content")
        for id in bundle_content:
            item = bundle_content.get(id)
            name = item.get("name")
            price = item.get("price")
            msg += f"\t\t- {name} for {price}\n"

        msg += f"\n\t- Weapons ({offers.get('timeUntilRefresh')} until refresh):\n"

        offers_content = offers.get("offers")
        for id in offers_content:
            item = offers_content.get(id)
            name = item.get("name")
            price = item.get("price")
            msg += f"\t\t- {name} for {price}\n"

        msg += "```"
        
        await send(msg)

class Client(discord.Client):
    async def on_ready(self):
        print("Logged in as {0}!".format(self.user))

    async def on_message(self, message):
        if type(message.channel) == discord.DMChannel:
            author = message.author
            content = message.content

            if author == self.user:
                return

            splitted_content = content.split()

            cmd = safe_list_get(splitted_content, 0)

            # args: region, username, password, save_user?
            if cmd == ".check_store":
                region = safe_list_get(splitted_content, 1) # either region or hash
                username = safe_list_get(splitted_content, 2)
                password = safe_list_get(splitted_content, 3)
                shouldSaveToFile = safe_list_get(splitted_content, 4)
                send = message.channel.send

                if region is None:
                    # the user must've only entered the command, so send him a help text so he knows what it does
                    await send(".check_store <region> <username> <password> <save_credentials>")
                    return

                # call valorant.run(region, username, password)
                # valorant.run should return 2 things
                # first: status_message(OK, ERROR)
                # second: if ok, a tuple with all the information about the store
                #         if error, an error message

                if username is None:
                    # region is probably a hash
                    hash = region
                    credentials = await get_saved_credentials(hash)

                    if credentials is None:
                        await send("The hash you provided wasn't found")
                        return

                    region = credentials.get("region")
                    username = credentials.get("username")
                    password = credentials.get("password")

                    print(f"Received information from {author} using hash: {hash} {region} {username} <password>")

                    await send("Checking store...")
                    await run(send, region, username, password)
                else:
                    print(f"Received information from {author}: {region} {username} <password>")

                    if shouldSaveToFile is not None and shouldSaveToFile in ("true", "yes"):
                        hash = await save_credentials_to_file(region, username, password)

                        status = hash[0]
                        hash = hash[1]

                        if status == "already_saved":
                            await send("Your credentials are already saved")
                        elif status == "successfully_saved":
                            await send("Saved credentials under: " + hash)

                    await send("Checking store...")
                    await run(send, region, username, password)

def main():

    # create or read config file for discord mode
    cfg = Config(True)

    token = cfg.discord_token

    if token == "SET_ME" or cfg.enc_key == "SET_ME":
        print("You tried to use the discord bot without setting the token or the encryption key!")
        input("\npress enter to exit..")
        os._exit(1)

    # create credentials file if it doesnt exist
    # and save an empty json table to it
    if not os.path.isfile(f"{os.getcwd()}/credentials.dat"):
        with open("credentials.dat", "w+") as f:
            s = json.dumps({})
            encr = crypt.encrypt(s, cfg.enc_key)
            f.write(encr)
            f.close()


    client = Client()
    client.run(token)

if __name__ == "__main__":
    main()