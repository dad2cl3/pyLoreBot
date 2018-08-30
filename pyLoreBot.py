import discord, json, math, re, requests, string

with open('config.json', 'r') as config_file:
    config = json.load(config_file)


def build_embed(lore_entry):

    '''lore_item_description = lore_entry['item_description']

    if lore_item_description != None:
        lore_item_description = scrub(lore_item_description)

    lore_item_name = scrub(lore_entry['item_name'])


    lore_embed = discord.Embed(
        title=lore_item_name,
        description=lore_item_description
    )'''

    #print(lore_entry['item_name'])
    #print(lore_entry['item_description'])

    lore_embed = discord.Embed(
        title = lore_entry['item_name'],
        description = lore_entry['item_description']
    )

    # add footer if present in bot configuration
    if 'footer' in config:
        lore_embed.set_footer(
            icon_url=config['footer']['icon_url'],
            text=config['footer']['text']
        )

    lore_description = lore_entry['lore_description']

    #lore_description = scrub(lore_description)

    print('{0} - {1}'.format(lore_entry['item_name'], len(lore_description)))

    if len(lore_description) > 1024:
        # calculate number of fields
        fields = math.ceil(len(lore_description)/1024)

        for i in range(0,fields):
            # get description chunk
            chunk_start = 1024 * i

            if i < (fields - 1):
                # not last chunk
                chunk_end = 1024 * (i + 1)
            else:
                # last chunk
                chunk_end = len(lore_description)

            chunk_description = lore_description[chunk_start:chunk_end]

            if i == 0:
                embed_name = 'Lore'
            else:
                embed_name = "Lore (cont'd)"

            lore_embed.add_field(
                name = embed_name,
                value = chunk_description
            )
    elif len(lore_description) < 1024 and len(lore_description) > 0:
        lore_embed.add_field(
            name='Lore',
            value=lore_description
        )

    lore_embed.set_thumbnail(
        url=lore_entry['item_icon']
    )

    return lore_embed


client = discord.Client()

@client.event
async def on_ready():
    print('Bot is ready...')

@client.event
async def on_message(message):

    if message.content.startswith('!lore'):
        print(message.content)

        # remove call to bot
        lore_search = message.content.replace('!lore ', '')
        # remove leading/trailing whitespace
        #lore_search = lore_search.strip()
        # remove any punctuation
        #lore_search = lore_search.translate(lore_search.maketrans('','', string.punctuation))

        # replace spaces with ampersands
        #lore_search = re.sub('\s\s+', ' ', lore_search)
        #lore_search = lore_search.replace(' ', ' & ')
        print(lore_search)

        response = requests.get(config['url'], params={'search': lore_search})
        print(response.status_code)
        if response.status_code == 200:
            lore_items = response.json()
            #print(lore_items) # debug statement

            if len(lore_items) > 0:
                if 'grimoire' in lore_items:
                    for lore_item in lore_items['grimoire']:
                        lore_embed = build_embed(lore_item)
                        # print(lore_embed.fields) # debug statement

                        await client.send_message(message.channel, embed=lore_embed)

                if 'inventory' in lore_items:
                    for lore_item in lore_items['inventory']:
                        lore_embed = build_embed(lore_item)
                        # print(lore_embed.fields) # debug statement

                        await client.send_message(message.channel, embed=lore_embed)

                if 'records' in lore_items:
                    for lore_item in lore_items['records']:
                        #print(lore_item)
                        lore_embed = build_embed(lore_item)
                        #print(lore_embed.fields) # debugging
                        await client.send_message(message.channel, embed=lore_embed)
            else:
                troll = config['troll']

                troll_embed = build_embed(troll)

                await client.send_message(message.channel, embed=troll_embed)


client.run(config['discord_token'])

