import discord
from discord.ext import commands


import asyncio
import functools
import os

from translators import google as tl
from langdetect import detect_langs

#

from dotenv import load_dotenv
load_dotenv()

TOKEN = os.getenv('TOKEN')


#Bot intents:
intents = discord.Intents.default()
intents.members = False
intents.presences = False
intents.typing = False

#Bot
bot = commands.Bot(command_prefix='.', intents=intents)


#Events
@bot.event
async def on_ready():
    print(f"> bot {bot.user.name} ready!")

@bot.event
async def on_message(message):
    if message.author.bot or not message.content or not message.guild: return
    await message.add_reaction('🌎')
    await bot.process_commands(message)

@bot.event
async def on_raw_reaction_add(payload):
    if payload.emoji.name != '🌎' or payload.user_id == bot.user.id or payload.guild_id != 764244286304681995:
        return

    ch = bot.get_channel(payload.channel_id)
    msg = await ch.fetch_message(payload.message_id)

    #Initial checks
    if not msg.content: return
    if len(msg.content) > 1900:
        await ch.send(embed=discord.Embed(description="Error:"
                                                       "Largo máximo del mensaje debe ser 1900 caracteres."
                                                       f"El mensaje contiene {len(msg.content)} caracteres.\n\n"
                                                       f"The message excedes the maximum character count of 1900."
                                                       f"The lenght of the message is {len(msg.content)} chars."))
        return
    string = msg.content

    if not string:
        return

    loop = asyncio.get_running_loop()

    #Languages
    conv = {
        'en': 'es',
        'es': 'en'
    }

    langs = (await loop.run_in_executor(
        None,  # executor
        detect_langs,  # function
        (string) # arguments
    ))
    print(langs)
    try:
        lang = next(l for x in langs if (l := x.lang) in conv.keys())
    except StopIteration:
        await ch.send(embed=discord.Embed(description=f'Language error:\n'
                                                      f"> I couldn't detect english nor spanish in the target message.\n\n"
                                                      f"> No pude detectar inglés ni español en el mensaje especificado"))
        return

    t = await loop.run_in_executor(None,
        functools.partial(tl, string, to_language=conv[lang])
    )

    if lang == 'en':
        title = f"Traducción del mensaje de {msg.author.display_name}"
        t += f"\n\n[link]({msg.jump_url}) al mensaje original"
    elif lang == 'es':
        title = f"Translation from {msg.author.display_name}'s message:"
        t += f"\n\n[link]({msg.jump_url}) to original message"
    else:
        return

    emb = discord.Embed(
        title=title,
        description=t,
        color=0x00FFFF,
    )
    emb.set_thumbnail(url=msg.author.avatar_url)
    emb.set_footer(text=f"{'Solicitado por ' if lang=='en' else 'Solicited by'} {payload.member.display_name}")
    await ch.send(embed=emb)

bot.run(TOKEN)
