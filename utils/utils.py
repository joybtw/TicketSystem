import discord, json


async def get_cat_by_name(guild: discord.Guild, name: str):
    for cat in guild.categories:
        if name == cat.name:
            return cat
    else:
        return False

async def get_cat_by_id(guild: discord.Guild, id: int):
    for cat in guild.categories:
        if id == cat.id:
            return cat
    else:
        return False


async def get_tc_by_name(guild: discord.Guild, name: str): 
    for tc in guild.text_channels: 
        if name == tc.name: 
            return tc
    else: 
        return False

async def get_role_by_name(guild: discord.Guild, name: str): 
    for r in guild.roles: 
        if name == r.name: 
            return r
    else:
        return False 

async def does_role_exists(guild: discord.Guild, id: int): 
    for r in guild.roles: 
        if r.id == id: 
            return True
    else: 
        return False

async def get_emoji(member_id: int): 
    with open("team_data.json", "r", encoding="utf-8") as file: 
        data = json.load(file)
    
    data = data["team_data"]
    for dataset in data: 
        if dataset["member_id"] == member_id: 
            return dataset["emoji"]
    
    return False

async def get_category(member_id: int): 
    with open("team_data.json", "r", encoding="utf-8") as file: 
        data = json.load(file)
    
    data = data["team_data"]
    for dataset in data: 
        if dataset["member_id"] == member_id: 
            return dataset["member_cat_id"]
    
    return False