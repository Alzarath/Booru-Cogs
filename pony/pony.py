import discord
from discord.ext import commands
from .utils.chat_formatting import *
from .utils.dataIO import fileIO
from .utils import checks
from __main__ import send_cmd_help
from urllib import parse
import aiohttp
import os

class Pony:
    def __init__(self, bot):
        self.bot = bot
        self.filters = fileIO("data/pony/filters.json", "load")
        self.settings = fileIO("data/pony/settings.json", "load")


    @commands.command(pass_context=True,no_pm=True)
    async def pony(self, ctx, *text):
        """Retrieves the latest result from Derpibooru"""
        server = ctx.message.server
        if len(text) > 0:
            await fetch_image(self, ctx, randomize=False, tags=text)
        else:
            await send_cmd_help(ctx)

    @commands.command(pass_context=True,no_pm=True)
    async def ponyr(self, ctx, *text):
        """Retrieves a random result from Derpibooru"""
        server = ctx.message.server
        await fetch_image(self, ctx, randomize=True, tags=text)

    @commands.group(pass_context=True)
    async def ponyfilter(self, ctx):
        """Manages pony filters
           Warning: Can be used to allow NSFW images

           Filters automatically apply tags to each search"""
        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)

    @ponyfilter.command(name="add", pass_context=True, no_pm=True)
    @checks.admin_or_permissions(manage_server=True)
    async def _add_ponyfilter(self, ctx, filtertag : str):
        """Adds a tag to the server's pony filter list

           Example: !ponyfilter add safe"""
        server = ctx.message.server
        if server.id not in self.filters:
            self.filters[server.id] = self.filters["default"]
            fileIO("data/pony/filters.json", "save", self.filters)
            self.filters = fileIO("data/pony/filters.json", "load")
        if len(self.filters[server.id]) < int(self.settings["maxfilters"]):
            if filtertag not in self.filters[server.id]:
                self.filters[server.id].append(filtertag)
                fileIO("data/pony/filters.json", "save", self.filters)
                await self.bot.say("Filter '{}' added to the server's pony filter list.".format(filtertag))
            else:
                await self.bot.say("Filter '{}' is already in the server's pony filter list.".format(filtertag))
        else:
            await self.bot.say("This server has exceeded the maximum filters ({}/{}). https://www.youtube.com/watch?v=1MelZ7xaacs".format(len(self.filters[server.id]), self.settings["maxfilters"]))

    @ponyfilter.command(name="del", pass_context=True, no_pm=True)
    @checks.admin_or_permissions(manage_server=True)
    async def _del_ponyfilter(self, ctx, filtertag : str=""):
        """Deletes a tag from the server's pony filter list

           Without arguments, reverts to the default loli filter list

           Example: !ponyfilter del safe"""
        server = ctx.message.server
        if len(filtertag) > 0:
            if server.id not in self.filters:
                self.filters[server.id] = self.filters["default"]
                fileIO("data/pony/filters.json", "save", self.filters)
                self.filters = fileIO("data/pony/filters.json", "load")
            if filtertag in self.filters[server.id]:
                self.filters[server.id].remove(filtertag)
                fileIO("data/pony/filters.json", "save", self.filters)
                await self.bot.say("Filter '{}' deleted from the server's pony filter list.".format(filtertag))
            else:
                await self.bot.say("Filter '{}' does not exist in the server's pony filter list.".format(filtertag))
        else:
            if server.id in self.filters:
                del self.filters[server.id]
                fileIO("data/pony/filters.json", "save", self.filters)
                await self.bot.say("Reverted the server to the default pony filter list.")
            else:
                await self.bot.say("Server is already using the default pony filter list.")

    @ponyfilter.command(name="list", pass_context=True)
    async def _list_ponyfilter(self, ctx):
        """Lists all of the filters currently applied to the current server"""
        server = ctx.message.server
        if server.id in self.filters:
            filterlist = '\n'.join(sorted(self.filters[server.id]))
            targetServer = "{}'s".format(server.name)
        else:
            filterlist = '\n'.join(sorted(self.filters["default"]))
            targetServer = "Default"
        await self.bot.say("{} pony filter list contains:```\n{}```".format(targetServer, filterlist))

    @commands.group(pass_context=True)
    async def ponyset(self, ctx):
        """Manages pony options"""
        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)

    @ponyset.command(pass_context=True,name="verbose")
    @checks.admin_or_permissions(manage_server=True)
    async def _verbose_ponyset(self, ctx, toggle : str="toggle"):
        """Toggles verbose mode"""
        server = ctx.message.server
        if server.id not in self.settings:
            self.settings[server.id] = {"verbose":False}
            fileIO("data/pony/settings.json", "save", self.settings)
            self.settings = fileIO("data/pony/settings.json", "load")
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
        fileIO("data/pony/settings.json", "save", self.settings)

    @ponyset.command(name="maxfilters")
    @checks.is_owner()
    async def _maxfilters_ponyset(self, maxfilters : int):
        """Sets the global tag limit for the filter list

           Gives an error when a user tries to add a filter while the server's filter list contains a certain amount of tags"""
        self.settings["maxfilters"] = maxfilters
        fileIO("data/pony/settings.json", "save", self.settings)
        await self.bot.say("Maximum filters allowed per server for pony set to '{}'.".format(maxfilters))

async def fetch_image(self, ctx, randomize : bool=False, tags : list=[]):
    server = ctx.message.server
    self.filters = fileIO("data/pony/filters.json", "load")
    self.settings = fileIO("data/pony/settings.json", "load")

    #Initialize variables
    artist      = "unknown artist"
    artists     = ""
    artistList  = []
    embedLink   = ""
    embedTitle  = ""
    imageId     = ""
    message     = ""
    output      = None
    rating      = ""
    ratingColor = "FFFFFF"
    ratingWord  = "unknown"
    search      = "https://derpibooru.org/search.json?q="
    tagSearch   = ""
    verbose     = False

    # Set verbosity to true if the current server has it set as such
    if server.id in self.settings and self.settings[server.id]["verbose"]:
        verbose = True

    # Assign tags to URL
    if tags:
        tagSearch += "{} ".format(" ".join(tags))
    if server.id in self.filters:
        if self.filters[server.id] != [] and tags:
            tagSearch += ", "
        tagSearch += ", ".join(self.filters[server.id])
    else:
        if tags:
            tagSearch += ", "
        tagSearch += ", ".join(self.filters["default"])
    search += parse.quote_plus(tagSearch)

    # Randomize results and apply Derpibooru's "Everything" filter
    if randomize:
        if not tags and server.id in self.filters:
           if self.filters[server.id] == []:
               search = "https://derpibooru.org/images/random.json?filter_id=56027"
           else:
               search += "&random_image=y&filter_id=56027"
        else:
           search += "&random_image=y&filter_id=56027"

    # Inform users about image retrieving
    message = await self.bot.say("Fetching pony image...")

    # Fetch the image or display an error
    try:
        async with aiohttp.get(search) as r:
            website = await r.json()
        if randomize:
            if "id" in website:
                imageId = str(website["id"])
                async with aiohttp.get("https://derpibooru.org/images/" + imageId + ".json") as r:
                    website = await r.json()
                imageURL = "https:{}".format(website["image"])
            else:
                return await self.bot.edit_message(message, "Your search terms gave no results.")
        else:
            if website["search"] != []:
                website = website["search"][0]
                imageURL = "https:{}".format(website["image"])
            else:
                return await self.bot.edit_message(message, "Your search terms gave no results.")
    except:
        return await self.bot.edit_message(message, "Error.")

    # If verbose mode is enabled, create an embed and fill it with information
    if verbose:
        # Sets the embed title
        embedTitle = "Derpibooru Image #{}".format(imageId)

        # Sets the URL to be linked
        embedLink = "https://derpibooru.org/{}".format(imageId)

        # Populates the tag list
        tagList = website["tags"].split(", ")
        
        # Checks for the rating and sets an appropriate color
        for i in range(0, len(tagList)):
            if tagList[i] == "safe":
                ratingColor = "00FF00"
                ratingWord = tagList.pop(i)
                break
            elif tagList[i] == "suggestive":
                ratingColor = "FFFF00"
                ratingWord = tagList.pop(i)
                break
            elif tagList[i] == "questionable":
                ratingColor = "FF9900"
                ratingWord = tagList.pop(i)
                break
            elif tagList[i] == "explicit":
                ratingColor = "FF0000"
                ratingWord = tagList.pop(i)
                break

        # Grabs the artist(s)
        for i in range(0, len(tagList)):
            if "artist:" in tagList[i]:
                while "artist:" in tagList[i]:
                    artistList.append(tagList.pop(i)[7:])
                break

        # Determine if there are multiple artists
        if len(artistList) == 1:
            artist = artistList[0]
        elif len(artistList) > 1:
            artists = ", ".join(artistList)
            artist = ""

        # Initialize verbose embed
        output = discord.Embed(title=embedTitle, url=embedLink, colour=discord.Colour(value=int(ratingColor, 16)))

        # Sets the thumbnail and adds the rating and tag fields to the embed
        output.add_field(name="Rating", value=ratingWord)
        if artist:
            output.add_field(name="Artist", value=artist)
        elif artists:
            output.add_field(name="Artists", value=artists)
        output.add_field(name="Tags", value=", ".join(tagList), inline=False)
        output.set_thumbnail(url=imageURL)
    else:
        # Sets the link to the image URL if verbose mode is not enabled
        output = imageURL
    
    # Edits the pending message with the results
    if verbose:
        return await self.bot.edit_message(message, "Image found.", embed=output)
    else:
        return await self.bot.edit_message(message, output)

def check_folder():
    if not os.path.exists("data/pony"):
        print("Creating data/pony folder...")
        os.makedirs("data/pony")

def check_files():
    filters = {"default":["-meme", "safe", "-spoiler:*", "-vulgar"]}
    settings = {"maxfilters":"50"}

    if not fileIO("data/pony/filters.json", "check"):
        print("Creating default pony filters.json...")
        fileIO("data/pony/filters.json", "save", filters)
    else:
        filterlist = fileIO("data/pony/filters.json", "load")
        if "default" not in filterlist:
            filterlist["default"] = filters["default"]
            print("Adding default pony filters...")
            fileIO("data/pony/filters.json", "save", filterlist)
    if not fileIO("data/pony/settings.json", "check"):
        print("Creating default pony settings.json...")
        fileIO("data/pony/settings.json", "save", settings)

def setup(bot):
    check_folder()
    check_files()
    bot.add_cog(Pony(bot))
