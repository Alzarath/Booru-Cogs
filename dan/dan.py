import discord
from discord.ext import commands
from __main__ import send_cmd_help
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

    @commands.command(pass_context=True,no_pm=True)
    async def dan(self, ctx, *text):
        """Retrieves the latest result from Danbooru
           Warning: Can and will display NSFW images"""
        server = ctx.message.server
        if len(text) > 0:
            try:
                msg = "+".join(text)
                search = "http://danbooru.donmai.us/posts.json?limit=" + str(settings["IMAGE_LIMIT"]) + "&tags=" + msg + check_info()
                async with aiohttp.get(search) as r:
                    result = await r.json()
                if result != []:
                    if "success" not in result:
                        for index in range(len(result)): # Goes through each result until it finds one that works
                            if "file_url" in result[index]:
                                url = "http://danbooru.donmai.us" + result[index]["file_url"]
                                await self.bot.say(url)
                                return
                        await self.bot.say("Cannot find an image that can be viewed by you.")
                    else:
                        await self.bot.say(result["message"] + ".")
                else:
                    await self.bot.say("Your search terms gave no results.")
            except:
                await self.bot.say("Error.")
        else:
            await send_cmd_help(ctx)

    @commands.command(pass_context=True,no_pm=True)
    async def danr(self, ctx, *text):
        """Retrieves a random result from Danbooru
           Warning: Can and will display NSFW images"""
        server = ctx.message.server
        if len(text) > 0:
            try:
                msg = "+".join(text)
                search = "http://danbooru.donmai.us/posts.json?limit=" + str(settings["IMAGE_LIMIT"]) + "&random=y" + "&tags=" + msg + check_info()
                async with aiohttp.get(search) as r:
                    result = await r.json()
                if result != []:
                    if "success" not in result:
                        for index in range(len(result)): # Goes through each result until it finds one that works
                            if "file_url" in result[index]:
                                url = "http://danbooru.donmai.us" + result[index]["file_url"]
                                await self.bot.say(url)
                                return
                        await self.bot.say("Cannot find an image that can not be viewed by you.")
                    else:
                        await self.bot.say(result["message"] + ".")
                else:
                    await self.bot.say("Your search terms gave no results.")
            except:
                await self.bot.say("Error.")
        else:
            try:
                msg = "+".join(text)
                search = "http://danbooru.donmai.us/posts.json?limit=" + str(settings["IMAGE_LIMIT"]) + "&random=y" + check_info()
                async with aiohttp.get(search) as r:
                    result = await r.json()
                if "success" not in result:
                    for index in range(len(result)): # Goes through each result until it finds one that works
                        if "file_url" in result[index]:
                            url = "http://danbooru.donmai.us" + result[index]["file_url"]
                            await self.bot.say(url)
                            return
                    await self.bot.say("Cannot find an image that can be viewed by you.")
                else:
                    await self.bot.say(result["message"] + ".")
            except:
                await self.bot.say("Error.")

def check_info():
    searchappend = ""
    if settings["USERNAME"] != "":
        searchappend += "&login=" + settings["USERNAME"]
        if settings["API_KEY"] == "":
            print("You must set API_KEY in cogs/dan.py for USERNAME to be relevant.")
    if settings["API_KEY"] != "":
        searchappend += "&api_key=" + settings["API_KEY"]
        if settings["USERNAME"] == "":
            print("You must set USERNAME in cogs/dan.py for API_KEY to be relevant.")
    return searchappend

def setup(bot):
    bot.add_cog(Dan(bot))
