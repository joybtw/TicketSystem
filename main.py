# normal imports
import discord
import asyncio as a
import shutil
import pytz
import os
import json
import sys

# from imports
from datetime import datetime as dt
from config import Config as cfg

from utils.utils import *
from utils.perm_handling import *
from utils.discord_ui import *

from callbacks.callbacks import *

from discord import Guild, TextChannel, app_commands, Role
from discord.ext import commands
from discord import ui

BOARD_ID = None
BOARD_CHANNEL = None


class init_client(commands.Bot):
    def __init__(self):
        super().__init__(intents=discord.Intents.all(), command_prefix="?")
        self.synced = False

    async def on_ready(self):
        await self.wait_until_ready()
        global BOARD_ID
        global BOARD_CHANNEL

        with open("tickets.json", "r", encoding="utf-8") as file: 
            data = json.load(file)
            if data["board"] != None: 
                BOARD_ID = data["board"]["id"]
                BOARD_CHANNEL = data["board"]["channel_id"]
        
        ticketdropdown = View(items=[
                                DiscordButton(label="Support", style=discord.ButtonStyle.blurple, custom_id="ticket_support_prev", cb=TicketCheckCallback, emoji="🛡️"), 
                                DiscordButton(label="Bug", style=discord.ButtonStyle.red, custom_id="ticket_bug_prev", cb=TicketCheckCallback, emoji="🐞"),
                                DiscordButton(label="Gewerbe", style=discord.ButtonStyle.red, custom_id="ticket_gewerbe_prev", cb=TicketCheckCallback, emoji="🛖"), 
                                DiscordButton(label="Natives", style=discord.ButtonStyle.gray, custom_id="ticket_native_prev", cb=TicketCheckCallback, emoji="🦅")
                            ])
        self.add_view(ticketdropdown)

        close_btns = View(items=[
                DiscordButton(label="Claim", style=discord.ButtonStyle.green, custom_id="ticket_claim", cb=claimTicket, emoji="🤚"),
                DiscordButton(label="Close", style=discord.ButtonStyle.red, custom_id="ticket_close", cb=closeTicket, emoji="🔒")
        ])
        self.add_view(close_btns)
        
        devticketview = View(items=[
          DiscordButton(label="Neues ToDo", style=discord.ButtonStyle.blurple, custom_id="ticket_dev", cb=TicketCheckCallback, emoji="💻")
        ])
        self.add_view(devticketview)
        
        if not self.synced:
            await self.tree.sync(guild=discord.Object(cfg.GUILD_ID))
            self.synced = True   
        self.guild: Guild = self.get_guild(cfg.GUILD_ID)

        print(f"{self.user} has logged in.")
        await self.log(f"{self.user} has logged in.")
           
        await self.loop.create_task(update_board())

    
    async def log(self, msg, file=None):
        log_channel: TextChannel = self.guild.get_channel(cfg.LOG_CHANNEL)
        await log_channel.send("[" + dt.now().strftime("%Y-%m-%d, %H:%M") + "] " + msg + " ( ©️ .discord.gg/clouddev)", file=file)



ticketbot = init_client()
# Event ###############################################################################################################################

# @ticketbot.event
# async def on_voice_state_update(member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
#     if not member.bot:
#         guild: discord.Guild = ticketbot.get_guild(cfg.GUILD_ID)
#         stream_role: discord.Role = guild.get_role(cfg.SUPPORTSTREAM)
#         if not after.channel: 
#             await member.remove_roles(stream_role)
#         elif after.channel.category == await get_cat_by_name(guild, "» 𝐒𝐔𝐏𝐏𝐎𝐑𝐓 𝐆𝐄𝐒𝐏𝐑Ä𝐂𝐇𝐄 «"): 
#             await member.add_roles(stream_role)

# Defines  ###############################################################################################################################

def save_ticket_file(data): 
    with open("tickets.json", "w", encoding="utf-8") as f: 
        json.dump(data, f)

def append_msg_to_ticket(ticket_id, message: discord.Message):
    with open("tickets.json", "r", encoding="utf-8") as file: 
        data = json.load(file)
        tickets = data["tickets"]

    new_tickets: list = []
    for ticket in tickets: 
        data_ticket = None
        if int(ticket["ticket_id"]) == int(ticket_id): 
            messages: list = ticket["messages"]
            messages.append(
                {
                    "author_name": message.author.global_name,
                    "author_img_url": message.author.avatar.url or message.author.default_avatar.url, 
                    "message": message.content, 
                    "created_at": message.created_at.strftime("am %d.%m.%Y um %H:%M Uhr")
                }
            )
            data_ticket = {
                "ticket_name": ticket["ticket_name"], 
                "ticket_id":  ticket["ticket_id"], 
                "creator_name": ticket["creator_name"], 
                "creator_id": ticket["creator_id"], 
                "status": ticket["status"],
                "messages": messages
            }
        else: 
            data_ticket = ticket

        new_tickets.append(data_ticket)

     
    jsonData = {
        "board": BOARD_ID, 
        "tickets": new_tickets
    }
    save_ticket_file(jsonData)

def append_to_database(ticket, creator):
    with open("tickets.json", "r", encoding="utf-8") as file: 
        data = json.load(file)
        tickets: list = data["tickets"]
        status = ""
        if "todo" in ticket.name: 
            status = "todo"
        newTicket = {
            "ticket_name": ticket.name, 
            "ticket_id": ticket.id, 
            "creator_name": creator.name, 
            "creator_id": creator.id, 
            "status": status, 
            "messages": [
                #msg obj
            ]
        }
        tickets.append(newTicket)
        jsonData = {
            "board": BOARD_ID, 
            "tickets": tickets
        }
        save_ticket_file(jsonData)

def remove_from_database(ticket_id):
    jsonData = None
    with open("tickets.json", "r",  encoding="utf-8") as file: 
        data = json.load(file)
        tickets: list = data["tickets"]
        for ticket in tickets: 
            if ticket["ticket_id"] == ticket_id: 
                tickets.remove(ticket)
                
        jsonData = {
            "board": BOARD_ID, 
            "tickets": tickets
        }
        save_ticket_file(jsonData)

def check_ticket_status(ticket_id):
    with open("tickets.json", "r", encoding="utf-8") as file: 
        data = json.load(file)
        tickets: list = data["tickets"]
        for ticket in tickets: 
            if ticket["ticket_id"] == ticket_id: 
                status = ticket["status"]
                new_status = ''

                if status == 'help_needed':
                    new_status = '🟥 Hilfe benötigt'
                elif status == 'todo':
                    new_status = '🟨 To-Do'
                elif status == 'clarify':
                    new_status = '🟧 Klärung'
                elif status == 'live_test':
                    new_status = '🟪 Test angefordert'
                elif status == 'done':
                    new_status = '🟩 Fertig'

                return new_status

def change_ticket_status(status, ticket_id):
    with open("tickets.json", "r", encoding="utf-8") as file: 
        data = json.load(file)
        tickets: list = data["tickets"]
        for ticket in tickets: 
            if ticket["ticket_id"] == ticket_id: 
                ticket["status"] = status
                jsonData = {
                    "board": BOARD_ID,
                    "tickets": tickets
                }
                save_ticket_file(jsonData)
                break

def get_ticket_owner(ticket_id):
    with open("tickets.json", "r", encoding="utf-8") as file: 
            data = json.load(file)
            tickets: list = data["tickets"]
            for ticket in tickets: 
                if int(ticket["ticket_id"]) == int(ticket_id): 
                    owner = ticket["creator_id"]
                    return owner

def get_ticket_name(ticket_id): 
    with open("tickets.json", "r", encoding="utf-8") as f: 
        data = json.load(f)
        tickets: list = data["tickets"]
        for ticket in tickets: 
            if ticket["ticket_id"] == ticket_id: 
                name = ticket["ticket_name"]
                return name
            
def get_highest_role(guild, author):
    teamler_roles = []
    highest_role = None

    for role in author.roles:
        teamler_roles.append(int(role.id))

    highest_role = discord.utils.get(guild.roles, id=teamler_roles[-1])

    if '*' in highest_role.name:
        highest_role = discord.utils.get(guild.roles, id=teamler_roles[-2])
        
    return highest_role

def get_messages(ticket_id):
    with open("tickets.json", "r", encoding="utf-8") as f: 
        data = json.load(f)
        tickets = data["tickets"]
        for t in tickets: 
            if int(t["ticket_id"]) == int(ticket_id): 
                return t["messages"]
        else: 
            return False

def is_ticket(ticket_id): 
    with open("tickets.json", "r", encoding="utf-8") as f: 
        json_data = json.load(f)
        tickets = json_data["tickets"]
        for ticket in tickets: 
            if int(ticket["ticket_id"]) == int(ticket_id): 
                return True
        else: 
            return False

def add_timeout(user_id): 
    with open("timeouts.json", "r", encoding="utf-8") as file:
        data = json.load(file)
        timeouts = data["timeouts"] 
        timeout = {
            "user_id": user_id, 
            "timeout_at": dt.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        timeouts.append(timeout)
        with open("timeouts.json", "w", encoding="utf-8") as f: 
            jsondata = {
                "timeouts": timeouts
            }
            json.dump(jsondata, f)

def is_in_timeout(user_id): 
    with open("timeouts.json", "r", encoding="utf-8") as f: 
        data = json.load(f)
        timeouts = data["timeouts"]
        for timeout in timeouts: 
            if int(timeout["user_id"]) == int(user_id): 
                return True
        else: 
            return False

        
# Asyncs    ##############################################################################################################################
        
async def create_transcript(interaction: discord.Interaction): 
    ch: TextChannel = interaction.channel
    name = ch.name
    fileName = name + ".html"
    
    message_list: list = get_messages(ch.id)
    if not message_list: 
        message_list = [
            {
                "author_img_url": "https://cdn.discordapp.com/attachments/1131591673869250590/1137685066928103494/LogoGreenVersion1.png", 
                "author_name": "SR | System#9947", 
                "created_at": dt.now().strftime("am %d.%m.%Y um %H:%M Uhr"),
                "message": "<span style='color: red; font-weight: 100;'>Das Ticket wurde ohne Nachricht geschlossen. Wenn das unbeabsichtigt war, informiere bitte den Support!</span>"
            }
        ]
    messages = ""
    for m in message_list: 
        messages = messages + f'''\r\n
            <div class="message">\r\n
                <img class="author_avatar" src={m["author_img_url"]}>
                <p class="author_name">{m["author_name"]}</p>
                <p class="msg_written_at">{m["created_at"]}</p>
                <p class="msg">{m["message"]}</p>
            </div>
        '''

    with open(fileName, "w", encoding="utf-8") as file:
        file.write('''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta http-equiv="X-UA-Compatible" content="IE=edge">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>''' + ch.name + '''</title>
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Montserrat:ital,wght@0,100;0,200;0,300;0,400;0,500;0,600;0,700;0,800;0,900;1,100;1,200;1,300;1,400;1,500;1,600;1,700;1,800;1,900&display=swap');

                :root {
                    --maincolor: #F39D00;
                }

                body {
                    margin: 0;
                    padding: 0;
                    overflow: hidden;
                    color: #dcddde;
                    font-family: 'Montserrat', sans-serif;
                    background-color: #36393f;
                }

                .title {
                    position: absolute;
                    left: 50%;
                    transform: translate(-50%, -50%);
                    top: 3%;
                    font-size: xx-large;
                }

                .powered {
                    position: absolute;
                    left: 50%;
                    transform: translate(-50%, 50%);
                    bottom: 1%;
                    font-size: xx-large;
                }

                .colored {
                    color: var(--maincolor);
                }

                .msgs {
                    position: absolute;
                    top: 50%;
                    left: 50%;
                    transform: translate(-50%, -50%);
                    height: 85vh;
                    width: 39.06vw;
                    display: flex;
                    flex-direction: column;
                    overflow-y: auto;
                    overflow-x: hidden;
                    box-sizing: content-box;
                }

                .msgs::-webkit-scrollbar {
                    width: 1vh;
                }
                
                .msgs::-webkit-scrollbar-track {
                    border-radius: 3vw;
                    background: #F39D00;
                }
                
                .msgs::-webkit-scrollbar-thumb {
                    border-radius: 3vw;
                    background: var(--maincolor);
                    transition: .5s;
                }

                .message {
                    position: relative;
                    padding: 0.52vw;
                    background-color: #2f3136;
                    border-radius: 1vh;
                    margin: 0.52vw;
                    width: 35.06vw;
                    min-width: 35.06vw;
                    max-width: 35.06vw;
                    left: 50%;
                    transform: translateX(-50%);
                }

                .author_avatar {
                    position: absolute;
                    width: 4vh;
                    height: 4vh;
                    border-radius: 50%;
                    left: 2%;
                    margin-right: 1vh;
                }

                .author_name {
                    position: absolute;
                    font-weight: 500;
                    margin-right: 0.26vw;
                    margin-top: 1vh;
                    left: 10%;
                }

                .msg_written_at {
                    position: absolute;
                    font-size: 1.2vh;
                    color: #747f8d;
                    margin-top: 1.2vh;
                    right: 5%;
                }

                .msg {
                    margin-top: 8%;
                    line-break: anywhere;
                }
            </style>
        </head>
        <body>
            <span class="title">'''+ ch.name + '''</span>
            <p class="powered">Powered by <span class="colored">Sundown-Rising</span></p>
            <div class="msgs"> ''' + 
                messages
        + '''</div>
        </body>
        </html>
        ''')   

    file = discord.File(fileName)
    embed=discord.Embed(title='Ticketsystem :envelope_with_arrow:', description=f'Das Teammitglied <@{interaction.user.id}> (*{get_highest_role(interaction.guild, interaction.user)}*) hat dein Ticket geschlossen!', color=cfg.HEX)
    embed.set_author(name='Sundown-Rising', icon_url='https://cdn.discordapp.com/attachments/1131591673869250590/1137685066928103494/LogoGreenVersion1.png')
    embed.set_footer(text='Powered by Sundown-Rising', icon_url='https://cdn.discordapp.com/attachments/1131591673869250590/1137685066928103494/LogoGreenVersion1.png')
    embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/1131591673869250590/1137685066928103494/LogoGreenVersion1.png')
    owner_id = get_ticket_owner(interaction.channel.id)
    owner: discord.Member = interaction.guild.get_member(owner_id)
    log_channel: TextChannel = interaction.guild.get_channel(cfg.LOG_CHANNEL)
    await log_channel.send(content="[" + dt.now().strftime("%Y-%m-%d, %H:%M") + "] Transcript " + interaction.channel.name +" ( ©️ .discord.gg/clouddev)", file=file)
    file = discord.File(fileName)
    if owner: 
        try: 
            await owner.send(embed=embed, file=file)
        except Exception as e: 
            await ch.send(f"{owner.mention}\r\n Melde dich im Support, wenn du das Transcript erhalten möchtest. Vielen Dank!")
            await a.sleep(4)
        await a.sleep(1)
        os.remove(f'{ch.name}.html')

async def update_board():
    await ticketbot.change_presence(
        activity=discord.Game('Sundown-Rising'), status=discord.Status.online)   
    while True: 
        global BOARD_ID, BOARD_CHANNEL
        if BOARD_CHANNEL:
            help_needed = []
            todo = []
            clarify = []
            live_test = []
            done = []

            with open("tickets.json", "r", encoding="utf-8") as file: 
                data = json.load(file)
                tickets = data["tickets"]
            
            for ticket in tickets: 
                status = ticket["status"]
                ticket_id = ticket["ticket_id"]
                channel: discord.TextChannel = ticketbot.guild.get_channel(ticket_id)
                if channel: 
                    if status == 'help_needed':
                        help_needed.append(ticket_id)
                    elif status == 'todo':
                        todo.append(ticket_id)
                    elif status == 'clarify':
                        clarify.append(ticket_id)
                    elif status == 'live_test':
                        live_test.append(ticket_id)
                    elif status == 'done':
                        done.append(ticket_id)
                else: 
                    tickets.remove(ticket)
                    json_data = {
                        "board": BOARD_ID, 
                        "tickets": tickets
                    }
                    with open("tickets.json", "w", encoding="utf-8") as file: 
                        json.dump(json_data, file)
                    

            red = ''
            for c in help_needed:
                red = red + f'-> <#{c}>\n' 

            yellow = ''
            for c in todo:
                yellow = yellow + f'-> <#{c}>\n'

            orange = ''
            for c in clarify:
                orange = orange + f'-> <#{c}>\n' 

            purple = ''
            for c in live_test:
                purple = purple + f'-> <#{c}>\n' 

            green = ''
            for c in done:
                green = green + f'<#{c}>\n' 
            
            embed=discord.Embed(title='Ticketboard', description=f'Hier findest du das Sundown-Rising Ticketboard', color=cfg.HEX)
            embed.add_field(name="🟥 Hilfe benötigt", value=red, inline=True)
            embed.add_field(name="🟨 To-Do", value=yellow, inline=True)
            embed.add_field(name="🟧 Klärung", value=orange, inline=True)
            embed.add_field(name="🟪 Test angefordert", value=purple, inline=True)
            embed.add_field(name="🟩 Fertig", value=green, inline=True)
            embed.set_author(name='Sundown-Rising', icon_url='https://cdn.discordapp.com/attachments/1131591673869250590/1137685066928103494/LogoGreenVersion1.png')
            embed.set_footer(text='Powered by Sundown-Rising', icon_url='https://cdn.discordapp.com/attachments/1131591673869250590/1137685066928103494/LogoGreenVersion1.png')
            embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/1131591673869250590/1137685066928103494/LogoGreenVersion1.png') 
            channel: discord.TextChannel = ticketbot.guild.get_channel(BOARD_CHANNEL)
            if BOARD_ID:
                try:
                    msg: discord.Message = await channel.fetch_message(BOARD_ID)
                    await msg.edit(embed=embed)
                    BOARD_ID = msg.id
                    BOARD_CHANNEL = msg.channel.id
                except: 
                    BOARD_ID = None 
                    BOARD_CHANNEL = None
            else: 
                msg = await channel.send(embed=embed)
                BOARD_ID = msg.id

        with open("tickets.json", "r", encoding="utf-8") as file: 
            data = json.load(file)
            tickets = data["tickets"]
            jsonData = {
                "board": {"id": BOARD_ID, "channel_id": BOARD_CHANNEL},
                "tickets": tickets
            }
            save_ticket_file(jsonData)

        with open("timeouts.json", "r", encoding="utf-8") as f: 
            data = json.load(f)
            timeouts = data["timeouts"]
            for timeout in timeouts: 
                timeout_at_str = timeout["timeout_at"]
                timeout_at = dt.strptime(timeout_at_str, "%Y-%m-%d %H:%M:%S") #2023-07-17 01:35:38.326599
                seconds = int((dt.now()-timeout_at).total_seconds())
                if seconds > 600: 
                    timeouts.remove(timeout)
                    with open("timeouts.json", "w", encoding="utf-8") as f: 
                        jsondata = {
                            "timeouts": timeouts
                        }
                        json.dump(jsondata, f)
        await a.sleep(6)

# Commands ###############################################################################################################################´
#  denied: discord.Role = interaction.guild.get_role(cfg.DENIED)
#      
#                                     else: 
#                                           


@ticketbot.hybrid_command(name="load", with_app_command=True, description="Loads a Cog-Extension")
@app_commands.guilds(discord.Object(id=cfg.GUILD_ID))
async def self(ctx): 
    if has_perm(ctx.author, "load"): 
        pass
    else: 
        await ctx.reply("Dir fehlen dafür die nötigen Berechtigungen", ephemeral=True)

@ticketbot.hybrid_command(name="embed", with_app_command=True, description="Send a Customized-Embed")
@app_commands.guilds(discord.Object(id=cfg.GUILD_ID))
async def self(ctx: commands.Context):
    if has_perm(ctx.author, "embed"): 
        modal = Modular(
                inputs=[
                    ui.TextInput(label="Titel", placeholder="Gebe deinen Titel ein...", style=discord.TextStyle.short),
                    ui.TextInput(label="Nachricht", placeholder="Gebe deinen Embed-Content ein...", style=discord.TextStyle.paragraph),
                    ui.TextInput(label="Bild", placeholder="Gebe deine Bild-URL ein...", style=discord.TextStyle.long, required=False)
                ], title="Erstelle dein Embed", custom_id="embed_creator", cb=embedModularCallback
        )
        await ctx.interaction.response.send_modal(modal)
    else: 
        await ctx.reply("Dir fehlen die nötigen Berechtigungen")

@ticketbot.hybrid_command(name="clear", with_app_command=True, description="Clear messages of a selected channel.")
@app_commands.guilds(discord.Object(id=cfg.GUILD_ID))
async def self(ctx, channel: discord.TextChannel = None, count: int = None ):
    if has_perm(ctx.author, "clear"):
        await ctx.reply(f"We will clear {count} messages.", ephemeral=True)
        if not channel: 
            channel = ctx.message.channel
        count = count if count else 1
        if count < 101: 
            await channel.purge(limit=count+1)
        else: 
            count = 100
            await channel.purge(limit=count)
        
        await ctx.send(f"{count} messages cleared successfully.", ephemeral=True)
    else: 
        await ctx.reply("Dir fehlen dafür die nötigen Berechtigungen", ephemeral=True)

@ticketbot.hybrid_command(name="warning", with_app_command=True, description="Send a Warning")
@app_commands.guilds(discord.Object(id=cfg.GUILD_ID))
async def self(ctx: commands.Context, member: discord.Member):
    author: discord.Member = ctx.author
    if has_perm(author, "warning"): 
        embed = discord.Embed(title="ACHTUNG", description="" \
        "> Lieber Bürger, \r\n" \
        "> Wir erwarten eine Nachricht innerhalb der nächsten **24 Stunden**. \r\n" \
        "> Sollte dies nicht erfolgen, so sind wir gezwungen das Ticket zu **schließen**." \
        "> \r\n" \
        "> MfG\r\n" \
        "> Ihr Sundown-Rising-Team", 
        color=cfg.HEX)
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1131591673869250590/1137685066928103494/LogoGreenVersion1.png")
        embed.set_footer(text="Copyright by Sundown-Rising", icon_url="https://cdn.discordapp.com/attachments/1131591673869250590/1137685066928103494/LogoGreenVersion1.png")

        await ctx.reply("Du hast den User " + member.mention + " erfolgreich erwähnt.", ephemeral=True)
        msg: discord.Message = await ctx.channel.send(embed=embed)
        await msg.reply(member.mention)
    else: 
        await ctx.reply("Dir fehlen dafür die nötigen Berechtigungen", ephemeral=True)

@ticketbot.event
async def on_message(message):
    ticket_list = []
    channel_history = []
    latest_msg = None
    ticketbot.guild = ticketbot.get_guild(cfg.GUILD_ID)
    team_role: Role = ticketbot.guild.get_role(cfg.TEAM_ROLE)

    if not message.author.bot and is_ticket(message.channel.id):
        append_msg_to_ticket(message.channel.id, message)
        if message.guild == ticketbot.guild: 
            latest_msg = message.channel.last_message

            if team_role:
                if team_role in message.author.roles:
                    if message.channel.id in ticket_list:
                        if int(latest_msg.author.id) == int(get_ticket_owner(message.channel.id)):
                            tz = pytz.timezone('Europe/Berlin')

                            latest_msg_written = latest_msg.created_at.replace(tzinfo=pytz.UTC).astimezone(tz)
                            time_now = dt.now(pytz.UTC).astimezone(tz)
                            time_difference = (time_now - latest_msg_written).total_seconds()
                            if time_difference >= 900:
                                owner_id = get_ticket_owner(message.channel.id)
                                owner = await ticketbot.fetch_user(int(owner_id))
                                embed = discord.Embed(title='Ticketsystem :envelope_with_arrow:', description=f'Das Teammitglied <@{message.author.id}> (*{get_highest_role(message.guild, message.author)}*) hat auf dein Ticket geantwortet!\nTicket: <#{message.channel.id}>', color=cfg.HEX)
                                embed.set_author(name='Sundown-Rising ☁️', icon_url='https://cdn.discordapp.com/attachments/1131591673869250590/1137685066928103494/LogoGreenVersion1.png')
                                embed.set_footer(text='Powered by Sundown-Rising', icon_url='https://cdn.discordapp.com/attachments/1131591673869250590/1137685066928103494/LogoGreenVersion1.png')
                                embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/1131591673869250590/1137685066928103494/LogoGreenVersion1.png')
                                await owner.send(embed=embed)

@ticketbot.hybrid_command(name="ticket_msg", with_app_command=True, description="Sendet die Ticket Nachricht")
@app_commands.guilds(discord.Object(id=cfg.GUILD_ID))
async def self(ctx: commands.Context, channel: discord.TextChannel=None):
    channel = channel if channel else ctx.channel
    if has_perm(ctx.author, "ticket_msg"):
        embed1 = discord.Embed(title="Neues Ticket", description="Bitte wähle ein Thema aus, zu welchem du uns ein Ticket senden möchtest.", color=cfg.HEX, timestamp=dt.now())
        embed1.add_field(name="**__Support-Ticket:__**", value = '''Wenn du technische Hilfe oder Unterstützung benötigst, wähle diese Option. Unsere Support-Mitarbeiter werden sich darum kümmern
                                                                dein Anliegen so schnell wie möglich zu bearbeiten und dir bei der Lösung deines Problems zu helfen.\r\n''', inline=False)
        embed1.add_field(name="**__Gewerbe-Ticket:__**", value = '''Wenn du Fragen oder Anliegen zu deines Gewerbes hast oder ein neues Gewerbe anmelden möchtest.
                                                                Unser Team wird dir dabei helfen, deine geschäftlichen Anforderungen zu erfüllen und eventuelle Probleme zu lösen.\r\n''', inline=False)
        
        embed1.add_field(name="**__Bug-Ticket:__**", value = '''Wenn du auf ein technisches Problem, einen Fehler oder eine Fehlfunktion gestoßen bist, wähle diese Option.
                                                            Durch die Erstellung eines Bug-Tickets hilfst du uns, potenzielle Probleme zu identifizieren und zu beheben, um eine bessere Benutzererfahrung für alle zu gewährleisten.
                                                            Bitte beschreibe den Fehler oder die Fehlfunktion so detailliert wie möglich, damit wir ihn effektiv reproduzieren und beheben können.\r\n''', 
                    inline=False)
        embed1.add_field(name="**__Native-Ticket:__**", value = '''Wenn es ein Problem gibt, welches nur Natives betrifft und kein Bug ist. Durch die Erstellung eines Native-Tickets kannst du z.B den Job
                                                                    als Native Spieler beantragen und mit unsere Community-Mangerin für Natives reden. Dort geht es hauptäshclich um Ideen oder Community-technische Probleme.\r\n''', 
        inline=False)
        embed1.add_field(name="**Vielen Dank für deine Auswahl!**", value="Sobald du das Thema ausgewählt hast, füge bitte weitere Informationen hinzu, damit wir dein Anliegen besser verstehen und angemessen darauf reagieren können.\r\n")
        embed1.set_author(name='Herzlich Willkommen', icon_url='https://cdn.discordapp.com/attachments/1131591673869250590/1137685066928103494/LogoGreenVersion1.png')
        embed1.set_footer(text='Powered by Sundown-Rising', icon_url='https://cdn.discordapp.com/attachments/1131591673869250590/1137685066928103494/LogoGreenVersion1.png')
        embed1.set_thumbnail(url='https://cdn.discordapp.com/attachments/1131591673869250590/1137685066928103494/LogoGreenVersion1.png')
        ticketdropdown = View(items=[
                                DiscordButton(label="Support", style=discord.ButtonStyle.blurple, custom_id="ticket_support_prev", cb=TicketCheckCallback, emoji="🛡️"), 
                                DiscordButton(label="Bug", style=discord.ButtonStyle.red, custom_id="ticket_bug_prev", cb=TicketCheckCallback, emoji="🐞"),
                                DiscordButton(label="Gewerbe", style=discord.ButtonStyle.green, custom_id="ticket_gewerbe_prev", cb=TicketCheckCallback, emoji="🏡"), 
                                DiscordButton(label="Natives", style=discord.ButtonStyle.gray, custom_id="ticket_native_prev", cb=TicketCheckCallback, emoji="🦅")
                            ])

        embed=discord.Embed(title='Ticketsystem :envelope_with_arrow:', description=f'Wähle unten aus, welches Ticket du erstellen willst', color=cfg.HEX, timestamp=dt.now())
        embed.set_author(name='Sundown-Rising 🌅', icon_url='https://cdn.discordapp.com/attachments/1131591673869250590/1137685066928103494/LogoGreenVersion1.png')
        embed.set_footer(text='Powered by Sundown-Rising', icon_url='https://cdn.discordapp.com/attachments/1131591673869250590/1137685066928103494/LogoGreenVersion1.png')
        embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/1131591673869250590/1137685066928103494/LogoGreenVersion1.png')
        await channel.send(embed=embed1)
        await channel.send(embed=embed, view=ticketdropdown)
        await ctx.reply(f'Die Ticket Nachricht wurde in {channel.mention} gesendet!', ephemeral=True)
    else: 
        await ctx.reply("Dir fehlen dafür die nötigen Berechtigungen", ephemeral=True)

@ticketbot.hybrid_command(name="change_status", with_app_command=True, description="Ändere den Status eines Tickets")
@app_commands.guilds(discord.Object(id=cfg.GUILD_ID))
@app_commands.choices(status=[
    app_commands.Choice(name="🟥 Hilfe benötigt", value="help_needed"),
    app_commands.Choice(name="🟨 To-Do", value="todo"),
    app_commands.Choice(name="🟧 Klärung", value="clarify"),
    app_commands.Choice(name="🟪 Test angefordert", value="live_test"),
    app_commands.Choice(name="🟩 Fertig", value="done"),
])
async def self(ctx: commands.Context, status: app_commands.Choice[str], ping: discord.Member = None):
    if has_perm(ctx.author, "change_status"):
        await ctx.reply(f'Das Ticket {ctx.channel.mention} wurde von *{check_ticket_status(ctx.channel.id)}* in *{status.name}* versetzt!', ephemeral=True)
        embed=discord.Embed(title='Ticketsystem :envelope_with_arrow:', description=f'Das Teammitglied <@{ctx.author.id}> (*{get_highest_role(ctx.guild, ctx.author)}*) hat dein Ticket <#{ctx.channel.id}> von  *{check_ticket_status(ctx.channel.id)}* in *{status.name}* versetzt!', color=cfg.HEX)
        embed.set_author(name='Sundown-Rising ☁️', icon_url='https://cdn.discordapp.com/attachments/1131591673869250590/1137685066928103494/LogoGreenVersion1.png')
        embed.set_footer(text='Powered by Sundown-Rising', icon_url='https://cdn.discordapp.com/attachments/1131591673869250590/1137685066928103494/LogoGreenVersion1.png')
        embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/1131591673869250590/1137685066928103494/LogoGreenVersion1.png')
        owner = await ticketbot.fetch_user(int(get_ticket_owner(ctx.channel.id)))
        await owner.send(embed=embed)

        if ping: 
            await ctx.channel.send(ping.mention)
        change_ticket_status(status.value, ctx.channel.id)
    else: 
        await ctx.reply("Dir fehlen dafür die nötigen Berechtigungen", ephemeral=True)

@ticketbot.hybrid_command(name="send_board", with_app_command=True, description="Sende das Sundown-Rising Ticketboard")
@app_commands.guilds(discord.Object(id=cfg.GUILD_ID))
async def self(ctx: commands.Context, channel: discord.TextChannel=None):
    channel = channel if channel else ctx.channel
    if has_perm(ctx.author, "send_board"):
        await ctx.reply(f'Das Sundown-Rising Ticketboard wurde in {channel.mention} gesendet!', ephemeral=True)
        global BOARD_CHANNEL
        BOARD_CHANNEL = channel.id
    else: 
        await ctx.reply("Dir fehlen dafür die nötigen Berechtigungen", ephemeral=True)

@ticketbot.hybrid_command(name="restart", with_app_command=True, description="Restartet den Bot")
@app_commands.guilds(discord.Object(id=cfg.GUILD_ID))
async def self(ctx: commands.Context): 
    if has_perm(ctx.author, "restart"): 
        os.execv(sys.executable, ['python'] + sys.argv)
    else: 
        await ctx.reply("Dir fehlen dafür die nötigen Berechtigungen", ephemeral=True)

@ticketbot.hybrid_command(name="custom_ticket", with_app_command=True, description="Erstellt ein Custom-Ticket")
@app_commands.guilds(discord.Object(id=cfg.GUILD_ID))
async def self(ctx: commands.Context, title: str, member: discord.Member, pl_only: bool): 
    if has_perm(ctx.author, "custom_ticket"):
            guild: discord.Guild = ctx.guild    
            category = await get_cat_by_name(guild, cfg.TICKET_CATEGORIES[4])
            ticket_channel = await guild.create_text_channel(title, category=category)
            await ctx.interaction.response.send_message(f"Dein Ticket wurde erstellt! {ticket_channel.mention}", ephemeral=True)
            if not pl_only:
                await ticket_channel.set_permissions(guild.get_role(cfg.TEAM_ROLE), send_messages=True, read_messages=True, add_reactions=False,
                                                    embed_links=True, attach_files=True, read_message_history=True,
                                                    external_emojis=True, view_channel=True, manage_channels=True)
            await ticket_channel.set_permissions(member, send_messages=True, read_messages=True, add_reactions=False,
                                                embed_links=True, attach_files=True, read_message_history=True,
                                                external_emojis=True, view_channel=True)
            await ticket_channel.set_permissions(guild.default_role, send_messages=False, read_messages=False, add_reactions=False,
                                                embed_links=False, attach_files=False, read_message_history=False,
                                                external_emojis=False, view_channel=False)                                                    
            embed=discord.Embed(title='Ticketsystem :envelope_with_arrow:', description=f'{member.mention} Es wurde ein Ticket erstellt, welches dich betrifft. Es meldet sich bald jemand!', color=cfg.HEX)
            embed.set_author(name='Sundown-Rising', icon_url='https://cdn.discordapp.com/attachments/1131591673869250590/1137685066928103494/LogoGreenVersion1.png')
            embed.set_footer(text='Powered by Sundown-Rising', icon_url='https://cdn.discordapp.com/attachments/1131591673869250590/1137685066928103494/LogoGreenVersion1.png')
            embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/1131591673869250590/1137685066928103494/LogoGreenVersion1.png')
            view = View(items=[
                    DiscordButton(label="Claim", style=discord.ButtonStyle.green, custom_id="ticket_claim", cb=claimTicket, emoji="🤚"),
                    DiscordButton(label="Close", style=discord.ButtonStyle.red, custom_id="ticket_close", cb=closeTicket, emoji="🔒")
                    ])
            await ticket_channel.send(embed=embed, view=view)
            await ticket_channel.send(f"{member.mention}")
            append_to_database(ticket_channel, ctx.author)
    else: 
        await ctx.reply("Dir fehlen dafür die nötigen Berechtigungen", ephemeral=True)

@ticketbot.hybrid_command(name="ticket_add", with_app_command=True, description="")
@app_commands.guilds(discord.Object(id=cfg.GUILD_ID))
async def self(ctx: commands.Context, member: discord.Member): 
    if has_perm(ctx.author, "ticket_add"):
        if is_ticket(ctx.channel.id):
            await ctx.channel.set_permissions(member, send_messages=True, read_messages=True, add_reactions=True,
                                        embed_links=True, attach_files=True, read_message_history=True,
                                        external_emojis=True)
            await ctx.interaction.response.send_message(f"Du hast den Spieler {member.mention} erfolgreich hinzugefügt.", ephemeral=True)

            try:
                embed=discord.Embed(title='Ticketsystem :envelope_with_arrow:', description=f'{member.mention} Du wurdest einem Ticket hinzugefügt. Schau jetzt rein: {ctx.channel.jump_url}', color=cfg.HEX)
                embed.set_author(name='Sundown-Rising', icon_url='https://cdn.discordapp.com/attachments/1131591673869250590/1137685066928103494/LogoGreenVersion1.png')
                embed.set_footer(text='Powered by Sundown-Rising', icon_url='https://cdn.discordapp.com/attachments/1131591673869250590/1137685066928103494/LogoGreenVersion1.png')
                embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/1131591673869250590/1137685066928103494/LogoGreenVersion1.png')
                await member.send(embed=embed)
            except: 
                pass
        else: 
            await ctx.interaction.response.send_message(f"Das ist kein Ticket!")
    else: 
        await ctx.reply("Dir fehlen dafür die nötigen Berechtigungen", ephemeral=True)

@ticketbot.hybrid_command(name="ticket_remove", with_app_command=True, description="")
@app_commands.guilds(discord.Object(id=cfg.GUILD_ID))
async def self(ctx: commands.Context, member: discord.Member): 
    if has_perm(ctx.author, "ticket_remove"):
        if is_ticket(ctx.channel.id):
            await ctx.channel.set_permissions(member, send_messages=False, read_messages=False, add_reactions=False,
                                        embed_links=False, attach_files=False, read_message_history=False,
                                        external_emojis=False)
            await ctx.interaction.response.send_message(f"Du hast den Spieler {member.mention} erfolgreich entfernt.", ephemeral=True)
        else: 
            await ctx.interaction.response.send_message(f"Das ist kein Ticket!")
    else: 
        await ctx.reply("Dir fehlen dafür die nötigen Berechtigungen", ephemeral=True)

@ticketbot.hybrid_command(name="create_team_data", with_app_command=True, description="Erstellt eine Kategorie für einen Teamler")
@app_commands.guilds(discord.Object(id=cfg.GUILD_ID))
async def self(ctx: commands.Context, member: discord.Member, emoji: str): 
    if has_perm(ctx.author, "create_team_data"): 
        team: Role = ctx.guild.get_role(cfg.TEAM_ROLE)
        if team in member.roles:
            with open("team_data.json", "r", encoding="utf-8") as file: 
                data = json.load(file)
            
            data = data["team_data"]

            for dataset in data:
                if dataset["member_id"] == member.id:
                    await ctx.reply("Das Teamitglied hat bereits eine angelegte Data", ephemeral=True)
                    return
            

            cat_name = "» "
            nick = ""
            try: 
                nick = (member.nick).split("|")[1]
            except: 
                try: 
                    nick = (member.nick).split("I")[1]
                except: 
                    nick = member.nick
            for l in nick: 
                for i, _l in enumerate(cfg.FONTSET): 
                    if l.upper() == _l:
                        try:
                            cat_name = cat_name + cfg.FONTSET[i+1]
                        except: 
                            pass

            cat_name = cat_name + " «"

            if not await get_cat_by_name(ctx.guild, cat_name):
                cat = await ctx.guild.create_category(name=cat_name)
                await cat.set_permissions(ctx.guild.get_role(cfg.TEAM_ROLE), send_messages=True, read_messages=True, add_reactions=False,
                                                      embed_links=True, attach_files=True, read_message_history=True,
                                                      external_emojis=True, manage_channels=True)
                await cat.set_permissions(ctx.guild.default_role, send_messages=False, read_messages=False, add_reactions=False,
                                                embed_links=False, attach_files=False, read_message_history=False,
                                                external_emojis=False) 

                dataset = {
                    "member_id": member.id, 
                    "member_nick": member.nick,
                    "member_cat_name": cat_name, 
                    "member_cat_id": cat.id, 
                    "emoji": emoji
                }

                data.append(dataset)

                with open("team_data.json", "w", encoding="utf-8") as f: 
                    jsonDATA = {
                        "team_data": data
                    }
                    json.dump(jsonDATA, f)

                await ctx.reply(f"Team-Data von {member.mention} erfolgreich erstellt", ephemeral=True)
            else: 
                await ctx.reply("Diese Kategorie existiert bereits.")
        else: 
            await ctx.reply("Dieses Mitglied ist kein Teamler (missing team-role)", ephemeral=True)
    else: 
        await ctx.reply("Dir fehlen dafür die nötigen Berechtigungen", ephemeral=True)

@ticketbot.hybrid_command(name="delete_team_data", with_app_command=True, description="Erstellt eine Kategorie für einen Teamler")
@app_commands.guilds(discord.Object(id=cfg.GUILD_ID))
async def self(ctx: commands.Context, member: discord.Member):
    with open("team_data.json", "r", encoding="utf-8") as f: 
        data = json.load(f)
        data = data["team_data"]
    
    for dataset in data: 
        if dataset["member_id"] == member.id: 
            cat = await get_cat_by_id(ctx.guild, dataset["member_cat_id"])
            if cat: 
                await cat.delete()
            data.remove(dataset)
            await ctx.reply("Team-Data für " + member.name + " gelöscht.", ephemeral=True)
            break
    else: 
        await ctx.reply("Keine Team-Data für " + member.name + " gefunden.", ephemeral=True)
    
    with open("team_data.json", "w", encoding="utf-8") as f: 
        jsonDATA = {
            "team_data": data
        }
        json.dump(jsonDATA, f)


            # dataset = {
            #     "member_id": member.id, 
            #     "member_nick": member.nick,
            #     "member_cat_name": cat_name, 
            #     "member_cat_id": cat.id, 
            #     "emoji": emoji
            # }

@ticketbot.hybrid_command(name="change_team_data", with_app_command=True, description="Verändert eine bereits bestehende Team-Data")
@app_commands.guilds(discord.Object(id=cfg.GUILD_ID))
async def self(ctx: commands.Context, member: discord.Member, change_name: bool=None, new_emoji: str=None):
    with open("team_data.json", "r", encoding="utf-8") as f: 
        data = json.load(f)
        data = data["team_data"]
    
    for dataset in data: 
        if dataset["member_id"] == member.id: 
            edit_msg = ""
            if change_name:
                cat = await get_cat_by_id(ctx.guild, dataset["member_cat_id"])
                if cat: 
                    cat_name = "» "
                    nick = ""
                    try: 
                        nick = (member.nick).split("|")[1]
                    except: 
                        pass
                    for l in nick: 
                        for i, _l in enumerate(cfg.FONTSET): 
                            if l.upper() == _l:
                                try:
                                    cat_name = cat_name + cfg.FONTSET[i+1]
                                except: 
                                    pass
                    edit_msg = edit_msg + "Kategorie: " + cat_name

                    cat_name = cat_name + " «"
                    await cat.edit(name=cat_name)
            if new_emoji:
                edit_msg = edit_msg + "Emoji: " + new_emoji

            await ctx.reply(f"Team-Data für {member.nick} bearbeitet. ({edit_msg})", ephemeral=True)
            break
    else: 
        await ctx.reply("Keine Team-Data für " + member.name + " gefunden.", ephemeral=True)
    
    with open("team_data.json", "w", encoding="utf-8") as f: 
        jsonDATA = {
            "team_data": data
        }
        json.dump(jsonDATA, f)


@ticketbot.hybrid_command(name="update_team_categories", with_app_command=True, description="Updated die Team-Kategorien oder erstellt sie neu")
@app_commands.guilds(discord.Object(id=cfg.GUILD_ID))
async def self(ctx: commands.Context):
    if has_perm(ctx.author, "update_team_categories"): 
        with open("team_data.json", "r", encoding="utf-8") as file: 
            data = json.load(file)
                
        data = data["team_data"]

        for dataset in data:
            cat = await get_cat_by_id(ctx.guild, dataset["member_cat_id"])
            await cat.set_permissions(ctx.guild.get_role(cfg.TEAM_ROLE), send_messages=True, read_messages=True, add_reactions=False,
                                                      embed_links=True, attach_files=True, read_message_history=True,
                                                      external_emojis=True, manage_channels=True)
            await cat.set_permissions(ctx.guild.default_role, send_messages=False, read_messages=False, add_reactions=False,
                                                embed_links=False, attach_files=False, read_message_history=False,
                                                external_emojis=False) 
    else: 
        await ctx.reply("Dir fehlen dafür die nötigen Berechtigungen", ephemeral=True)

@ticketbot.hybrid_command(name="weiterleiten", with_app_command=True, description="Leitet das Ticket an einen Teamler weiter")
@app_commands.guilds(discord.Object(id=cfg.GUILD_ID))
async def self(ctx: commands.Context, member: discord.Member):
    if has_perm(ctx.author, "weiterleiten"): 
        team: Role = ctx.guild.get_role(cfg.TEAM_ROLE)
        if team in member.roles:
            await redirect(ctx.interaction, member.id)
        else: 
            await ctx.reply("Dieses Mitglied ist kein Teamler (missing team-role)", ephemeral=True)
    else: 
        await ctx.reply("Dir fehlen dafür die nötigen Berechtigungen", ephemeral=True)

@ticketbot.hybrid_command(name="clearticketfiles", with_app_command=True, description="Löscht den Server cache")
@app_commands.guilds(discord.Object(id=cfg.GUILD_ID))
async def self(ctx: commands.Context):
    if has_perm(ctx.author, "clearticketfiles"):
        for file in os.listdir("/home/SR_Bot"):
            if file.endswith(".html"):
                os.remove(file)
        await ctx.reply("Cache erfolgreich gelöscht!", ephemeral=True)
    else: 
        await ctx.reply("Dir fehlen dafür die nötigen Berechtigungen", ephemeral=True)
# END ##############################################################################################################################

if __name__ == "__main__":
    ticketbot.run(cfg.TOKEN)