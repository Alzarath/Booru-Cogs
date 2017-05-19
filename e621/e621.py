import discord
from discord.ext import commands
from .utils.dataIO import fileIO
from .utils import checks
from __main__ import send_cmd_help
from urllib import parse
import os
import aiohttp

settings = {
# Maximum filters per server before it starts restricting tags from being added to the filter list.
# Does not represent the amount of tags a search permits.
    "MAX_FILTER_TAGS" : 50
}

class E621:
    def __init__(self, bot):
        self.bot = bot
        self.filters = fileIO("data/e621/filters.json", "load")
        self.settings = fileIO("data/e621/settings.json", "load")

    @commands.command(pass_context=True, no_pm=True)
    async def e621(self, ctx, *text):
        """Retrieves the latest result from e621"""
        if len(text) > 0:
            await fetch_image(self=self, ctx=ctx, randomize=False, tags=text)
        else:
            await send_cmd_help(ctx)

    @commands.command(pass_context=True, no_pm=True)
    async def e621r(self, ctx, *text):
        """Retrieves a random result from e621"""
        await fetch_image(self=self, ctx=ctx, randomize=True, tags=text)

    @commands.group(pass_context=True)
    async def e621filter(self, ctx):
        """Manages e621 filters
           Warning: Can be used to allow NSFW images

           Filters automatically apply tags to each search"""
        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)

    @e621filter.command(name="add", pass_context=True, no_pm=True)
    @checks.admin_or_permissions(manage_server=True)
    async def _add_e621filter(self, ctx, filtertag : str):
        """Adds a tag to the server's e621 filter list

           Example: !e621filter add rating:s"""
        server = ctx.message.server
        if server.id not in self.filters:
            self.filters[server.id] = self.filters["default"]
            fileIO("data/e621/filters.json", "save", self.filters)
            self.filters = fileIO("data/e621/filters.json", "load")
        if len(self.filters[server.id]) < int(self.settings["maxfilters"]):
            if filtertag not in self.filters[server.id]:
                self.filters[server.id].append(filtertag)
                fileIO("data/e621/filters.json", "save", self.filters)
                await self.bot.say("Filter '{}' added to the server's e621 filter list.".format(filtertag))
            else:
                await self.bot.say("Filter '{}' is already in the server's e621 filter list.".format(filtertag))
        else:
            await self.bot.say("This server has exceeded the maximum filters ({}/{}). https://www.youtube.com/watch?v=1MelZ7xaacs".format(len(self.filters[server.id]), self.settings["maxfilters"]))

    @e621filter.command(name="del", pass_context=True, no_pm=True)
    @checks.admin_or_permissions(manage_server=True)
    async def _del_e621filter(self, ctx, filtertag : str=""):
        """Deletes a tag from the server's e621 filter list

           Without arguments, reverts to the default e621 filter list

           Example: !e621filter del rating:s"""
        server = ctx.message.server
        if len(filtertag) > 0:
            if server.id not in self.filters:
                self.filters[server.id] = self.filters["default"]
                fileIO("data/e621/filters.json", "save", self.filters)
                self.filters = fileIO("data/e621/filters.json", "load")
            if filtertag in self.filters[server.id]:
                self.filters[server.id].remove(filtertag)
                fileIO("data/e621/filters.json", "save", self.filters)
                await self.bot.say("Filter '{}' deleted from the server's e621 filter list.".format(filtertag))
            else:
                await self.bot.say("Filter '{}' does not exist in the server's e621 filter list.".format(filtertag))
        else:
            if server.id in self.filters:
                del self.filters[server.id]
                fileIO("data/e621/filters.json", "save", self.filters)
                await self.bot.say("Reverted the server to the default e621 filter list.")
            else:
                await self.bot.say("Server is already using the default e621 filter list.")

    @e621filter.command(name="list", pass_context=True)
    async def _list_e621filter(self, ctx):
        """Lists all of the filters currently applied to the current server"""
        server = ctx.message.server
        if server.id in self.filters:
            filterlist = '\n'.join(sorted(self.filters[server.id]))
            targetServer = "{}'s".format(server.name)
        else:
            filterlist = '\n'.join(sorted(self.filters["default"]))
            targetServer = "Default"
        await self.bot.say("{} e621 filter list contains:```\n{}```".format(targetServer, filterlist))

    @commands.group(pass_context=True)
    @checks.is_owner()
    async def e621set(self, ctx):
        """Manages e621 settings"""
        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)

    @e621set.command(pass_context=True,name="verbose")
    @checks.admin_or_permissions(manage_server=True)
    async def _verbose_e621set(self, ctx, toggle : str="toggle"):
        """Toggles verbose mode"""
        server = ctx.message.server
        if server.id not in self.settings:
            self.settings[server.id] = {"verbose":False}
            fileIO("data/e621/settings.json", "save", self.settings)
            self.settings = fileIO("data/e621/settings.json", "load")
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
        fileIO("data/e621/settings.json", "save", self.settings)

    @e621set.command(name="maxfilters")
    async def _maxfilters_e621set(self, maxfilters):
        """Sets the global tag limit for the filter list

           Gives an error when a user tries to add a filter while the server's filter list contains a certain amount of tags"""
        self.settings["maxfilters"] = maxfilters
        fileIO("data/e621/settings.json", "save", self.settings)
        await self.bot.say("Maximum filters allowed per server for e621 set to '{}'.".format(maxfilters))

async def fetch_image(self, ctx, randomize, tags):
    server = ctx.message.server
    self.filters = fileIO("data/e621/filters.json", "load")
    self.settings = fileIO("data/e621/settings.json", "load")

    # Initialize verbosity as false
    verbose = False

    # Set verbosity to true if the current server has it set as such
    if server.id in self.settings and self.settings[server.id]["verbose"]:
        verbose = True

    # initialize base URL
    search = "http://e621.net/post/index.json?limit=1&tags="
    tagSearch = ""

    # Assign tags to URL
    if tags:
        tagSearch += "{} ".format(" ".join(tags))
    if server.id in self.filters:
        tagSearch += " ".join(self.filters[server.id])
    else:
        tagSearch += " ".join(self.filters["default"])

    # Randomize results
    if randomize:
        tagSearch += " order:random"
    search += parse.quote_plus(tagSearch)

    #Inform users about image retrieval
    message = await self.bot.say("Fetching e621 image...")

    # Fetch and display the image or an error
    try:
        async with aiohttp.get(search) as r:
            website = await r.json()
        if website != []:
            if "success" not in website:
                imageURL = website[0].get('file_url')
                if verbose:
                    # Check for the rating and set an appropriate color
                    tagList = website[0].get('tags')
                    rating = website[0].get('rating')
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
                    link = "https://e621.net/post/show/{}".format(website[0].get('id'))
                    
                    # Initialize verbose embed
                    output = discord.Embed(description=link, colour=discord.Colour(value=int(ratingColor, 16)))

                    # Sets the thumbnail and adds the rating and tag fields to the embed
                    output.add_field(name="Rating", value=rating)
                    output.add_field(name="Tags", value=tagList.replace('_', '\_'))
                    output.set_thumbnail(url=imageURL)

                    # Edits the pending message with the results
                    return await self.bot.edit_message(message, "Image found.", embed=output)
                else:
                    # Edits the pending message with the result
                    return await self.bot.edit_message(message, imageURL)
            else:
                return await self.bot.edit_message(message, "{}".format(website["message"]))
        else:
            return await self.bot.edit_message(message, "Your search terms gave no results.")
    except:
        return await self.bot.edit_message(message, "Error.")

def check_folder():
    if not os.path.exists("data/e621"):
        print("Creating data/e621 folder...")
        os.makedirs("data/e621")

def check_files():
    filters = {"default":["rating:safe", "-grimdark", "-suggestive"]}
    settings = {"maxfilters":"50"}

    if not fileIO("data/e621/filters.json", "check"):
        print("Creating default e621 filters.json...")
        fileIO("data/e621/filters.json", "save", filters)
    else:
        filterlist = fileIO("data/e621/filters.json", "load")
        if "default" not in filterlist:
            filterlist["default"] = filters["default"]
            print("Adding default e621 filters...")
            fileIO("data/e621/filters.json", "save", filterlist)
    if not fileIO("data/e621/settings.json", "check"):
        print("Creating default e621 settings.json...")
        fileIO("data/e621/settings.json", "save", settings)

def setup(bot):
    check_folder()
    check_files()
    bot.add_cog(E621(bot))
