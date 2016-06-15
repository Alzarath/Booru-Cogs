import discord
from discord.ext import commands
from .utils.dataIO import fileIO
from .utils import checks
from __main__ import send_cmd_help
import os
import aiohttp

MAX_FILTER_TAGS = 50

class E621:
    def __init__(self, bot):
        self.bot = bot
        self.filters = fileIO("data/e621/filters.json","load")

    @commands.command(pass_context=True, no_pm=True)
    async def e621(self, ctx, *text):
        """Retrieves the latest result from e621"""
        server = ctx.message.server
        if len(text) > 0:
            msg = "+".join(text)
            search = "http://e621.net/post/index.json?limit=1&tags={}".format(msg)
            url = await fetch_image(self=self, ctx=ctx, randomize=False, search=search)
            await self.bot.say(url)
        else:
            await send_cmd_help(ctx)

    @commands.command(pass_context=True, no_pm=True)
    async def e621r(self, ctx, *text):
        """Retrieves a random result from e621"""
        server = ctx.message.server
        if len(text) > 0:
            msg = "+".join(text)
            search = "http://e621.net/post/index.json?limit=1&tags={}".format(msg)
        else:
            search = "http://e621.net/post/index.json?limit=1&tags="
        url = await fetch_image(self=self, ctx=ctx, randomize=True, search=search)
        await self.bot.say(url)

    @commands.group(pass_context=True)
    async def e621filter(self, ctx):
        """Manages e621 filters
           Warning: Can be used to allow NSFW images

           Filters automatically apply tags to each search"""
        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)

    @e621filter.command(name="add", pass_context=True, no_pm=True)
    @checks.mod_or_permissions(manage_server=True)
    async def _add_e621filter(self, ctx, filtertag : str):
        """Adds a tag to the server's e621 filter list

           Example: !e621filter add rating:s"""
        server = ctx.message.server
        if server.id not in self.filters:
            self.filters[server.id] = self.filters["default"]
            fileIO("data/e621/filters.json","save",self.filters)
            self.filters = fileIO("data/e621/filters.json","load")
        if len(self.filters[server.id]) > MAX_FILTER_TAGS:
            return await self.bot.say("Too many tags. https://www.youtube.com/watch?v=1MelZ7xaacs")
        self.filters[server.id].append(filtertag)
        fileIO("data/e621/filters.json","save",self.filters)
        await self.bot.say("Filter '{}' added to the server's e621 filter list.".format(filtertag))

    @e621filter.command(name="del", pass_context=True, no_pm=True)
    @checks.mod_or_permissions(manage_server=True)
    async def _del_e621filter(self, ctx, filtertag : str=""):
        """Deletes a tag from the server's e621 filter list

           Without arguments, reverts to the default e621 filter list

           Example: !e621filter del rating:s"""
        server = ctx.message.server
        if len(filtertag) > 0:
            if server.id not in self.filters:
                self.filters[server.id] = self.filters["default"]
                fileIO("data/e621/filters.json","save",self.filters)
                self.filters = fileIO("data/e621/filters.json","load")
            if filtertag in self.filters[server.id]:
                self.filters[server.id].remove(filtertag)
                fileIO("data/e621/filters.json","save",self.filters)
                await self.bot.say("Filter '{}' deleted from the server's e621 filter list.".format(filtertag))
            else:
                await self.bot.say("Filter '{}' does not exist in the server's e621 filter list.".format(filtertag))
        else:
            if server.id in self.filters:
                del self.filters[server.id]
                fileIO("data/e621/filters.json","save",self.filters)
                await self.bot.say("Reverted the server to the default e621 filter list.")
            else:
                await self.bot.say("Server is already using the default e621 filter list.")

    @e621filter.command(name="list", pass_context=True)
    async def _list_e621filter(self, ctx):
        """Lists all of the filters currently applied to the current server"""
        server = ctx.message.server
        if server.id in self.filters:
            filterlist = '\n'.join(sorted(self.filters[server.id]))
        else:
            filterlist = '\n'.join(sorted(self.filters["default"]))
        await self.bot.say("This server's filter list contains:```\n{}```".format(filterlist))

async def fetch_image(self, ctx, randomize, search):
    server = ctx.message.server
    self.filters = fileIO("data/e621/filters.json","load")

    try:
        if server.id in self.filters:
            search += "+{}".format("+".join(self.filters[server.id]))
        else:
            search += "+{}".format("+".join(self.filters["default"]))
        if randomize == True:
            search += "+order:random"
        async with aiohttp.get(search) as r:
            website = await r.json()
        if website != []:
            if "success" not in website:
                return website[0]["file_url"]
            else:
                return "{} Keep in mind the filter list is not excluded from tag limits.".format(website["message"])
        else:
            return "Your search terms gave no results."
    except:
        return "Error."

def check_folder():
    if not os.path.exists("data/e621"):
        print ("Creating data/e621 folder...")
        os.makedirs("data/e621")

def check_files():
    filters = {"default":["rating:safe", "-grimdark", "-suggestive"]}

    if not fileIO("data/e621/filters.json", "check"):
        print ("Creating default e621 filters.json...")
        fileIO("data/e621/filters.json", "save", filters)
    else:
        filterlist = fileIO("data/e621/filters.json","load")
        if "default" not in filterlist:
            filterlist["default"] = filters["default"]
            print ("Adding default e621 filters...")
            fileIO("data/e621/filters.json","save",filterlist)

def setup(bot):
    check_folder()
    check_files()
    bot.add_cog(E621(bot))
