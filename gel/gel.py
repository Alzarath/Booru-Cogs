import discord
from discord.ext import commands
from .utils.dataIO import fileIO
from .utils import checks
from __main__ import send_cmd_help
from urllib import parse
import os
import aiohttp
import random

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

async def fetch_image(self, ctx, randomize : bool=False, tags : list=[]):
    server = ctx.message.server
    self.filters = fileIO("data/gel/filters.json", "load")
    self.settings = fileIO("data/gel/settings.json", "load")

    # Initialize variables
    #artist      = "unknown artist"
    #artists     = ""
    #artistList  = []
    embedLink   = ""
    embedTitle  = ""
    imageId     = ""
    message     = ""
    output      = None
    rating      = ""
    ratingColor = "FFFFFF"
    ratingWord  = "unknown"
    search      = "http://gelbooru.com/index.php?page=dapi&s=post&limit=1&q=index&tags="
    tagSearch   = ""
    verbose     = False

    # Set verbosity to true if the current server has it set as such
    if server.id in self.settings and self.settings[server.id]["verbose"]:
        verbose = True

    # Apply tags to URL
    if tags:
        tagSearch += "{} ".format(" ".join(tags))
    if server.id in self.filters:
        tagSearch += " ".join(self.filters[server.id])
    else:
        tagSearch += " ".join(self.filters["default"])
    search += parse.quote_plus(tagSearch)
    
    # Inform users about image retrieval
    message = await self.bot.say("Fetching gel image...")

    # Fetch and display the image or an error
    try:
        # Fetch the xml page to randomize the results
        if randomize:
            async with aiohttp.get(search) as r:
                website = await r.text()

            # Gets the amount of results
            countStart = website.find("count=\"")
            countEnd = website.find("\"", countStart+7)
            count = website[countStart+7:countEnd]

            # Picks a random page and sets the search URL to json
            pid = str(random.randint(0, int(count)))
            search += "&json=1&pid={}".format(pid)
        else:
            # Sets the search URL to json
            search += "&json=1"

        # Fetches the json page
        async with aiohttp.get(search) as r:
            website = await r.json()
        if website:
            # Sets the image URL
            imageURL = "https:{}".format(website[0]['file_url'])
            if verbose:
                # Fetches the image ID
                imageId = website[0].get('id')

                # Sets the embed title
                embedTitle = "Gelbooru Image #{}".format(imageId)

                # Sets the URL to be linked
                embedLink = "https://gelbooru.com/index.php?page=post&s=view&id={}".format(imageId)

                # Check for the rating and set an appropriate color
                rating = website[0].get('rating')
                if rating == "s":
                    ratingColor = "00FF00"
                    ratingWord = "safe"
                elif rating == "q":
                    ratingColor = "FF9900"
                    ratingWord = "questionable"
                elif rating == "e":
                    ratingColor = "FF0000"
                    ratingWord = "explicit"

                # Sets the tags to be listed
                tagList = website[0].get('tags').replace(' ', ', ').replace('_', '\_')
                
                # Initialize verbose embed
                output = discord.Embed(title=embedTitle, url=embedLink, colour=discord.Colour(value=int(ratingColor, 16)))

                # Sets the thumbnail and adds the rating and tag fields to the embed
                output.add_field(name="Rating", value=ratingWord)
                output.add_field(name="Tags", value=tagList, inline=False)
                output.set_thumbnail(url=imageURL)

                # Edits the pending message with the results
                return await self.bot.edit_message(message, "Image found.", embed=output)
            else:
                # Edits the pending message with the result
                return await self.bot.edit_message(message, imageURL)
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
