import discord
from discord.ext import commands
from __main__ import send_cmd_help
import aiohttp
import random
import xml

class Loli:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True,no_pm=True)
    async def loli(self, ctx, *text):
        """Retrieves the latest result from Lolibooru
           Warning: Can and will display NSFW images"""
        server = ctx.message.server
        if len(text) > 0:
            try:
                msg = "+".join(text)
                search = "https://lolibooru.moe/post/index.json?limit=1&tags=" + msg
                async with aiohttp.get(search) as r:
                    website = await r.json()
                print("Debug")
                if website != []:
                    url = website[0]["file_url"]
                    url = url.replace(" ", "+")
                    await self.bot.say(url)
                else:
                    await self.bot.say("Your search terms gave no results.")
            except:
                await self.bot.say("Error.")
        else:
            await send_cmd_help(ctx)

    @commands.command(pass_context=True,no_pm=True)
    async def lolir(self, ctx, *text):
        """Retrieves a random result from Lolibooru
           Warning: Can and will display NSFW images"""
        server = ctx.message.server
        if len(text) > 0:
            try:
                msg = "+".join(text)
                search = "https://lolibooru.moe/post/index.json?limit=1&tags=order:random+" + msg
                async with aiohttp.get(search) as r:
                    website = await r.json()
                print("Debug")
                if website != []:
                    url = website[0]["file_url"]
                    url = url.replace(" ", "+")
                    await self.bot.say(url)
                else:
                    await self.bot.say("Your search terms gave no results.")
            except:
                await self.bot.say("Error.")
        else:
            try:
                msg = "+".join(text)
                search = "https://lolibooru.moe/post/index.json?limit=1&tags=order:random"
                async with aiohttp.get(search) as r:
                    website = await r.json()
                print("Debug")
                if website != []:
                    url = website[0]["file_url"]
                    url = url.replace(" ", "+")
                    await self.bot.say(url)
                else:
                    await self.bot.say("Your search terms gave no results.")
            except:
                await self.bot.say("Error.")

def setup(bot):
    bot.add_cog(Loli(bot))
