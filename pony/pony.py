import discord
from discord.ext import commands
from .utils.chat_formatting import *
from .utils.dataIO import fileIO
from .utils import checks
from __main__ import send_cmd_help
import aiohttp
import os

class Pony:
    def __init__(self, bot):
        self.bot = bot
        self.availablefilters = fileIO("data/pony/availablefilters.json","load")
        self.activefilters = fileIO("data/pony/activefilters.json","load")

    @commands.command(pass_context=True,no_pm=True)
    async def pony(self, ctx, *text):
        """Retrieves the latest result from Derpibooru"""
        server = ctx.message.server
        if len(text) > 0:
            if server.id in self.activefilters:
                ponyfilter = self.activefilters[server.id]
            else:
                ponyfilter = "default"
            try:
                msg = "+".join(text)
                search = "https://derpiboo.ru/search.json?q=" + msg + "&filter_id=" + self.availablefilters[ponyfilter]
                async with aiohttp.get(search) as r:
                    website = await r.json()
                if website["search"] != []:
                    url = "http:" + website["search"][0]["image"]
                    await self.bot.say(url)
                else:
                    await self.bot.say("Your search terms gave no results.")
            except:     
                await self.bot.say("Error.")
        else:   
            await send_cmd_help(ctx)

    @commands.command(pass_context=True,no_pm=True)
    async def ponyr(self, ctx, *text):
        """Retrieves a random result from Derpibooru"""
        server = ctx.message.server
        if server.id in self.activefilters:
            ponyfilter = self.activefilters[server.id]
        else:
            ponyfilter = "default"
        if len(text) > 0:
            try:
                msg = "+".join(text)
                search = "https://derpiboo.ru/search.json?q=" + msg + "&random_image=y&filter_id=" + self.availablefilters[ponyfilter] 
                async with aiohttp.get(search) as r:
                    website = await r.json()
                if "id" in website:
                    imgid = str(website["id"])
                    async with aiohttp.get("https://derpiboo.ru/images/" + imgid + ".json") as r:
                        website = await r.json()
                    url = "http:" + website["image"]
                    await self.bot.say(url)
                else:
                    await self.bot.say("Your search terms gave no results.")
            except:
                await self.bot.say("Error.")
        else:
            try:
                search = "https://derpiboo.ru/search.json?q=*&random_image=y&filter_id=" + self.availablefilters[ponyfilter] 
                async with aiohttp.get(search) as r:
                    website = await r.json()
                if "id" in website:
                    imgid = str(website["id"])
                    async with aiohttp.get("https://derpiboo.ru/images/" + imgid + ".json") as r:
                        website = await r.json()
                    url = "http://" + website["image"]
                    await self.bot.say(url)
                else:
                    await self.bot.say("Your search terms gave no results.")
            except:
                await self.bot.say("Error.")

    @commands.group(pass_context = True)
    async def ponyfilter(self, ctx):
        """Manages filters.

           Filters determine what tags will not show up in the results"""
        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)

    @ponyfilter.command(name="add")
    @checks.is_owner()
    async def _add_ponyfilter(self, filtername, filterid):
        """Adds a filter to the global filter list

           Filter IDs can be found in the filter list (https://derpiboo.ru/filters/**ID**)

           Example: !ponyfilter add legacy 37431"""
        self.availablefilters[filtername] = filterid
        fileIO("data/pony/availablefilters.json","save",self.availablefilters)
        await self.bot.say("Filter '{}' added to the global filter list.".format(filtername))

    @ponyfilter.command(name="del")
    @checks.is_owner()
    async def _add_ponyfilter(self, filtername):
        """Deletes a filter from the global filter list

           Example: !ponyfilter del legacy"""
        for i in self.availablefilters:
            if self.availablefilters[i] == self.availablefilters[filtername]:
                self.availablefilters.pop(i)
                fileIO("data/pony/availablefilters.json","save",self.availablefilters)
                await self.bot.say("Filter '{}' deleted from the global filter list.".format(filtername))
                break

    @ponyfilter.command(name="list")
    async def _list_ponyfilter(self):
        """Lists all of the filters available in the global filter list."""
        filters = self.availablefilters
        filterlist = '\n'.join(sorted(self.availablefilters))
        await self.bot.say("The global filter list contains:\n" + filterlist)

    @ponyfilter.command(name="set", pass_context=True)
    @checks.mod_or_permissions(manage_server=True)
    async def _set_ponyfilter(self, ctx, filtername : str="default"):
        """Sets the filter for the current server
           Warning: Some filters may display NSFW images

           Default filters: default, everything, dark, r34

           Example: !ponyfilter set default"""
        server = ctx.message.server
        if filtername in self.availablefilters:
            self.activefilters[server.id] = filtername
            fileIO("data/pony/activefilters.json","save",self.activefilters)
            await self.bot.say("Filter set to '{}'.".format(filtername))
        else:
            await self.bot.say("'{}' does not exist in the filter list.".format(filtername))

def check_folder():
    if not os.path.exists("data/pony"):
        print("Creating data/pony folder...")
        os.makedirs("data/pony")

def check_files():
    availablefilters = {"default":"100073","everything":"56027","dark":"37429","r34":"37432"}
    activefilters = {}

    if not fileIO("data/pony/availablefilters.json", "check"):
        print ("Creating default pony's availablefilters.json...")
        fileIO("data/pony/availablefilters.json", "save", availablefilters)

    if not fileIO("data/pony/activefilters.json", "check"):
        print ("Creating default pony's activefilters.json...")
        fileIO("data/pony/activefilters.json", "save", activefilters)

def setup(bot):
    check_folder()
    check_files()
    bot.add_cog(Pony(bot))
