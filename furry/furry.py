import discord
from discord.ext import commands
from __main__ import send_cmd_help
import aiohttp
import random
import xml

class Furry:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True,no_pm=True)
    async def furry(self, ctx, *text):
        """Retrieves the latest result from Furrybooru
           Warning: Can and will display NSFW images"""
        server = ctx.message.server
        if len(text) > 0:
            try:
                msg = "+".join(text)
                search = "http://furry.booru.org/index.php?page=dapi&s=post&q=index&limit=1&tags=" + msg
                async with aiohttp.get(search) as r:
                    result = await r.text()
                attr = result.split('"')[1::2]
                cindex = 0
                while cindex != -1:
                    if attr[cindex] == "UTF-8":
                        count = int(attr[cindex+1])
                        cindex = -1
                    else:
                        cindex += 1
                if count > 0:
                    newresult = xml.etree.ElementTree.fromstring(result)
                    url = newresult[0].get('file_url')
                    await self.bot.say(url)
                    return
                else:
                    await self.bot.say("Your search terms gave no results.")
            except:
                await self.bot.say("Error.")
        else:
            await send_cmd_help(ctx)

    @commands.command(pass_context=True,no_pm=True)
    async def furryr(self, ctx, *text):
        """Retrieves a random result from Furrybooru
           Warning: Can and will display NSFW images"""
        server = ctx.message.server
        try:
            msg = "+".join(text)
            search = "http://furry.booru.org/index.php?page=dapi&s=post&q=index&limit=1&tags=" + msg
            async with aiohttp.get(search) as r:
                result = await r.text()
            attr = result.split('"')[1::2]
            cindex = 0
            while cindex != -1:
                if attr[cindex] == "UTF-8":
                    count = int(attr[cindex+1])
                    cindex = -1
                else:
                    cindex += 1
            if count > 0:
                pid = str(random.randrange(0, count-1)) # Generates a random number between 0 and the amount of available images
                search = "http://furry.booru.org/index.php?page=dapi&s=post&q=index&limit=1&pid=" + pid + "&tags=" + msg
                async with aiohttp.get(search) as r:
                    result = await r.text()
                newresult = xml.etree.ElementTree.fromstring(result)
                url = newresult[0].get('file_url')
                await self.bot.say(url)
                return
            else:
                await self.bot.say("Your search terms gave no results.")
        except:
            await self.bot.say("Error.")

def setup(bot):
    bot.add_cog(Furry(bot))
