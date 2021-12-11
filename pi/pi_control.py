#!/usr/bin/env python3
import logging
import threading
import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import pi_server

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(levelname)s %(threadName)s %(name)s %(message)s")
logger = logging.getLogger('PI CONTROLLER')
logger.setLevel(logging.DEBUG)


class PiController:
    _response = None
    _command = None
    _distance_data = None

    def __init__(self):
        logger.error("TEST ERROR")
        self.pi_server = pi_server.PiControlServer(self)
        logger.debug("Server created. Going to start server %s", "TEST")
        self._distance_data = "0"
        threading.Thread(target=self.start_server).start()

    def start_server(self):
        threading.Thread(target=self.pi_server.start_server).start()

    def process_request(self, request):
        if request.get("methode") == "GET":
            if request.get("parameter") == "distance_data":
                self._response = self._response = dict(methode="RESPONSE", description="distance data",
                                                       value=self.distance_data)
                self._distance_data = int(self._distance_data) + 20
        else:
            logger.info("Default response message send")
            self._response = dict(methode="ERROR", parameter="Unknown Methode")

    @property
    def response(self):
        logger.debug("Response %s", self._response)
        return self._response

    @property
    def distance_data(self):
        return self._distance_data

    @distance_data.setter
    def distance_data(self, distance_data):
        if distance_data is isinstance(int):
            logger.debug("New distance data set")
            self._distance_data = distance_data
        else:
            logger.error("New distance data not set. Data not instance of int")


if __name__ == "__main__":
    pi_controller = PiController()

    logger = logging.getLogger('DISCORD BOT')
    logger.setLevel(level=logging.INFO)

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
        embed = discord.Embed(title="GitHub Projekt",
                              description="Ihr findet allen Quellcode in diesem GitHub Repository "
                                          "\n**https://github.com/milantheiss/**", color=0x0998c8)
        await ctx.send(embed=embed)


    bot.run(TOKEN)
