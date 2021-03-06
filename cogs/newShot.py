import os
import discord
import requests
import json
from discord.ext import commands
import asyncio


#config = imgkit.config(wkhtmltoimage="./bin/wkhtmltopdf")



class newShot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @property
    def character_page_link(self):
        '''getting the character link'''
        with open("data/config.json") as f:
            link = json.load(f)
            if link["char_link"] == "link_here":
                char_link = os.environ.get("char_link")
            else:
                char_link = link["char_link"]
        return char_link

    @commands.command()
    async def sendshot(self,ctx, *, args:str = None):
        try:
            if args == None:
                await ctx.send(content = "`Missing name`")
                return
            link = self.character_page_link
            token = args
            args = args.lower()
            new_text = args.replace(' ','+')
            link = link+new_text
            #imgkit.from_url(f'{link}', './imgs/out.jpg',config=config)
            try:
                sendsnap = "{}/".format(os.environ.get("linksnap"))+link
                await asyncio.sleep(2.5)
                em = discord.Embed(color = 0000, description = token)
                em.set_image(url = "{}".format(sendsnap))
                await ctx.send(embed =em)
            except Exception as e:
                print(e)
                await ctx.send("`some error..`")

        except Exception as e:
            print(e)




def setup(bot):
    bot.add_cog(newShot(bot))
