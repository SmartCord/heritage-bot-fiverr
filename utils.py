from pymongo import MongoClient
from os import environ
import discord
import asyncio
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from discord.ext import commands
import traceback, random, datetime as dt
db_password = environ.get('DB_PASSWORD')
#DATABASE_URI = "localhost:27017"
DATABASE_URI = "mongodb://zen:{}@heritage-shard-00-00-conyf.mongodb.net:27017,heritage-shard-00-01-conyf.mongodb.net:27017,heritage-shard-00-02-conyf.mongodb.net:27017/test?ssl=true&replicaSet=heritage-shard-0&authSource=admin&retryWrites=true".format(db_password)
client = MongoClient(DATABASE_URI)
db = client['djswertz']

formatTime = "%B %d %Y at %I:%M %p"

c = 0x0a91ff
g = 0x18d45c
r = 0xff4343
gif = {
    'yes':'https://media.giphy.com/media/GCvktC0KFy9l6/giphy.gif',
    'nobird':'https://media.giphy.com/media/W5YVAfSttCqre/giphy.gif'
}

def is_admin(bot, ctx):
    try:
        roles = [x.id for x in ctx.author.roles]
    except:
        roles = []
        for server in bot.guilds:
            for member in server.members:
                if member.id == ctx.author.id:
                    for role in member.roles:
                    #roles = [x.id for x in member.roles]
                        roles.append(role.id)
    role_ids = [x['role_id'] for x in db.authorized_roles.find({})]

    auth = []

    for role in roles:
        print(role)
        if role in role_ids:
            auth.append(role)

    print(auth)
    if auth == []:
        return False
    return True

default_prefix = "!"

async def is_pm(ctx):
    if not db.pm.count({}):
        if not ctx.channel == discord.DMChannel:
            return await ctx.send('This command is only usuable on private messages.'), True
        return False

    data = [int(x['pm']) for x in db.pm.find({})]
    if data[0] is 1:
        print('data 1')
        try:
            ctx.guild.members
            return await ctx.send('This command is only usuable on private messages.'), True
        except:
            return False
    return False

async def is_guild(ctx):
    try:
        ctx.guild.members
        return False
    except:
        return await ctx.send('This command is only usuable on a server.'), True

async def giveRankMember(bot, member, rank):
    if not db.ranks.count({"rank_id":rank}):
        return await member.send("Unknown rank. Please send this to the owner.")

    for a in db.ranks.find({"rank_id":rank}):
        rank_list = [x['ranks'] for x in db.users.find({"user_id":member.id})][0]
        if rank in rank_list:
            pass
        else:
            db.users.update_one({"user_id":member.id}, {'$push':{'ranks':rank}})
        #db.users.update_one({"user_id":ctx.author.id}, {'$inc':{'xp':a['rank_xp']}})
        db.users.update_one({"user_id":member.id}, {'$inc':{'gold':a['rank_gold']}})
        e = discord.Embed(color=color())
        if a['rank_image'] != "None":
            e.title = "You have a new rank."
            e.set_image(url=a['rank_image'])
        else:
            e.title = "You just recieved the rank " + a['rank_name']
            e.description = f"Here are your rewards\nGold : {a['rank_gold']}"
            e.set_thumbnail(url="https://cdn.discordapp.com/avatars/514365334568828931/6846abf6dc5000ff5eb885215b7fc002.png")

        if a['rank_role'] != "None":
            def get_shit():
                for server in bot.guilds:
                    return server.roles

            meme = discord.utils.get(get_shit(), id=a['rank_role'])
            noshit = discord.utils.get(bot.get_all_members(), id=member.id)
            print(noshit)
            print(meme)
            if not meme is None:
                try:
                    await noshit.add_roles(meme)
                except discord.Forbidden:
                    pass
        try:
            await member.send(embed=e)
        except:
            await member.send(embed=e)

async def giveRankAuthor(bot, ctx, rank):
    if not db.ranks.count({"rank_id":rank}):
        return await ctx.author.send("Unknown rank. Please send this to the owner.")

    for a in db.ranks.find({"rank_id":rank}):
        rank_list = [x['ranks'] for x in db.users.find({"user_id":ctx.author.id})][0]
        if rank in rank_list:
            pass
        else:
            db.users.update_one({"user_id":ctx.author.id}, {'$push':{'ranks':rank}})
        #db.users.update_one({"user_id":ctx.author.id}, {'$inc':{'xp':a['rank_xp']}})
        db.users.update_one({"user_id":ctx.author.id}, {'$inc':{'gold':a['rank_gold']}})
        e = discord.Embed(color=color())
        footer(ctx, e)
        if a['rank_image'] != "None":
            e.title = "You have a new rank."
            e.set_image(url=a['rank_image'])
        else:
            e.title = "You just recieved the rank " + a['rank_name']
            e.description = f"Here are your rewards\nGold : {a['rank_gold']}"
            e.set_thumbnail(url="https://cdn.discordapp.com/avatars/514365334568828931/6846abf6dc5000ff5eb885215b7fc002.png")

        if a['rank_role'] != "None":
            def get_shit():
                roles = []
                for server in bot.guilds:
                    for role in server.roles:
                        roles.append(role)
                return roles

            meme = discord.utils.get(get_shit(), id=a['rank_role'])
            noshit = discord.utils.get(bot.get_all_members(), id=ctx.author.id)
            print(noshit)
            print(meme)
            if not meme is None:
                try:
                    await bot.add_roles(noshit, meme)
                except discord.Forbidden:
                    pass
        try:
            await ctx.author.send(embed=e)
        except:
            await ctx.send(embed=e)

async def giveAchievementMember(ctx, achievement):
    if not db.achievement.count({"achievement_id":achievement}):
        return await ctx.send("Unknown achievement. Please send this to the owner.")

    for a in db.achievement.find({"achievement_id":achievement}):
        achievement_list = [x['achievements'] for x in db.users.find({"user_id":ctx.id})]
        if achievement in achievement_list[0]:
            pass
        else:
            db.users.update_one({'user_id':ctx.id}, {'$push':{"achievements":achievement}})
        db.users.update_one({"user_id":ctx.id}, {'$inc':{'xp':a['achievement_xp']}})
        e = discord.Embed(title=a['achievement_title'], color=color())
        footer(ctx, e)
        if a['achievement_image'] != "None":
            e.description = "Reward : " + str(a['achievement_xp']) + " XP"
            e.set_image(url=a['achievement_image'])
        else:
            e.description = a['achievement_description'] + "\nReward : " + str(a['achievement_xp']) + " XP"
            e.set_thumbnail(url="https://cdn.discordapp.com/avatars/514365334568828931/6846abf6dc5000ff5eb885215b7fc002.png")

    await ctx.send("You have a new achievement")
    await ctx.send(embed=e)

async def giveAchievementAuthor(ctx, achievement):
    if not db.achievement.count({"achievement_id":achievement}):
        return await ctx.author.send("Unknown achievement. Please send this to the owner.")

    for a in db.achievement.find({"achievement_id":achievement}):
        achievement_list = [x['achievements'] for x in db.users.find({"user_id":ctx.author.id})]
        if achievement in achievement_list[0]:
            pass
        else:
            db.users.update_one({'user_id':ctx.author.id}, {'$push':{"achievements":achievement}})
        db.users.update_one({"user_id":ctx.author.id}, {'$inc':{'xp':a['achievement_xp']}})
        e = discord.Embed(title=a['achievement_title'], color=color())
        footer(ctx, e)
        if a['achievement_image'] != "None":
            e.description = "Reward : " + str(a['achievement_xp']) + " XP"
            e.set_image(url=a['achievement_image'])
        else:
            e.description = a['achievement_description'] + "\nReward : " + str(a['achievement_xp']) + " XP"
            e.set_thumbnail(url="https://cdn.discordapp.com/avatars/514365334568828931/6846abf6dc5000ff5eb885215b7fc002.png")

    await ctx.author.send("You have a new achievement")
    await ctx.author.send(embed=e)

def achievement(name):
    base = Image.open("assets/achievement.png").convert('RGBA')
    font = ImageFont.truetype(font='assets/GeosansLight.ttf', size=40)
    base = base.convert('RGBA')
    canvas = ImageDraw.Draw(base)
    canvas.text((195, 80), name, font=font, fill="white")
    file = BytesIO()
    base.save(file, "png")
    file.seek(0)
    return file

def color():
    return random.choice([0xff66c1, 0x6666c1, 0xb0d996, 0x588585, 0x21ff94, 0x1d4457, 0x77003c, 0x936dd4, 0xd46db6, 0x48cfa6])

def icon(ctx, guild):
    return guild.icon_url if guild else ctx.me.avatar_url

def returnPrefix(message):
    try:
        if db.server_prefixes.count({"server_id":message.guild.id}):
            for x in db.server_prefixes.find({"server_id":message.guild.id}):
                return x['prefix']
        return default_prefix
    except:
        return default_prefix

def footer(ctx, embed, extra=None):
    try:
        if ctx.author.avatar_url:
            avatar = ctx.author.avatar_url
        else:
            avatar = ctx.me.avatar_url
        author = ctx.author
    except:
        avatar = ctx.avatar_url
        author = ctx
    embed.timestamp = dt.datetime.utcnow()
    if extra is None:
        extra = ""
    else:
        extra = " " + extra
    embed.set_footer(text=f"{author}{extra}", icon_url=avatar)

async def usage(ctx, arguments, example, description):
    prefix = returnPrefix(ctx)
    args = [f"<{arg}>" for arg in arguments]
    arguments = " ".join(args)
    example = " ".join(example)
    command = ctx.command.qualified_name
    e = discord.Embed(title="Wrong Usage", color=color())
    e.add_field(name="Proper Usage", value=f"{prefix}{command} {arguments}")
    e.add_field(name="\u200b", value="\u200b")
    e.add_field(name="Example", value=f"{prefix}{command} {example}")
    e.add_field(name="Description", value=description)
    e.set_thumbnail(url=gif['nobird'])
    footer(ctx, e)
    await ctx.send(embed=e)

async def error(ctx, error, description):
    e = discord.Embed(title=error, description=description, color=r)
    e.set_thumbnail(url=ctx.me.avatar_url)
    footer(ctx, e)
    await ctx.send(embed=e)

async def success(ctx, message, image=None):
    e = discord.Embed(title="Success!", description=message, color=g)
    try:
        e.set_thumbnail(url=ctx.avatar_url) if not image else None
    except:
        e.set_thumbnail(url=ctx.author.avatar_url) if not image else None
    e.set_image(url=image) if image else None
    footer(ctx, e)
    await ctx.send(embed=e)

async def boterror(bot, message, e):
    e = traceback.format_exc()
    em = discord.Embed(title="An unexpected error has occured", description=f"```{e}```\nThe error has now been sent to the bot developer", color=r)
    em.set_thumbnail(url=bot.user.avatar_url)
    footer(message, em)
    await message.send(embed=em)

    if message.author.id == 363880571614527488:
        return

    ctx = bot.get_channel(514437538564538384)
    em = discord.Embed(title=f"Command Error", description=f"Command : {message.message.content}\n \
    User : {message.author} ({message.author.id})\n \
    Server : {message.guild} ({message.guild.id})", color=r)
    em.add_field(name="Error", value=f"```{e}```")
    if message.author.avatar_url:
        a = message.author.avatar_url
    else:
        a = message.me.avatar_url
    em.set_thumbnail(url=a)
    await ctx.send(embed=em)
