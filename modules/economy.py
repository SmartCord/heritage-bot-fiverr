from imports import *

class Economy:
    def __init__(self, bot):
        self.bot = bot
        self.antispam = []

    async def checkAntiSpam(self, id):
        await asyncio.sleep(180)
        self.antispam.remove(id)

    async def on_message(self, message):
        if message.author.bot:
            return

        try:
            message.channel.recipient
            print('channel is dm lol')
            return
        except:
            pass

        if db.users.count({"user_id":message.author.id}):
            if db.non_gaming.count({}):
                non_gaming_channels = [x['channel_id'] for x in db.non_gaming.find({})]
            else:
                non_gaming_channels = []
            db.users.update_one({"user_id":message.author.id}, {'$inc':{"messages":1}})
            if message.author.id in self.antispam:
                pass
            else:

                db.users.update_one({"user_id":message.author.id}, {'$inc':{"gold":1}})
                db.users.update_one({"user_id":message.author.id}, {'$inc':{"xp":1}})
                self.antispam.append(message.author.id)
                self.bot.loop.create_task(self.checkAntiSpam(message.author.id))

            if message.channel.category_id == 516063826429607938:
                if not db.lfg.count({"user_id":message.author.id}):
                    data = {
                        'user_id':message.author.id,
                        'amount':1,
                        'time':int(time.time())
                    }
                    db.lfg.insert_one(data)
                else:
                    for p in db.lfg.find({"user_id":message.author.id}):
                        cooldown = 86400
                        f = p['time']
                        r = int(time.time())
                        g = r - f
                        if g >= cooldown:
                            db.lfg.update_one({"user_id":message.author.id}, {'$inc':{'amount':1}})
                            db.lfg.update_one({"user_id":message.author.id}, {'$set':{'time':int(time.time())}})
                            new_data = [x['amount'] for x in db.lfg.find({"user_id":message.author.id})][0]
                            if new_data == 3:
                                await giveAchievementAuthor(message, 4)


            for x in db.users.find({"user_id":message.author.id}):
                if x['messages'] == 500:
                    await giveAchievementAuthor(message, 1)

                nonce = x['gaming_channels']
                if message.channel.id in non_gaming_channels:
                    if non_gaming_channels == []:
                        pass
                    else:
                        if message.channel.id in nonce:
                            pass
                        else:
                            db.users.update_one({"user_id":message.author.id}, {'$push':{'gaming_channels':message.channel.id}})
                nonce = x['gaming_channels']
                print(nonce)
                print(non_gaming_channels)
                if set(nonce) == set(non_gaming_channels):
                    heh = x['achievements']
                    if non_gaming_channels == []:
                        pass
                    else:
                        if 2 in heh:
                            pass
                        else:
                            await giveAchievementAuthor(message, 2)

                #if db.ranks.count({"rank_xp":x['xp']}): #checked
                #    thing_id = [i for i in db.ranks.find({"rank_xp":x['xp']})][0]
                #    await giveRankAuthor(self.bot, message, thing_id['rank_id'])

                if x['xp'] >= x['xp_max']: #checked
                    ranks_xps = [i for i in db.ranks.find({})]
                    ranks_xps = ranks_xps[1:]
                    required_xp = [i for i in db.ranks.find({"rank_xp":x['xp_max']})][0]
                    #new_data = 9
                    new_data = next((index for (index, d) in enumerate(ranks_xps) if d["rank_xp"] == required_xp['rank_xp']), None)
                    if new_data >= 8:
                        new_data = None

                    if new_data != None:
                        new_max = ranks_xps[new_data + 1]
                        wow = ranks_xps[new_data]
                        db.users.update_one({"user_id":message.author.id}, {'$set':{'xp_max':new_max['rank_xp']}})
                        #db.users.update_one({"user_id":message.author.id}, {'$set':{'xp':0}})
                        await giveRankAuthor(self.bot, message, wow['rank_id'])


                #if x['xp'] >= x['xp_max']: #checked
                    #ranks = x['ranks']
                    #if ranks == []:
                    #    pushed = 0
                    #else:
                    #    pushed = ranks[-1] + 1

                    #level_data = {}

                    #db.users.update_one({"user_id":message.author.id}, {'$inc':{'xp_max':200}})
                    #db.users.update_one({"user_id":message.author.id}, {'$set':{'xp':0}})
                    #db.users.update_one({"user_id":message.author.id}, {'$push':{'ranks':pushed}}) #not sure what to do
                    #db.users.update_one({"user_id":message.author.id}, {'$inc':{'gold':400}})


                # FINISHED SOME ACHIEVEMENTS SHIT



def setup(bot):
    bot.add_cog(Economy(bot))
