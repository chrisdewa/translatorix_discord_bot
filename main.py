import discord
from discord.ext import commands

import asyncio
import functools

from translators import google as tl
from langdetect import detect_langs as dl


TOKEN = "NzY1MDM3NTk4NDY0Mjc4NTI4.X4O-yQ.fA-G2_HbjyGLNIbgpBmhcPzeP_o"


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
async def on_raw_reaction_add(payload):
    if payload.emoji.name != '🌎':
        return

    ch = bot.get_channel(payload.channel_id)
    msg = await ch.fetch_message(payload.message_id)
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

    det_lang = (await loop.run_in_executor(
        None,
        dl,
        (string)
    ))[0].lang

    # Translator
    conv = {
        'en': 'es',
        'es': 'en'
    }

    if det_lang not in conv.keys():
        await ch.send(embed=discord.Embed(description='language error'))
        return

    t = await loop.run_in_executor(None,
        functools.partial(tl, string, to_language=conv[det_lang])
    )

    if det_lang == 'en':
        title = f"Traducción del mensaje de {msg.author.display_name}"
        t += f"\n\n[link]({msg.jump_url}) al mensaje original"
    elif det_lang == 'es':
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
    await ch.send(embed=emb)

bot.run(TOKEN)
