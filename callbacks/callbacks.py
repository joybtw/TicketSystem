import discord 
import json
import math
import asyncio as a
import random
import datetime

from discord import ui
from datetime import datetime as dt
from main import create_transcript, append_to_database, remove_from_database, get_ticket_owner, add_timeout, is_in_timeout, is_ticket
from config import Config as cfg
from utils.utils import get_cat_by_name, get_emoji, get_category, get_cat_by_id
from utils.discord_ui import *

correct_answers = []
in_whitelist = []


async def TicketCreateCallback(interaction: discord.Interaction, self): 
      guild: discord.Guild = interaction.guild
      ticket_channel = None
      embed = None
      name = None
      category = None
      custom_message = None
      setPerm = True
      attributes = []
      if "~" in self.custom_id: 
            attributes = self.custom_id.split("~")
            self.custom_id = attributes[0]
            attributes.remove(self.custom_id)
      if self.custom_id == "ticket_report":
            name = f"report-{interaction.user.name}"
            category = await get_cat_by_name(guild, cfg.TICKET_CATEGORIES[0])
            attributes[1] = attributes[1] if attributes[1] != "" else "Keine weiteren Informationen"
            custom_message =  f"Steamname: `" + attributes[0] + "`\r\n"\
                              f"Vorfall passiert um: `" + attributes[1] + "`\r\n"\
                              f"Weitere Informationen: \r\n ```" + attributes[2] + "```\r\n"\
                              f"**Bitte halte mögliche Beweise auf Abruf bereit oder schicke sie gleich ins Ticket!**\r\n"\

      elif self.custom_id == "ticket_support": 
            name = f"support-{interaction.user.name}"
            category = await get_cat_by_name(guild, cfg.TICKET_CATEGORIES[0])
            custom_message =  f"Steamname: `{attributes[0]}`\r\n "\
                              f"Problem: \r\n ```{attributes[1]}```"

      elif self.custom_id == "ticket_gewerbe":
            category = await get_cat_by_name(guild, cfg.TICKET_CATEGORIES[1])
            name = f"{attributes[0]}"
            custom_message =  f"Steamname: `{attributes[0]}`\r\n "\
                              f"Gewerbe: `{attributes[1]}`\r\n"\
                              f"Mitarbeiter: > {attributes[2]}"
      
      elif self.custom_id == "ticket_gewerbe_besitz": 
            category = await get_cat_by_name(guild, cfg.TICKET_CATEGORIES[1])
            name = f"{attributes[1]}-{interaction.user.name}"

            custom_message =  f"Steamname: `{attributes[0]}`\r\n"\
                              f"Gewerbe: `{attributes[1]}`\r\n"\
                              f"Grund: ```{attributes[2]}```\r\n"
      
      elif self.custom_id == "ticket_gewerbe_wunsch":
            category = await get_cat_by_name(guild, cfg.TICKET_CATEGORIES[6])
            name = f"{attributes[0]}"
            custom_message =  f"Steamname: `{attributes[0]}`\r\n "\
                              f"Gewerbe: `{attributes[1]}`\r\n"\
                              f"Wünsche: \r\n{attributes[2]}"
      
      elif self.custom_id == "ticket_bug":
            category = await get_cat_by_name(guild, cfg.TICKET_CATEGORIES[2])
            name = f"bugrep-{interaction.user.name}"
            custom_message =  f"Steamname: `{attributes[0]}`\r\n "\
                              f"Beschreibung: ```{attributes[1]}```"

      elif self.custom_id == "ticket_bug_replace": 
            category = await get_cat_by_name(guild, cfg.TICKET_CATEGORIES[7])
            name = f"erstattung-{interaction.user.name}"
            attributes[1] = "Clip:" + attributes[1] if attributes[1] != "" else f"{interaction.user.mention} Vergesse nicht deine Datei zu schicken!" 
            custom_message =  f"Steamname: `{attributes[0]}`\r\n "\
                              f"{attributes[1]}"

      elif self.custom_id == "ticket_native": 
            category = await get_cat_by_name(guild, cfg.TICKET_CATEGORIES[3])
            name = f"native-{interaction.user.name}"
            custom_message =  f"Steamname: `{attributes[0]}`\r\n "\
                              f"Job: `{attributes[1]}`"
      
      elif self.custom_id == "ticket_native_wunsch": 
            category = await get_cat_by_name(guild, cfg.TICKET_CATEGORIES[3])
            name = f"wunsch-{interaction.user.name}"
            custom_message =  f"Steamname: `{attributes[0]}`\r\n "\
                              f"Wünsche: ```{attributes[1]}```"
      
      elif self.custom_id == "ticket_native_stamm": 
            category = await get_cat_by_name(guild, cfg.TICKET_CATEGORIES[8])
            name = f"stamm-{interaction.user.name}"
            custom_message =  f"Steamname: `{attributes[0]}`\r\n "\
                              f"Beschreibung: \r\n {attributes[1]}"

      elif self.custom_id == "ticket_dev": 
            category = await get_cat_by_name(guild, cfg.TICKET_CATEGORIES[5])
            name = f"todo-{interaction.user.name}"
            ticket_channel = await guild.create_text_channel(name, category=category)
            await ticket_channel.set_permissions(guild.get_role(cfg.DEV_ROLE), send_messages=True, read_messages=True, add_reactions=False,
                                                      embed_links=True, attach_files=True, read_message_history=True,
                                                      external_emojis=True, manage_channels=True)
            await ticket_channel.set_permissions(interaction.user, send_messages=True, read_messages=True, add_reactions=False,
                                                embed_links=True, attach_files=True, read_message_history=True,
                                                external_emojis=True)
            await ticket_channel.set_permissions(guild.default_role, send_messages=False, read_messages=False, add_reactions=False,
                                                embed_links=False, attach_files=False, read_message_history=False,
                                                external_emojis=False)      
            setPerm = False

      if setPerm:
            ticket_channel = await guild.create_text_channel(name, category=category)
            await ticket_channel.set_permissions(guild.get_role(cfg.TEAM_ROLE), send_messages=True, read_messages=True, add_reactions=False,
                                                      embed_links=True, attach_files=True, read_message_history=True,
                                                      external_emojis=True, manage_channels=True)
            await ticket_channel.set_permissions(interaction.user, send_messages=True, read_messages=True, add_reactions=False,
                                                embed_links=True, attach_files=True, read_message_history=True,
                                                external_emojis=True)
            await ticket_channel.set_permissions(guild.default_role, send_messages=False, read_messages=False, add_reactions=False,
                                                embed_links=False, attach_files=False, read_message_history=False,
                                                external_emojis=False)                                                   
      embed=discord.Embed(title='Ticketsystem :envelope_with_arrow:', description=f'{interaction.user.mention} es wird sich bald jemand um dich kümmern!', color=cfg.HEX)
      embed.set_author(name='Sundown-Rising', icon_url='https://cdn.discordapp.com/attachments/1131591673869250590/1137685066928103494/LogoGreenVersion1.png')
      embed.set_footer(text='Powered by Sundown-Rising', icon_url='https://cdn.discordapp.com/attachments/1131591673869250590/1137685066928103494/LogoGreenVersion1.png')
      embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/1131591673869250590/1137685066928103494/LogoGreenVersion1.png')
      add_timeout(interaction.user.id)
      view = View(items=[
                  DiscordButton(label="Claim", style=discord.ButtonStyle.green, custom_id="ticket_claim", cb=claimTicket, emoji="🤚"),
                  DiscordButton(label="Close", style=discord.ButtonStyle.red, custom_id="ticket_close", cb=closeTicket, emoji="🔒")
      ])
      await ticket_channel.send(embed=embed, view=view)
      if custom_message:
            await ticket_channel.send(custom_message)
      await interaction.response.send_message(f"Dein Ticket wurde erstellt! {ticket_channel.mention}", ephemeral=True)
      append_to_database(ticket_channel, interaction.user)

async def TicketCheckCallback(interaction: discord.Interaction, self):
      if not is_in_timeout(interaction.user.id):

            if "ticket_support" in self.custom_id:
                  view = View(items=[
                        Selection(placeholder="Art des Supports?", min_v=1, max_v=1, options=[
                              discord.SelectOption(default=False, description="Melde einen Regelwerkverstoß, wenn du dir sicher bist.", value="ticket_report", label="Spieler melden", emoji=None),
                              discord.SelectOption(default=False, description="Klicke hier, wenn du ein allgemeines Supportthema hast.", value="ticket_support", label="Anderer Support", emoji=None)
                        ], cb=TicketSelectCallback),
                  ])
                  await interaction.response.send_message(content="Bitte wähle aus, welche Art von Support du benötigst.", view=view, ephemeral=True)
            elif "ticket_gewerbe" in self.custom_id:
                  view = View(items=[
                        Selection(placeholder="Anliegen?", min_v=1, max_v=1, options=[
                              discord.SelectOption(default=False, description='Vom Gewerbeamt aufgefordert ein "Telegram" zu schreiben?', value="ticket_gewerbe", label="Gewerbe-Zulassung", emoji=None),
                              discord.SelectOption(default=False, description="Wunsch als Besitzer eines Gewerbes.", value="ticket_gewerbe_wunsch", label="Gewerbe-Wunsch", emoji=None),
                              discord.SelectOption(default=False, description="Gewerbe abgeben oder übertragen.", value="ticket_gewerbe_besitz", label="Gewerbe-Besitz", emoji=None)
                        ], cb=TicketSelectCallback)
                  ])
                  await interaction.response.send_message(content="Bitte wähle dein genaueres Anliegen aus.", view=view, ephemeral=True)
            elif "ticket_bug" in self.custom_id:
                  view = View(items=[
                        Selection(placeholder="Anliegen?", min_v=1, max_v=1, options=[
                              discord.SelectOption(default=False, description='Technisches Problem, Fehler oder Fehlfunktion?.', value="ticket_bug", label="Bug melden", emoji=None),
                              discord.SelectOption(default=False, description="Geld oder Sachverlust, durch einen Bug?", value="ticket_bug_replace", label="Erstattung anfordern", emoji=None)
                        ], cb=TicketSelectCallback)
                  ])
                  await interaction.response.send_message(content="Bitte wähle dein genaueres Anliegen aus.", view=view, ephemeral=True)
            elif "ticket_native" in self.custom_id: 
                  view = View(items=[
                        Selection(placeholder="Anliegen?", min_v=1, max_v=1, options=[
                              discord.SelectOption(default=False, description='Fordere deinen Native-Job an.', value="ticket_native", label="Native-Job", emoji=None),
                              discord.SelectOption(default=False, description="Einen Native-Stamm (Fraktion) anmelden.", value="ticket_native_stamm", label="Stamm Anfrage", emoji=None),
                              discord.SelectOption(default=False, description="Nenne uns einen Wunsch, welcher Natives betrifft.", value="ticket_native_wunsch", label="Native-Wunsch", emoji=None)
                        ], cb=TicketSelectCallback)
                  ])
                  await interaction.response.send_message(content="Bitte wähle dein genaueres Anliegen aus.", view=view, ephemeral=True)

            else:
                  await TicketCreateCallback(interaction, self)
      else:
            with open("timeouts.json", "r", encoding="utf-8") as file: 
                  data = json.load(file)
                  timeouts = data["timeouts"]
                  for timeout in timeouts: 
                        if timeout["user_id"] == interaction.user.id: 
                              timeout_at_str = timeout["timeout_at"]
                              timeout_at = dt.strptime(timeout_at_str, "%Y-%m-%d %H:%M:%S") #2023-07-17 01:35:38.326599
                              seconds = int((dt.now()-timeout_at).total_seconds())
                              if seconds <= 600: 
                                    minutes = math.floor(10-seconds/60)
                                    minutes_str = "Minuten"
                                    if minutes == 1:
                                          minutes_str = "Minute"
                                    await interaction.response.send_message(f"Bitte warte noch rund {minutes} {minutes_str}...", ephemeral=True)
                                    return


async def TicketSelectCallback(interaction: discord.Interaction, self: discord.ui.Select):
      self.custom_id = self.values[0]
      if self.custom_id == "ticket_report":
            await openSelecton(self,interaction=interaction,
                                    message="Hast du BILD-HOCH drücken können, damit der Spieler eindeutig identifizierbar ist?", 
                                    placeholder="BILD-Hoch?"), 
      elif self.custom_id == "ticket_gewerbe":
            await openSelecton(self,interaction=interaction,
                                    message='Wurdest du aufgefordert ein "Telegram" ans Goverment zu schreiben?', 
                                    placeholder="Wirklich aufgefordert?"), 
      elif self.custom_id == "ticket_bug_replace":
            await openSelecton(self,interaction=interaction, 
                                    message="Hast du einen Clip, welcher das Problem eindeutig Zeigt?", 
                                    placeholder="Clip?")
      else: 
            await openModular(interaction, self)



async def openSelecton(self, interaction: discord.Interaction, placeholder: str, message: str): 
            view = View(items=[
            Selection(placeholder=placeholder, min_v=1, max_v=1, options=[
                  discord.SelectOption(default=False, description='', value="y", label="Ja", emoji=None), 
                  discord.SelectOption(default=False, description='', value="n", label="Nein", emoji=None)
            ], custom_id=self.custom_id, cb=openModular)])  

            await interaction.response.send_message(content=message, view=view, ephemeral=True)

# async def openClipSelection(self, interaction: discord.Interaction, callback): 
#       view = View(items=[
#             Selection(placeholder="Clip?", min_v=1, max_v=1, options=[
#                   discord.SelectOption(default=False, description='Ja, ich habe einen Clip.', value="y", label="Ja", emoji=None), 
#                   discord.SelectOption(default=False, description='Nein, ich habe keinen Clip.', value="n", label="Nein", emoji=None)
#             ], custom_id=self.custom_id ,cb=callback)
#       ])
#       await interaction.followup.send(content="Hast du einen Clip, welcher eindeutig dein Problem nachweist.", view=view)

async def openModular(interaction: discord.Interaction, self):
      if str(self.values[0]) == "y" or str(self.values[0]).startswith("ticket_"):
            modal = None 
            if self.custom_id == "ticket_report":
                  modal = Modular(title="Spieler melden", inputs=[
                              ui.TextInput(label="Steamname? (Pflichtfeld)", placeholder="z.B. Joybtw", style=discord.TextStyle.short), 
                              ui.TextInput(label="Wann ist der Vorfall passiert? (Pflichtfeld)", placeholder="Ungefähre Uhrzeit...", style=discord.TextStyle.short), 
                              ui.TextInput(label="Weitere Informationen", placeholder="z.B. ID, IC-Name, etc.", style=discord.TextStyle.long, required=False)
                  ], custom_id=self.custom_id, cb=ModularCallback)

            elif self.custom_id == "ticket_support":
                  modal = Modular(title="Anderer Support", inputs=[
                              ui.TextInput(label="Steamname? (Pflichtfeld)", placeholder="z.B. Joybtw", style=discord.TextStyle.short), 
                              ui.TextInput(label="Bitte beschreibe dein Anliegen (Plichtfeld)", placeholder="...", style=discord.TextStyle.paragraph, required=True), 
                  ], custom_id=self.custom_id, cb=ModularCallback)

            elif self.custom_id == "ticket_gewerbe": 
                  modal = Modular(title="Neues Gewerbe anmelden", inputs=[
                        ui.TextInput(label="Steamname? (Pflichtfeld)", placeholder="z.B. Joybtw", style=discord.TextStyle.short), 
                        ui.TextInput(label="Um welches Gewerbe geht es? (Pflichtfeld)", placeholder='z.B. "Saloon, Blackwater"', style=discord.TextStyle.short, required=True),
                        ui.TextInput(label="Bei welchem Mitarbeiter warst du?", placeholder="Ggf. IC-Name/Discord-Name", style=discord.TextStyle.short, required=False)
                  ], custom_id=self.custom_id, cb=ModularCallback) 

            elif self.custom_id == "ticket_gewerbe_besitz": 
                  modal = Modular(title="Gewerbe Änderung", inputs=[
                        ui.TextInput(label="Steamname? (Pflichtfeld)", placeholder="z.B. Joybtw", style=discord.TextStyle.short), 
                        ui.TextInput(label="Welches Gewerbe betreibst du? (Pflichtfeld)", placeholder='z.B. "Saloon, Blackwater"', style=discord.TextStyle.short, required=True),
                        ui.TextInput(label="Übergeben oder abgeben? (Pflichtfeld)", placeholder="Übergabe/Abgabe", style=discord.TextStyle.short, required=True), 
                        ui.TextInput(label="Bitte nenne uns deinen Grund (Pflichtfeld)", placeholder="Grund...", style=discord.TextStyle.paragraph, required=True)
                  ], custom_id=self.custom_id, cb=ModularCallback) 

            elif self.custom_id == "ticket_gewerbe_wunsch": 
                  modal = Modular(title="Gewerbewunsch äußern", inputs=[
                        ui.TextInput(label="Steamname? (Pflichtfeld)", placeholder="z.B. Joybtw", style=discord.TextStyle.short), 
                        ui.TextInput(label="Welches Gewerbe bespieltst du? (Pflichtfeld)", placeholder="z.B. Saloon, Blackwater", style=discord.TextStyle.short, required=True),
                        ui.TextInput(label="Welche Wünsche hast du? (Pflichtfeld)", placeholder="Tob dich aus...", style=discord.TextStyle.paragraph, required=False)
                  ], custom_id=self.custom_id, cb=ModularCallback) 
            
            elif self.custom_id == "ticket_bug": 
                  modal = Modular(title="Bug melden", inputs=[
                        ui.TextInput(label="Steamname? (Pflichtfeld)", placeholder="z.B. Joybtw", style=discord.TextStyle.short), 
                        ui.TextInput(label="Beschreibe den Bug genauer (Pflichtfeld)", placeholder="...", style=discord.TextStyle.paragraph, required=True),
                  ], custom_id=self.custom_id, cb=ModularCallback) 
            
            elif self.custom_id == "ticket_bug_replace": 
                  modal = Modular(title="Anfrage-Rückerstattung", inputs=[
                        ui.TextInput(label="Steamname? (Pflichtfeld)", placeholder="z.B. Joybtw", style=discord.TextStyle.short), 
                        ui.TextInput(label="Link zum Clip (Datei=Leer lassen)", placeholder="...", style=discord.TextStyle.short, required=False),
                  ], custom_id=self.custom_id, cb=ModularCallback) 

            elif self.custom_id == "ticket_native": 
                  modal = Modular(title="Native-Job", inputs=[
                        ui.TextInput(label="Steamname? (Pflichtfeld)", placeholder="z.B. Joybtw", style=discord.TextStyle.short), 
                        ui.TextInput(label="Job, den du anfragen möchtest. (Pflichtfeld)", placeholder="Normaler Native, Waffenbauer, Heiler, Pferdeplüsterer", style=discord.TextStyle.short, required=True),
                  ], custom_id=self.custom_id, cb=ModularCallback) 
            
            elif self.custom_id == "ticket_native_stamm": 
                  modal = Modular(title="Native-Stamm", inputs=[
                        ui.TextInput(label="Steamname? (Pflichtfeld)", placeholder="z.B. Joybtw", style=discord.TextStyle.short),
                        ui.TextInput(label="Beschreibung oder Konzept-Link. (Pflichtfeld)", placeholder="Beschreibung/Link", style=discord.TextStyle.short, required=True),
                  ], custom_id=self.custom_id, cb=ModularCallback) 

            elif self.custom_id == "ticket_native_wunsch": 
                  modal = Modular(title="Native-Stamm", inputs=[
                        ui.TextInput(label="Steamname? (Pflichtfeld)", placeholder="z.B. Joybtw", style=discord.TextStyle.short),
                        ui.TextInput(label="Nenne uns deine Wünsche (Pflichtfeld)", placeholder="...", style=discord.TextStyle.paragraph, required=True),
                  ], custom_id=self.custom_id, cb=ModularCallback) 

            await interaction.response.send_modal(modal)
      else: 
            await interaction.response.send_message("Wir können leider nicht ohne diese Bedingung das Problem bearbeiten. Tut uns sehr leid!", ephemeral=True)


async def ModularCallback(interaction: discord.Interaction, self):
      items: list = self.items 
      for val in items: 
            self.custom_id =  self.custom_id + "~" + str(val)
      await TicketCreateCallback(interaction, self)

async def closeTicket(interaction: discord.Interaction, self): 
      team_role = discord.utils.get(interaction.guild.roles, id=cfg.TEAM_ROLE)
      if team_role in interaction.user.roles or get_ticket_owner(interaction.channel.id) == interaction.user.id:
            embed=discord.Embed(title='Ticketsystem :envelope_with_arrow:', description=f'Dieses Ticket wird nun geschlossen', color=cfg.HEX)
            embed.set_author(name='Sundown-Rising', icon_url='https://cdn.discordapp.com/attachments/1131591673869250590/1137685066928103494/LogoGreenVersion1.png')
            embed.set_footer(text='Powered by Sundown-Rising', icon_url='https://cdn.discordapp.com/attachments/1131591673869250590/1137685066928103494/LogoGreenVersion1.png')
            embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/1131591673869250590/1137685066928103494/LogoGreenVersion1.png')
            await interaction.response.send_message(embed=embed)

            await create_transcript(interaction)
            remove_from_database(interaction.channel.id)
            await interaction.channel.delete()
      else:
            await interaction.response.send_message("Du kannst dies nicht tun!", ephemeral=True)
            return


async def claimTicket(interaction: discord.Interaction, self): 
      team_role = discord.utils.get(interaction.guild.roles, id=cfg.TEAM_ROLE)
      if not team_role in interaction.user.roles:
            await interaction.response.send_message("Du kannst dies nicht tun!", ephemeral=True)
            return
      else:
            embed=discord.Embed(title='Ticketsystem :envelope_with_arrow:', description=f'Du wirst nun von {interaction.user.mention} supportet!', color=cfg.HEX)
            embed.set_author(name='Sundown-Rising', icon_url='https://cdn.discordapp.com/attachments/1131591673869250590/1137685066928103494/LogoGreenVersion1.png')
            embed.set_footer(text='Powered by Sundown-Rising', icon_url='https://cdn.discordapp.com/attachments/1131591673869250590/1137685066928103494/LogoGreenVersion1.png')
            embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/1131591673869250590/1137685066928103494/LogoGreenVersion1.png')

            emoji = await get_emoji(interaction.user.id)
            cat_id = await get_category(interaction.user.id)
            cat = await get_cat_by_id(interaction.guild, cat_id)
            if not emoji:
                  emoji = ""
            if cat: 
                  await interaction.channel.edit(name=emoji + " " + interaction.channel.name, category=cat)
            else:
                  await interaction.channel.edit(name=emoji + " " + interaction.channel.name)

            await interaction.response.send_message(embed=embed)

async def redirect(interaction: discord.Interaction, member_id: int): 
      if is_ticket(interaction.channel.id):
            emoji = await get_emoji(member_id)
            cat_id = await get_category(member_id)
            cat = await get_cat_by_id(interaction.guild, cat_id)
            if not emoji:
                  emoji = ""
            if cat: 
                  await interaction.channel.edit(name=emoji + " " + interaction.channel.name, category=cat)
            else:
                  await interaction.channel.edit(name=emoji + " " + interaction.channel.name)
            
            await interaction.response.send_message("Weitergeleitet an: <@" + str(member_id) + ">")
      else: 
            await interaction.response.send_message("Dieser Channel ist kein Ticket!", ephemeral=True)


async def embedModularCallback(interaction: discord.Interaction, items: list): 
      embed_title = items[0]
      msg = items[1]
      img = items[2]
      embed = discord.Embed(title=embed_title, description=msg, color=cfg.HEX, timestamp=dt.now()) 
      if img: 
            embed.set_image(url=img)
      embed.set_footer(text="Copyright by Sundown-Rising", icon_url="https://cdn.discordapp.com/attachments/1131591673869250590/1137685066928103494/LogoGreenVersion1.png")
      embed.set_author(name="Sundown-Rising", icon_url="https://cdn.discordapp.com/attachments/1131591673869250590/1137685066928103494/LogoGreenVersion1.png")
      await interaction.response.send_message(embed=embed)