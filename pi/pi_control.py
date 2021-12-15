#!/usr/bin/env python3
import logging
import threading
import os
from time import sleep

import discord
from discord.ext import commands
from dotenv import load_dotenv
import pi_server
import pi_client

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(threadName)s %(name)s %(message)s")
logger = logging.getLogger('PI CONTROLLER')
logger.setLevel(logging.INFO)


class PiController:
    _response = None
    _command = None
    _distance_data = None
    _request_queue = []
    _requesting_thread = None

    def process_request(self, request):
        if request.get("methode") == "GET":
            if request.get("parameter") == "distance_data":
                self._response = dict(methode="RESPONSE", description="distance_data",
                                      value=str(self.distance_data))
        else:
            logger.info("Default response message send")
            self._response = dict(methode="ERROR", parameter="Unknown Methode")

    def process_response(self, response):
        if response.get("methode") == "RESPONSE":
            if response.get("description") == "distance_data":
                try:
                    self.distance_data = round(float(response.get("value")))
                    self.queue_get_distance_data()
                    self._response_received = True
                except ValueError:
                    logger.error("Error while casting response into int. Current value of distance data: %s",
                                 self._distance_data)
            elif response.get("description") == "CONFIRMATION":
                logger.info("EV3 has received to command.")
                self._response_received = True

    def add_request_to_queue(self, methode, parameter):
        self._request_queue.append(dict(methode=methode, parameter=parameter))

    def start_requesting(self):
        def _start_requesting(self):
            self._running = True
            while True:
                self._response_received = False
                _request = self._request_queue.pop(0)
                self.pi_client.send_server_request(_request.get("methode"), _request.get("parameter"))
                sleep(1)
                while self._response_received is False:
                    sleep(1)

        self._requesting_thread = threading.Thread(target=_start_requesting, args=(self,))
        self._requesting_thread.start()

    @property
    def response(self):
        logger.debug("Response %s", self._response)
        return self._response

    @property
    def distance_data(self):
        return self._distance_data

    @distance_data.setter
    def distance_data(self, distance_data):
        if isinstance(self._distance_data, int):
            logger.debug("New distance data set")
            self._distance_data = distance_data
        else:
            logger.error("New distance data not set. Data not instance of int")

    def queue_get_distance_data(self):
        def _queue_get_distance_data(self):
            sleep(0.5)
            self.add_request_to_queue("GET", "distance_data")

        threading.Thread(target=_queue_get_distance_data, args=(self,), daemon=True).start()

    def __init__(self):
        self.pi_server = pi_server.PiControlServer(self)
        self.pi_client = pi_client.PiClient(self)
        self._response_received = False
        logger.debug("Server created. Going to start server")
        self._distance_data = 0
        threading.Thread(target=self.pi_server.start_server).start()
        self.add_request_to_queue("GET", "distance_data")
        self.start_requesting()
        self.queue_get_distance_data()


if __name__ == "__main__":
    pi_controller = PiController()

    ev3_commands_active = True

    logger = logging.getLogger('DISCORD BOT')
    logger.setLevel(level=logging.INFO)

    load_dotenv()
    TOKEN = os.getenv("DISCORD_TOKEN")

    intents = discord.Intents.default()
    intents.members = True
    bot = commands.Bot(intents=intents, command_prefix=["eve ", "EVE "], help_command=None)


    @bot.event
    async def on_ready():
        print("EVE is ready to go")


    @bot.command(name='ping')
    async def _ping(ctx):
        await ctx.send('pong')


    @bot.command(name="mitwirkende")
    async def post_credits(ctx):
        embed_var = discord.Embed(title="Mitwirkende", color=0x0998c8)
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
                                          "\n**https://github.com/milantheiss/ev3-demo**", color=0x0998c8)
        await ctx.send(embed=embed)


    @bot.command(name="vor")
    async def move_forwards(ctx, timeout=None, speed=None):
        global ev3_commands_active
        timeout = int(timeout)
        speed = int(speed)
        if not ev3_commands_active:
            await commands_blocked(ctx)
        elif timeout is None and timeout is None:
            await ctx.send("```Du hast den Command falsch aufgerufen.\neve vor <Zeit> <Prozent>```")
        else:
            if timeout > 15:
                timeout = 15
            elif timeout < 0:
                timeout = 0
            if speed < 0:
                speed = abs(speed)
            if speed > 100:
                speed = 100
            embed = discord.Embed(title="Bewegungsbefehl",
                                  description=f"WALL·E bewegt sich jetzt {timeout} Sekunden mit {speed}% seine Max "
                                              f"Geschwindigkeit vorwärts.", color=0x0998c8)
            if pi_controller.distance_data <= 200:
                embed.add_field(name="Distance Data",
                                value=f"WALL·E meldet Momentan ein Objekt {pi_controller.distance_data} cm vor ihm")
            else:
                embed.add_field(name="Distance Data", value=f"WALL·E meldet Momentan kein Objekt vor ihm")
            if speed > 0 and timeout > 0:
                pi_controller.add_request_to_queue("POST", dict(command="forwards", timeout=timeout, speed=speed))
            await ctx.send(embed=embed)


    @bot.command(name="zurück")
    async def move_backwards(ctx, timeout=None, speed=None):
        global ev3_commands_active
        timeout = int(timeout)
        speed = int(speed)
        if not ev3_commands_active:
            await commands_blocked(ctx)
        elif timeout is None and timeout is None:
            await ctx.send("```Du hast den Command falsch aufgerufen.\neve zurück <Zeit> <Prozent>```")
        else:
            if timeout > 15:
                timeout = 15
            elif timeout < 0:
                timeout = 0
            if speed < 0:
                speed = abs(speed)
            if speed > 100:
                speed = 100
            embed = discord.Embed(title="Bewegungsbefehl",
                                  description=f"WALL·E bewegt sich jetzt {timeout} Sekunden mit {speed}% seine Max "
                                              f"Geschwindigkeit rückwärts.", color=0x0998c8)
            if pi_controller.distance_data <= 200:
                embed.add_field(name="Distance Data",
                                value=f"WALL·E meldet Momentan ein Objekt {pi_controller.distance_data} cm vor ihm")
            else:
                embed.add_field(name="Distance Data", value=f"WALL·E meldet Momentan kein Objekt vor ihm")
            if speed > 0 and timeout > 0:
                pi_controller.add_request_to_queue("POST", dict(command="backwards", timeout=timeout, speed=speed))
            await ctx.send(embed=embed)


    @bot.command(name="drehen")
    async def rotate_for(ctx, degrees=None):
        global ev3_commands_active
        if not ev3_commands_active:
            await commands_blocked(ctx)
        elif degrees is None:
            await ctx.send("```Du hast den Command falsch aufgerufen.\neve drehen <Grad>```")
        else:
            degrees = int(degrees)
            if degrees < 0:
                if (abs(degrees) / 360) > 1:
                    degrees = abs(degrees) % 360 * -1
            else:
                if (degrees / 360) > 1:
                    degrees = degrees % 360
            embed = discord.Embed(title="Bewegungsbefehl",
                                  description=f"WALL·E dreht sich jetzt um {degrees}°", color=0x0998c8)
            if pi_controller.distance_data <= 200:
                embed.add_field(name="Distance Data",
                                value=f"WALL·E meldet Momentan ein Objekt {pi_controller.distance_data} cm vor ihm")
            else:
                embed.add_field(name="Distance Data", value=f"WALL·E meldet Momentan kein Objekt vor ihm")
            if degrees != 0:
                pi_controller.add_request_to_queue("POST", dict(command="rotate", degrees=degrees))
            await ctx.send(embed=embed)


    @bot.command("help")
    async def send_help(ctx):
        embed = discord.Embed(title="Help", color=0x097dc8)
        embed.add_field(name="`eve vor <Zeit> <Prozent>`", value="EV3 fährt `<Zeit>` Sekunden mit `<"
                                                                         "Prozent>` der maximal Geschw. vorwärts."
                                                                         "\n`<Zeit>` - Min: 0, Max: 15"
                                                                         "\n`<Prozent>` - Min: 0, Max: 100",
                        inline=False)
        embed.add_field(name="`eve zurück <Zeit> <Prozent>`", value="EV3 fährt `<Zeit>` Sekunden mit `<"
                                                                         "Prozent>` der maximal Geschw. rückwärts"
                                                                         "\n`<Zeit>` - Min: 0, Max: 15"
                                                                         "\n`<Prozent>` - Min: 0, Max: 100",
                        inline=False)
        embed.add_field(name="`eve drehen <Grad>`",
                        value="EV3 dreht sich `<Grad>` um sich selbst\npositiv `<Grad>` ~ Linksdrehung\nnegativ `<Grad>` ~ "
                              "Rechtsdrehung", inline=False)
        embed.add_field(name="`eve mitwirkende`", value="Jeder, der an diesem Projekt mitgearbeitet hat.", inline=False)
        embed.add_field(name="`eve github`", value="Link zum Source Code", inline=False)
        embed.add_field(name="`eve help`", value="Liste aller Befehle", inline=False)
        await ctx.send(embed=embed)


    @bot.command("ev3commands")
    async def set_ev3_commands_blocked(ctx, boolean=None):
        global ev3_commands_active
        if ctx.message.author.guild_permissions.administrator and boolean is not None:
            embed = discord.Embed(title="EV3 Commands Config",
                                  description=f"EV3 Commands aktiv: `{boolean}`", color=0x0998c8)
            ev3_commands_active = bool(boolean)
            await ctx.send(embed=embed)
        elif not ctx.message.author.guild_permissions.administrator and boolean is not None:
            await ctx.send("`Du musst Administrator Rechte haben um diesen Command ausführen zu können!`")
        else:
            embed = discord.Embed(title="EV3 Commands Config",
                                  description=f"EV3 Commands aktiv: `{ev3_commands_active}`", color=0x0998c8)
            await ctx.send(embed=embed)


    async def commands_blocked(ctx):
        embed = discord.Embed(title="EV3 Commands deaktiviert",
                              description="Commands an den EV3 Roboter wurden von einem Admin deaktiviert.",
                              color=0x097dc8)
        await ctx.send(embed=embed)


    bot.run(TOKEN)
