from imports import *


def returnImage(binary):
    img = Image.open(binary).convert('RGBA')
    file = BytesIO()
    img.save(file, "png")
    file.seek(0)
    return file

class General:
    def __init__(self, bot):
        self.bot = bot

    async def on_message(self, message): #checked
        if message.author.bot:
            return

        if is_admin(self.bot, message):
            if not db.users.count({"user_id":message.author.id}):
                data = {
                    "user_id":message.author.id,
                    "xp":0,
                    "xp_max":100,
                    "ranks":[],
                    "gold":0,
                    "level":1,
                    "achievements":[],
                    "messages":1,
                    "gaming_channels":[]
                }
                #verified_role = message.guild.get_role(514984584354594837) # Testing
                verified_role = message.guild.get_role(514950485942468609)
                if verified_role is None:
                    well_fuck = await message.channel.send("Member role not found. Please message the owner.")
                    await asyncio.sleep(4)
                    await well_fuck.delete()
                    return
                db.users.insert_one(data)
                try:
                    await message.author.edit(roles=[verified_role])
                except discord.Forbidden:
                    pass
                await giveAchievementAuthor(message, 0)
                await giveRankAuthor(self.bot, message, 0)
                data = {
                    "card_name":"ADVENTURER",
                    "act_name":"Adventurer",
                    "card_image":"https://cdn.discordapp.com/attachments/517009241643548682/517044094317494283/Adventurer.png",
                    "purchased_on":int(time.time()),
                    "gifted_on":"None",
                    "gifted_by":"None",
                    "user_id":message.author.id,
                    "amount":1
                }
                if db.user_cards.count({"user_id":message.author.id, "card_name":"ADVENTURER"}):
                    pass
                else:
                    db.user_cards.insert_one(data)
                    e = discord.Embed(title="New Card!", color=color())
                    e.set_image(url="https://cdn.discordapp.com/attachments/517009241643548682/517044094317494283/Adventurer.png")
                    await message.author.send(embed=e)

        if message.channel.id == 514950788150329354 or message.channel.id == 514057242396327964:

            rational_fuck_is_dis = similar("AGREE", message.content.upper())
            if rational_fuck_is_dis >= 0.6:
                if not db.users.count({"user_id":message.author.id}):
                    data = {
                        "user_id":message.author.id,
                        "xp":0,
                        "xp_max":100,
                        "ranks":[0],
                        "gold":0,
                        "level":1,
                        "achievements":[],
                        "messages":1,
                        "gaming_channels":[]
                    }
                    #verified_role = message.guild.get_role(514984584354594837) # Testing
                    verified_role = message.guild.get_role(514950485942468609)
                    if verified_role is None:
                        well_fuck = await message.channel.send("Member role not found. Please message the owner.")
                        await asyncio.sleep(4)
                        await well_fuck.delete()
                        return
                    db.users.insert_one(data)
                    try:
                        await message.author.edit(roles=[verified_role])
                    except discord.Forbidden:
                        pass
                    await message.delete()
                    await giveAchievementAuthor(message, 0)
                    await giveRankAuthor(self.bot, message, 0)
                    data = {
                        "card_name":"ADVENTURER",
                        "act_name":"Adventurer",
                        "card_image":"https://cdn.discordapp.com/attachments/517009241643548682/517044094317494283/Adventurer.png",
                        "purchased_on":int(time.time()),
                        "gifted_on":"None",
                        "gifted_by":"None",
                        "user_id":message.author.id,
                        "amount":1
                    }
                    if db.user_cards.count({"user_id":message.author.id, "card_name":"ADVENTURER"}):
                        pass
                    else:
                        db.user_cards.insert_one(data)
                        e = discord.Embed(title="New Card!", color=color())
                        e.set_image(url="https://cdn.discordapp.com/attachments/517009241643548682/517044094317494283/Adventurer.png")
                        await message.author.send(embed=e)
            if not is_admin(self.bot, message):
                await message.delete()

    @commands.command()
    async def trade(self, ctx, user: discord.Member = None, *, card: str = None):
        try:

            if user is None or card is None:
                return await usage(ctx, ['mention a user', 'card name'], [ctx.author.mention, 'cool card'], 'Lets you trade cards with other users.')

            card = card.upper()

            if not db.user_cards.count({"user_id":ctx.author.id, "card_name":card}):
                return await error(ctx, "Card Error", "You do not have that card.")

            if not db.users.count({"user_id":user.id}):
                return await error(ctx, "User Error", "The user you mentioned is not yet verified.")

            if user is ctx.author:
                return await error(ctx, "User Error", "That's just sad, why would you trade with yourself?")

            actname = [x['act_name'] for x in db.user_cards.find({"user_id":ctx.author.id, "card_name":card})][0]
            authorimagecard = [x['card_image'] for x in db.user_cards.find({"user_id":ctx.author.id, "card_name":card})][0]


            x = False
            def check(m):
                return m.channel == user.dm_channel and m.author == user

            await ctx.send("Successfully asked {} what card he wants to trade to you. If he does not reply within 10 minutes the trade will be canceled. From now on I will private message you.".format(user))
            e = discord.Embed(title=f"{ctx.author.name} Wants to trade with you", description=f"What card do you want to trade to him. His card offer is the card **{actname}** (Image Below).\nPlease enter the card you want to trade to him. If you want to cancel then type cancel. **You will automatically agree and we only have to wait for {ctx.author} to agree once you enter a card.**", color=color())
            e.set_image(url=authorimagecard)
            footer(user, e)
            await user.send(embed=e)

            while x is False:
                try:
                    msg = await self.bot.wait_for('message', check=check, timeout=600.0)
                except asyncio.TimeoutError:
                    await user.send("Nevermind. Trade has been canceled because you didn't reply within 10 minutes.")
                    return await ctx.author.send("Your trade with {} has been canceled because he didn't reply within 10 minutes.".format(user))
                msg = msg.content
                if msg.upper() == card:
                    await user.send("Unfortunately you cannot use the same card that {} is offering you. Please try again.".format(ctx.author))
                    x = False
                else:
                    x = True
                if msg.upper() == 'CANCEL':
                    await user.send("Successfully canceled.")
                    return await ctx.author.send("{} decided to cancel the trade. :(".format(user))
                if not db.user_cards.count({"user_id":user.id, "card_name":msg.upper()}) and x == True:
                    await user.send("You do not have that card. Please try again. Use the command `{}collection` to view all your cards.".format(returnPrefix(ctx)))
                    x = False
                else:
                    if x == True:
                        oldamount = [y['amount'] for y in db.user_cards.find({"user_id":user.id, "card_name":msg.upper()})][0]
                        for m in db.user_cards.find({"user_id":user.id, "card_name":msg.upper()}):
                            user_data = m
                            user_data['purchased_on'] = user.id
                            user_data['user_id'] = ctx.author.id
                            user_data['_id'] = str(uuid.uuid4())
                            user_data['amount'] = 1
                            if user_data['gifted_by'] != "None":
                                user_data['gifted_by'] = "None"
                                user_data['gifted_on'] = "None"
                            usercard = m['act_name']
                            usercardname = msg.upper()
                        useractname = [y['act_name'] for y in db.user_cards.find({"user_id":user.id, "card_name":usercardname})][0]
                        userimagecard = [y['card_image'] for y in db.user_cards.find({"user_id":user.id, "card_name":usercardname})][0]

            await user.send("Successfully set your card to {} and {}'s card to {}.".format(useractname, ctx.author.name, actname))
            await user.send("Waiting for {} to agree. If he doesn't reply within 10 minutes the trade will be automatically canceled.".format(ctx.author))
            await ctx.author.send("{} Agreed to the trade and his card offer is the card {}.".format(user, useractname))

            e = discord.Embed(title=f"{user.name} Agreed with the trade!", description=f"His card offer is the card **{useractname}** (Image Below).\nPlease type agree to start the trade. If you do not reply within 10 minutes the trade will be canceled. If you want to cancel now then type cancel.", color=color())
            e.set_image(url=userimagecard)
            footer(ctx, e)
            await ctx.author.send(embed=e)
            def check(m):
                return m.channel == ctx.author.dm_channel and m.author == ctx.author
            x = False
            for m in db.user_cards.find({"user_id":ctx.author.id, "card_name":card}):
                data = m
                data['purchased_on'] = ctx.author.id
                data['user_id'] = user.id
                data['_id'] = str(uuid.uuid4())
                data['amount'] = 1
                if data['gifted_by'] != "None":
                    data['gifted_by'] = "None"
                    data['gifted_on'] = "None"
            while x is False:
                try:
                    message = await self.bot.wait_for('message', check=check, timeout=600.0)
                except asyncio.TimeoutError:
                    await user.send("The trade has been canceled because {} didn't reply within 10 minutes.".format(ctx.author))
                    return await ctx.author.send("Successfully canceled the trade because you didn't reply within 10 minutes.")
                if message.content.upper() == 'CANCEL':
                    await user.send("{} Didn't agree with the trade. The trade is now canceled.".format(ctx.author))
                    return await ctx.author.send("Successfully canceled the trade.")
                elif message.content.upper() == 'AGREE' or message.content.upper() == 'AGREE.':
                    loading_emoji = self.bot.get_emoji(514771904284852224)
                    loading_msg = await ctx.author.send(f"{loading_emoji} Processing data.")
                    loading_msg1 = await user.send(f"{loading_emoji} Processing data.")
                    if db.user_cards.count({"user_id":user.id, "card_name":card}):
                        db.user_cards.update_one({"user_id":user.id, "card_name":card}, {'$inc':{'amount':1}})
                    else:
                        db.user_cards.insert_one(data)

                    if db.user_cards.count({"user_id":ctx.author.id, "card_name":usercardname}):
                        db.user_cards.update_one({"user_id":ctx.author.id, "card_name":usercardname}, {'$inc':{'amount':1}})
                    else:
                        db.user_cards.insert_one(user_data)

                    oldshit = [y['amount'] for y in db.user_cards.find({"user_id":user.id, "card_name":usercardname})][0]
                    if oldshit - 1 < 1:
                        db.user_cards.delete_one({'user_id':user.id, "card_name":usercardname})
                    else:
                        db.user_cards.update_one({"user_id":user.id, 'card_name':usercardname}, {'$inc':{'amount':-1}})

                    oldshit = [y['amount'] for y in db.user_cards.find({"user_id":ctx.author.id, "card_name":card})][0]
                    if oldshit - 1 < 1:
                        db.user_cards.delete_one({"user_id":ctx.author.id, "card_name":card})
                    else:
                        db.user_cards.update_one({"user_id":ctx.author.id, "card_name":card}, {'$inc':{'amount':-1}})
                    x = True
                    await loading_msg.delete()
                    await loading_msg1.delete()
                    await success(ctx.author, f"Successfully traded cards with {user}. {user.name} Gave you the card {usercard} and you gave {user.name} the card {actname}.", image=userimagecard)
                    await success(user, f"Successfully traded cards with {ctx.author}. {ctx.author} Gave you the card {actname} and you gave {ctx.author} the card {usercard}.", image=authorimagecard)

            if not db.trades.count({'user_id':ctx.author.id}):
                data = {
                    'user_id':ctx.author.id,
                    'amount':1
                }
                db.trades.insert_one(data)
            else:
                db.trades.update_one({"user_id":ctx.author.id}, {'$inc':{'amount':1}})
                amount = [x['amount'] for x in db.trades.find({"user_id":ctx.author.id})][0]
                if amount == 3:
                    achievements_earned = [x['achievements'] for x in db.users.find({"user_id":ctx.author.id})][0]
                    if 3 in achievements_earned:
                        pass
                    else:
                        await giveAchievementAuthor(ctx, 3)

            if not db.trades.count({'user_id':user.id}):
                data = {
                    'user_id':user.id,
                    'amount':1
                }
                db.trades.insert_one(data)
            else:
                db.trades.update_one({"user_id":user.id}, {'$inc':{'amount':1}})
                amount = [x['amount'] for x in db.trades.find({"user_id":user.id})][0]
                if amount == 3:
                    achievements_earned = [x['achievements'] for x in db.users.find({"user_id":user.id})][0]
                    if 3 in achievements_earned:
                        pass
                    else:
                        await giveAchievementMember(user, 3)


        except Exception as e:
            await boterror(self.bot, ctx, e)

    @commands.command() #checked
    async def my_achievements(self, ctx):
        try:
            if await is_pm(ctx):
                return

            if not db.users.count({"user_id":ctx.author.id}):
                return await error(ctx, "No account found", "You don't have an account yet. You first have to read the rules channel and type agree on the rules channel.")

            pg = commands.Paginator(prefix="", suffix="", max_size=1022)
            for x in db.users.find({"user_id":ctx.author.id}):
                user = x['achievements']
                despacito = [x['achievement_id'] for x in db.achievement.find({})]
                data = {}
                for i, o in zip(user, despacito):
                    title = [l['achievement_title'] for l in db.achievement.find({"achievement_id":i})][0]
                    description = [l['achievement_description'] for l in db.achievement.find({'achievement_id':i})][0]
                    pg.add_line(f"""
:large_blue_diamond: {title}
{description}
""")

            embeds = []
            for page in pg.pages:
                e = discord.Embed(title="Your Achievements!", description=page, color=color())
                e.set_thumbnail(url=ctx.author.avatar_url)
                footer(ctx, e)
                embeds.append(e)

            p = paginator.EmbedPages(ctx, author=ctx.author, embeds=embeds)
            await p.paginate()

        except Exception as e:
            await boterror(self.bot, ctx, e)

    @commands.command() #checked
    async def gift(self, ctx, user: discord.Member = None, *, card: str = None):
        try:
            auth = is_admin(self.bot, ctx)

            if user is None or card is None:
                return await usage(ctx, ['mention a user', 'card name'], [ctx.author.mention, 'cool card'], 'Lets you gift a card to another user.')

            if user is ctx.author:
                return await error(ctx, "User Error", "Sorry but no. Why would you give yourself a card you already have. That's just a sad :(")

            if not db.users.count({"user_id":user.id}):
                return await error(ctx, "User Error", "The user you have mentioned is not yet verified.")

            card = card.upper()

            users_cards = []
            if not db.user_cards.count({"user_id":ctx.author.id}):
                if auth == True and db.mod_cards.count({}):
                    pass
                else:
                    return await error(ctx, "Cards not found", "You do not have any cards at all. You can purchase one from the store by using the `{}purchase` command.".format(returnPrefix(ctx)))

            if not db.user_cards.count({"user_id":ctx.author.id, "card_name":card}):
                if auth == True and db.mod_cards.count({"card_name":card}):
                    pass
                else:
                    return await error(ctx, "Card not found", "The card you entered is not in your collection. Check your collection by using the `{}collection` command.".format(returnPrefix(ctx)))
            try:
                oldamount = [x['amount'] for x in db.user_cards.find({"user_id":ctx.author.id, "card_name":card})][0]
            except IndexError:
                pass

            if db.mod_cards.count({"card_name":card}) and auth == True:
                for x in db.mod_cards.find({"card_name":card}):
                    # data = x
                    # data['purchased_on'] = "None"
                    # data['gifted_on'] = int(time.time())
                    # data['gifted_by'] = ctx.author.id
                    # data['amount'] = 1
                    # data['_id'] = str(uuid.uuid4())
                    # data['user_id'] = user.id

                    data = {
                        "card_name":card,
                        "act_name":x['act_name'],
                        "card_image":x['card_image_url'],
                        "purchased_on":"None",
                        "gifted_on":int(time.time()),
                        "gifted_by":ctx.author.id,
                        "user_id":user.id,
                        "amount":1
                    }

                    if db.user_cards.count({"user_id":user.id, "card_name":card}):
                        def check(m):
                            return m.channel == ctx.channel and m.author == ctx.author
                        try:
                            await ctx.send("That user already has the same card. Are you sure you still want to gift that to him? Type yes if yes, no if no")
                            msg = await self.bot.wait_for('message', check=check, timeout=20.0)
                            yeet = similar('YES', msg.content.upper())
                            oof = similar('NO', msg.content.upper())
                            if yeet >= 0.6:
                                db.user_cards.update_one({"user_id":user.id, "card_name":card}, {'$inc':{'amount':1}})
                            elif oof >= 0.6:
                                return await ctx.send("Understandable have a nice day.")
                        except asyncio.TimeoutError:
                            return await ctx.send("Time out, The process has been successfully canceled because you didn't reply.")
                    else:
                        db.user_cards.insert_one(data)

                    actname = data['act_name']
                    await success(ctx, "Successfully gifted {} the card {}.".format(user, actname))
            else:
                for x in db.user_cards.find({"user_id":ctx.author.id, "card_name":card}):
                    data = x
                    data['purchased_on'] = "None"
                    data['gifted_on'] = int(time.time())
                    data['gifted_by'] = ctx.author.id
                    data['amount'] = 1
                    data['_id'] = str(uuid.uuid4())
                    data['user_id'] = user.id

                    oldamount = oldamount - 1


                    if db.user_cards.count({"user_id":user.id, "card_name":card}):
                        def check(m):
                            return m.channel == ctx.channel and m.author == ctx.author
                        try:
                            await ctx.send("That user already has the same card. Are you sure you still want to gift that to him? Type yes if yes, no if no")
                            msg = await self.bot.wait_for('message', check=check, timeout=20.0)
                            yeet = similar('YES', msg.content.upper())
                            oof = similar('NO', msg.content.upper())
                            if yeet >= 0.6:
                                db.user_cards.update_one({"user_id":user.id, "card_name":card}, {'$inc':{'amount':1}})
                            elif oof >= 0.6:
                                return await ctx.send("Understandable have a nice day.")
                        except asyncio.TimeoutError:
                            return await ctx.send("Time out, The process has been successfully canceled because you didn't reply.")
                    else:
                        db.user_cards.insert_one(data)
                    if oldamount < 1:
                        db.user_cards.delete_one({"user_id":ctx.author.id, "card_name":card})
                    else:
                        db.user_cards.update_one({"user_id":ctx.author.id, "card_name":card}, {'$inc':{'amount':-1}})

                    actname = data['act_name']

                    await success(ctx, "Successfully gifted {} the card {}. You now have {} of that card left.".format(user, actname, oldamount))

            if not db.gave_gifts.count({'user_id':ctx.author.id}):
                data = {
                    'user_id':ctx.author.id,
                    'amount':1
                }
                db.gave_gifts.insert_one(data)
            else:
                db.gave_gifts.update_one({"user_id":ctx.author.id}, {'$inc':{'amount':1}})
                amount = [x['amount'] for x in db.gave_gifts.find({"user_id":ctx.author.id})][0]
                if amount == 3:
                    achievements_earned = [x['achievements'] for x in db.users.find({"user_id":ctx.author.id})][0]
                    if 8 in achievements_earned:
                        pass
                    else:
                        await giveAchievementAuthor(ctx, 8)


        except Exception as e:
            await boterror(self.bot, ctx, e)

    @commands.command() #checked
    async def stats(self, ctx):
        try:
            if await is_pm(ctx):
                return
            if not db.users.count({"user_id":ctx.author.id}):
                return await error(ctx, "No account found", "You don't have an account yet. You first have to read the rules channel and type agree on the rules channel.")

            cards = 0
            if db.user_cards.count({"user_id":ctx.author.id}):
                lul = [x['amount'] for x in db.user_cards.find({"user_id":ctx.author.id})]
                for item in lul:
                    cards += item
            auth = is_admin(self.bot, ctx)
            if auth:
                if db.mod_cards.count({}):
                    lul = len([x for x in db.mod_cards.find({})])
                    cards += lul
            for x in db.users.find({"user_id":ctx.author.id}):
                if x['ranks'] != []:
                    current_rank = [y['rank_name'] for y in db.ranks.find({"rank_id":x['ranks'][-1]})][0]
                else:
                    current_rank = "None :("

                if x['gold'] < 2:
                    g = ""
                else:
                    g = "s"
                description = f"""
<:gold:514791023671509003> Gold{g} : {x['gold']}
<:card:515865391663284225> Cards : {cards}
:star: XP : {x['xp']}
:large_blue_diamond: Achievements : {len(x['achievements'])}
:trophy: Highest Rank : {current_rank}
"""
                e = discord.Embed(title="User Stats", description=description, color=color())
                e.set_thumbnail(url=ctx.author.avatar_url)
                footer(ctx, e)
                await ctx.send(embed=e)

        except Exception as e:
            await boterror(self.bot, ctx, e)

    @commands.command() #checked
    async def store(self, ctx):
        try:

            if not db.store.count({}):
                return await error(ctx, "Store Error", "The store is currently empty. This is a very unlikely error and it usually only happens when the database is cleared (Which normally we will not do). Please send this error to the owner.")

            embeds = []

            common = []#x
            uncommon = []#y
            rare = []#z
            epic = []#h
            legendary = []#w
            for data in db.store.find({}):
                e = discord.Embed(title=f"{data['act_name']}", description=f"<:gold:514791023671509003> Price : {data['card_price']} Golds\n<:db:514791975007027220> Stock : {data['card_amount']}\n<:diagay:515536803407593486> Rarity : {data['rarity']}", color=color())
                e.set_image(url=data['card_image_url'])
                footer(ctx, e)
                if similar('COMMON', data['rarity'].upper()) >= 0.9:
                    common.append(e)
                elif similar('UNCOMMON', data['rarity'].upper()) >= 0.9:
                    uncommon.append(e)
                elif similar('RARE', data['rarity'].upper()) >= 0.9:
                    rare.append(e)
                elif similar('EPIC', data['rarity'].upper()) >= 0.9:
                    epic.append(e)
                elif similar('LEGENDARY', data['rarity'].upper()) >= 0.9:
                    legendary.append(e)
                else:
                    embeds.append(e)

            for x in common:
                embeds.append(x)

            for x in uncommon:
                embeds.append(x)

            for x in rare:
                embeds.append(x)

            for x in epic:
                embeds.append(x)

            for x in legendary:
                embeds.append(x)

            p = paginator.EmbedPages(ctx, embeds=embeds)
            await p.paginate()

        except Exception as e:
            await boterror(self.bot, ctx, e)

    @commands.command(aliases=['buy']) #checked
    async def purchase(self, ctx, *, card: str = None):
        try:

            if card is None:
                return await usage(ctx, ['card name'], ['Cool Card'], 'Allows you to purchase a card from the store.')

            card = card.upper()

            if not db.users.count({"user_id":ctx.author.id}):
                return await error(ctx, "Profile not found", "The bot was not able to find your profile on the database. Please try again.")

            if not db.store.count({"card_name":card}):
                return await error(ctx, "Card not found", "The card you entered is not found on the store.")

            data = [x for x in db.store.find({"card_name":card})]
            price = data[0]['card_price']
            left = data[0]['card_amount']
            act_name = data[0]['act_name']

            if left != "Infinite":

                if left < 1:
                    return await error(ctx, "Purchase Error", "The card you entered is out of stock.")

            user_data = [x for x in db.users.find({"user_id":ctx.author.id})][0]
            user_golds = user_data['gold']

            if price > user_golds:
                return await error(ctx, "Purchase Error", "You don't have enough gold to purchase this item.")

            if left != "Infinite":
                db.store.update_one({"card_name":card}, {'$inc':{'card_amount':-1}})
            db.users.update_one({"user_id":ctx.author.id}, {'$inc':{'gold':-price}})
            data = {
                "card_name":card,
                "act_name":act_name,
                "card_image":data[0]['card_image_url'],
                "purchased_on":int(time.time()),
                "gifted_on":"None",
                "gifted_by":"None",
                "user_id":ctx.author.id,
                "amount":1
            }
            if db.user_cards.count({"user_id":ctx.author.id, "card_name":card}):
                db.user_cards.update_one({"user_id":ctx.author.id}, {'$inc':{'amount':1}})
            else:
                db.user_cards.insert_one(data)

            leftgold = [x['gold'] for x in db.users.find({"user_id":ctx.author.id})][0]
            if leftgold < 2:
                g = ""
            else:
                g = "s"
            await success(ctx, f"Successfully purchased the card. You only have {leftgold} Gold{g} left on your account. You may now view it using the `{returnPrefix(ctx)}collection` command.")


        except Exception as e:
            await boterror(self.bot, ctx, e)

    @commands.command() #checked
    async def collection(self, ctx):
        try:
            auth = is_admin(self.bot, ctx)
            if not db.user_cards.count({"user_id":ctx.author.id}):
                if auth == True and db.mod_cards.count({}):
                    pass
                else:
                    return await error(ctx, "Collection Error", f"You haven't purchased any cards yet. Use the `{returnPrefix(ctx)}store` command to view all cards. Use the `{returnPrefix(ctx)}purchase` to purchase a card.")
            embeds = []
            total_cards = len([x for x in db.user_cards.find({"user_id":ctx.author.id})])
            for x in db.user_cards.find({"user_id":ctx.author.id}):
                e = discord.Embed(title=f"{x['act_name']}", color=color())
                e.description = f"""
<:db:514791975007027220> Quantity : {x['amount']}
"""

                if x['purchased_on'] != "None":
                    try:
                        e.description += ":clock10: Purchased on (UTC) : {}".format(datetime.datetime.utcfromtimestamp(x['purchased_on']).strftime(utils.formatTime))
                    except: # If it didn't work then it's probably traded lmao
                        user = discord.utils.get(self.bot.get_all_members(), id=x['purchased_on'])
                        if user is None:
                            user = "Unknown User"
                        e.description += f"<:trade:516533473813594133> Traded With : {user}"
                if db.store.count({"card_name":x['card_name']}):
                    priceon = [y['card_price'] for y in db.store.find({"card_name":card})][0]
                    e.description += "\n<:gold:514791023671509003> Price on store : {}".format(priceon)

                if x['gifted_by'] != "None":
                    e.description += ":gift: Gifted by : {}".format(discord.utils.get(self.bot.get_all_members(), id=x['gifted_by']))
                    e.description += "\n:clock130: Gifted on (UTC): {}".format(datetime.datetime.utcfromtimestamp(x['gifted_on']).strftime(utils.formatTime))

                e.set_image(url=x['card_image'])
                footer(ctx, e, extra=f"Total : {total_cards}")
                embeds.append(e)
            if auth == True and db.mod_cards.count({}):
                total_cards = total_cards + len([x for x in db.mod_cards.find({})])
                for x in db.mod_cards.find({}):
                    e = discord.Embed(title=f"{x['act_name']}", color=color())
                    e.description = f"""
<:db:514791975007027220> Quantity : Infinite
"""
                    e.set_image(url=x['card_image_url'])
                    footer(ctx, e, extra=f"Total : {total_cards}")
                    embeds.append(e)
            p = paginator.EmbedPages(ctx, embeds=embeds)
            await p.paginate()
        except Exception as e:
            await boterror(self.bot, ctx, e)

    @commands.command() #checked
    async def menu(self, ctx):
        try:
            if not db.commands.count({}):
                return await error(ctx, "Menu Error", "The bot was not able to reach the commands database. This is a very unlikely error and it usually only happens when the database is cleared (Which normally we will not do). Please send this error to the owner.")
            commandsx = []
            for command in db.commands.find({}):
                commandsx.append(f"{returnPrefix(ctx)}{command['name']} {command['arguments']}\n{command['description']}\n")

            if is_admin(self.bot, ctx):
                for command in db.commands_admin.find({}):
                    commandsx.append(f"{returnPrefix(ctx)}{command['name']} {command['arguments']}\n{command['description']}\n")


            pg = commands.Paginator(prefix="", suffix="", max_size=1022)
            for cmd in commandsx:
                pg.add_line(cmd)

            embeds = []
            for page in pg.pages:
                e = discord.Embed(title="Commands", description=page, color=color())
                e.set_thumbnail(url=ctx.me.avatar_url)
                footer(ctx, e)
                embeds.append(e)

            p = paginator.EmbedPages(ctx, embeds=embeds)
            await p.paginate()

        except Exception as e:
            await boterror(self.bot, ctx, e)

def setup(bot):
    bot.add_cog(General(bot))
