import discord
import interactions
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext
from discord_slash.utils.manage_commands import create_option
import os


intents = discord.Intents.default()
intents.reactions = True

client = commands.Bot(command_prefix='$', intents=intents)
slash = SlashCommand(client, sync_commands=True)


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@slash.slash(name='move',
             description='Move the message to the channel the command is used in, deletes original',
             options=[
                 create_option(
                     name='message_link',
                     description='Link to message that will be moved',
                     required=True,
                     option_type=interactions.OptionType.STRING
                 )
             ],
             # TODO add geekhub id 365078454003302400
             guild_ids=[951200945012875264])
async def move(ctx: SlashContext, message_link: str):

    messageLinkToCopy = message_link.split('/')
    serverId = int(messageLinkToCopy[4])
    channelId = int(messageLinkToCopy[5])
    msgId = int(messageLinkToCopy[6])

    server = client.get_guild(serverId)
    origChannel = server.get_channel(channelId)
    origMessage = await origChannel.fetch_message(msgId)

    # destinationChannelId = channel_mention[2:len(channel_mention) - 1]

    embed = discord.Embed(timestamp=origMessage.created_at)
    embed.set_author(name=origMessage.author.name + '#' + origMessage.author.discriminator,
                     icon_url=origMessage.author.avatar_url)
    embed.set_footer(text=origMessage.author.id)
    embed.add_field(name='Moved from', value=origChannel.mention, inline=False)
    embed.add_field(name='Message', value=origMessage.content, inline=False)
    embed.add_field(name='Notice', value='The original author can delete this by reacting \U0001F5D1', inline=False)

    # TODO maybe try and fix this to not use API call
    # channel = server.get_channel(destinationChannelId)
    # channel = await client.fetch_channel(destinationChannelId)
    newMessage = await ctx.send(embed=embed)
    await newMessage.add_reaction('\U0001F5D1')
    # await ctx.send('Moved message to ' + channel_mention)

    # TODO add this after testing
    # await origMessage.delete()


"""@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$move'):

        isOperator = False
        for role in message.author.roles:
            # TODO update role id to geekhub operator id 365130913241104384
            if role.id == 951212802880725042:
                isOperator = True

        if not isOperator:
            return

        content = message.content.split()
        messageLinkToCopy = content[1].split('/')

        serverId = int(messageLinkToCopy[4])
        channelId = int(messageLinkToCopy[5])
        msgId = int(messageLinkToCopy[6])

        server = client.get_guild(serverId)
        origChannel = server.get_channel(channelId)
        origMessage = await origChannel.fetch_message(msgId)

        destinationChannelId = content[2][2:len(content[2])-1]

        embed = discord.Embed(timestamp=origMessage.created_at)
        embed.set_author(name=origMessage.author.name + '#' + origMessage.author.discriminator,
                         icon_url=origMessage.author.avatar_url)
        embed.set_footer(text=origMessage.author.id)
        embed.add_field(name='Moved from', value=origChannel.mention, inline=False)
        embed.add_field(name='Message', value=origMessage.content, inline=False)
        embed.add_field(name='Notice', value='The original author can delete this by reacting \U0001F5D1', inline=False)

        # TODO maybe try and fix this to not use API call
        # channel = server.get_channel(destinationChannelId)
        channel = await client.fetch_channel(destinationChannelId)
        newMessage = await channel.send(embed=embed)
        await newMessage.add_reaction('\U0001F5D1')

        # TODO add this after testing
        # await origMessage.delete()
        # await message.delete()
"""

@client.event
async def on_raw_reaction_add(payload):
    if payload.member.id == client.user.id:
        return

    serverId = payload.guild_id
    channelId = payload.channel_id
    msgId = payload.message_id

    server = client.get_guild(serverId)
    origChannel = server.get_channel(channelId)
    origMessage = await origChannel.fetch_message(msgId)

    if origMessage.author.id == client.user.id:
        if int(discord.Embed.from_dict(origMessage.embeds[0].to_dict()).footer.text) == payload.member.id:
            await origMessage.delete()


client.run(os.getenv('TOKEN'))
