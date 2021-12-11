import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(intents=intents, command_prefix=["eve ", "EVE "])


@bot.event
async def on_ready():
    print("EVE is ready to go")


@bot.event
async def on_message(message):
    if message.content == "VORWÄRTS":
        print("Fahre vorwärts")
        return
    if message.content == "RÜCKWÄRTS":
        print("Fahre vorwärts")
        return

    await bot.process_commands(message)


@bot.command(name='ping')
async def _ping(ctx, args):
    await ctx.send(f'pong {args}')


@bot.command(name="mitwirkende")
async def post_credits(ctx):
    embed_var = discord.Embed(title="Mitwirkende", color=0x0998c8)
    embed_var.add_field(name="Project Lead", value="<@252817187247620097>", inline=False)
    embed_var.add_field(name="EV3 Programmierung", value="<@252817187247620097>", inline=False)
    embed_var.add_field(name="Backend", value="<@252817187247620097>", inline=False)
    embed_var.add_field(name="Radar App", value="<@409660466617516033>", inline=False)
    embed_var.add_field(name="Discord Bot", value="<@252817187247620097> & <@444437469128294411>", inline=False)
    embed_var.add_field(name="Roboter gebaut", value="<@409660466617516033>, <@444437469128294411> & "
                                                     "<@272292540940550145>", inline=False)
    embed_var.add_field(name="Seelische & Mentale Unterstützung", value="<@348424220969140225>", inline=False)
    await ctx.send(embed=embed_var)


@bot.command(name="github")
async def post_github(ctx):
    embed = discord.Embed(title="GitHub Projekt", description="Ihr findet allen Quellcode in diesem GitHub Repository "
                                                              "\n**https://github.com/milantheiss/**", color=0x0998c8)
    await ctx.send(embed=embed)

bot.run(TOKEN)
