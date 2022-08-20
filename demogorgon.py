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
             # TODO add geekhub id int(os.getenv('GEEKHUB'))
             guild_ids=[int(os.getenv('TESTGUILD'))])
async def move(ctx: SlashContext, message_link: str):

    messageLinkToCopy = message_link.split('/')
    serverId = int(messageLinkToCopy[4])
    channelId = int(messageLinkToCopy[5])
    msgId = int(messageLinkToCopy[6])

    server = client.get_guild(serverId)
    origChannel = server.get_channel(channelId)
    origMessage = await origChannel.fetch_message(msgId)

    embed = discord.Embed(timestamp=origMessage.created_at)
    embed.set_author(name=origMessage.author.name + '#' + origMessage.author.discriminator,
                     icon_url=origMessage.author.avatar_url)
    embed.set_footer(text=origMessage.author.id)
    embed.add_field(name='Moved from', value=origChannel.mention, inline=False)
    if origMessage.content:
        embed.add_field(name='Message', value=origMessage.content, inline=False)
    embed.add_field(name='Notice',
                    value='{0.mention} may react \U0001F5D1 to delete this message'.format(origMessage.author),
                    inline=False)

    newMessage = await ctx.send(embed=embed, files=[await f.to_file() for f in origMessage.attachments])
    await newMessage.add_reaction('\U0001F5D1')

    await origMessage.delete()


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


@client.event
async def on_voice_state_update(member, before, after):

    if before.channel is not None and after.channel != before.channel:
        # check if a channel needs to be removed
        category = before.channel.category
        if category.name.startswith('/VAR/MAIL/OFF-TOPIC/'):
            channelList = category.voice_channels
            emptyOffTopicChannels = 0
            emptyGamingChannels = 0

            for channel in channelList:
                if channel.name.startswith('off-topic/voice_') and len(channel.members) == 0:
                    emptyOffTopicChannels += 1
                if channel.name.startswith('gaming.voice_') and len(channel.members) == 0:
                    emptyGamingChannels += 1

            for channel in channelList:
                if channel.name.startswith('off-topic/voice_') and not channel.name.startswith('off-topic/voice_1'):
                    if len(channel.members) == 0 and emptyOffTopicChannels > 1:
                        await channel.delete()
                        break

                if channel.name.startswith('gaming.voice_') and not channel.name.startswith('gaming.voice_1'):
                    if len(channel.members) == 0 and emptyGamingChannels > 1:
                        await channel.delete()
                        break

            channelList = category.voice_channels
            curOffTopicID = 1
            curGamingID = 1
            position = 0

            for channel in channelList:
                if channel.name.startswith('off-topic/voice_'):
                    if int(channel.name[-1]) != curOffTopicID:
                        newName = 'off-topic/voice_' + str(curOffTopicID)
                        await channel.edit(name=newName)
                    curOffTopicID += 1

                if channel.name.startswith('gaming.voice_'):
                    if int(channel.name[-1]) != curGamingID:
                        newName = 'gaming.voice_' + str(curGamingID)
                        await channel.edit(name=newName)
                    curGamingID += 1

                position += 1

    if after.channel is not None and before.channel != after.channel:
        # check if more vc are needed
        guild = after.channel.guild
        category = after.channel.category
        if category.name.startswith('/VAR/MAIL/OFF-TOPIC/'):
            channelList = category.voice_channels
            offTopicFull = True
            offTopicCount = 0
            gamingFull = True
            gamingCount = 0
            lastOffTopic = None
            lastGaming = None
            for channel in channelList:
                if channel.name.startswith('off-topic/voice_'):
                    offTopicCount += 1
                    lastOffTopic = channel
                    if len(channel.members) == 0:
                        offTopicFull = False

                if channel.name.startswith('gaming.voice_'):
                    gamingCount += 1
                    lastGaming = channel
                    if len(channel.members) == 0:
                        gamingFull = False

            if offTopicFull and offTopicCount < 5:
                newChannelNumber = str(offTopicCount + 1)
                newChannelName = 'off-topic/voice_' + newChannelNumber
                await guild.create_voice_channel(name=newChannelName, category=category, position=lastOffTopic.position)
                offTopicCount += 1

            if gamingFull and gamingCount < 5:
                newChannelNumber = str(gamingCount + 1)
                newChannelName = 'gaming.voice_' + newChannelNumber
                await guild.create_voice_channel(name=newChannelName, category=category, position=lastGaming.position)


client.run(os.getenv('TOKEN'))
