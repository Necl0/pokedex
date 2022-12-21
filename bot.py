import discord
import re
import requests

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


@client.event
async def on_message(message):
    if message.author == client.user:
        return


    if message.content.startswith('!p'):
        name = message.content.split(' ')[1].lower().strip()

        p_json = get_poke(name)

        if p_json is None:
            await message.channel.send('Pokemon not found')
            return
        else:
            sprite = p_json['sprites']['front_default']
            name = p_json['name']
            types = [t['type']['name'] + ", " for t in p_json['types'][:-1]] + [p_json['types'][-1]['type']['name']]

            embed = discord.Embed(title=name.title(), description=f"Types: {' '.join(types).title()}\nWeight: {p_json['weight']}\nHeight: {p_json['height']}")

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


client.run('token')



