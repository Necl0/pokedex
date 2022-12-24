import discord
import re
import requests
import random
import asyncio
import json
import datetime
import string
import math
from discord.ext import tasks
from pydantic import BaseModel, conint, confloat
from typing import Literal, Optional, Annotated


class Pokemon(BaseModel):
    num: conint(ge=1, le=898)
    id: str
    level: conint(ge=1, le=100)
    name: str
    sprite: str
    types: list[Literal['fire', 'water', 'grass', 'bug', 'normal', 'poison', 'electric', 'ground', 'fairy', 'fighting',
                   'psychic', 'rock', 'ghost', 'ice', 'dragon', 'dark', 'steel', 'flying']]
    atk: Annotated[int, conint(ge=1, le=255)]
    d: Annotated[int, conint(ge=1, le=255)]
    satk: Annotated[int, conint(ge=1, le=255)]
    sdef: Annotated[int, conint(ge=1, le=255)]
    spd: Annotated[int, conint(ge=1, le=255)]
    hp: Annotated[int, conint(ge=1, le=255)]
    weight: Annotated[int, confloat(ge=0.2, le=9999.9)]
    height: Annotated[int, confloat(ge=0.2, le=9999.9)]
    iv: Annotated[int, conint(ge=0, le=31)]
    ev: Annotated[int, conint(ge=0, le=252)]
    abilities: Optional[list[str]] = None
    moves: Optional[list[str]] = None
    nature: Optional[Literal['adamant', 'bashful', 'bold', 'brave', 'calm', 'careful', 'docile', 'gentle', 'hardy',
                             'hasty', 'impish', 'jolly', 'lax', 'lonely', 'mild', 'modest', 'naive', 'naughty', 'quiet',
                             'quirky', 'rash', 'relaxed', 'sassy', 'serious', 'timid']] = None

    def return_json(self):
        # return each parameter in json
        return {
            "num": self.num,
            "id": self.id,
            "level": self.level,
            "name": self.name,
            "sprite": self.sprite,
            "types": self.types,
            "atk": self.atk,
            "def": self.d,
            "satk": self.satk,
            "sdef": self.sdef,
            "spd": self.spd,
            "hp": self.hp,
            "weight": self.weight,
            "height": self.height,
            "iv": self.iv,
            "ev": self.ev,
            "abilities": self.abilities,
            "moves": self.moves,
            "nature": self.nature

        }


intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)


def get_poke(name):
    url = f'https://pokeapi.co/api/v2/pokemon/{name}'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None


@client.event
async def on_ready():
    print(f'Entering world as {client.user}')
    spawner.start()


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!setspawn'):
        id = message.content.split(' ')[1]
        channel = client.get_channel(id)
        # dump the id into json file
        with open('channel.json', 'w') as f:
            json.dump({'id': id}, f)

        await message.channel.send('Spawn channel set!')

    elif message.content.startswith('!p'):
        name = message.content.split(' ')[1].lower().strip()

        p_json = get_poke(name)

        if p_json is None:
            await message.channel.send('Pokemon not found')
            return
        else:
            sprite = p_json['sprites']['front_default']
            name = p_json['name']
            types = [t['type']['name'] + ", " for t in p_json['types'][:-1]] + [p_json['types'][-1]['type']['name']]
            embed = discord.Embed(title=name.title(), description=f"Types: {' '.join(types).title()}\nWeight: {p_json['weight']} lb\nHeight: {p_json['height']/10} m")

            match = re.search(r'(fire|water|grass|bug|normal|poison|electric|ground|fairy|fighting|psychic|rock|ghost|ice|dragon|dark|steel)', ' '.join(types).lower())

            if match:
                if match.group(1) == 'fire':
                    embed.color = discord.Color.red()
                elif match.group(1) == 'water':
                    embed.color = discord.Color.blue()
                elif match.group(1) == 'grass':
                    embed.color = discord.Color.green()
                elif match.group(1) == 'bug':
                    embed.color = discord.Color.dark_green()
                elif match.group(1) == 'normal':
                    embed.color = discord.Color.dark_grey()
                elif match.group(1) == 'poison':
                    embed.color = discord.Color.purple()
                elif match.group(1) == 'electric':
                    embed.color = discord.Color.gold()
                elif match.group(1) == 'ground':
                    embed.color = discord.Color.dark_gold()
                elif match.group(1) == 'fairy':
                    embed.color = discord.Color.light_grey()
                elif match.group(1) == 'fighting':
                    embed.color = discord.Color.dark_red()
                elif match.group(1) == 'psychic':
                    embed.color = discord.Color.dark_magenta()
                elif match.group(1) == 'rock':
                    embed.color = discord.Color.dark_orange()
                elif match.group(1) == 'ghost':
                    embed.color = discord.Color.dark_purple()
                elif match.group(1) == 'ice':
                    embed.color = discord.Color.teal()
                elif match.group(1) == 'dragon':
                    embed.color = discord.Color.dark_teal()
                elif match.group(1) == 'dark':
                    embed.color = discord.Color.dark_grey()
                elif match.group(1) == 'steel':
                    embed.color = discord.Color.dark_grey()

            embed.add_field(name="Stats", value=f"""
                                                HP: {p_json['stats'][0]['base_stat']}
                                                Attack: {p_json['stats'][1]['base_stat']}
                                                Defense: {p_json['stats'][2]['base_stat']}
                                                Special Attack: {p_json['stats'][3]['base_stat']}
                                                Special Defense: {p_json['stats'][4]['base_stat']}
                                                Speed: {p_json['stats'][5]['base_stat']}""", inline=False)

            embed.add_field(name="Abilities", value='\n'.join([a['ability']['name'].title() for a in p_json['abilities']]), inline=False)
            embed.add_field(name="Moves", value='\n'.join([m['move']['name'].title() for m in p_json['moves'][:5]]), inline=False)

            embed.set_image(url=sprite)

            embed.set_footer(text="Made by @Neclo#5545")
            await message.channel.send(embed=embed)

            return

    elif message.content.startswith('!help'):
        await message.channel.send(""""!p <pokemon name> - get info on a pokemon
            !setspawn <channel id> - set the channel to spawn pokemon in
            !help - get help""")

    elif message.content.startswith('!about'):
        await message.channel.send('Pokedex Discord bot.\nMade by Neclo#5545')
    elif message.content.startswith('!invite'):
        await message.channel.send('https://discord.com/api/oauth2/authorize?client_id=1053883092684783748&permissions=8&scope=bot')
    elif message.content.startswith('!github'):
        await message.channel.send('https://github.com/Necl0/pokedex')
    elif message.content.startswith('!list'):
        # list all user's pokemon in embed format
        with open('data.json', 'r') as f:
            users = json.load(f)

        if str(message.author.id) not in users:
            return None

        poke_list = users[str(message.author.id)]
        poke_embed = discord.Embed(title="", description="Your pokemon:")
        for poke in poke_list:
            poke_embed.add_field(name=f"(lvl {poke['level']}) {poke['name'].title()}", value=f"", inline=False)

        poke_embed.set_footer(text="Made by @Neclo#5545")
        await message.channel.send(embed=poke_embed)


async def poke_spawn():
    num = random.randint(1, 898)
    p_json = get_poke(num)

    poke = Pokemon(
        num=num,
        id=''.join(random.choices(string.ascii_letters + string.digits, k=20)),
        level=random.randint(1, 100),
        name=p_json['name'],
        sprite=p_json['sprites']['front_default'],
        types=[t['type']['name'] for t in p_json['types']],
        atk=p_json['stats'][1]['base_stat'],
        d=p_json['stats'][2]['base_stat'],
        satk=p_json['stats'][3]['base_stat'],
        sdef=p_json['stats'][4]['base_stat'],
        spd=p_json['stats'][5]['base_stat'],
        hp=p_json['stats'][0]['base_stat'],
        weight=float(p_json['weight']),
        height=float(p_json['height']),
        iv=random.randint(1, 31),
        ev=random.randint(1, 255),
        abilities=[a['ability']['name'] for a in p_json['abilities']],
        moves=[m['move']['name'] for m in p_json['moves'][:5]],
        nature=random.choice(['hardy', 'lonely', 'brave', 'adamant', 'naughty', 'bold', 'docile', 'relaxed', 'impish',
                              'lax', 'timid', 'hasty', 'serious', 'jolly', 'naive', 'modest', 'mild', 'quiet',
                              'bashful', 'rash', 'calm', 'gentle', 'sassy', 'careful', 'quirky'])
    )

    # get the channel to send the message to
    with open('channel.json', 'r') as f:
        channel_id = json.load(f)['id']

    channel = client.get_channel(int(channel_id))
    poke_embed = discord.Embed(title="", description="A wild pokemon has spawned! Type **<pokemon name>** to catch it!")
    poke_embed.set_image(url=poke.sprite)
    poke_embed.set_footer(text="Made by @Neclo#5545")

    await channel.send(embed=poke_embed)
    await timer(poke.name, poke.level, poke)


@tasks.loop(seconds=10)
async def spawner():
    chance = random.randint(1, 3)

    if chance == 1:
        # print current time
        print(f"Spawning at {datetime.datetime.now()}")
        await poke_spawn()


async def timer(name, lvl, poke):
    with open('channel.json', 'r') as f:
        channel_id = json.load(f)['id']

    channel = client.get_channel(int(channel_id))

    def check(m):
        return m.content == name.lower().strip() and m.channel.id == int(channel_id)

    try:
        msg = await client.wait_for('message', timeout=15.0, check=check)
        await msg.channel.send(f"{msg.author.mention} caught the pokemon!")
        await catch_poke(poke, msg.author.id)
    except asyncio.TimeoutError:
        await channel.send(f"The pokemon ran away! It was a **level {lvl}** {name}!")


async def catch_poke(poke, user_id):
    with open('data.json', 'r') as f:
        users = json.load(f)

    if str(user_id) not in users:
        users[str(user_id)] = []

    poke.hp = calculate_stat(poke.hp, poke.iv, poke.ev, poke.level, True)
    poke.atk = calculate_stat(poke.atk, poke.iv, poke.ev, poke.level)
    poke.d = calculate_stat(poke.d, poke.iv, poke.ev, poke.level)
    poke.satk = calculate_stat(poke.satk, poke.iv, poke.ev, poke.level)
    poke.sdef = calculate_stat(poke.sdef, poke.iv, poke.ev, poke.level)
    poke.spd = calculate_stat(poke.spd, poke.iv, poke.ev, poke.level)

    users[str(user_id)].append(poke.return_json())

    with open('data.json', 'w') as f:
        json.dump(users, f)


def calculate_stat(stat, iv, ev, lvl, is_hp=False):
    return int((((2 * stat + iv + (ev / 4)) * lvl) / 100) + lvl + 10) if is_hp else int(
        (((2 * stat + iv + (ev / 4)) * lvl) / 100) + 5)


client.run('token')



