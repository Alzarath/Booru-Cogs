import discord
from discord.ext import commands
from .utils.dataIO import fileIO
from .utils import checks
from __main__ import send_cmd_help
import os
import aiohttp

settings = {
# Maximum image results. Capped at 100. Increasing probably isn't necessary.
    "IMAGE_LIMIT" : 10,
# Your Danbooru username. Sadly doesn't implement blacklists.
    "USERNAME" : "",
# Your Danbooru API Key. Used for basic, gold, and platinum features. Requires USERNAME.
    "API_KEY" : ""
}

class Dan:
    def __init__(self, bot):
        self.bot = bot
        self.filters = fileIO("data/dan/filters.json","load")

    @commands.command(pass_context=True,no_pm=True)
    async def dan(self, ctx, *text):
        """Retrieves the latest result from Danbooru"""
        server = ctx.message.server
        if len(text) > 0:
            msg = "+".join(text)
            search = "http://danbooru.donmai.us/posts.json?limit={}&tags={}".format(str(settings["IMAGE_LIMIT"]), msg)
            url = await fetch_image(self, ctx, randomize=False, search=search)
            await self.bot.say(url)
        else:
            await send_cmd_help(ctx)

    @commands.command(pass_context=True,no_pm=True)
    async def danr(self, ctx, *text):
        """Retrieves a random result from Danbooru"""
        server = ctx.message.server
        if len(text) > 0:
            msg = "+".join(text)
            search = "http://danbooru.donmai.us/posts.json?limit={}&tags={}".format(str(settings["IMAGE_LIMIT"]), msg)
        else:
            search = "http://danbooru.donmai.us/posts.json?limit={}".format(str(settings["IMAGE_LIMIT"]))
        url = await fetch_image(self, ctx, randomize=True, search=search)
        await self.bot.say(url)

    @commands.group(pass_context=True)
    async def danfilter(self, ctx):
        """Manages dan filters
           Warning: Can be used to allow NSFW images

           Filters automatically apply tags to each search"""
        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)

    @danfilter.command(name="add", pass_context=True, no_pm=True)
    @checks.mod_or_permissions(manager_server=True)
    async def _add_danfilter(self, ctx, filtertag : str):
        """Adds a tag to the server's dan filter list

           Example: !danfilter add rating:safe"""
        server = ctx.message.server
        if server.id not in self.filters:
            self.filters[server.id] = self.filters["default"]
            fileIO("data/dan/filters.json","save",self.filters)
            self.filters = fileIO("data/dan/filters.json","load")
        if len(self.filters[server.id]) > MAX_SERVER_TAGS:
            return await self.bot.say("Too many tags. https://www.youtube.com/watch?v=1MelZ7xaacs")
        self.filters[server.id].append(filtertag)
        fileIO("data/dan/filters.json","save",self.filters)
        await self.bot.say("Filter '{}' added to the server's dan filter list.".format(filtertag))

    @danfilter.command(name="del", pass_context=True, no_pm=True)
    @checks.mod_or_permissions(manager_server=True)
    async def _del_danfilter(self, ctx, filtertag : str):
        """Deletes a tag from the server's dan filter list

           Without arguments, revers to the default dan filter list

           Example: !danfilter del rating:safe"""
        server = ctx.message.server
        if len(filtertag) > 0:
            if server.id not in self.filters:
                self.filters[server.id] = self.filters["default"]
                fileIO("data/dan/filters.json","save",self.filters)
                self.filters = fileIO("data/dan/filters.json","load")
            if filtertag in self.filters[server.id]:
                self.filters[server.id].remove(filtertag)
                fileIO("data/dan/filters.json","save",self.filters)
                await self.bot.say("Filter '{}' deleted from the server's dan filter list.".format(filtertag))
            else:
                await self.bot.say("Filter '{}' does not exist in the server's dan filter list.".format(filtertag))
        else:
            if server.id in self.filters:
                del self.filters[server.id]
                fileIO("data/dan/filters.json","save",self.filters)
                await self.bot.say("Reverted the server to the default dan filter list.")
            else:
                await self.bot.say("Server is already using the default dan filter list.")

async def fetch_image(self, ctx, randomize, search):
    server = ctx.message.server
    self.filters = fileIO("data/dan/filters.json","load")

    try:
        if server.id in self.filters:
            search += "+{}".format("+".join(self.filters[server.id]))
        else:
            search += "+{}".format("+".join(self.filters["default"]))
        if randomize == True:
            search += "&random=y"
        if settings["USERNAME"] != "" and settings["API_KEY"] != "":
            search += "&login={}&api_key={}".format(settings["USERNAME"], settings["API_KEY"])
        async with aiohttp.get(search) as r:
            website = await r.json()
        if website != []:
            if "success" not in website:
                for index in range(len(website)): # Goes through each result until it finds one that works
                    if "file_url" in website[index]:
                        return "http://danbooru.donmai.us{}".format(website[index]["file_url"])
                return "Cannot find an image that can be viewed by you."
            else:
                return "{} Keep in mind the filter list is not excluded from tag limits.".format(website["message"])
        else:
            return "Your search terms gave no results."
    except:
        return "Error."

def check_folder():
    if not os.path.exists("data/dan"):
        print ("Creating data/dan folder...")
        os.makedirs("data/dan")

def check_files():
    filters = {"default":["rating:safe"]}

    if not fileIO("data/dan/filters.json", "check"):
        print ("Creating default dan filters.json...")
        fileIO("data/dan/filters.json", "save", filters)
    else:
        filterlist = fileIO("data/dan/filters.json","load")
        if "default" not in filterlist:
            filterlist["default"] = filters["default"]
            print ("Adding default dan filters...")
            fileIO("data/dan/filters.json","save",filterlist)

def check_info():
    if settings["USERNAME"] != "":
        if settings["API_KEY"] == "":
            print("You must set API_KEY in cogs/dan.py for USERNAME to be relevant.")
    if settings["API_KEY"] != "":
        if settings["USERNAME"] == "":
            print("You must set USERNAME in cogs/dan.py for API_KEY to be relevant.")

def setup(bot):
    check_folder()
    check_files()
    check_info()
    bot.add_cog(Dan(bot))
