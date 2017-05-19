import discord
from discord.ext import commands
from .utils.dataIO import fileIO
from .utils import checks
from __main__ import send_cmd_help
from urllib import parse
import os
import aiohttp

class Dan:
    # Danbooru is awful and it should feel awful
    def __init__(self, bot):
        self.bot = bot
        self.filters = fileIO("data/dan/filters.json","load")
        self.settings = fileIO("data/dan/settings.json","load")

    @commands.command(pass_context=True,no_pm=True)
    async def dan(self, ctx, *text):
        """Retrieves the latest result from Danbooru"""
        if len(text) > 0:
            await fetch_image(self, ctx, randomize=False, tags=text)
        else:
            await send_cmd_help(ctx)

    @commands.command(pass_context=True,no_pm=True)
    async def danr(self, ctx, *text):
        """Retrieves a random result from Danbooru"""
        await fetch_image(self, ctx, randomize=True, tags=text)

    @commands.group(pass_context=True)
    async def danfilter(self, ctx):
        """Manages dan filters
           Warning: Can be used to allow NSFW images

           Filters automatically apply tags to each search"""
        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)

    @danfilter.command(name="add", pass_context=True, no_pm=True)
    @checks.admin_or_permissions(manage_server=True)
    async def _add_danfilter(self, ctx, filtertag : str):
        """Adds a tag to the server's dan filter list

           Example: !danfilter add rating:safe"""
        server = ctx.message.server
        if server.id not in self.filters:
            self.filters[server.id] = self.filters["default"]
            fileIO("data/dan/filters.json","save",self.filters)
            self.filters = fileIO("data/dan/filters.json","load")
        if len(self.filters[server.id]) < int(self.settings["maxfilters"]):
            if filtertag not in self.filters[server.id]:
                self.filters[server.id].append(filtertag)
                fileIO("data/dan/filters.json","save",self.filters)
                await self.bot.say("Filter '{}' added to the server's dan filter list.".format(filtertag))
            else:
                await self.bot.say("Filter '{}' is already in the server's dan filter list.".format(filtertag))
        else:
            await self.bot.say("This server has exceeded the maximum filters ({}/{}). https://www.youtube.com/watch?v=1MelZ7xaacs".format(len(self.filters[server.id]), self.settings["maxfilters"]))

    @danfilter.command(name="del", pass_context=True, no_pm=True)
    @checks.admin_or_permissions(manage_server=True)
    async def _del_danfilter(self, ctx, filtertag : str=""):
        """Deletes a tag from the server's dan filter list

           Without arguments, reverts to the default dan filter list

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

    @danfilter.command(name="list", pass_context=True)
    async def _list_danfilter(self, ctx):
        """Lists all of the filters currently applied to the current server"""
        server = ctx.message.server
        if server.id in self.filters:
            filterlist = '\n'.join(sorted(self.filters[server.id]))
            targetServer = "{}'s".format(server.name)
        else:
            filterlist = '\n'.join(sorted(self.filters["default"]))
            targetServer = "Default"
        await self.bot.say("{} dan filter list contains:```\n{}```".format(targetServer, filterlist))

    @commands.group(pass_context=True)
    @checks.is_owner()
    async def danset(self, ctx):
        """Manages dan options
           Global only

           Keep in mind that your information, while stored locally, is stored in plain text"""
        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)

    @danset.command(name="username")
    async def _username_danset(self, username:str=""):
        """Sets the username used for Danbooru

           Useful to apply premium benefits to searches"""
        self.settings["username"] = username
        if username != "":
            msg = "Username assigned to dan's settings."
            if self.settings["api_key"] == "":
                msg += " Don't forget to add the API key."
        else:
            msg = "Username cleared."
        fileIO("data/dan/settings.json","save",self.settings)
        await self.bot.say(msg)

    @danset.command(name="apikey")
    async def _apikey_danset(self, api_key:str=""):
        """Sets the API key used for Danbooru

           Useful to apply premium benefits to searches"""
        self.settings["api_key"] = api_key
        if api_key != "":
            msg = "API key assigned to dan's settings."
            if self.settings["username"] == "":
                msg += " Don't forget to add the username."
        else:
            msg = "API key cleared."
        fileIO("data/dan/settings.json","save",self.settings)
        await self.bot.say(msg)

    @danset.command(name="maxfilters")
    async def _maxfilters_danset(self, maxfilters):
        """Sets the global tag limit for the filter list

           Gives an error when a user tries to add a filter when the server's filter list contains a certain amount of tags"""
        self.settings = fileIO("data/dan/settings.json","load")
        self.settings["maxfilters"] = maxfilters
        fileIO("data/dan/settings.json","save",self.settings)
        await self.bot.say("Maximum filters allowed per server for dan set to '{}'.".format(maxfilters))
    
    @danset.command(pass_context=True,name="verbose")
    @checks.admin_or_permissions(manage_server=True)
    async def _verbose_danset(self, ctx, toggle : str = "toggle"):
        """Toggles verbose mode"""
        server = ctx.message.server
        if server.id not in self.settings:
            self.settings[server.id] = {"verbose":False}
            fileIO("data/dan/settings.json", "save", self.settings)
            self.settings = fileIO("data/dan/settings.json", "load")
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
        fileIO("data/dan/settings.json", "save", self.settings)

async def fetch_image(self, ctx, randomize, tags):
    server = ctx.message.server
    self.filters = fileIO("data/dan/filters.json", "load")
    self.settings = fileIO("data/dan/settings.json", "load")

    # Initialize verbosity as false
    verbose = False

    # Set verbosity to true if the current server has it set as such
    if server.id in self.settings and self.settings[server.id]["verbose"]:
        verbose = True

    # Initialize base URL
    search = "http://danbooru.donmai.us/posts.json?tags="
    tagSearch = ""

    # Assign tags to URL
    if tags:
        tagSearch += "{} ".format(" ".join(tags))
    if server.id in self.filters:
        tagSearch += " ".join(self.filters[server.id])
    else:
        tagSearch += " ".join(self.filters["default"])
    search += parse.quote_plus(tagSearch)

    # Randomize results
    if randomize:
        search += "&random=y"

    # Assign login information
    if self.settings["username"] != "" and self.settings["api_key"] != "":
        search += "&login={}&api_key={}".format(self.settings["username"], self.settings["api_key"])

    # Inform users about image retrieval
    message = await self.bot.say("Fetching dan image...")

    # Fetch and display the image or an error
    try:
        async with aiohttp.get(search) as r:
            website = await r.json()
        if website != []:
            if "success" not in website:
                for index in range(len(website)): # Goes through each result until it finds one that works
                    if "file_url" in website[index]:
                        imageURL = "https://danbooru.donmai.us{}".format(website[index].get('file_url'))
                        if verbose:
                            # Check for the rating and set an appropriate color
                            tagList = website[index].get('tag_string')
                            rating = website[index].get('rating')
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
                            link = "https://danbooru.donmai.us/posts/{}".format(website[index].get('id'))
                            
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
                return await self.bot.edit_message(message, "Cannot find an image that can be viewed by you.")
            else:
                # Edits the pending message with an error received by the server
                return await self.bot.edit_message(message, "{}".format(website["message"]))
        else:
            return await self.bot.edit_message(message, "Your search terms gave no results.")
    except:
        return await self.bot.edit_message(message, "Error.")

def check_folder():
    if not os.path.exists("data/dan"):
        print ("Creating data/dan folder...")
        os.makedirs("data/dan")

def check_files():
    filters = {"default":["rating:safe"]}
    settings = {"username":"", "api_key":"", "maxfilters":"10"}

    if not fileIO("data/dan/filters.json", "check"):
        print ("Creating default dan filters.json...")
        fileIO("data/dan/filters.json", "save", filters)
    else:
        filterlist = fileIO("data/dan/filters.json", "load")
        if "default" not in filterlist:
            filterlist["default"] = filters["default"]
            print ("Adding default dan filters...")
            fileIO("data/dan/filters.json", "save", filterlist)
    if not fileIO("data/dan/settings.json", "check"):
        print ("Creating default dan settings.json...")
        fileIO("data/dan/settings.json", "save", settings)

def setup(bot):
    check_folder()
    check_files()
    bot.add_cog(Dan(bot))
