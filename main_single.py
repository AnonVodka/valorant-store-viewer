import os
import asyncio
import valorant
from config import Config

async def main(region=None, username=None, password=None):

    cfg = Config()

    region = cfg.region if region is None else region
    username = cfg.username if username is None else username
    password = cfg.password if password is None else password

    if region == "SET_ME" or username == "SET_ME" or password == "SET_ME":
        print("You tried to check your store without setting your account credentials in the config!")
        input("\npress enter to exit..")
        os._exit(1)

    data = await valorant.run(region, username, password, cfg.dumpDataToFile)

    status = data[0]

    if status == "error":
        print(f"An error happened when trying to check your store:\n\t{data[1]}\n")

    elif status == "ok":
        offers = data[1][0]
        bundle = data[1][1]
        
        msg = "Current store items:\n"
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
        
        print(msg)

    input("press enter to exit..")
    os._exit(1)

if __name__ == "__main__":
    asyncio.run(main())