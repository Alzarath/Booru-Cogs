import discord
from discord.ext import commands
from __main__ import send_cmd_help
import aiohttp
import random
import xml

class E621:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True,no_pm=True)
    async def e621(self, ctx, *text):
        """Retrieves the latest result from e621
           Warning: Can and will display NSFW images"""
        server = ctx.message.server
        if len(text) > 0:
            msg = "+".join(text)
            search = "http://e621.net/post/index.json?limit=1&tags=" + msg
            url = await fetch_image(randomize=False, search=search)
            await self.bot.say(url)
        else:
            await send_cmd_help(ctx)

    @commands.command(pass_context=True,no_pm=True)
    async def e621r(self, ctx, *text):
        """Retrieves a random result from e621
           Warning: Can and will display NSFW images"""
        server = ctx.message.server
        if len(text) > 0:
            msg = "+".join(text)
            search = "http://e621.net/post/index.json?limit=1&tags=" + msg
            url = await fetch_image(randomize=True, search=search)
            await self.bot.say(url)
        else:
            msg = "+".join(text)
            search = "http://e621.net/post/index.json?limit=1&tags="
            url = await fetch_image(randomize=True, search=search)
            await self.bot.say(url)

async def fetch_image(randomize, search):
    try:
        if randomize == True:
            search += "+order:random"
        async with aiohttp.get(search) as r:
            website = await r.json()
        if website != []:
            return website[0]["file_url"]
        else:
            return "Your search terms gave no results."
    except:
        return "Error."

def setup(bot):
    bot.add_cog(E621(bot))
