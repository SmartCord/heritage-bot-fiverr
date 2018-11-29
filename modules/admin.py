from imports import *

owners = [438206313894379520, 363880571614527488]

yeses = ('YES', 'TRUE', 'INDEED', 'ABSOLUTELY', 'YEAH', 'YE')
noes = ('NO', 'NAH', 'NOTY', 'FALSE', 'NOT A CHANCE', 'NU')

def returnBinary(image):
    img = requests.get(image)
    img_bytes = BytesIO(img.content).read()
    #img = Image.open(img_bytes).convert('RGBA')
    #file = BytesIO()
    #img.save(file, "png")
    #file.seek(0)
    binary_image = Binary(img_bytes)
    return binary_image

def is_url_image(image_url):
   image_formats = ("image/png", "image/jpeg", "image/jpg")
   r = requests.head(image_url)
   if r.headers["content-type"] in image_formats:
      return True
   return False

class Admin:
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def give_golds(self, ctx, user: discord.Member = None, amount: str = None):
        try:
            auth = is_admin(self.bot, ctx)
            if auth == False:
                return

            if user is None or amount is None:
                return await usage(ctx, ['mention a user', 'amount'], [ctx.author.mention, '1000'], "Lets you give gold to other users.")

            try:
                amount = int(amount)
            except:
                return await error(ctx, "Integer Error", "Amount must be an integer.")

            if not db.users.count({"user_id":user.id}):
                return await error(ctx, "User Error", "The user you mentioned does not have an account yet. He has to type agree on the rules channel to get an account.")

            db.users.update_one({'user_id':user.id}, {'$inc':{'gold':amount}})
            if amount < 2:
                g = ""
            else:
                g = "s"
            await success(ctx, f"Successfully gave {user} {amount} Gold{g}")

        except Exception as e:
            await boterror(self.bot, ctx, e)

    @commands.command()
    async def give_achievement(self, ctx, user: discord.Member = None, achievement_id: str = None):
        try:
            auth = is_admin(self.bot, ctx)

            if auth == False:
                return

            if user is None or achievement_id is None:
                return await usage(ctx, ['mention a user', 'achievement id'] [ctx.author.mention, 5], 'Lets you give users achievements')

            try:
                id = int(achievement_id)
            except:
                return await error(ctx, "Achievement Error", "Achievement ID must be an integer. To get a list of achievements together with their id then use the `{}achievements` commands".format(returnPrefix(ctx)))

            if not db.achievement.count({"achievement_id":id}):
                return await error(ctx, "Achievement Error", "Achievement ID not found, use the `{}achievements` command to get a list of achievements together with their id.".format(returnPrefix(ctx)))

            await giveAchievementMember(user, id)

            await success(ctx, f"Successfully gave {user} the achievement.")
            for x in db.achievement.find({"achievement_id":id}):
                await success(ctx.author, f"Successfully gave {user} the achievement {x['achievement_title']}")

        except Exception as e:
            await boterror(self.bot, ctx, e)

    @commands.command()
    async def non_gaming_channels(self, ctx):
        try:
            auth = is_admin(self.bot, ctx)
            if auth == False:
                return

            pg = commands.Paginator(prefix="", suffix="", max_size=1022)
            i = 1
            for x in db.non_gaming.find({}):
                channel = discord.utils.get(self.bot.get_all_channels(), id=x['channel_id'])
                if channel is None:
                    data = "Channel cannot be found."
                else:
                    data = channel.mention
                pg.add_line(f"{i}. {data}")
                i += 1

            embeds = []
            for page in pg.pages:
                e = discord.Embed(title="Non gaming channels!", description=page, color=color())
                e.set_thumbnail(url=ctx.me.avatar_url)
                footer(ctx, e)
                embeds.append(e)

            p = paginator.EmbedPages(ctx, author=ctx.author, embeds=embeds)
            await p.paginate()

        except Exception as e:
            await boterror(self.bot, ctx, e)

    @commands.command()
    async def edit_achievement(self, ctx, id: str = None):
        try:
            auth = is_admin(self.bot, ctx)
            if auth == False:
                return
            if id is None:
                return await usage(ctx, ['achievement id'], ['1'], 'Lets you edit an achievement. To get the list of achievement with their ids use the `{}achievements` command.'.format(returnPrefix(ctx)))

            try:
                id = int(id)
            except:
                return await error(ctx, "Achievement Error", "Achievement ID must be an integer.")

            if not db.achievement.count({"achievement_id":id}):
                return await error(ctx, "Achievement not found", "The achievement ID you enter didn't match any results. To get the ids of the achievements use the `{}achievements` command.".format(returnPrefix(ctx)))

            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel

            await ctx.send("Alright let me walk you through the process of editing an achievement. (**You can cancel this process anytime by sending CANCEL**)\nPlease select an option from the list below.\n\nOptions : \nA : Edit the achievement title/name\nB : Edit the achievement image\nC : Edit the achievement description\nD : Edit the reward xp of the achievement")

            async def a():
                await ctx.send("Alright it's time to edit the achievement title/name.\nPlease enter the new title/name of the achievement.")
                shit = [x['achievement_title'].upper() for x in db.achievement.find({})]
                old = [x['achievement_title'] for x in db.achievement.find({"achievement_id":id})][0]
                m = False
                while m is False:
                    msg = await self.bot.wait_for('message', check=check)
                    msg = msg.content
                    if msg.upper() == 'CANCEL':
                        return await ctx.send("Successfully canceled.")
                    if msg.upper() in shit:
                        await ctx.send("A achievement with the same name already exists. Please try again.")
                    else:
                        name = msg
                        m = True

                db.achievement.update_one({'achievement_id':id}, {'$set':{'achievement_title':name}})
                return await success(ctx, "Successfully changed the achievement title from {} to {}.".format(old, name))

            async def b():
                await ctx.send("Alright it's time to edit the achievement image.\nPlease enter the new image of the achievement, it can either be an attachment or an image url. (Enter None to remove the image)")
                img_error = "Failed to set the image. Make sure you attach an image or send an image url. Try again. (If you want to remove the image then enter None)"
                old = [x['achievement_image'] for x in db.achievement.find({"achievement_id":id})][0]
                m = False
                while m is False:
                    msg_1 = await self.bot.wait_for('message', check=check)
                    msg = msg_1.content

                    if msg.upper() == 'CANCEL':
                        return await ctx.send("Successfully canceled.")

                    if msg.upper() == 'NONE':
                        image = "None"
                        m = True

                    if msg.startswith(('http://', 'https://')) and m is False:
                        image = msg.split()
                        image = image[0]
                        if is_url_image(image):
                            image = image
                            m = True
                        else:
                            await ctx.send(img_error)
                    else:
                        if msg_1.attachments != [] and m is False:
                            image = msg_1.attachments[0].url
                            if is_url_image(image):
                                image = image
                                m = True
                            else:
                                await ctx.send(img_error)
                    if m is False:
                        await ctx.send(img_error)

                db.achievement.update_one({"achievement_id":id}, {'$set':{'achievement_image':image}})
                return await success(ctx, "Successfully set the achievement image from {} to {}.".format(old, image))

            async def c():
                await ctx.send("Alright it's time to edit the achievement description.\nPlease enter the new description of the achievement.")
                old = [x['achievement_description'] for x in db.achievement.find({"achievement_id":id})][0]
                new = await self.bot.wait_for('message', check=check)
                new = new.content
                db.achievement.update_one({"achievement_id":id}, {'$set':{'achievement_description':new}})
                await success(ctx, "Successfully set the achievement description from {} to {}.".format(old, new))

            async def d():
                await ctx.send("Alright it's time to edit the amount of xp to reward to a user.\nPlease enter the new amount of xp to give to a user when they reach this achievement (Value cannot be less than 1 or negative).")
                old = [x['achievement_xp'] for x in db.achievement.find({"achievement_id":id})][0]
                m = False
                while m is False:
                    msg = await self.bot.wait_for('message', check=check)
                    msg = msg.content
                    if msg.upper() == 'CANCEL':
                        return await ctx.send('Successfully canceled.')

                    for x in msg.split():
                        try:
                            new = int(x)
                            if new < 1:
                                await ctx.send("Invalid answer. Answer must be greater than 0.")
                            else:
                                m = True
                        except:
                            m = False
                    if m is False:
                        await ctx.send("Invalid answer. Answer must be an integer.")

                db.achievement.update_one({'achievement_id':id}, {'$set':{'achievement_xp':new}})
                await success(ctx, "Successfully set the reward xp from {} to {}.".format(old, new))

            oof = {
                'A':a,
                'B':b,
                'C':c,
                'D':d
            }

            x = False
            while x is False:
                msg = await self.bot.wait_for('message', check=check)
                msg = msg.content
                if msg.upper() == 'CANCEL':
                    return await ctx.send("Successfully canceled.")
                for c in msg.split():
                    try:
                        await oof[c.upper()]()
                        x = True
                    except KeyError:
                        x = False
                if x is False:
                    await ctx.send("Invalid option")

        except Exception as e:
            await boterror(self.bot, ctx, e)

    @commands.command() #checked
    async def edit_rank(self, ctx, id: str = None):
        try:
            auth = is_admin(self.bot, ctx)
            if auth == False:
                return
            if id is None:
                return await usage(ctx, ['rank id'], ['1'], 'Lets you edit a rank. To get the ids of ranks use the `{}ranks` command.'.format(returnPrefix(ctx)))

            try:
                id = int(id)
            except:
                return await error(ctx, "Rank Error", "Rank ID must be an integer.")

            if not db.ranks.count({'rank_id':id}):
                return await error(ctx, "Rank not found", "The rank ID you entered didn't match any rankds. To get the ids of ranks use the `{}ranks` command.".format(returnPrefix(ctx)))

            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel

            await ctx.send("Alright let me walk you through the process of editing a rank. (**You can cancel this process anytime by sending CANCEL**)\nPlease select an option from the list below.\n\nOptions : \nA : Edit the rank name\nB : Edit the required xp to reach the rank\nC : Edit the amount of golds to give when the user reaches the rank.\nD : Edit the rank's image\nE : Edit the role the bot gives to a user when the user reaches the rank")

            async def a():
                m = False
                await ctx.send("Alright it's time to rename the rank.\nPlease enter the new name for the rank.")
                old_name = [x['rank_name'] for x in db.ranks.find({"rank_id":id})][0]
                while m is False:
                    msg = await self.bot.wait_for('message', check=check)
                    msg = msg.content
                    if msg.upper() == 'CANCEL':
                        return await ctx.send("Successfully canceled.")
                    if db.ranks.count({"rank_name":msg}):
                        await ctx.send("A rank with the same name already exists. Please try again.")
                    else:
                        m = True

                db.ranks.update_one({"rank_id":id}, {'$set':{'rank_name':msg}})
                return await success(ctx, "Successfully renamed the rank {} to {}".format(old_name, msg))

            async def b():
                m = False
                await ctx.send("Alright it's time to change the required xp of the rank.\nPlease enter the new required xp.")
                despacito = [x['rank_xp'] for x in db.ranks.find({"rank_id":id})][0]
                while m is False:
                    msg = await self.bot.wait_for('message', check=check)
                    msg = msg.content
                    if msg.upper() == 'CANCEL':
                        return await ctx.send("Successfully canceled.")
                    for shitto in msg.split():
                        try:
                            despacito_2 = int(shitto)
                            if despacito_2 <= 1:
                                await ctx.send("Invalid Answer. Answer cannot be lower than 2.")
                            else:
                                m = True
                        except:
                            m = False

                    if m is False:
                        await ctx.send("Invalid Answer. Answer must be an integer.")
                db.ranks.update_one({"rank_id":id}, {'$set':{'rank_xp':despacito_2}})
                return await success(ctx, "Successfully changed the required xp from {} to {}".format(despacito, despacito_2))

            async def c():
                m = False
                await ctx.send("Alright it's time to change the amount of golds to reward to the user.\nPlease enter the new amount.")
                tseries_is_gay = [x['rank_gold'] for x in db.ranks.find({"rank_id":id})][0]
                while m is False:
                    msg = await self.bot.wait_for('message', check=check)
                    msg = msg.content
                    if msg.upper() is 'CANCEL':
                        return await ctx.send("Successfully canceled.")

                    for kys in msg.split():
                        try:
                            v = int(kys)
                            if v <= 0:
                                await ctx.send("Invalid Answer. Answer cannot be lower than 1.")
                            else:
                                m = True
                        except Exception as e:
                            m = False

                    if m is False:
                        await ctx.send("Invalid Answer. Answer must be an integer.")

                db.ranks.update_one({"rank_id":id}, {'$set':{'rank_gold':v}})
                return await success(ctx, "Successfully change the amount of golds to reward from {} to {}".format(tseries_is_gay, v))

            async def d():
                m = False
                await ctx.send("Alright it's time to change the rank's image.\nPlease either attach an image or enter a image url. (If you want to remove the image then enter None)")
                fuck = [x['rank_image'] for x in db.ranks.find({"rank_id":id})][0]
                img_error = "Failed to set the image. Make sure you attach an image or send an image url. Try again. (If you want to remove the image then enter None)"
                while m is False:
                    msg_1 = await self.bot.wait_for('message', check=check)
                    msg = msg_1.content
                    if msg.upper() == "CANCEL":
                        return await ctx.send("Successfully canceled.")

                    if msg.upper() == "NONE":
                        image = "None"
                        m = True

                    else:
                        if msg.startswith(('http://', 'https://')):
                            image = [x for x in msg.split()]
                            image = image[0]
                            if is_url_image(image):
                                image = image
                                m = True
                            else:
                                await ctx.send(img_error)
                        else:
                            if msg_1.attachments != []:
                                image = msg_1.attachments[0].url
                                if is_url_image(image):
                                    image = image
                                    m = True
                                else:
                                    await ctx.send(img_error)
                    if m is False:
                        await ctx.send(img_error)


                db.ranks.update_one({"rank_id":id}, {'$set':{'rank_image':image}})
                return await success(ctx, "Successfully set the rank image from {} to {}".format(fuck, image))

            async def e():
                m = False
                await ctx.send("Alright it's time to change the role of the rank.\nPlease enter the name of the new role (This will look for the role in the server)")
                shit = [x['rank_role'] for x in db.ranks.find({"rank_id":id})][0]
                def get_shit():
                    roles = []
                    for server in self.bot.guilds:
                        for role in server.roles:
                            roles.append(role)
                    return roles
                shit = discord.utils.get(get_shit(), id=shit)
                if shit is None:
                    shit = "None"
                else:
                    shit = shit.name
                while m is False:
                    msg = await self.bot.wait_for('message', check=check)
                    msg = msg.content
                    if msg.upper() == 'CANCEL':
                        return await ctx.send("Successfully canceled.")
                    server_roles = []
                    for meme in self.bot.guilds:
                        for role in meme.roles:
                            server_roles.append(role)

                    print([x.name for x in server_roles])

                    for role in server_roles:
                        if role.name.upper() == msg.upper():
                            role_to_update_to = role.id
                            m = True

                    if m is False:
                        await ctx.send("Invalid Answer. No role found.")

                db.ranks.update_one({"rank_id":id}, {'$set':{'rank_role':role_to_update_to}})
                return await success(ctx, "Successfully set the rank's role from {} to {}.".format(shit, msg))



            oof = {
                'A':a,
                'B':b,
                'C':c,
                'D':d,
                'E':e
            }

            x = False
            while x is False:
                msg = await self.bot.wait_for('message', check=check)
                msg = msg.content
                if msg.upper() == 'CANCEL':
                    return await ctx.send("Successfully canceled.")
                for shitto in msg.split():
                    try:
                        await oof[shitto.upper()]()
                        x = True
                    except KeyError:
                        x = False
                if x is False:
                    await ctx.send("Invalid Option")


        except Exception as e:
            await boterror(self.bot, ctx, e)

    @commands.command() #checked
    async def achievements(self, ctx):
        try:
            auth = is_admin(self.bot, ctx)
            if auth == False:
                return

            if not db.achievement.count({}):
                return await error(ctx, "No achievements found", "The achievements collction is empty. Please send this error to the owner.")

            pg = commands.Paginator(prefix="", suffix="", max_size=1022)
            for x in db.achievement.find({}):
                if x['achievement_image'] == "None":
                    achievement_image = "None"
                else:
                    achievement_image = f"[Click Here!]({x['achievement_image']})"

                pg.add_line(f"Achievement Title : {x['achievement_title']}\nAchievement ID : {x['achievement_id']}\nAchievement Description : {x['achievement_description']}\nAchievement Image : {achievement_image}\nAchievement XP Reward : {x['achievement_xp']}\n")

            gays = []
            for lol in pg.pages:
                e = discord.Embed(title="Achievements", description=lol, color=color())
                e.set_thumbnail(url=ctx.me.avatar_url)
                footer(ctx, e)
                gays.append(e)

            p = paginator.EmbedPages(ctx, embeds=gays)
            await ctx.send("To edit achievements use the `{}edit_achievement` command.".format(returnPrefix(ctx)))
            await p.paginate()

        except Exception as e:
            await boterror(self.bot, ctx, e)

    @commands.command() #checked
    async def ranks(self, ctx):
        try:
            auth = is_admin(self.bot, ctx)

            if auth == False:
                return

            if not db.ranks.count({}):
                return await error(ctx, "No ranks found", "The rank collection is empty. Please send this error to the owner.")

            pg = commands.Paginator(prefix="", suffix="", max_size=1022)
            for x in db.ranks.find({}):
                if x['rank_image'] == "None":
                    rank_image = "None"
                else:
                    rank_image == "[Click Here!]({})".format(x['rank_image'])

                if x['rank_role'] == "None":
                    rank_role = "None"
                else:
                    def get_shit():
                        roles = []
                        for server in self.bot.guilds:
                            for role in server.roles:
                                roles.append(role)
                        return roles
                    rank_role = discord.utils.get(get_shit(), id=x['rank_role'])
                    if rank_role is None:
                        rank_role = "Cannot find role"

                pg.add_line(f"Rank Name : {x['rank_name']}\nRank ID : {x['rank_id']}\nRank Image : {rank_image}\nRank Role : {rank_role}\nRequired XP : {x['rank_xp']}\n")

            embeds = []
            for page in pg.pages:
                e = discord.Embed(title="Ranks!", description=page, color=color())
                e.set_thumbnail(url=ctx.me.avatar_url)
                footer(ctx, e)
                embeds.append(e)

            p = paginator.EmbedPages(ctx, embeds=embeds)
            await ctx.send("To edit ranks use the `{}edit_rank` command.".format(returnPrefix(ctx)))
            await p.paginate()

        except Exception as e:
            await boterror(self.bot, ctx, e)

    @commands.command() #checked
    async def remove_card(self, ctx, *, card: str = None):
        try:
            auth = is_admin(self.bot, ctx)

            if auth == False:
                return

            if card is None:
                return await usage(ctx, ['card_name'], ['Cool Card'], 'Allows you to remove a card from the store. (Moves to recycle bin)')

            card = card.upper()
            if not db.store.count({"card_name":card}):
                return await error(ctx, "Card not found", "The card you entered is not found on the store")

            oof = [x for x in db.store.find({"card_name":card})][0]
            if db.bin.count({}):
                last = [x['item_id'] for x in db.bin.find({})]
                if last == []:
                    id = 1
                else:
                    id = last[-1] + 1
            else:
                id = 1
            data = {
                "item_name":oof['card_name'],
                "item_type":'card',
                "item_act_name":oof['act_name'],
                "trashed_by":ctx.author.id,
                "item_image":oof['card_image'],
                "item_image_url":oof['card_image_url'],
                "is_special":oof['is_special'],
                "item_rarity":oof['rarity'],
                "item_price":oof['card_price'],
                "item_id":id,
                "item_amount":oof['card_amount']
            }
            db.bin.insert_one(data)
            db.store.delete_one({"card_name":card})
            await success(ctx, "Successfully moved the card to the recycle bin. You can access it using the `{}recycle_bin` command".format(returnPrefix(ctx)))
        except Exception as e:
            await boterror(self.bot, ctx, e)

    @commands.command() #checked
    async def restore(self, ctx, item_id: str = None):
        try:
            auth = is_admin(self.bot, ctx)
            if auth is False:
                return
            if item_id is None:
                return await usage(ctx, ['item id'], ['1'], 'Lets you restore an item from the recycle bin. To get the list of item ids use the `{}recycle_bin` command.'.format(returnPrefix(ctx)))
            try:
                item = int(item_id)
            except:
                return await error(ctx, "Item Error", "Item ID must be an integer.")

            if not db.bin.count({"item_id":item}):
                return await error(ctx, "Item ID not found", "To get the list of item ids use the `{}recycle_bin` command.".format(returnPrefix(ctx)))

            for x in db.bin.find({'item_id':item}):
                if x['item_type'] == "card":
                    data = {
                        "card_name":x['item_name'],
                        "act_name":x['item_act_name'],
                        "card_image":x['item_image'],
                        "card_amount":x['item_amount'],
                        "card_price":x['item_price'],
                        "card_image_url":x['item_image_url'],
                        "is_special":x['is_special'],
                        "rarity":x['item_rarity']
                    }
                    db.store.insert_one(data)
                    db.bin.delete_one({"item_id":item})

            await success(ctx, "Successfully restored the item from the recycle bin.")


        except Exception as e:
            await boterror(self.bot, ctx, e)

    @commands.command() # checked
    async def recycle_bin(self, ctx):
        try:
            auth = is_admin(self.bot, ctx)
            if auth == False:
                return

            if not db.bin.count({}):
                return await error(ctx, "Bin Empty", "The recycle bin is currently empty.")

            pg = commands.Paginator(prefix="", suffix="", max_size=1022)
            i = 1
            for x in db.bin.find({}):
                trashed_by = discord.utils.get(self.bot.get_all_members(), id=x['trashed_by'])
                if trashed_by is None:
                    trashed_by = "Cannot be found."
                pg.add_line(f"Item : {x['item_act_name']}\nItem type : {x['item_type']}\nTrashed by : {trashed_by}\nItem ID : {x['item_id']}\n")
                i += 1

            embeds = []
            for page in pg.pages:
                e = discord.Embed(title="Bin", description=page, color=color())
                e.set_thumbnail(url="http://icons.iconarchive.com/icons/graphicloads/flat-finance/256/recycle-bin-icon.png")
                footer(ctx, e)
                embeds.append(e)

            p = paginator.EmbedPages(ctx, embeds=embeds)
            await p.paginate()

        except Exception as e:
            await boterror(self.bot, ctx, e)

    @commands.command() #checked
    async def add_card_stock(self, ctx, *, card: str = None):
        try:
            auth = is_admin(self.bot, ctx)

            if auth == False:
                return

            if card is None:
                return await usage(ctx, ['card name'], ['Cool Card'], 'Allows you to stock up cards on the store.')

            card = card.upper()

            if not db.store.count({"card_name":card}):
                return await error(ctx, "Card not found", "The card you entered is not found on the store.")

            amount = [x['card_amount'] for x in db.store.find({"card_name":card})]
            if amount[0] == "Infinite":
                return await error(ctx, "Card is infinite", "You don't need to stock up because the amount of cards is infinite.")

            def check(m):
                return m.channel == ctx.channel and m.author == ctx.author

            x = False
            await ctx.send("Alright, How many cards do you want to stock up?")
            while x is False:
                msg = await self.bot.wait_for('message', check=check)
                msg = msg.content
                msg = msg.split()
                try:
                    for m in msg:
                        amount = int(m)
                    x = True
                except:
                    await ctx.send(f'Invalid answer. Answer must be a number.')


            db.store.update_one({"card_name":card}, {'$inc':{'card_amount':amount}})
            await success(ctx, "Successfully stocked up the cards.")

        except Exception as e:
            await boterror(self.bot, ctx, e)

    @commands.command() #checked
    async def remove_non_gaming_channel(self, ctx, *, channel: discord.TextChannel = None):
        try:
            auth = is_admin(self.bot, ctx)

            if auth == False:
                return

            if channel is None:
                return await usage(ctx, ['mention a channel'], [ctx.channel.mention], 'Allows you to make a channel a gaming one.')

            if not db.non_gaming.count({"channel_id":channel.id}):
                return await error(ctx, "Channel is not yet a non-gaming channel", f"The channel you mentioned is not yet a non-gaming channel. If you want a channel to be non-gaming then use the `{returnPrefix(ctx)}add_non_gaming_channel` command.")

            db.non_gaming.remove({"channel_id":channel.id})
            await success(ctx, 'Successfully set the channel to a gaming channel.')

        except Exception as e:
            await boterror(self.bot, ctx, e)

    @commands.command() #checked
    async def add_non_gaming_channel(self, ctx, *, channel: discord.TextChannel = None):
        try:
            auth = is_admin(self.bot, ctx)

            if auth == False:
                return

            if channel is None:
                return await usage(ctx, ['mention a channel'], [ctx.channel.mention], 'Allows you to make a channel a non-gaming one.')

            if db.non_gaming.count({"channel_id":channel.id}):
                return await error(ctx, "Channel is already a non-gaming channel", f"The channel you mentioned is already a non gaming channel. If you want a channel to be no longer non-gaming then use the `{returnPrefix(ctx)}remove_non_gaming_channel` command.")

            data = {
                "channel_id":channel.id
            }
            db.non_gaming.insert_one(data)
            await success(ctx, "Successfully set the channel to a non-gaming channel.")

        except Exception as e:
            await boterror(self.bot, ctx, e)


    @commands.command() #checked
    async def upload_card(self, ctx):
        try:
            auth = is_admin(self.bot, ctx)
            if auth == False:
                return
            await ctx.send("Alright it's time for me to walk you through the process of uploading cards to the database. (**YOU CAN CANCEL THIS PROCESS ANYTIME BY SENDING \"CANCEL\"**)")
            await ctx.send("Please enter the name of the card.")

            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel

            x = False

            while x is False:
                name = await self.bot.wait_for('message', check=check)
                name = name.content
                if name.upper() == "CANCEL":
                    return await ctx.send("Successfully canceled")
                if db.store.count({"card_name":name.upper()}):
                    await ctx.send(f"Failed to set the name. A card with the same name already exists.")
                else:
                    x = True

            await ctx.send("Successfully set the name to {}\nNow enter the image link. (It can either be a link or an attachment)".format(name))

            x = False
            img_error = "Failed to set the image. Make sure you attach an image or send an image url. Try again"
            url_image_owo = []
            while x is False:
                image = await self.bot.wait_for('message', check=check)
                if image.content.upper() == "CANCEL":
                    return await ctx.send("Successfully canceled")
                    x = True
                if image.content.startswith(('https://', 'http://')):
                    image = image.content
                    image = image.split()
                    image = image[0]
                    if is_url_image(image):
                        image = image
                        url_image_owo.append(image)
                        x = True
                    else:
                        await ctx.send(img_error)
                else:
                    if image.attachments != []:
                        image = image.attachments[0]
                        image = image.url
                        if is_url_image(image):
                            image = image
                            url_image_owo.append(image)
                            x = True
                        else:
                            await ctx.send(img_error)
                    else:
                        await ctx.send(img_error)

            log_channel = self.bot.get_channel(514786835302711307)
            msg_sent = await log_channel.send(url_image_owo[0]) # I decided to send the image url to a channe; and just grab the image there when it's needed to use. Forget about me storing the image in a database. it's fuckin complicated lol

            await ctx.send(f"Successfully set the image to : {image}")
            await ctx.send(f"Would you want the card to be special? (Special cards won't show up on the store and it can only be used my mods/admins to gift to other users)")
            x = False
            while x is False:
                is_special = await self.bot.wait_for('message', check=check)
                msg = is_special.content
                if msg.upper() == "CANCEL":
                    return await ctx.send("Successfully canceled")
                    x = True
                for m in msg.split():
                    if m.upper() in yeses:
                        is_special = True
                        x = True
                    if m.upper() in noes:
                        is_special = False
                        x = True

                if x is False:
                    await ctx.send('Invalid answer. Please answer with either yes or no. It is that simple.')

            mk = {True:'a special one.', False:'a non-special one.'}
            if not is_special:
                blah = "\nHow much do you want the card to cost?"
            else:
                blah = ""
            await ctx.send(f'Successfully set the card to {mk[is_special]}{blah}')
            if is_special:
                price = "Free"
                amount = "Infinite"
                rarity = "It's infinite gaddem"
                g = ""
            else:
                x = False
                while x is False:
                    amount = await self.bot.wait_for('message', check=check)
                    msg = amount.content
                    if msg.upper() == "CANCEL":
                        return await ctx.send("Successfully canceled")
                        x = True
                    for m in msg.split():
                        try:
                            price = int(m)
                            x = True
                        except:
                            pass

                    if x is False:
                        await ctx.send('Invalid answer. Please answer how much do you want the card to cost? (Answer must be a number)')
                if price == 1:
                    g = "Gold"
                elif price == 0:
                    g = "Gold? Well I guess the card is free."
                else:
                    g = "Golds"

                await ctx.send(f'Successfully set the price of the card to {price} {g}\nHow many of these cards do you want uploaded? (Answer must be either a number or the word infinite)')
                x = False
                while x is False:
                    msg = await self.bot.wait_for('message', check=check)
                    msg = msg.content
                    if msg.upper() == "CANCEL":
                        return await ctx.send("Successfully canceled")
                        x = True
                    for m in msg.split():
                        if m.upper() == "INFINITE":
                            amount = "Infinite"
                            x = True
                        try:
                            amount = int(m)
                            if amount < 1:
                                x = False
                            else:
                                 x = True
                        except:
                            pass

                    if amount != "Infinite":
                        if amount < 1:
                            error = "Amount of cards cannot be 0 or negative."
                        elif x is False:
                            error = "Please answer how many of these cards do you want uploaded? (Answer must be either a number or the word infinite)"
                    else:
                        error = "Please answer how many of these cards do you want uploaded? (Answer must be either a number or the word infinite)"

                    if x is False:
                        await ctx.send(f'Invalid answer. {error}')

                await ctx.send(f"Successfully set the amount of cards to upload to {amount} cards.\nNow enter the rarity of the card, Example : Legendary, Common, etc. (This will not change the amount of cards to upload. It will only show as text)")
                msg = await self.bot.wait_for('message', check=check)
                rarity = msg.content
                await ctx.send(f"Successfully set the rarity of the card to {rarity}.")

            loading_emoji = self.bot.get_emoji(514771904284852224)
            loading_msg = await ctx.send(f"{loading_emoji} Processing image.")
            image = "placeholder_test"
            data = {
                "card_name":name.upper(),
                "act_name":name,
                "card_image":image,
                "card_amount":amount,
                "card_price":price,
                "card_image_url":msg_sent.content,
                "is_special":is_special,
                "rarity":rarity
            }
            if not is_special:
                db.store.insert_one(data)
            else:
                db.mod_cards.insert_one(data)

            await loading_msg.delete()
            await success(ctx, f"Successfully uploaded the card to the database with the details :\nIs Special : {is_special}\nCard Name : {name}\nCard Amount : {amount}\nCard Price : {price} {g}\nCard Rarity : {rarity}", url_image_owo[0])


        except Exception as e:
            await boterror(self.bot, ctx, e)

    @commands.command() #checked
    async def authorize_role(self, ctx, *, role: discord.Role = None):
        try:
            if not ctx.author.id in owners:
                return

            if role is None:
                return await usage(ctx, ['mention or name a role'], ['Admin'], 'Authorizes a role so that that role can use administrator commands.')

            if db.authorized_roles.count({"role_id":role.id}):
                return await error(ctx, "Role already authorized", f"The role you gave is already authorized. If you want to unauthorize a role use the `{returnPrefix(ctx)}deauthorize_role` command.")

            data = {
                "name":role.name,
                "role_id":role.id
            }

            db.authorized_roles.insert_one(data)
            await success(ctx, "Successfully authorized the role : `{}`.".format(role.name))

        except Exception as e:
            await boterror(self.bot, ctx, e)

    @commands.command() #checked
    async def deauthorize_role(self, ctx, *, role: discord.Role = None):
        try:
            if not ctx.author.id in owners:
                return

            if role is None:
                return await usage(ctx, ['mention or name a role'], ['Admin'], 'Deauthorizes a role so that that role can no longer use administrator commands.')

            if not db.authorized_roles.count({"role_id":role.id}):
                return await error(ctx, "Role not yet authorized", f"The role you gave is not even authorized yet. If you want to authorize a role use the `{returnPrefix(ctx)}authorize_role` command.")

            db.authorized_roles.delete_one({"role_id":role.id})
            await success(ctx, "Successfully deauthorized the role : `{}`.".format(role.name))

        except Exception as e:
            await boterror(self.bot, ctx, e)


def setup(bot):
    bot.add_cog(Admin(bot))
