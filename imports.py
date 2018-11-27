from discord.ext import commands
import asyncio
import discord, requests, time, utils
from pathlib import Path
from difflib import SequenceMatcher
import datetime
from pymongo import MongoClient
from bson.binary import Binary
from utils import db, color, returnPrefix, icon, footer, usage, error, success, boterror, is_pm, is_admin, giveAchievementAuthor, is_guild, giveRankAuthor, giveAchievementMember
from PIL import Image
import paginator, uuid
from io import BytesIO
from os import environ

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

class config:
    bot_token = envrion.get('BOT_TOKEN')
