import discord
from discord.ext import commands
from __main__ import send_cmd_help
import aiohttp
import random
import xml

class Gel:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True,no_pm=True)
    async def gel(self, ctx, *text):
        """Retrieves the latest result from Gelbooru
           Warning: Can and will display NSFW images"""
        server = ctx.message.server
        if len(text) > 0:
            msg = "+".join(text)
            search = "http://gelbooru.com/index.php?page=dapi&s=post&q=index&limit=1&tags=" + msg
            url = await fetch_image(randomize=False, search=search)
            await self.bot.say(url)
        else:
            send_cmd_help(ctx)

    @commands.command(pass_context=True,no_pm=True)
    async def gelr(self, ctx, *text):
        """Retrieves a random result from Gelbooru
           Warning: Can and will display NSFW images"""
        server = ctx.message.server
        if len(text) > 0:
            msg = "+".join(text)
            search = "http://gelbooru.com/index.php?page=dapi&s=post&q=index&limit=1&tags=" + msg
            url = await fetch_image(randomize=True, search=search)
            await self.bot.say(url)
        else:
            search = "http://gelbooru.com/index.php?page=dapi&s=post&q=index&limit=1"
            url = await fetch_image(randomize=True, search=search)
            await self.bot.say(url)

async def fetch_image(randomize, search):
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

def setup(bot):
    bot.add_cog(Gel(bot))
