'''
from selfbot ~ edited by Quanta#5556

'''
import discord
from discord.ext import commands
from urllib.parse import urlparse
import datetime
import asyncio
import random
import pip
import os
import io


class Mod:

    def __init__(self, bot):
        self.bot = bot

    async def have_permissions(ctx):
        return (ctx.author.guild_permissions.administrator == True or ctx.author.guild_permissions.kick_members == True or ctx.author.guild_permissions.ban_members == True or ctx.author.guild_permissions.manage_guild == True or ctx.author.guild_permissions.manage_messages == True )


    async def format_mod_embed(self, ctx, user, success, method, duration = None, location=None):
        '''prevention of extra data'''
        emb = discord.Embed()
        emb.set_author(name=method.title(), icon_url=user.avatar_url)
        emb.color = await ctx.get_dominant_color(user.avatar_url)
        emb.set_footer(text=f'User ID: {user.id}')
        if success:
            if method == 'ban' or method == 'hackban':
                emb.description = f'{user} was just {method}ned.'
            elif method == 'unmute':
                emb.description = f'{user} was just {method}d.'
            elif method == 'mute':
                emb.description = f'{user} was just {method}d for {duration}.'
            elif method == 'channel-lockdown' or method == 'server-lockdown':
                emb.description = f'`{location.name}` is now in lockdown mode!'
            else:
                emb.description = f'{user} was just {method}ed.'
        else:
            if method == 'lockdown' or 'channel-lockdown':
                emb.description = f"You do not have the permissions to {method} `{location.name}`."
            else:
                emb.description = f"You do not have the permissions to {method} {user.name}."

        return emb

    @commands.command()
    @commands.check(have_permissions)
    async def kick(self, ctx, member : discord.Member, *, reason='Please write a reason!'):
        '''Kick someone'''
        try:
            await ctx.guild.kick(member, reason=reason)
        except:
            success = False
        else:
            success = True

        emb = await self.format_mod_embed(ctx, member, success, 'kick')

        await ctx.send(embed=emb)

    @commands.command()
    @commands.check(have_permissions)
    async def ban(self, ctx, member : discord.Member, *, reason='Please write a reason!'):
        '''Ban someone '''
        try:
            await ctx.guild.ban(member, reason=reason)
        except:
            success = False
        else:
            success = True

        emb = await self.format_mod_embed(ctx, member, success, 'ban')

        await ctx.send(embed=emb)

    @commands.command()
    @commands.check(have_permissions)
    async def unban(self, ctx, name_or_id, *, reason=None):
        '''Unban someone '''
        ban = await ctx.get_ban(name_or_id)

        try:
            await ctx.guild.unban(ban.user, reason=reason)
        except:
            success = False
        else:
            success = True

        emb = await self.format_mod_embed(ctx, ban.user, success, 'unban')

        await ctx.send(embed=emb)

    @commands.command(aliases=['del','p','prune'])
    @commands.check(have_permissions)
    async def purge(self, ctx, limit : int):
        '''Clean a no. of messages'''
        await ctx.purge(limit=limit+1) # TODO: add more functionality

    @commands.command()
    async def clean(self, ctx, limit : int=15):
        '''Clean a no. of self messages'''
        await ctx.purge(limit=limit+1, check=lambda m: m.author == ctx.author)


    @commands.command()
    @commands.check(have_permissions)
    async def bans(self, ctx):
        '''list of banned users in the guild'''
        try:
            bans = await ctx.guild.bans()
        except:
            return await ctx.send("`I don't have Permission to view`")

        em = discord.Embed(title=f'List of Banned Members ({len(bans)}):')
        em.description = ', '.join([str(b.user) for b in bans])
        em.color = await ctx.get_dominant_color(ctx.guild.icon_url)

        await ctx.send(embed=em)

    @commands.command()
    @commands.check(have_permissions)
    async def baninfo(self, ctx, *, name_or_id):
        '''reason of a ban from the audit logs.'''
        ban = await ctx.get_ban(name_or_id)
        em = discord.Embed()
        em.color = await ctx.get_dominant_color(ban.user.avatar_url)
        em.set_author(name=str(ban.user), icon_url=ban.user.avatar_url)
        em.add_field(name='Reason', value=ban.reason or 'None')
        em.set_thumbnail(url=ban.user.avatar_url)
        em.set_footer(text=f'User ID: {ban.user.id}')

        await ctx.send(embed=em)

    @commands.command()
    @commands.check(have_permissions)
    async def addrole(self, ctx, member: discord.Member, *, rolename: str):
        '''Adding role to someone else.'''
        role = discord.utils.find(lambda m: rolename.lower() in m.name.lower(), ctx.message.guild.roles)
        if not role:
            return await ctx.send('That role does not exist.')
        try:
            await member.add_roles(role)
            em = discord.Embed(description = f'Added Role: `{role.name}` to {member}', colour = discord.Colour.green())
            await ctx.send(embed = em)
        except:
            await ctx.send("`No Permission to add that role`")


    @commands.command()
    @commands.check(have_permissions)
    async def removerole(self, ctx, member: discord.Member, *, rolename: str):
        '''Remove a role'''
        role = discord.utils.find(lambda m: rolename.lower() in m.name.lower(), ctx.message.guild.roles)
        if not role:
            return await ctx.send('That role does not exist.')
        try:
            await member.remove_roles(role)
            em = discord.Embed(description = f'Removed Role: `{role.name}` from {member}', colour = discord.Colour.red())
            await ctx.send(embed = em)
        except:
            await ctx.send("`I don't have the perms to add that role.`")


    @commands.command()
    @commands.check(have_permissions)
    async def mute(self, ctx, member:discord.Member, duration, *, reason=None):
        '''mute someone for sometime'''
        unit = duration[-1]
        if unit == 's':
            time = int(duration[:-1])
            longunit = 'seconds'
        elif unit == 'm':
            time = int(duration[:-1]) * 60
            longunit = 'minutes'
        elif unit == 'h':
            time = int(duration[:-1]) * 60 * 60
            longunit = 'hours'
        else:
            await ctx.send('Invalid Unit! Use `s`, `m`, or `h`.')
            return

        progress = await ctx.send('Muting user!')
        try:
            for channel in ctx.guild.text_channels:
                await channel.set_permissions(member, overwrite=discord.PermissionOverwrite(send_messages = False), reason=reason)

            for channel in ctx.guild.voice_channels:
                await channel.set_permissions(member, overwrite=discord.PermissionOverwrite(speak=False), reason=reason)
        except:
            success = False
        else:
            success = True

        emb = await self.format_mod_embed(ctx, member, success, 'mute', f'{str(duration[:-1])} {longunit}')
        progress.delete()
        await ctx.send(embed=emb)
        await asyncio.sleep(time)
        try:
            for channel in ctx.guild.channels:
                await channel.set_permissions(member, overwrite=None, reason=reason)
        except:
            pass

    @commands.command()
    @commands.check(have_permissions)
    async def unmute(self, ctx, member:discord.Member, *, reason=None):
        '''Removes channel overrides for specified member (UNMUTE)'''
        progress = await ctx.send('Unmuting user!')
        try:
            for channel in ctx.message.guild.channels:
                await channel.set_permissions(member, overwrite=None, reason=reason)
        except:
            success = False
        else:
            success = True

        emb = await self.format_mod_embed(ctx, member, success, 'unmute')
        progress.delete()
        await ctx.send(embed=emb)


def setup(bot):
	bot.add_cog(Mod(bot))
