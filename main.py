'''
Copyright (c) 2021 Frigyes06
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
'''

from multiprocessing.connection import Client
import requests
from bs4 import BeautifulSoup
import discord
from discord.ext import tasks

#this is the url to Sonoma County's NWS RSS feed
default_url = "https://alerts.weather.gov/cap/wwaatmget.php?x=CAC097"

client = discord.Client()

discord_token = "YOUR_TOKEN_HERE"

current_watches = []
previous_watches = []
current_zone = ""
bot_ok = False

def getwarnings(url):
    global current_zone
    global current_watches

    current_watches = []

    if not url:
        url = default_url
    
    response = requests.get(url)
    soup = BeautifulSoup(response.content, features="xml")

    current_zone = soup.title.text

    entries = soup.findAll('entry')

    if entries[0].title.text == "There are no active watches, warnings or advisories":
        return False
    
    for entry in entries:
        watch = {}
        watch['title'] = entry.title.text
        watch['link'] = entry.id.text
        watch['summary'] = entry.summary.text
        watch['event'] = entry.event.text
        watch['effective'] = entry.effective.text
        watch['expires'] = entry.expires.text
        current_watches.append(watch)
    return True


@client.event
async def on_ready():
    global bot_ok
    game = discord.Game("!help")
    await client.change_presence(status=discord.Status.online, activity=game)
    print('We have logged in as {0.user}'.format(client))
    bot_ok = True


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if not message.content.startswith("!"):
        return

    if message.content.startswith("!help"):
        await message.channel.send("Usage:\n!get - gives the current watches for Sonoma, CA\n!get california - gives the current watches for California\n!get {Area code, like CAC097} gives the current watches for that area.\n!get {NWS RSS feed url} gives the current watches from the provided url")

    if message.content.startswith('!get'):

        status = False
        
        if not len(message.content.split(" ")) == 2:
            status = getwarnings("")
        else:
            parameter = message.content.split(" ")[1]
        
            if parameter.startswith("https://"):
                status = getwarnings(message.content.split(" ")[1])
            if parameter.startswith("california") or parameter.startswith("California") or parameter.startswith("CA"):
                status = getwarnings("https://alerts.weather.gov/cap/ca.php?x=1")
            else:
                status = getwarnings("https://alerts.weather.gov/cap/wwaatmget.php?x=" + message.content.split(" ")[1])
        
        if status:
            await message.channel.send(current_zone)
            for watch in current_watches:
                embed = discord.Embed(title = watch['title'], url = watch['link'], description = watch['summary'])
                await message.channel.send(embed = embed)
            return
        
        await message.channel.send(current_zone)
        await message.channel.send("There are no active watches, warnings or advisories")


@tasks.loop(minutes=1)
async def get_new_warnings():
    
    to_announce = []
    print("started retrieving warnings")
    getwarnings(default_url)
    
    for watch in current_watches:
        if watch not in previous_watches:
            to_announce.append(watch)
            previous_watches.append(watch)
    
    for watch in previous_watches:
        if watch not in current_watches:
            previous_watches.remove(watch)
    
    print(to_announce)
    
    if bot_ok:
        channel = Client.get_channel('919341495243407380')
        await channel.send("New Watches, Warnings and Advisories for Sonoma (CAC097) California Issued by the National Weather Service")
        
        for watch in current_watches:
            embed = discord.Embed(title = watch['title'], url = watch['link'], description = watch['summary'])
            await channel.send(embed = embed)


get_new_warnings.start()

client.run(discord_token)
