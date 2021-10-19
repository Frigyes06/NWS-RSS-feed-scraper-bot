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

import requests
from bs4 import BeautifulSoup
import discord

#this is the url to Sonoma County's NWS RSS feed
default_url = "https://alerts.weather.gov/cap/wwaatmget.php?x=CAC097"

client = discord.Client()

discord_token = "YOUR TOKEN"

current_watches = []
current_zone = ""

def getwarnings(url):
    global current_zone

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
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!get'):

        status = False
        
        if not len(message.content.split(" ")) == 2:
            status = getwarnings("")
        else:
            status = getwarnings(message.content.split(" ")[1])
        
        if status:
            await message.channel.send(current_zone)
            for watch in current_watches:
                embed = discord.Embed(title = watch['title'], url = watch['link'], description = watch['summary'])
                await message.channel.send(embed = embed)
            return
        
        await message.channel.send(current_zone)
        await message.channel.send("There are no active watches, warnings or advisories")

client.run(discord_token)
