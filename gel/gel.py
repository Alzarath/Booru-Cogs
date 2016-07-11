import discord
from discord.ext import commands
from .utils.dataIO import fileIO
from .utils import checks
from __main__ import send_cmd_help
from urllib.parse import quote
import os
import aiohttp
import random
import xml

settings = {
# Maximum filters per server before it starts restricting tags from being added to the filter list.
# Does not represent the amount of tags a search permits.
    "MAX_FILTER_TAGS" : 50
}

class Gel:
    def __init__(self, bot):
        self.bot = bot
        self.filters = fileIO("data/gel/filters.json","load")

    @commands.command(pass_context=True,no_pm=True)
    async def gel(self, ctx, *text):
        """Retrieves the latest result from Gelbooru"""
        server = ctx.message.server
        if len(text) > 0:
            msg = quote("+".join(text))
            search = "http://gelbooru.com/index.php?page=dapi&s=post&q=index&limit=1&tags=" + msg
            url = await fetch_image(self, ctx, randomize=False, search=search)
            await self.bot.say(url)
        else:
            await send_cmd_help(ctx)

    @commands.command(pass_context=True,no_pm=True)
    async def gelr(self, ctx, *text):
        """Retrieves a random result from Gelbooru"""
        server = ctx.message.server
        if len(text) > 0:
            msg = quote("+".join(text))
            search = "http://gelbooru.com/index.php?page=dapi&s=post&q=index&limit=1&tags=" + msg
        else:
            search = "http://gelbooru.com/index.php?page=dapi&s=post&q=index&limit=1&tags="
        url = await fetch_image(self, ctx, randomize=True, search=search)
        await self.bot.say(url)

    @commands.group(pass_context=True)
    async def gelfilter(self, ctx):
        """Manages gel filters
           Warning: Can be used to allow NSFW images

           Filters automatically apply tags to each search"""
        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)

    @gelfilter.command(name="add", pass_context=True, no_pm=True)
    @checks.mod_or_permissions(manage_server=True)
    async def _add_gelfilter(self, ctx, filtertag : str):
        """Adds a tag to the server's gel filter list

           Example: !gelfilter add rating:s"""
        server = ctx.message.server
        if server.id not in self.filters:
            self.filters[server.id] = self.filters["default"]
            fileIO("data/gel/filters.json","save",self.filters)
            self.filters = fileIO("data/gel/filters.json","load")
        if len(self.filters[server.id]) > settings["MAX_FILTER_TAGS"]:
            return await self.bot.say("Too many tags. https://www.youtube.com/watch?v=1MelZ7xaacs")
        if filtertag not in self.filters[server.id]:
            self.filters[server.id].append(filtertag)
            fileIO("data/gel/filters.json","save",self.filters)
            await self.bot.say("Filter '{}' added to the server's gel filter list.".format(filtertag))
        else:
            await self.bot.say("Filter '{}' is already in the server's gel filter list.".format(filtertag))

    @gelfilter.command(name="del", pass_context=True, no_pm=True)
    @checks.mod_or_permissions(manage_server=True)
    async def _del_gelfilter(self, ctx, filtertag : str=""):
        """Deletes a tag from the server's gel filter list

           Without arguments, reverts to the default gel filter list

           Example: !gelfilter del rating:s"""
        server = ctx.message.server
        if len(filtertag) > 0:
            if server.id not in self.filters:
                self.filters[server.id] = self.filters["default"]
                fileIO("data/gel/filters.json","save",self.filters)
                self.filters = fileIO("data/gel/filters.json","load")
            if filtertag in self.filters[server.id]:
                self.filters[server.id].remove(filtertag)
                fileIO("data/gel/filters.json","save",self.filters)
                await self.bot.say("Filter '{}' deleted from the server's gel filter list.".format(filtertag))
            else:
                await self.bot.say("Filter '{}' does not exist in the server's gel filter list.".format(filtertag))
        else:
            if server.id in self.filters:
                del self.filters[server.id]
                fileIO("data/gel/filters.json","save",self.filters)
                await self.bot.say("Reverted the server to the default gel filter list.")
            else:
                await self.bot.say("Server is already using the default gel filter list.")

    @gelfilter.command(name="list", pass_context=True)
    async def _list_gelfilter(self, ctx):
        """Lists all of the filters currently applied to the current server"""
        server = ctx.message.server
        if server.id in self.filters:
            filterlist = '\n'.join(sorted(self.filters[server.id]))
        else:
            filterlist = '\n'.join(sorted(self.filters["default"]))
        await self.bot.say("This server's filter list contains:```\n{}```".format(filterlist))

async def fetch_image(self, ctx, randomize, search):
    server = ctx.message.server
    self.filters = fileIO("data/gel/filters.json","load")

    try:
        if server.id in self.filters:
            search += "+{}".format("+".join(self.filters[server.id]))
        else:
            search += "+{}".format("+".join(self.filters["default"]))
        async with aiohttp.get(search) as r:
            website = await r.text()
        attr = website.split('"')[1::2]
        cindex = 0
        while cindex != -1:
            if attr[cindex] == "UTF-8":
                count = int(attr[cindex+1])
                cindex = -1
            else:
                cindex += 1
        if count > 0:
            if randomize == True:
                pid = str(round(count * random.random())) # Generates a random number between 0 and the amount of available images
                search += "&pid=" + pid # Grabs an image at the generated number index
                async with aiohttp.get(search) as r:
                    website = await r.text()
            result = xml.etree.ElementTree.fromstring(website)
            return result[0].get('file_url')
        else:
            return "Your search terms gave no results."
    except:
        return "Error."

def check_folder():
    if not os.path.exists("data/gel"):
        print ("Creating data/gel folder...")
        os.makedirs("data/gel")

def check_files():
    filters = {"default":["rating:safe"]}

    if not fileIO("data/gel/filters.json", "check"):
        print ("Creating default gel filters.json...")
        fileIO("data/gel/filters.json", "save", filters)
    else:
        filterlist = fileIO("data/gel/filters.json","load")
        if "default" not in filterlist:
            filterlist["default"] = filters["default"]
            print ("Adding default gel filters...")
            fileIO("data/gel/filters.json","save",filterlist)

def setup(bot):
    check_folder()
    check_files()
    bot.add_cog(Gel(bot))
