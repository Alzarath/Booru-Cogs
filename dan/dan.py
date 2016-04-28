import discord
from discord.ext import commands
from __main__ import send_cmd_help
import aiohttp

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
                search = "http://danbooru.donmai.us/posts.json?limit=1&tags=" + msg
                async with aiohttp.get(search) as r:
                    result = await r.json()
                if result != []:
                    if "success" not in result:
                        if "file_url" in result[0]:
                            url = "http://danbooru.donmai.us" + result[0]["file_url"]
                            await self.bot.say(url)
                        else:
                            await self.bot.say("This image can not be viewed by you.")
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
                search = "http://danbooru.donmai.us/posts.json?limit=1&random=y&tags=" + msg
                async with aiohttp.get(search) as r:
                    result = await r.json()
                if result != []:
                    if "success" not in result:
                        if "file_url" in result[0]:
                            url = "http://danbooru.donmai.us" + result[0]["file_url"]
                            await self.bot.say(url)
                        else:
                            await self.bot.say("This image can not be viewed by you.")
                    else:
                        await self.bot.say(result["message"] + ".")
                else:
                    await self.bot.say("Your search terms gave no results.")
            except:
                await self.bot.say("Error.")
        else:
            try:
                msg = "+".join(text)
                search = "http://danbooru.donmai.us/posts.json?limit=1&random=y"
                async with aiohttp.get(search) as r:
                    result = await r.json()
                if result != []:
                    if "success" not in result:
                        if "file_url" in result[0]:
                            url = "http://danbooru.donmai.us" + result[0]["file_url"]
                            await self.bot.say(url)
                        else:
                            await self.bot.say("This image can not be viewed by you.")
                    else:
                        await self.bot.say(result["message"] + ".")
                else:
                    await self.bot.say("Your search terms gave no results.")
            except:
                await self.bot.say("Error.")

def setup(bot):
    bot.add_cog(Dan(bot))
