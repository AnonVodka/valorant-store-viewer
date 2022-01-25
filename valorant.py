import os
import re
import requests
import json
from datetime import timedelta

cwd = os.getcwd()

TOKEN_PATTERN = re.compile("access_token=((?:[a-zA-Z]|\d|\.|-|_)*).*id_token=((?:[a-zA-Z]|\d|\.|-|_)*).*expires_in=(\d*)")
TIME_PATTERN = re.compile("(\d+)")

# some of the follwing code is yoinked from
# https://github.com/OwOHamper/Valorant-item-shop-discord-bot
# so thanks for that

async def login(session, username, password):
    """
    log in into the api and return tokens??
    """

    data = {
        "client_id": "play-valorant-web-prod",
        "nonce": "1",
        "redirect_uri": "https://playvalorant.com/opt_in",
        "response_type": "token id_token",
    }
    r = session.post("https://auth.riotgames.com/api/v1/authorization", json=data)

    data = {
        "type": "auth",
        "username": username,
        "password": password
    }
    r = session.put("https://auth.riotgames.com/api/v1/authorization", json=data)

    r = r.json()

    if r.get("error") == "auth_failure":
        return ["error", "[!] Auth error... validate username, password and region!"]

    data = TOKEN_PATTERN.findall(r["response"]["parameters"]["uri"])[0]
    auth_token = data[0]

    headers = {
        "Authorization": f"Bearer {auth_token}",
    }
    r = session.post("https://entitlements.auth.riotgames.com/api/token/v1", headers=headers, json={})
    ent_token = r.json()["entitlements_token"]

    r = session.post("https://auth.riotgames.com/userinfo", headers=headers, json={})

    user_id = r.json()["sub"]

    return ["ok", [auth_token, ent_token, user_id]]

async def get_valorant_version():
    """
    get and return the current game version
    """

    versionData = requests.get("https://valorant-api.com/v1/version")
    versionDataJson = versionData.json()["data"]
    final = f"{versionDataJson['branch']}-shipping-{versionDataJson['buildVersion']}-{versionDataJson['version'][-6:]}"
    return final

async def get_store_items(session, region, auth_token, ent_token, user_id):
    """
    get and return our current store offers
    """

    session = requests.session()

    data = {
        "X-Riot-Entitlements-JWT": ent_token,
        "Authorization": f"Bearer {auth_token}",
    }
    r = session.get(f"https://pd.{region}.a.pvp.net/store/v2/storefront/{user_id}", headers=data)

    session.close()

    return r.json()

async def get_valorant_currencies():
    """
    parse valorant currency id's and return them in a dictionary
    """

    currencies = {}
    
    data = requests.get("https://valorant-api.com/v1/currencies").json().get("data")

    for d in data:
        currencies[d.get("uuid")] = d.get("displayName")

    return currencies

async def get_bundle_info(bundle_id):
    """
    get and return bundle name for the passed bundle id
    """
   
    bundle_data = requests.get(f"https://valorant-api.com/v1/bundles/{bundle_id}").json().get("data")
    
    return bundle_data.get("displayName")

async def get_items(dumpDataToFile=False):
    """
    get and return all items that could be sold
    """
    
    items = {}

    weapons_data = requests.get("https://valorant-api.com/v1/weapons").json().get("data")
    
    if dumpDataToFile:
        with open("data/weapons_data.json", "w") as f:
            json.dump(weapons_data, f)
            f.close()

    # loop through all weapons
    # get all skin level uuids and save them as the skin name
    # the uuid is used to identify the item thats being sold in the shop
    # same applies to the sprays, player cards and buddies

    for weapon in weapons_data:
        skins = weapon.get("skins") # get weapon skins
        for skin in skins: # loop through weapon skins
            levels = skin.get("levels") # get skin levels
            for level in levels: # loop through levels
                uuid = level.get("uuid") # get level uuid
                name = skin.get("displayName") #  get skin name
                items[uuid] = name # save to dictionary

    sprays_data = requests.get("https://valorant-api.com/v1/sprays").json().get("data")
    
    if dumpDataToFile:
        with open("data/sprays_data.json", "w") as f:
            json.dump(sprays_data, f)
            f.close()

    for spray in sprays_data: # loop through sprays
        uuid = spray.get("uuid") # get spray uuid
        name = spray.get("displayName") # get spray name
        items[uuid] = name # save to dictionary

    player_cards_data = requests.get("https://valorant-api.com/v1/playercards").json().get("data")
    
    if dumpDataToFile:
        with open("data/player_cards_data.json", "w") as f:
            json.dump(player_cards_data, f)
            f.close()

    for card in player_cards_data: # loop through player cards
        uuid = card.get("uuid") # get card uuid
        name = card.get("displayName") # get card name
        items[uuid] = name # save to dictionary

    buddies_data = requests.get("https://valorant-api.com/v1/buddies").json().get("data")
    
    if dumpDataToFile:
        with open("data/buddies_data.json", "w") as f:
            json.dump(buddies_data, f)
            f.close()

    for buddy in buddies_data: # loop through buddies
        name = buddy.get("displayName") #  get buddy name
        levels = buddy.get("levels") # get buddy levels, which apperantly is a thing lmao
        for level in levels: # loop through levels
            uuid = level.get("uuid") # get level uuid
            items[uuid] = name # save to dictionary

    if dumpDataToFile:
        with open("data/items.json", "w") as f:
            json.dump(items, f)
            f.close()

    return items # return all parsed items

async def get_offers(region, auth_token, ent_token, dumpDataToFile=False):
    """
    get and return the prices for todays item offers
    """
    
    # get available currencies
    currencies = await get_valorant_currencies()

    offers = {}

    headers = {
        "X-Riot-Entitlements-JWT": ent_token,
        "Authorization": f"Bearer {auth_token}",
        "X-Riot-ClientVersion": await get_valorant_version(),
        "X-Riot-ClientPlatform": "ew0KCSJwbGF0Zm9ybVR5cGUiOiAiUEMiLA0KCSJwbGF0Zm9ybU9TIjogIldpbmRvd3MiLA0KCSJwbGF0Zm9ybU9TVmVyc2lvbiI6ICIxMC4wLjE5MDQyLjEuMjU2LjY0Yml0IiwNCgkicGxhdGZvcm1DaGlwc2V0IjogIlVua25vd24iDQp9"
    }

    item_offers = requests.get(f"https://pd.{region}.a.pvp.net/store/v1/offers/", headers=headers).json().get("Offers")

    if dumpDataToFile:
        with open("data/item_offers.json", "w") as f:
            json.dump(item_offers, f)
            f.close()

    for offer in item_offers: # loop through offers
        uuid = offer.get("OfferID") # get offer uuid
        cs = offer.get("Cost") # get all available currency types
        for c in cs: # loop through em
            price = cs.get(c) # get the price
            type = currencies.get(c) # convert the currency uuid to name
            offers[uuid] = f"{price} {type}" # save to dictionary

    if dumpDataToFile:
        with open("data/offers.json", "w") as f:
            json.dump(offers, f)
            f.close()

    return offers # return offer prices

async def run(region, username, password, dumpDataToFile=False):
    """
    run our program
    """

    if dumpDataToFile:
        if not os.path.exists(f"{cwd}/data"):
            os.makedirs(f"{cwd}/data")

    session = requests.session()

    # login in using given credentials
    data = await login(session, username, password)

    status = data[0] # status 
    data = data[1] # status message or authentication information

    if status == "error":
        return ["error", data]

    auth_token = data[0]
    ent_token = data[1]
    user_id = data[2]

    if auth_token is None:
        return ["error", "Login failed"]

    # get the items we have in store
    store_items = await get_store_items(session, region, auth_token, ent_token, user_id)

    if dumpDataToFile:
        with open("data/store_items.json", "w") as f:
            json.dump(store_items, f)
            f.close()

    # get all available skins, sprays, buddies and player cards that are in the game
    # maybe a bit overkill but who cares
    items = await get_items(dumpDataToFile)

    skin_offers = store_items.get("SkinsPanelLayout").get("SingleItemOffers")
    skin_offers_refresh_time = store_items.get("SkinsPanelLayout").get("SingleItemOffersRemainingDurationInSeconds")
    bundle_offer = store_items.get("FeaturedBundle").get("Bundle")
    bundle_offer_refresh_time = bundle_offer.get("DurationRemainingInSeconds")

    # get currency names
    currencies = await get_valorant_currencies()

    # get todays shop offers
    item_offers = await get_offers(region, auth_token, ent_token, dumpDataToFile)

    my_offers = {
        "timeUntilRefresh": 0,
        "offers": {}
    }
    my_bundle_offer = {
        "name": await get_bundle_info(bundle_offer.get("DataAssetID")),
        "timeUntilRefresh": 0,
        "content": {}
    }

    # convert seconds to usable time
    timeUntilRefresh = timedelta(seconds=skin_offers_refresh_time)
    bundleTimeUntilRefresh = timedelta(seconds=bundle_offer_refresh_time)
    
    # convert time to string
    my_bundle_offer["timeUntilRefresh"] = ":".join(re.findall(TIME_PATTERN, str(bundleTimeUntilRefresh)))
    my_offers["timeUntilRefresh"] = ":".join(re.findall(TIME_PATTERN, str(timeUntilRefresh)))

    for id in skin_offers: # loop through our offers
        my_offers["offers"][id] = {
            "name": items.get(id), # get item name for id
            "price": item_offers.get(id) # get item price
        }

    for item in bundle_offer.get("Items"): # loop through bundle items
        id = item.get("Item").get("ItemID") # get item id
        price = item.get("BasePrice") # get price
        currency = currencies.get(item.get("CurrencyID")) # get currency type
        name = items.get(id) # get item name

        # save to dictionary
        my_bundle_offer["content"][id] = {
            "name": name,
            "price": f"{price} {currency}"
        }

    return [
        "ok", [
            my_offers,
            my_bundle_offer
        ]
    ]