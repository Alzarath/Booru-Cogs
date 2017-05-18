import discord
from discord.ext import commands
from .utils.dataIO import fileIO
from .utils import checks
from __main__ import send_cmd_help
from urllib import parse
import os
import aiohttp
import random
import xml

class Gel:
    def __init__(self, bot):
        self.bot = bot
        self.filters = fileIO("data/gel/filters.json", "load")
        self.settings = fileIO("data/gel/settings.json", "load")

    @commands.command(pass_context=True,no_pm=True)
    async def gel(self, ctx, *text):
        """Retrieves the latest result from Gelbooru"""
        server = ctx.message.server
        if len(text) > 0:
            await fetch_image(self, ctx, randomize=False, tags=text)
        else:
            await send_cmd_help(ctx)

    @commands.command(pass_context=True,no_pm=True)
    async def gelr(self, ctx, *text):
        """Retrieves a random result from Gelbooru"""
        server = ctx.message.server
        await fetch_image(self, ctx, randomize=True, tags=text)

    @commands.group(pass_context=True)
    async def gelfilter(self, ctx):
        """Manages gel filters
           Warning: Can be used to allow NSFW images

           Filters automatically apply tags to each search"""
        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)

    @gelfilter.command(name="add", pass_context=True, no_pm=True)
    @checks.admin_or_permissions(manage_server=True)
    async def _add_gelfilter(self, ctx, filtertag : str):
        """Adds a tag to the server's gel filter list

           Example: !gelfilter add rating:s"""
        server = ctx.message.server
        if server.id not in self.filters:
            self.filters[server.id] = self.filters["default"]
            fileIO("data/gel/filters.json", "save", self.filters)
            self.filters = fileIO("data/gel/filters.json", "load")
        if len(self.filters[server.id]) < int(self.settings["maxfilters"]):
            if filtertag not in self.filters[server.id]:
                self.filters[server.id].append(filtertag)
                fileIO("data/gel/filters.json", "save", self.filters)
                await self.bot.say("Filter '{}' added to the server's gel filter list.".format(filtertag))
            else:
                await self.bot.say("Filter '{}' is already in the server's gel filter list.".format(filtertag))
        else:
            await self.bot.say("This server has exceeded the maximum filters ({}/{}). https://www.youtube.com/watch?v=1MelZ7xaacs".format(len(self.filters[server.id]), self.settings["maxfilters"]))

    @gelfilter.command(name="del", pass_context=True, no_pm=True)
    @checks.admin_or_permissions(manage_server=True)
    async def _del_gelfilter(self, ctx, filtertag : str=""):
        """Deletes a tag from the server's gel filter list

           Without arguments, reverts to the default gel filter list

           Example: !gelfilter del rating:s"""
        server = ctx.message.server
        if len(filtertag) > 0:
            if server.id not in self.filters:
                self.filters[server.id] = self.filters["default"]
                fileIO("data/gel/filters.json", "save", self.filters)
                self.filters = fileIO("data/gel/filters.json", "load")
            if filtertag in self.filters[server.id]:
                self.filters[server.id].remove(filtertag)
                fileIO("data/gel/filters.json", "save", self.filters)
                await self.bot.say("Filter '{}' deleted from the server's gel filter list.".format(filtertag))
            else:
                await self.bot.say("Filter '{}' does not exist in the server's gel filter list.".format(filtertag))
        else:
            if server.id in self.filters:
                del self.filters[server.id]
                fileIO("data/gel/filters.json", "save", self.filters)
                await self.bot.say("Reverted the server to the default gel filter list.")
            else:
                await self.bot.say("Server is already using the default gel filter list.")

    @gelfilter.command(name="list", pass_context=True)
    async def _list_gelfilter(self, ctx):
        """Lists all of the filters currently applied to the current server"""
        server = ctx.message.server
        if server.id in self.filters:
            filterlist = '\n'.join(sorted(self.filters[server.id]))
            targetServer = "{}'s".format(server.name)
        else:
            filterlist = '\n'.join(sorted(self.filters["default"]))
            targetServer = "Default"
        await self.bot.say("{} gel filter list contains:```\n{}```".format(targetServer, filterlist))

    @commands.group(pass_context=True)
    async def gelset(self, ctx):
        """Manages gel options"""
        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)

    @gelset.command(pass_context=True,name="verbose")
    @checks.admin_or_permissions(manage_server=True)
    async def _verbose_gelset(self, ctx, toggle : str="toggle"):
        """Toggles verbose mode"""
        server = ctx.message.server
        if server.id not in self.settings:
            self.settings[server.id] = {"verbose":False}
            fileIO("data/gel/settings.json", "save", self.settings)
            self.settings = fileIO("data/gel/settings.json", "load")
        if toggle.lower() == "on" or toggle.lower() == "true" or toggle.lower() == "enable":
            if not self.settings[server.id]["verbose"]:
                self.settings[server.id]["verbose"] = True
                await self.bot.say("Verbose mode is now enabled.")
            else:
                await self.bot.say("Verbose mode is already enabled.")
        elif toggle.lower() == "off" or toggle.lower() == "false" or toggle.lower() == "disable":
            if self.settings[server.id]["verbose"]:
                self.settings[server.id]["verbose"] = False
                await self.bot.say("Verbose mode is now disabled.")
            else:
                await self.bot.say("Verbose mode is already disabled.")
        else:
            if self.settings[server.id]["verbose"]:
                self.settings[server.id]["verbose"] = False
                await self.bot.say("Verbose mode is now disabled.")
            else:
                self.settings[server.id]["verbose"] = True
                await self.bot.say("Verbose mode is now enabled.")
        fileIO("data/gel/settings.json", "save", self.settings)

    @gelset.command(name="maxfilters")
    @checks.is_owner()
    async def _maxfilters_gelset(self, maxfilters):
        """Sets the global tag limit for the filter list

           Gives an error when a user tries to add a filter while the server's filter list contains a certain amount of tags"""
        self.settings["maxfilters"] = maxfilters
        fileIO("data/gel/settings.json", "save", self.settings)
        await self.bot.say("Maximum filters allowed per server for gel set to '{}'.".format(maxfilters))

async def fetch_image(self, ctx, randomize, tags):
    server = ctx.message.server
    self.filters = fileIO("data/gel/filters.json", "load")

    if server.id in self.settings:
        if self.settings[server.id]["verbose"]:
            verbose = True
        else:
            verbose = False
    else:
        verbose = False

    # initialize base URL
    search = "http://gelbooru.com/index.php?page=dapi&s=post&q=index&limit=1&tags="
    tagSearch = ""

    # Apply tags to URL
    if tags:
        tagSearch += "{} ".format(" ".join(tags))
    if server.id in self.filters:
        tagSearch += " ".join(self.filters[server.id])
    else:
        tagSearch += " ".join(self.filters["default"])
    search += parse.quote_plus(tagSearch)
    
    # Inform users about image retrieving
    message = await self.bot.say("Fetching gel image...")

    # Fetch and display the image or an error
    try:
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
            if randomize:
                pid = str(round(count * random.random())) # Generates a random number between 0 and the amount of available images
                search += "&pid=" + pid
                async with aiohttp.get(search) as r: # Fetches an image with the chosen pid
                    website = await r.text()
            result = xml.etree.ElementTree.fromstring(website)
            imageURL = "https:{}".format(result[0].get('file_url'))
            if verbose:
                # Checks for the rating and sets an appropriate color
                tagList = result[0].get('tags').split(", ")
                rating = result[0].get('rating')
                if rating == "s":
                    rating = "safe"
                    ratingColor = "00FF00"
                elif rating == "q":
                    rating = "questionable"
                    ratingColor = "FF9900"
                elif rating == "e":
                    rating = "explicit"
                    ratingColor = "FF0000"
                if not rating:
                    rating = "unknown"
                    ratingColor = "FFFFFF"

                # Sets the URL to be linked
                link = "https://gelbooru.com/index.php?page=post&s=view&id={}".format(result[0].get('id'))
                
                # Initialize verbose embed
                output = discord.Embed(description=link, colour=discord.Colour(value=int(ratingColor, 16)))

                # Sets the thumbnail and adds the rating and tag fields to the embed
                output.add_field(name="Rating", value=rating)
                output.add_field(name="Tags", value=", ".join(tagList))
                output.set_thumbnail(url=imageURL)
            else:
                # Sets the link to the image URL if verbose mode is not enabled
                output = imageURL
            
            # Edits the pending message with the results
            if verbose:
                return await self.bot.edit_message(message, "Image found.", embed=output)
            else:
                return await self.bot.edit_message(message, output)
        else:
            return await self.bot.edit_message(message, "Your search terms gave no results.")
    except:
        return await self.bot.edit_message(message, "Error.")

def check_folder():
    if not os.path.exists("data/gel"):
        print("Creating data/gel folder...")
        os.makedirs("data/gel")

def check_files():
    filters = {"default":["rating:safe"]}
    settings = {"maxfilters":"50"}

    if not fileIO("data/gel/filters.json", "check"):
        print("Creating default gel filters.json...")
        fileIO("data/gel/filters.json", "save", filters)
    else:
        filterlist = fileIO("data/gel/filters.json", "load")
        if "default" not in filterlist:
            filterlist["default"] = filters["default"]
            print("Adding default gel filters...")
            fileIO("data/gel/filters.json", "save", filterlist)
    if not fileIO("data/gel/settings.json", "check"):
        print("Creating default gel settings.json...")
        fileIO("data/gel/settings.json", "save", settings)

def setup(bot):
    check_folder()
    check_files()
    bot.add_cog(Gel(bot))
