import requests
from bs4 import BeautifulSoup
import discord

#this is the url to Sonoma County's NWS RSS feed
default_url = "https://alerts.weather.gov/cap/wwaatmget.php?x=CAC097"

client = discord.Client()

discord_token = "YOUR TOKEN"

def getwarnings(url):

    global current_watches
    current_watches = []

    if not url:
        url = default_url
    
    response = requests.get(url)
    soup = BeautifulSoup(response.content, features="xml")

    entries = soup.findAll('entry')

    print(entries)
    if entries[0].title.text == "There are no active watches, warnings or advisories":
        return False
    else:
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
            for watch in current_watches:
                embed = discord.Embed(title = watch['title'], url = watch['link'], description = watch['summary'])
                await message.channel.send(embed = embed)
        else:
            await message.channel.send("There are no active watches, warnings or advisories")

client.run(discord_token)
