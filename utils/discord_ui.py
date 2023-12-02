from typing import Optional
import discord
from discord.interactions import Interaction
from discord.utils import MISSING

class View(discord.ui.View):
    def __init__(self, items: list):
        super().__init__(timeout=None)
        if items: 
            for item in items: 
                self.add_item(item)

class DiscordButton(discord.ui.Button): 
    def __init__(self, label: str, style: discord.ButtonStyle, custom_id: str, cb, emoji: str=None):
        self.cb = cb
        button = {
            "label": label, 
            "style": style,
            "custom_id": custom_id,
        }
        super().__init__(
            label = button["label"], 
            style = button["style"],
            custom_id = button["custom_id"], 
            emoji=emoji
        )
        
    async def callback(self, interaction: discord.Interaction):
        if self.cb:  
            await self.cb(interaction, self)

class DiscordURLButton(discord.ui.Button): 
    def __init__(self, label: str, style: discord.ButtonStyle, emoji: str=None, url: str = None):
        button = {
            "label": label, 
            "style": style,
            "url": url
        }
        super().__init__(
            label = button["label"], 
            style = button["style"],
            emoji=emoji, 
            url=button["url"]
        )

class Modular(discord.ui.Modal): 
    def __init__(self, inputs: list, title: str, custom_id: str, cb):
        super().__init__(
            custom_id=custom_id, 
            title=title, 
            timeout=None
        )
        for inpt in inputs: 
            self.add_item(inpt)
        self.items = inputs
        self.cb = cb
    
    async def on_submit(self, interaction: discord.Interaction):
        await self.cb(interaction, self)
        

class Selection(discord.ui.Select): 
    def __init__(self, placeholder, min_v, max_v, options, cb, custom_id=None):
        self.cb = cb
        super().__init__(
            placeholder=placeholder,
            min_values=min_v,
            max_values=max_v,
            options=options,
            custom_id= custom_id if custom_id else ""
        )

    async def callback(self, interaction: discord.Interaction):
        await self.cb(interaction, self)
