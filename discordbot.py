# -*- coding: utf-8 -*-
"""
Created on Sun Apr  3 18:58:24 2022

@author: marco

this code is free to use.
better if you credit me but NOT mandatory.

"""

import pyscreenshot 
import inspect as i
import colorama

from colorama import Fore
from colorama import Style

import time
import threading
import asyncio
import youtube_dl
from discord.utils import get
import discord
from discord.ext import commands, tasks
from discord_slash import SlashCommand
from discord_slash import ButtonStyle
from discord_slash.utils.manage_components import *

import random



import sys
sys.path.append("./data/")
                 
from database_handler import DatabaseHandler

database_handler = DatabaseHandler("database.db")

bot = commands.Bot(command_prefix = "!", description = "bot")

slash = SlashCommand(bot, sync_commands = True)

randomtimeforclaim = random.randint(60, 120)
randomtimeforcalcul = random.randint(180, 240)
randomtimeforleplusproche = random.randint(180, 240)


musics = {
    "" : "",
    }

ytdl = youtube_dl.YoutubeDL()

class Video:
    def __init__(self, link):
        video = ytdl.extract_info(link, download=False)
        video_format = video["formats"][0]
        self.url = video["webpage_url"]
        self.stream_url = video_format["url"]

@bot.command()
async def leave(ctx):
    client = ctx.guild.voice_client
    await client.disconnect()
    musics[ctx.guild] = []

@bot.command()
async def resume(ctx):
    client = ctx.guild.voice_client
    if client.is_paused():
        client.resume()


@bot.command()
async def pause(ctx):
    client = ctx.guild.voice_client
    if not client.is_paused():
        client.pause()


@bot.command()
async def skip(ctx):
    client = ctx.guild.voice_client
    client.stop()


def play_song(client, queue, song):
    source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(song.stream_url
        , before_options = "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"))

    def next(_):
        if len(queue) > 0:
            new_song = queue[0]
            del queue[0]
            play_song(client, queue, new_song)
        else:
            asyncio.run_coroutine_threadsafe(client.disconnect(), bot.loop)

    client.play(source, after=next)
    


@bot.command()
async def play(ctx, url):
    print("play")
    client = ctx.guild.voice_client

    if client and client.channel:
        video = Video(url)
        musics[ctx.guild].append(video)
    else:
        channel = ctx.author.voice.channel
        video = Video(url)
        musics[ctx.guild] = []
        client = await channel.connect()
        await ctx.send(f"Je lance : {video.url}")
        play_song(client, musics[ctx.guild], video)   
        



@tasks.loop(minutes = 6)
async def timemoney():
    print("entered the taskloop event")
    i = 1
    while i < 50:
        database_handler.add_money_by_sql_id(i, 3)
        i += 1

@tasks.loop(minutes = randomtimeforclaim)
async def timeclaim():
    channel = bot.get_channel(962327355341303849)
    firstemote = "<:marcoV:785980560635199528>"
    message = await channel.send("claim for 10 money")
    await message.add_reaction(firstemote)
    
    def checkEmoji(reaction, user):
        return message.id == reaction.message.id and str(reaction.emoji) == firstemote and user != message.author
    
    reaction, user = await bot.wait_for("reaction_add", timeout = 60, check = checkEmoji)
    database_handler.add_money(user.id, 10)
    await channel.send(f"{user} gagne 10 money")
    global randomtimeforclaim
    randomtimeforclaim = random.randint(60, 120)
    return

@tasks.loop(minutes = randomtimeforcalcul)
async def timerandomcalcul():
    first = random.randint(100, 999)
    second = random.randint(100, 999)
    channel = bot.get_channel(962327355341303849)
    await calculchallenge(channel, first, second)
    global randomtimeforcalcul
    randomtimeforcalcul = random.randint(180, 240)
    return

@tasks.loop(minutes = randomtimeforleplusproche)
async def timeleplusproche():
    result = random.randint(1000, 9999)
    channel = bot.get_channel(962327355341303849)
    await channel.send("je pense à un nombre entre 1000 et 9999, le plus proche remporte le butin!")
    players = []
    answers = []
    
    def checkplayer(newmessage):
        is_int = None
        try:
            int(newmessage.content)
            is_int = True
        except ValueError:
            is_int = False
        return players.count(newmessage.author.id) == 0 and channel == newmessage.channel and is_int == True
    
    try:
        while True:
            response = await bot.wait_for("message", timeout = 15, check = checkplayer)
            players.append(response.author.id)
            answers.append(int(response.content))
    except ValueError:
        tamp = False
    finally:
    
        i = 0
        while i < len(answers):
            answers[i] -= result
            if answers[i] < 0:
                answers[i] *= -1
            i += 1
                
                
        i = 0
        mini = 100000
        minindex = 0
        while i < len(answers):
            if mini > answers[i]:
                mini = answers[i]
                minindex = i
            i += 1
                        
        ID : int = players[minindex]
        winner = f"<@{ID}>"
        if mini == 0:
            await channel.send(f"Le résultat était {result}, c'est donc un tout pile!!! et {winner} qui gagne 500 money!!!")
            database_handler.add_money(ID, 500)
        else:
            await channel.send(f"Le résultat était {result}, c'est donc {winner} qui gagne 50 money!")
            database_handler.add_money(ID, 50)
        return
        

@bot.event
async def on_ready():
    print("Ready !")
    game = discord.Game("-helpcard for commands")
    await bot.change_presence(activity = game)
    #timemoney.start()
    #timeclaim.start()
    #timerandomcalcul.start()
    #timeleplusproche.start()


@bot.command()
async def say(ctx, *message):
    print("say bien recu")
    #messages = await ctx.channel.history(limit = 1).flatten()
    #await messages[0].delete()
    await ctx.send(" ".join(message))
    
@bot.command()
async def ferme(ctx, *message):
    print("ferme bien recu")
    if isOwner(ctx) or ctx.message.author.id == 218771232324059136:
        await ctx.send("ouai ferme " + " ".join(message))
    else:
        await ctx.send("ptdr t'es qui? (longue vie au roi @nortonuss#3738)")

@bot.command()
async def vien(ctx, *nothing):
    if not isOwner(ctx):
        await ctx.send("ptdr t ki?")
        return
    await ctx.send("oui monsieur")
    
@bot.command()
async def clear(ctx, nombre : int):
    messages = await ctx.channel.history(limit = nombre + 1).flatten()
    for message in messages:
        await message.delete()
    print("clear ended")

@bot.command()
async def traitrise(ctx):
    rand = random.randint(1, 2)
    if rand == 1:
        await ctx.send("exempté de la game des bro, sale loser, honte à toi")
    else:
        await ctx.send("game des bro doublée!!!! c'est la fête les gars, tu vas jouer gros CONNARD!!")

@bot.command()
async def helpcard(ctx):
    embed = discord.Embed(title = "** liste des commandes**", description = "")
    embed.add_field(name = "register:", value = "permet de vous enregistrer pour commencer ce merveilleux jeu")
    embed.add_field(name = "mycollection:", value = "affiche votre collection")
    embed.add_field(name = "mymoney:", value = "affiche votre money")
    embed.add_field(name = "buybooster:", value = "achete un booster pour 100 money")
    embed.add_field(name = "managecards(a,b):", value = "échange votre carte a la place a avec celle a la place b")
    embed.add_field(name = "displaycard(name):", value = "affiche la carte avec le nom 'name'")
    embed.add_field(name = "sellcard(name):", value = "vend votre premiere carte avec le nom 'name' commune: 5, rare: 10, epique: 100, legendaire: 500" )
    embed.add_field(name = "tarot:", value = "tirez une carte de tarot pour 10 money... à vos risques et périls...")
    embed.add_field(name = "unesurdeux(bet):", value = "vous pariez 'bet' money, 1 chance sur 2 de doubler ou de perdre cette somme")
    embed.add_field(name = "quitteoudouble:", value = "vous pariez tout votre argent sur un 1/2")
    embed.add_field(name = "betchallenge(bet, receiver):", value = "pariez 'bet' contre 'receiver' pour un une chance sur 2")
    embed.add_field(name = "tradecard(firstcard, secondcard, receiver):", value = "proposez d'echanger votre 'fiscard' contre la 'secondcard' de 'receiver' (entrez les noms des cartes)")
    embed.add_field(name = "givecard(givedcard, receiver):", value = "donne la carte 'givedcard' à 'receiver'")
    embed.add_field(name = "givemoney(donation, receiver):", value = "donne 'donation' money à 'receiver'")
    
    await ctx.send(embed = embed)
    return
    
##############################################################################
"""users management"""
##############################################################################


@bot.command()
async def register(ctx):
    #if not isOwner(ctx):
    #    await ctx.send("patience mon cher, tu pourras bientôt collectionner toutes les cartes de ce merveilleux jeu")
    #    return
    if ctx.message.author.id == 370624263440564225:
        await ctx.send("TG pierre! TU FERME TA PUTAIN DE GUEULE")
        return
    discordID = ctx.message.author.id
    database_handler.create_person(discordID)
    await ctx.send("register réussi, bienvenue dnas le toonmarcoV card game!")
    if ctx.message.author.id == 249284580908072962:
        await ctx.send("par contre fait pas le malin je sais où tu habites Victor")
        await ctx.send("(j'ai dit bite)")

@bot.command()
async def emojiID(ctx, emoji: discord.Emoji):
    print(emoji.id)

@bot.command()    
async def mycollection(ctx):
    discordID = ctx.message.author.id
    cardstringlist : str = database_handler.getcardslist(discordID)
    cardlist = string_to_list_card(str(cardstringlist))
    
    firstemote = "<:marcoV:785980560635199528>"
    secondemote = "<:degout:836402411592876073>"
    
    description = ""
    if cardlist == "":
        await ctx.send("Vous n'avez aucune carte...")
        return
    i = 0
    lenght = len(cardlist)
    name = database_handler.getcardname(cardlist[i])
    embed = discord.Embed(title = "**" + name + "**", description = description)
    
    rarity = database_handler.getcardrarity(name)
    image = database_handler.getcardimage(name)
    
    file = discord.File("cardimages/" + image, filename=image)
    embed.set_image(url = "attachment://" + image)
    embed.add_field(name = "rareté:", value = rarity)
    embed.add_field(name = "pos:", value = f"{i+1}/{lenght}")
    message = await ctx.send(file=file, embed = embed)
    await message.add_reaction(firstemote)
    await message.add_reaction(secondemote)
    
    def checkEmoji(reaction, user):
        return message.id == reaction.message.id and (str(reaction.emoji) == firstemote or str(reaction.emoji) == secondemote) and user != message.author
    
    while True:
        reaction, user = await bot.wait_for("reaction_add", timeout = 10, check = checkEmoji)
        if str(reaction.emoji) == firstemote:
            i -= 1
            if i < 0:
                i = len(cardlist) - 1
        elif str(reaction.emoji) == secondemote:
            i += 1
            if i > len(cardlist) - 1:
                i = 0
    
        await message.delete()
        name = database_handler.getcardname(cardlist[i])
        embed = discord.Embed(title = "**" + name + "**", description = description)
        
        rarity = database_handler.getcardrarity(name)
        image = database_handler.getcardimage(name)
    
        file = discord.File("cardimages/" + image, filename=image)
        embed.set_image(url = "attachment://" + image)
        embed.add_field(name = "rareté:", value = rarity)
        embed.add_field(name = "pos:", value = f"{i+1}/{lenght}")
        message = await ctx.send(file=file, embed = embed)
        
    
        await message.add_reaction(firstemote)
        await message.add_reaction(secondemote)
    
@bot.command()    
async def toonformarco(ctx):
    if not isOwner(ctx):
        await ctx.send("you dont have the right for this command")
        return
    discordID = ctx.message.author.id
    cardstringlist = database_handler.getcardslist(discordID)
    cardlist = string_to_list_card(cardstringlist)
    cardlist.append(1)
    newstring = list_to_string_card(cardlist)
    database_handler.update_player_cards(discordID, newstring)
    database_handler.less_one_card(1)
    
    await ctx.send("action réussi")
    
@bot.command()    
async def buybooster(ctx):
    actualmoney = database_handler.getmoney(ctx.message.author.id)
    if actualmoney < 100:
        await ctx.send("vous n'avez pas assez d'argent pour acheter un booster, un booster coute 100 money")
        return
    cardID1 = 0
    cardID2 = 0
    cardID3 = 0
    communes = [3, 4, 9, 14, 15, 17, 19, 21, 24, 25, 27, 30, 35, 36, 38, 40, 41, 43, 45, 48, 49]
    rares = [5, 6, 11, 16, 22, 26, 28, 34, 42]
    epiques = [8, 10, 13, 18, 20, 23, 29, 32, 33, 39, 44, 46, 47]
    legendaires = [2, 7, 12, 31, 37]
    noresultflag = 0
    while cardID1 == 0:
        if noresultflag == 1000:
            await ctx.send("les cartes sont épuisée, veuillez appeler un responsable pour une extention, nous sommes désolé pour la gène ocasionnée")
            return
        
        rand = random.randint(0, len(communes) - 1)
        rand = communes[rand]
        (nbleft, rarity) = database_handler.getcardfromrandomID(rand)
        if nbleft <= 0 or rarity != "commune":
             noresultflag += 1
             continue
        cardID1 = rand
    
    noresultflag = 0
    while cardID2 == 0:
        if noresultflag == 1000:
            await ctx.send("les cartes sont épuisée, veuillez appeler un responsable pour une extention, nous sommes désolé pour la gène ocasionnée")
            return
        
        rand = random.randint(0, len(communes) - 1)
        rand = communes[rand]
        (nbleft, rarity) = database_handler.getcardfromrandomID(rand)
        if nbleft <= 0 or rarity != "commune":
             noresultflag += 1
             continue
        cardID2 = rand
        
    randomrarity = random.randint(1, 100)
    
    if randomrarity == 100:
        noresultflag = 0
        while cardID3 == 0:
            if noresultflag == 1000:
                await ctx.send("les cartes sont épuisée, veuillez appeler un responsable pour une extention, nous sommes désolé pour la gène ocasionnée")
                return
        
            rand = random.randint(0, len(legendaires) - 1)
            rand = legendaires[rand]
            (nbleft, rarity) = database_handler.getcardfromrandomID(rand)
            if nbleft <= 0 or rarity != "legendaire":
                noresultflag += 1
                continue
            cardID3 = rand
    elif randomrarity > 95:
        noresultflag = 0
        while cardID3 == 0:
            if noresultflag == 1000:
                await ctx.send("les cartes sont épuisée, veuillez appeler un responsable pour une extention, nous sommes désolé pour la gène ocasionnée")
                return
        
            rand = random.randint(0, len(epiques) - 1)
            rand = epiques[rand]
            (nbleft, rarity) = database_handler.getcardfromrandomID(rand)
            if nbleft <= 0 or rarity != "epique":
                noresultflag += 1
                continue
            cardID3 = rand
    else:
        noresultflag = 0
        while cardID3 == 0:
            if noresultflag == 1000:
                await ctx.send("les cartes sont épuisée, veuillez appeler un responsable pour une extention, nous sommes désolé pour la gène ocasionnée")
                return
        
            rand = random.randint(0, len(rares) - 1)
            rand = rares[rand]
            (nbleft, rarity) = database_handler.getcardfromrandomID(rand)
            if nbleft <= 0 or rarity != "rare":
                noresultflag += 1
                continue
            cardID3 = rand
    
    print("1")
    name = database_handler.getcardname(cardID1)
    print("1.1")
    description = ""
    embed = discord.Embed(title = "**" + name + "**", description = description)
    
    print("1.2")
    
    rarity = database_handler.getcardrarity(name)
    image = database_handler.getcardimage(name)
    nbleft = database_handler.getcardleft(name)
    
    print("1.3")
    
    file = discord.File("cardimages/" + image, filename=image)
    
    print("1.4")
    
    embed.set_image(url = "attachment://" + image)
    
    print("1.5")
    
    embed.add_field(name = "rareté:", value = rarity)
    
    print("1.6")
    
    await ctx.send(file=file, embed = embed)
    
    print("2")
    
    name = database_handler.getcardname(cardID2)
    description = ""
    embed = discord.Embed(title = "**" + name + "**", description = description)
    
    rarity = database_handler.getcardrarity(name)
    image = database_handler.getcardimage(name)
    nbleft = database_handler.getcardleft(name)
    
    file = discord.File("cardimages/" + image, filename=image)
    embed.set_image(url = "attachment://" + image)
    embed.add_field(name = "rareté:", value = rarity)
    await ctx.send(file=file, embed = embed)
    
    print("3")
    
    
    await ctx.send("*roulement de tambour*..., et la carte rare...:")
    name = database_handler.getcardname(cardID3)
    description = ""
    embed = discord.Embed(title = "**" + name + "**", description = description)
    
    rarity = database_handler.getcardrarity(name)
    image = database_handler.getcardimage(name)
    nbleft = database_handler.getcardleft(name)
    
    file = discord.File("cardimages/" + image, filename=image)
    embed.set_image(url = "attachment://" + image)
    embed.add_field(name = "rareté:", value = rarity)
    time.sleep(1)
    await ctx.send(file=file, embed = embed)
    
    print("5")
    
    
    discordID = ctx.message.author.id
    cardstringlist = database_handler.getcardslist(discordID)
    cardlist = string_to_list_card(str(cardstringlist))
    cardlist.append(cardID1)
    cardlist.append(cardID2)
    cardlist.append(cardID3)
    newstring = list_to_string_card(cardlist)
    database_handler.update_player_cards(discordID, newstring)
    database_handler.less_one_card(cardID1)
    database_handler.less_one_card(cardID2)
    database_handler.less_one_card(cardID3)
    
    database_handler.add_money(discordID, -100)
    
    print("achat du paquet réussi")
    
@bot.command()    
async def mymoney(ctx):
    discordID = ctx.message.author.id
    money = database_handler.getmoney(discordID)
    await ctx.send("vous avez actuellement " + str(money) + " money")
    
def isOwner(ctx):
    return ctx.message.author.id == 340450685487153153
    
@bot.command()
async def addmoney(ctx, money, receiver):
    discordID = ctx.message.mentions[0].id
    if isOwner(ctx):
        database_handler.add_money(discordID, money)
        newmoney = database_handler.getmoney(discordID)
        await ctx.send("money succesfully added, he now has " + str(newmoney) + " money")
    else:
        await ctx.send("you dont have the right for this command")

        
@bot.command()
async def managecards(ctx, firstplace : int, secondplace : int):     
    firstplace -= 1
    secondplace -= 1
    discordID = ctx.message.author.id
    cardstringlist : str = database_handler.getcardslist(discordID)
    cardlist = string_to_list_card(str(cardstringlist))
    lenght = len(cardlist)
    if firstplace >= lenght or secondplace >= lenght:
        await ctx.send("seems like you dont have this much cards")
        return
    temp = cardlist[firstplace]
    cardlist[firstplace] = cardlist[secondplace]
    cardlist[secondplace] = temp
    cardstringlist = list_to_string_card(cardlist)
    database_handler.update_player_cards(discordID, cardstringlist)
    await ctx.send("swap successfull")

def string_to_list_card(string : str):
    ret = []
    lenght = len(string)
    i = 0
    while i < lenght:
        if string[i] == " ":
            i += 1
            continue
        u = i
        newint = ""
        while u < lenght and string[u] != " ":
            newint += string[u]
            u += 1
        ret.append(int(newint))
        i = u
    return ret

def list_to_string_card(intlist):
    ret = ""
    if intlist == []:
        return ret
    ret += str(intlist[0])
    i = 1
    lenght = len(intlist)
    while i < lenght:
        ret += " " + str(intlist[i])
        i += 1
    return ret

##############################################################################
"""cards management"""
##############################################################################


@bot.command()
async def createcard(ctx, name, image, number : int, rarity):
    if not isOwner(ctx):
        await ctx.send("you dont have the right for this command")
        return
    database_handler.create_card(name, image, number, rarity)
    await ctx.send("création réussie, bienvenue parmis les cartes " + name + "!")
    
@bot.command()
async def changecardimage(ctx, cardID, newimage):
    if not isOwner(ctx):
        await ctx.send("you dont have the right for this command")
        return
    database_handler.change_card_image(cardID, newimage)
    await ctx.send("update réussi")
    
@bot.command()
async def changecardname(ctx, cardID, newname):
    if not isOwner(ctx):
        await ctx.send("you dont have the right for this command")
        return
    database_handler.change_card_name(cardID, newname)
    await ctx.send("update réussi")
    
@bot.command()
async def changecardnbleft(ctx, cardID, newnbleft):
    if not isOwner(ctx):
        await ctx.send("you dont have the right for this command")
        return
    database_handler.change_card_nbleft(cardID, newnbleft)
    await ctx.send("update réussi")
    
@bot.command()
async def changecardrarity(ctx, cardID, newrarity):
    if not isOwner(ctx):
        await ctx.send("you dont have the right for this command")
        return
    database_handler.change_card_rarity(cardID, newrarity)
    await ctx.send("update réussi")

@bot.command()
async def displaycard(ctx, name):
    description = ""
    if name == "toonmarcoV":
        description = "Carte du dieux, créateur originel!"
    embed = discord.Embed(title = "**" + name + "**", description = description)
    
    rarity = database_handler.getcardrarity(name)
    image = database_handler.getcardimage(name)
    nbleft = database_handler.getcardleft(name)
    
    file = discord.File("cardimages/" + image, filename=image)
    embed.set_image(url = "attachment://" + image)
    embed.add_field(name = "rareté:", value = rarity)
    embed.add_field(name = "cartes restantes:", value = nbleft)
    await ctx.send(file=file, embed = embed)
    
@bot.command()
async def sellcard(ctx, name):
    discordID = ctx.message.author.id
    cardstringlist : str = database_handler.getcardslist(discordID)
    cardlist = string_to_list_card(str(cardstringlist))
    for cardID in cardlist:
        actualname = database_handler.getcardname(cardID)
        if name == actualname:
            cardlist.remove(cardID)
            rarity = database_handler.getcardrarity(actualname)
            newstring = list_to_string_card(cardlist)
            database_handler.update_player_cards(discordID, newstring)
            database_handler.plus_one_card(cardID)
            if rarity == "commune":
                database_handler.add_money(discordID, 5)
                await ctx.send("succefully deleted from your cards, you earned 5 money")
                return
            if rarity == "rare":
                database_handler.add_money(discordID, 10)
                await ctx.send("succefully deleted from your cards, you earned 10 money")
                return
            if rarity == "epique":
                database_handler.add_money(discordID, 100)
                await ctx.send("succefully deleted from your cards, you earned 100 money")
                return
            if rarity == "legendaire":
                database_handler.add_money(discordID, 500)
                await ctx.send("succefully deleted from your cards, you earned 500 money")
                return
            return
    await ctx.send("seems like you dont have this card")
        
            
    
    
##############################################################################
"""events management"""
##############################################################################
    
@bot.command()
async def calculchallenge(ctx, first, second):
    channel = bot.get_channel(962327355341303849)
    if channel != ctx and not isOwner(ctx):
        await ctx.send("vous n'avez pas les droits requis pour cette commande")
        return
    first = int(first)
    second = int(second)
    result = first * second 
    rand1 = random.randrange(-100, 100, 5)
    while rand1 == 0:
        rand1 = random.randrange(-100, 100, 5)
    rand2 = random.randrange(-100, 100, 5)
    while rand2 == 0:
        rand2 = random.randrange(-100, 100, 5)
    rand3 = random.randrange(-100, 100, 5)
    while rand3 == 0:
        rand3 = random.randrange(-100, 100, 5)
    randomplace = random.randint(1, 4)
    buttons = None
    rand1 += result
    rand2 += result
    rand3 += result
    if randomplace == 1:
        buttons = [
        create_button(
            style=ButtonStyle.green,
            label=f"{result}",
            custom_id="oui"
            ),
        create_button(
            style=ButtonStyle.green,
            label=f"{rand1}",
            custom_id="non1"
            ),
        create_button(
            style=ButtonStyle.green,
            label=f"{rand2}",
            custom_id="non2"
            ),
        create_button(
            style=ButtonStyle.green,
            label=f"{rand3}",
            custom_id="non3"
            )
        ]
    if randomplace == 2:
        buttons = [
        create_button(
            style=ButtonStyle.green,
            label=f"{rand1}",
            custom_id="non1"
            ),
        create_button(
            style=ButtonStyle.green,
            label=f"{result}",
            custom_id="oui"
            ),
        create_button(
            style=ButtonStyle.green,
            label=f"{rand2}",
            custom_id="non2"
            ),
        create_button(
            style=ButtonStyle.green,
            label=f"{rand3}",
            custom_id="non3"
            )
        ]
    if randomplace == 3:
        buttons = [
        create_button(
            style=ButtonStyle.green,
            label=f"{rand1}",
            custom_id="non1"
            ),
        create_button(
            style=ButtonStyle.green,
            label=f"{rand2}",
            custom_id="non2"
            ),
        create_button(
            style=ButtonStyle.green,
            label=f"{result}",
            custom_id="oui"
            ),
        create_button(
            style=ButtonStyle.green,
            label=f"{rand3}",
            custom_id="non3"
            )
        ]
    if randomplace == 4:
        buttons = [
        create_button(
            style=ButtonStyle.green,
            label=f"{rand1}",
            custom_id="non1"
            ),
        create_button(
            style=ButtonStyle.green,
            label=f"{rand2}",
            custom_id="non2"
            ),
        create_button(
            style=ButtonStyle.green,
            label=f"{rand3}",
            custom_id="non3"
            ),
        create_button(
            style=ButtonStyle.green,
            label=f"{result}",
            custom_id="oui"
            )
        ]
    action_row = create_actionrow(*buttons)
    fait_choix = await ctx.send(f"quel est le résultat de {first} * {second}?", components=[action_row])
    
    def check(m):
        return True
    
    button_ctx = await wait_for_component(bot, components=action_row, check=check)
    if button_ctx.custom_id == "oui":
        database_handler.add_money(button_ctx.author.id, 50)
        await ctx.send(f"Bravo à {button_ctx.author}, qui gagne 50 de thune!")
        await button_ctx.edit_origin(content=f"quel est le résultat de {first} * {second}?")
    else:
        database_handler.add_money(button_ctx.author.id, -100)
        await ctx.send(f"ho le gros nul de {button_ctx.author}, il perd 100 de thune!!")
        await button_ctx.edit_origin(content=f"quel est le résultat de {first} * {second}?")
 
@bot.command()
async def tarot(ctx):
    discordID = ctx.message.author.id
    actualmoney = database_handler.getmoney(discordID)
    if actualmoney < 10:
        await ctx.send("vous n'avez pas assez d'argent, il vous faut minimum 10 money pour tirer une carte de tarot")
        return
    rand = random.randint(1, 100)
    if rand >= 2 and rand <= 6:
        name = "the moon"
        description = "vous perdez 100 money"
        image = "Tarot_the_moon.webp"
        embed = discord.Embed(title = "**" + name + "**", description = description)
    
        file = discord.File("cardimages/" + image, filename=image)
        embed.set_image(url = "attachment://" + image)
        
        database_handler.add_money(discordID, -110)
        
        await ctx.send(file=file, embed = embed)
        return
    
    if rand >= 95 and rand <= 99:
        name = "the sun"
        description = "vous gagnez 100 money"
        image = "Tarot_the_sun.webp"
        embed = discord.Embed(title = "**" + name + "**", description = description)
    
        file = discord.File("cardimages/" + image, filename=image)
        embed.set_image(url = "attachment://" + image)
        
        database_handler.add_money(discordID, 110)
        
        await ctx.send(file=file, embed = embed)
        return
    
    if rand == 100:
        name = "the high preistess"
        description = "tous les autres joueurs gagnent 100 money"
        image = "Tarot_the_high_preistess.webp"
        embed = discord.Embed(title = "**" + name + "**", description = description)
    
        file = discord.File("cardimages/" + image, filename=image)
        embed.set_image(url = "attachment://" + image)
        
        ID = database_handler.get_ID_by_discord_ID(discordID)
        i = 1
        while i < 50:
            if i == ID:
                i += 1
                continue
            database_handler.add_money_by_sql_id(i, 100)
            i += 1
        
        database_handler.add_money(discordID, -10)
        
        await ctx.send(file=file, embed = embed)
        return
    
    if rand == 1:
        name = "the hanged man"
        description = "vous perdez 500 money"
        image = "Tarot_the_hanged_man.webp"
        embed = discord.Embed(title = "**" + name + "**", description = description)
    
        file = discord.File("cardimages/" + image, filename=image)
        embed.set_image(url = "attachment://" + image)
        
        database_handler.add_money(discordID, -510)
        
        await ctx.send(file=file, embed = embed)
        return
    
    if rand >= 7 and rand <= 26:
        name = "the wheel of fortune"
        description = "vous gagnez ou perdez 50 money"
        rand2 = random.randint(0, 1)
        image = "Tarot_the_wheel_of_fortune.webp"
        embed = discord.Embed(title = "**" + name + "**", description = description)
    
        file = discord.File("cardimages/" + image, filename=image)
        embed.set_image(url = "attachment://" + image)
        
        if rand2 == 0:
            embed.add_field(name = "résultat:", value = "perdu")
            database_handler.add_money(discordID, -60)
        elif rand2 == 1:
            embed.add_field(name = "résultat:", value = "gagné")
            database_handler.add_money(discordID, 60)
        
        await ctx.send(file=file, embed = embed)
        return
    
    if rand >= 27 and rand <= 36:
        name = "the devil"
        description = "quitte ou double!!!"
        rand2 = random.randint(0, 1)
        bet = database_handler.getmoney(discordID)
        image = "Tarot_the_devil.webp"
        embed = discord.Embed(title = "**" + name + "**", description = description)
    
        file = discord.File("cardimages/" + image, filename=image)
        embed.set_image(url = "attachment://" + image)
        
        if rand2 == 0:
            embed.add_field(name = "résultat:", value = "perdu")
            database_handler.add_money(discordID, -bet)
        elif rand2 == 1:
            embed.add_field(name = "résultat:", value = "gagné")
            database_handler.add_money(discordID, bet)
        
        await ctx.send(file=file, embed = embed)
        return
    
    if rand >= 37 and rand <= 46:
        name = "the hermit"
        description = "vous gagnez/perdez entre 0 et 100 money"
        rand2 = random.randint(-10, 10)
        image = "Tarot_the_hermit.webp"
        embed = discord.Embed(title = "**" + name + "**", description = description)
    
        file = discord.File("cardimages/" + image, filename=image)
        embed.set_image(url = "attachment://" + image)
        
        embed.add_field(name = "résultat:", value = f"{10 * rand2}")
        database_handler.add_money(discordID, 10 * rand2 - 10)
        
        await ctx.send(file=file, embed = embed)
        return
    
    if rand >= 47 and rand <= 51:
        name = "death"
        description = "vous perdez tout votre argent"
        bet = database_handler.getmoney(discordID)
        image = "Tarot_death.webp"
        embed = discord.Embed(title = "**" + name + "**", description = description)
    
        file = discord.File("cardimages/" + image, filename=image)
        embed.set_image(url = "attachment://" + image)
        
        database_handler.add_money(discordID, -bet)
        
        await ctx.send(file=file, embed = embed)
        return
    
    if rand >= 52 and rand <= 76:
        name = "the tower"
        description = "rien ne se passe... fiou..."
        image = "Tarot_the_tower.webp"
        embed = discord.Embed(title = "**" + name + "**", description = description)
    
        file = discord.File("cardimages/" + image, filename=image)
        embed.set_image(url = "attachment://" + image)
        
        database_handler.add_money(discordID, -10)
        
        await ctx.send(file=file, embed = embed)
        return
    
    if rand >= 77 and rand <= 94:
        name = "the fool"
        description = "PLUS!!! PLUS DE CARTES!!! deux autres cartes tirés"
        image = "Tarot_the_fool.webp"
        embed = discord.Embed(title = "**" + name + "**", description = description)
    
        file = discord.File("cardimages/" + image, filename=image)
        embed.set_image(url = "attachment://" + image)
        
        await ctx.send(file=file, embed = embed)
        
        time.sleep(1)
        await tarot(ctx)
        time.sleep(1)
        await tarot(ctx)
        
        return
    
    return
 
@bot.command()
async def unesurdeux(ctx, bet):
    discordID = ctx.message.author.id
    bet = int(bet)
    money = database_handler.getmoney(discordID)
    if money < bet:
        await ctx.send("vous n'avez pas autant d'argent, vous ne voudriez pas vous endettez quand même?")
        return
    rand = random.randint(0, 1)
    if rand == 0:
        database_handler.add_money(discordID, -bet)
        await ctx.send("perdu... pas de chance... non mais le nul quoi, t'as pas fini de perdre ta thune la loser?")
    else:
        database_handler.add_money(discordID, bet)
        await ctx.send("et c'est gagné!!! sale enfoiré de chanceux va, arrête toi là ou tu vas tout perdre par contre")
  
@bot.command()
async def quitteoudouble(ctx):
    discordID = ctx.message.author.id
    bet = database_handler.getmoney(discordID)
    bet = int(bet)
    money = database_handler.getmoney(discordID)
    if money < bet:
        await ctx.send("vous n'avez pas autant d'argent, vous ne voudriez pas vous endettez quand même?")
        return
    rand = random.randint(0, 1)
    if rand == 0:
        database_handler.add_money(discordID, -bet)
        await ctx.send("perdu... pas de chance... non mais le nul quoi, t'as pas fini de perdre ta thune la loser?")
    else:
        database_handler.add_money(discordID, bet)
        await ctx.send("et c'est gagné!!! sale enfoiré de chanceux va, arrête toi là ou tu vas tout perdre par contre")
    
@bot.command()
async def betchallenge(ctx, bet, receiver):
    discordID1 = ctx.message.author.id
    discordID2 = ctx.message.mentions[0].id
    secondauthor = ctx.message.mentions[0]
    firstauthormention = f"<@{discordID1}>"
    secondauthormention = f"<@{discordID2}>"
    
    def checkauthor(newmessage):
        return newmessage.author.id == discordID2 and ctx.message.channel == newmessage.channel
    
    await ctx.send(f"{secondauthormention}, {firstauthormention} vous défis pour un betchallenge d'un montant de {bet}, tappez \"ok\" pour accepter")
    response = await bot.wait_for("message", timeout = 30, check = checkauthor)
    if response.content != "ok" and response.content != "OK":
        await ctx.send("challenge annulé, le deuxieme joueur n'a pas l'air d accord...")
        return
    
    bet = int(bet)
    money1 = database_handler.getmoney(discordID1)
    money2 = database_handler.getmoney(discordID2)
    if money1 < bet or money2 < bet:
        await ctx.send("l'un de vous n'as pas assez d'argent pour jouer cette somme")
        return
    rand = random.randint(0, 1)
    if rand == 0:
        database_handler.add_money(discordID1, bet)
        database_handler.add_money(discordID2, -bet)
        await ctx.send(f"et c'est {ctx.message.author} qui gagne!")
    else:
        database_handler.add_money(discordID1, -bet)
        database_handler.add_money(discordID2, bet)
        await ctx.send(f"et c'est {secondauthor} qui gagne!")

@bot.command()
async def lejusteprix(ctx):
    if not isOwner(ctx):
        await ctx.send("vous n'avez pas les droits requis pour cette commande")
        return
    result = random.randint(1000, 9999)
    channel = bot.get_channel(962327355341303849)
    await channel.send("début du juste prix!! entrez 'ok' dans ce channel pour vous inscrire")
    players = []
    i = 0
    
    def checkplayer(newmessage):
        return players.count(newmessage.author.id) == 0 and channel == newmessage.channel and (newmessage.content == "ok" or newmessage.content == "OK")
    
    def checkplayertry(newmessage):
        is_int = None
        try:
            int(newmessage.content)
            is_int = True
        except ValueError:
            is_int = False
        return players[i] == newmessage.author.id and channel == newmessage.channel and is_int == True
    
    try:
        while True:
            response = await bot.wait_for("message", timeout = 15, check = checkplayer)
            players.append(response.author.id)
            await channel.send(f"<@{response.author.id}> bien enregistré pour le juste prix")
    except ValueError:
        tamp = False
    finally: 
        await channel.send("je pense à un nombre entre 1000 et 9999, le plus proche remporte le butin, chacun son tour!!!")
        try:
            while True:
                ID = players[i]
                await channel.send(f"<@{ID}>, à ton tour de jouer, tu as 15 secondes pour entrer ta reponse")
                response = await bot.wait_for("message", timeout = 15, check = checkplayertry)
                guess= response.content
                if int(guess) < result:
                    await channel.send("c'est plus!")
                elif int(guess) > result:
                    await channel.send("c'est moin!")
                else:
                    await channel.send(f"c'est gagné, <@{ID}> empoche 50 money!")
                    database_handler.add_money(players[i], 50)
                    return
                i += 1
                if i >= len(players):
                    i = 0
        except ValueError:
            ID = players[i]
            database_handler.add_money(ID, -10)
            await channel.send(f"<@{ID}> n'a pas répondu, il perd 10 money...")
    return
                
@bot.command()
async def tradecard(ctx, firstcard, secondcard, receiver):
    if not isOwner(ctx):
        await ctx.send("you don't have the rights for this command (ask dev)")
        return
    discordID1 = ctx.message.author.id
    discordID2 = ctx.message.mentions[0].id
    if discordID1 == discordID2:
        await ctx.send("you can't trade with yourself")
        return
    firstauthormention = f"<@{discordID1}>"
    secondauthormention = f"<@{discordID2}>"
    
    cardstringlist1 : str = database_handler.getcardslist(discordID1)
    cardstringlist2 : str = database_handler.getcardslist(discordID2)
    cardlist1 = string_to_list_card(str(cardstringlist1))
    cardlist2 = string_to_list_card(str(cardstringlist2))
    firstcardID = database_handler.getcardID(firstcard)
    secondcardID = database_handler.getcardID(secondcard)
    
    if cardlist1.count(firstcardID) == 0:
        await ctx.send(f"{firstauthormention} n'a pas la carte {firstcard}")
        return
    if cardlist2.count(secondcardID) == 0:
        await ctx.send(f"{secondauthormention} n'a pas la carte {secondcard}")
        return
    
    def checkauthor(newmessage):
        return newmessage.author.id == discordID2 and ctx.message.channel == newmessage.channel
    
    await ctx.send(f"{secondauthormention}, {firstauthormention} vous propose d'echanger sa \'{firstcard}\' contre votre \'{secondcard}\', tappez \"ok\" pour accepter")
    response = await bot.wait_for("message", timeout = 30, check = checkauthor)
    if response.content != "ok" and response.content != "OK":
        await ctx.send("échange annulé, le deuxieme joueur n'a pas l'air d accord...")
        return
    
    
    firstindex = cardlist1.index(firstcardID)
    secondindex = cardlist2.index(secondcardID)
    
    temp = cardlist1[firstindex]
    cardlist1[firstindex] = cardlist2[secondindex]
    cardlist2[secondindex] = temp
    
    newstr1 = list_to_string_card(cardlist1)
    newstr2 = list_to_string_card(cardlist2)
    database_handler.update_player_cards(discordID1, newstr1)
    database_handler.update_player_cards(discordID2, newstr2)
    
    await ctx.send("échange réussi, profitez bien vos supers nouvelles cartes!")
    
@bot.command()
async def givecard(ctx, givedcard, receiver):
    discordID1 = ctx.message.author.id
    discordID2 = ctx.message.mentions[0].id
    if discordID1 == discordID2:
        await ctx.send("you can't give to yourself")
        return
    firstauthormention = f"<@{discordID1}>"
    secondauthormention = f"<@{discordID2}>"
    
    cardstringlist1 : str = database_handler.getcardslist(discordID1)
    cardstringlist2 : str = database_handler.getcardslist(discordID2)
    cardlist1 = string_to_list_card(str(cardstringlist1))
    cardlist2 = string_to_list_card(str(cardstringlist2))
    firstcardID = database_handler.getcardID(givedcard)
    
    if cardlist1.count(firstcardID) == 0:
        await ctx.send(f"{firstauthormention} n'a pas la carte {givedcard}")
        return
    
    def checkauthor(newmessage):
        return newmessage.author.id == discordID2 and ctx.message.channel == newmessage.channel
    
    await ctx.send(f"{secondauthormention}, {firstauthormention} vous propose de vous donner \'{givedcard}\', tappez \"ok\" pour accepter")
    response = await bot.wait_for("message", timeout = 30, check = checkauthor)
    if response.content != "ok" and response.content != "OK":
        await ctx.send("échange annulé, le deuxieme joueur n'a pas l'air d accord...")
        return
    
    
    cardlist1.remove(firstcardID)
    newstring1 = list_to_string_card(cardlist1)
    cardlist2.append(firstcardID)
    newstring2 = list_to_string_card(cardlist2)
    
    database_handler.update_player_cards(discordID1, newstring1)
    database_handler.update_player_cards(discordID2, newstring2)
    
    await ctx.send("don réussi, quel geste noble!")
     
@bot.command()
async def givemoney(ctx, donation : int, receiver):
    discordID1 = ctx.message.author.id
    discordID2 = ctx.message.mentions[0].id
    if discordID1 == discordID2:
        await ctx.send("you can't give to yourself")
        return
    if donation <= 0:
        return
    firstauthormention = f"<@{discordID1}>"
    secondauthormention = f"<@{discordID2}>"
    
    money1 : int = database_handler.getmoney(discordID1)
    money2 : int = database_handler.getmoney(discordID2)
    
    if donation > money1:
        await ctx.send(f"{firstauthormention} n'a que {money1} argent, il ne peux pas donner autant!")
        return
    
    def checkauthor(newmessage):
        return newmessage.author.id == discordID2 and ctx.message.channel == newmessage.channel
    
    await ctx.send(f"{secondauthormention}, {firstauthormention} vous propose de vous donner {donation} money, tappez \"ok\" pour accepter")
    response = await bot.wait_for("message", timeout = 30, check = checkauthor)
    if response.content != "ok" and response.content != "OK":
        await ctx.send("échange annulé, le deuxieme joueur n'a pas l'air d accord...")
        return
    
    database_handler.add_money(discordID1, -donation)
    database_handler.add_money(discordID2, donation)
    
    await ctx.send(f"don réussi, quel geste noble!\n{firstauthormention} à maintenant {money1 - donation} money\n{secondauthormention} à maintenant {money2 + donation} money")
    
def create_rooster(dlc_list, banlist):
    ret = []
    
    #gratuit pour tous de base
    ret.append(("Allemands (Frédéric Barberousse)",""))
    ret.append(("Américains (Theodore Roosevelt)",""))
    ret.append(("Anglais (Victoria)",""))
    ret.append(("Arabes (Saladin)",""))
    ret.append(("Brésiliens (Pierre II)",""))
    ret.append(("Chinois (Qin Shi Huang)",""))
    ret.append(("Kongolais (Mvemba a Nzinga)",""))
    ret.append(("Égyptiens (Cléopâtre)",""))
    ret.append(("Espagnols (Philippe II)",""))
    ret.append(("Français (Catherine de Médicis)",""))
    ret.append(("Grecs (Périclès ou Gorgô)",""))
    ret.append(("Indiens (Gandhi)",""))
    ret.append(("Japonais (Hōjō Tokimune)",""))
    ret.append(("Norvégiens (Harald Hardrada)",""))
    ret.append(("Romains (Trajan)",""))
    ret.append(("Russes (Pierre Ier le Grand)",""))
    ret.append(("Scythes (Tomyris)",""))
    ret.append(("Sumériens (Gilgamesh)",""))
    ret.append(("Aztèques (Moctezuma Ier)",""))
    
    #contenue telechargeable
    ret.append(("Pologne (Hedwige Ire)",""))
    ret.append(("Australie (John Curtin)",""))
    ret.append(("Perse (Cyrus le Grand)",""))
    ret.append(("Macédoine (Alexandre le Grand)",""))
    ret.append(("Nubie (Amanitore)",""))
    ret.append(("Khmers (Jayavarman VII)",""))
    ret.append(("Indonésie (Tribhuwana Wijayatunggadewi)",""))
    
    
    #rise and fall
    if dlc_list[0] != '0':
        print("entered rise and fall")
        ret.append(("Zoulous (Chaka)",""))
        ret.append(("Mongolie (Gengis Khan)",""))
        ret.append(("Mapuches (Lautaro)",""))
        ret.append(("Cris des plaines (Pitikwahanapiwiyin)",""))
        ret.append(("Écosse (Robert Ier d Écosse)",""))
        ret.append(("Corée (Seondeok)",""))
        ret.append(("Géorgie (Tamar Ire)",""))
        ret.append(("Pays-Bas (Wilhelmine des Pays-Bas)",""))
        ret.append(("Inde (Chandragupta Ier)",""))
    
    
    #Gathering Storm
    if dlc_list[1] != '0':
        print("entered gathering")
        ret.append(("Suède (Christine de Suède)",""))
        ret.append(("Phénicie (Didon)",""))
        ret.append(("Maoris (Kupe)",""))
        ret.append(("Mali (Mansa Moussa)",""))
        ret.append(("Hongrie (Matthias Corvin)",""))
        ret.append(("Incas (Pachacutec)",""))
        ret.append(("Empire ottoman (Soliman Ier)",""))
        ret.append(("Canada (Wilfrid Laurier)",""))
        ret.append(("France (Aliénor d Aquitaine)",""))
        ret.append(("Angleterre (Aliénor d Aquitaine)",""))
    
    #pass nouvelle Frontiere
    if dlc_list[2] != '0':
        print("entered nouvelle frontiere")
        ret.append(("Mayas (Dame Six Cieux)",""))
        ret.append(("Grande Colombie (Simón Bolívar)",""))
        ret.append(("Éthiopie (Menelik II)",""))
        ret.append(("Byzance (Basile II)",""))
        ret.append(("Gaule (Ambiorix)",""))
        ret.append(("Babylone (Hammurabi)",""))
        ret.append(("Vietnam (Triệu Thị Trinh)",""))
        ret.append(("Mongolie (Kubilai Khan)",""))
        ret.append(("Chine (Kubilai Khan)",""))
        ret.append(("Portugal (Jean III)",""))
    
    i = 0
    while i < len(ret):
        a,b = ret[i]
        if banlist.count(a) != 0:
            ret.remove(ret[i])
            i -= 1
        i += 1
    
    return ret

def randomisation(players):
    ret = []
    lenght = len(players)
    while len(ret) != lenght:
        rand = random.randint(0, lenght - 1)
        if ret.count(rand) == 0:
            ret.append(rand)
    return ret

@bot.command()
async def civ_pick_ban(ctx):
    
    await ctx.send("début du pick/ban de civ!! entrez 'ok' dans ce channel pour vous inscrire")
    players = []
    banlist = []
    i = 0
    
    def checkplayer(newmessage):
        return players.count(newmessage.author.id) == 0 and ctx.channel == newmessage.channel and (newmessage.content == "ok" or newmessage.content == "OK")
    
    def checkplayeranswer(newmessage):
        return players[i] == newmessage.author.id and ctx.channel == newmessage.channel
    
    
    
    
    try:
        while True:
            response = await bot.wait_for("message", timeout = 15, check = checkplayer)
            players.append(response.author.id)
            await ctx.send(f"<@{response.author.id}> bien enregistré pour la game")
    except ValueError:
        tamp = False
    finally: 
        await ctx.send("randomisation de l'ordre de pick/ban")
        randomlist = randomisation(players)
        
        civ_list = create_rooster("111", [])
        civ_string = ""
        for a,b in civ_list:
            civ_string += a
            civ_string += '\n'
        await ctx.send(f"voici la liste des civilisations:\n{civ_string}")
        
        u = 0
        while u < len(randomlist):
            ID = players[u]
            i = players.index(ID)
            await ctx.send(f"<@{ID}>, à ton tour de ban, qui souhaites-tu ban? (entrer nom de dirigeant et la civ en copiant-collant au dessus ou 'nothing' pour ne rien ban)")
            response = await bot.wait_for("message", timeout = 60, check = checkplayeranswer)
            ####  FAIRE LE BANNISEMENT!!!!!!!!!!!
            banlist.append(response.content)
            u += 1
        u = 0
        while u < len(randomlist):
            ID = players[u]
            i = players.index(ID)
            await ctx.send(f"<@{ID}>, à ton tour de pick, quelles extentions possedes tu?? (entrer série de 0 et de 1 correspondant à si vous possedez ou non l'extentions)/npar exemple, 000 si vous ne possedez rien et 111 si vous posedez tout/n entrez dans l'ordre:/nrise and fall\ngathering storm\nPass Nouvelle Frontière")
            response = await bot.wait_for("message", timeout = 60, check = checkplayeranswer)
            rooster = create_rooster(response.content, banlist)
            rand1 = random.randint(0, len(rooster))
            civ1 = rooster[rand1]
            rooster.pop(rand1)
            rand2 = random.randint(0, len(rooster))
            civ2 = rooster[rand2]
            rooster.pop(rand2)
            rand3 = random.randint(0, len(rooster))
            civ3 = rooster[rand3]
            rooster.pop(rand3)
            rand4 = random.randint(0, len(rooster))
            civ4 = rooster[rand4]
            rooster.pop(rand4)
            await ctx.send(f"<@{ID}>, choisi parmis ces 4 civilisations (entre nom de civilisation et dirigent en copiant-collant)")
            await ctx.send(f"{civ1[0]}, {civ1[1]}\n{civ2[0]}, {civ2[1]}\n{civ3[0]}, {civ3[1]}\n{civ4[0]}, {civ4[1]}\n")
            response = await bot.wait_for("message", timeout = 60, check = checkplayeranswer)
            await ctx.send(f"<@{ID}> viens de choisir {response.content}")
            ### RETIRER LA CIVILISATION DU ROOSTER
            banlist.append(response.content)
            u += 1
        await ctx.send("selection terminée, bonne game à tous!")
        
        
        
        
def start_bingo():
    M = create_matrix()
    print("----------------------------------------------------------------------------------------------------------")
    i = 0
    while i < 5:
        k = 0
        print_to_square()
        while k < 2:
            print("|", end = '')
            j = 0
            while j < 5:
                a,b = int_to_string(M[i*5 + j])
                act = ""
                if k == 0:
                    act = a
                else:
                    act = b
                    
                rest = 20 - len(act)
                bef = rest/2
                aft = rest - bef
                if len(act) % 2 == 1:
                    aft -= 1
                x = 0
                while x < bef:
                    print(" ", end = '')
                    x += 1
                print(act, end = '')
                x = 0
                while x < aft:
                    print(" ", end = '')
                    x += 1
                print("|", end = '')
                j += 1
            k += 1
            print("")
        i += 1
        print_to_square()
        print("----------------------------------------------------------------------------------------------------------")    
    print("")
    print(M) 


def print_to_square():
    print("|", end = '')
    i = 0
    while i < 5:
        j = 0
        while j < 20:
            print(" ", end = '')
            j += 1
        print("|", end = '')
        i += 1
    print("")
    
def int_to_string(i):
    if i == 0:
        return ("le double taz","escalier")
    if i == 1:
        return ("le tonnerre","")
    if i == 2:
        return ("l'arbre tueur","")
    if i == 3:
        return ("le sheriff"," et son adjoint")
    if i == 4:
        return ("la gre de dieu","")
    if i == 5:
        return ("le pouvoir du texas","et le l'amerique")
    if i == 6:
        return ("","")
    if i == 7:
        return ("le tonnerre de zeus","(haut du perchoire)")
    if i == 8:
        return ("la traumatisation","")
    if i == 9:
        return ("chat perche","")
    if i == 10:
        return ("ninja defuse","")
    if i == 11:
        return ("le rewind","")
    if i == 12:
        return ("purification","(awp jambe + gre)")
    if i == 13:
        return ("je le vois pas","il me voit pas")
    if i == 14:
        return ("la piraterie","")
    if i == 15:
        return ("la frappe du brezil","")
    if i == 16:
        return ("peekaboo","")
    if i == 17:
        return ("la michael mayers","")
    if i == 18:
        return ("recyclage","de la chiasse enemie")
    if i == 19:
        return ("le 360 zeus","")
    if i == 20:
        return ("la cut zone","")
    if i == 21:
        return ("le tetanos","")
    if i == 22:
        return ("la plante","tueuse")
    if i == 23:
        return ("l aigle assassin","")
    if i == 24:
        return ("bonjour taz","au revoir")
    if i == 25:
        return ("tazed","")
    if i == 26:
        return ("pistolet a bille","")
    if i == 27:
        return ("des portes","autour de moi")
    if i == 28:
        return ("entree par","effraction")
    if i == 29:
        return ("livraison","uber eats")
    if i == 30:
        return ("la tourelle","")
    if i == 31:
        return ("cuted","")
    
def take_screenshot():
    #image = pyscreenshot.grab(bbox=(1019, 550, 1760, 935))
    image = pyscreenshot.grab(bbox=(0, 575, 850, 980))
    #image.show()
    image.save("newbingo.png") 
    return

def create_matrix():
    M = []
    i = 0
    while i < 25:
        rand = random.randint(0, 31)
        if M.count(rand) == 0:
            M.append(rand)
            i += 1
    return M


@bot.command()
async def bingo(ctx):
    if not isOwner(ctx):
        await ctx.send("vous n'avez pas les droits requis pour cette commande")
        return
    start_bingo()
    take_screenshot()
    await ctx.send(file=discord.File('newbingo.png'))
    return




def color_bingo(M):
    print("--------------------------------------------------------------------------------------------------------------------")
    i = 0
    M3 = []
    while i < 25:
        M3.append(int_to_string(M[i]))
        i += 1
    
    
    M2 = get_result(M3)
    i = 0
    while i < 5:
        k = 0
        print_to_square_color(M2,i)
        while k < 2:
            print("|", end = '')
            j = 0
            while j < 5:
                if M2[i*5 + j] == True:
                    print(f"{Fore.GREEN}${Style.RESET_ALL}", end = '')
                else:
                    print(f"{Fore.RED}${Style.RESET_ALL}", end = '')
                
                
                a,b = int_to_string(M[i*5 + j])
                act = ""
                if k == 0:
                    act = a
                else:
                    act = b
                    
                rest = 20 - len(act)
                bef = rest/2
                aft = rest - bef
                if len(act) % 2 == 1:
                    aft -= 1
                x = 0
                while x < bef:
                    print(" ", end = '')
                    x += 1
                print(act, end = '')
                x = 0
                while x < aft:
                    print(" ", end = '')
                    x += 1
                if M2[i*5 + j] == True:
                    print(f"{Fore.GREEN}${Style.RESET_ALL}", end = '')
                else:
                    print(f"{Fore.RED}${Style.RESET_ALL}", end = '')
                print("|", end = '')
                j += 1
            k += 1
            print("")
        print_to_square_color(M2,i)
        i += 1
        print("--------------------------------------------------------------------------------------------------------------------") 
    return


def get_result(M):
    file = open("result.txt", 'r')
    stringlist = file.readlines()
    lenght = len(stringlist)
    i = 0
    while i < lenght:
        stringlist[i] = stringlist[i][:-1]
        i += 1
    M2 = [False]*25
    j = 0
    while j < lenght:
        i = 0
        while i < 25:
            a,b = M[i]
            if a == stringlist[j]:
                M2[i] = True
            i += 1
        j += 1
    return M2

def print_to_square_color(M, col):
    print("|", end = '')
    i = 0
    while i < 5:
        j = 0
        while j < 22:
            if M[col*5 + i] == True:
                print(f"{Fore.GREEN}#{Style.RESET_ALL}", end = '')
            else:
                print(f"{Fore.RED}#{Style.RESET_ALL}", end = '')
            j += 1
        print("|", end = '')
        i += 1
    print("")
    

##############################################################################
"""starting the bot"""
##############################################################################
bot.run("") #but your bot id here