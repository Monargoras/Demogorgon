import discord
import os

intents = discord.Intents.default()

client = discord.Bot(intents=intents)


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


async def addVote(button, interaction):
    category = interaction.message.content.split(' ')[0]
    rating = interaction.message.content.split(' ')[2]
    newRating = int(rating.split(':')[0]) + int(button.label)
    votes = interaction.message.content.split(' ')[4]
    newVotes = int(votes) + 1
    await interaction.message.edit(content='{cat} ----- {newR}:star: ----- {votes} Votes'.format(cat=category, newR=newRating, votes=newVotes))
    await interaction.response.send_message('Your vote: {cat} - {r}'.format(cat=category, r=int(button.label)), ephemeral=True)


async def updateVote(button, interaction, oldVote: int):
    category = interaction.message.content.split(' ')[0]
    rating = interaction.message.content.split(' ')[2]
    newRating = int(rating.split(':')[0]) - oldVote + int(button.label)
    votes = interaction.message.content.split(' ')[4]
    await interaction.message.edit(content='{cat} ----- {newR}:star: ----- {votes} Votes'.format(cat=category, newR=newRating, votes=votes))
    await interaction.response.send_message('Your vote: {cat} - {r}'.format(cat=category, r=int(button.label)), ephemeral=True)


class ButtonView(discord.ui.View):
    users = {}

    def __init__(self):
        super().__init__(timeout=600)
        self.users = {}

    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
        message = client.get_message(self.message.id)
        category = message.content.split(' ')[0]
        rating = message.content.split(' ')[2].split(':')[0]
        votes = int(message.content.split(' ')[4])
        if votes > 0:
            newR = float(rating) / float(votes)
            await self.message.edit(content='{cat} ----- {newR}/5:star: ----- {votes} Votes'.format(cat=category, newR=newR, votes=votes), view=self)
        else:
            await self.message.edit(content='{cat} ----- No votes were cast.'.format(cat=category), view=self)

    @discord.ui.button(label='1', style=discord.ButtonStyle.danger)
    async def button1_callback(self, button, interaction):
        if interaction.user.id in self.users.keys():
            await updateVote(button, interaction, self.users[interaction.user.id])
        else:
            await addVote(button, interaction)
        self.users[interaction.user.id] = int(button.label)

    @discord.ui.button(label='2', style=discord.ButtonStyle.danger)
    async def button2_callback(self, button, interaction):
        if interaction.user.id in self.users.keys():
            await updateVote(button, interaction, self.users[interaction.user.id])
        else:
            await addVote(button, interaction)
        self.users[interaction.user.id] = int(button.label)

    @discord.ui.button(label='3', style=discord.ButtonStyle.primary)
    async def button3_callback(self, button, interaction):
        if interaction.user.id in self.users.keys():
            await updateVote(button, interaction, self.users[interaction.user.id])
        else:
            await addVote(button, interaction)
        self.users[interaction.user.id] = int(button.label)

    @discord.ui.button(label='4', style=discord.ButtonStyle.success)
    async def button4_callback(self, button, interaction):
        if interaction.user.id in self.users.keys():
            await updateVote(button, interaction, self.users[interaction.user.id])
        else:
            await addVote(button, interaction)
        self.users[interaction.user.id] = int(button.label)

    @discord.ui.button(label='5', style=discord.ButtonStyle.success)
    async def button5_callback(self, button, interaction):
        if interaction.user.id in self.users.keys():
            await updateVote(button, interaction, self.users[interaction.user.id])
        else:
            await addVote(button, interaction)
        self.users[interaction.user.id] = int(button.label)


@client.slash_command(
    name='rate',
    description='Create a rating message for the restaurant given',
    # TODO add geekhub id int(os.getenv('GEEKHUB'))
    guild_ids=[int(os.getenv('TESTGUILD'))]
)
async def rate(ctx: discord.ApplicationContext, restaurant: discord.Option(str, "Name of the restaurant")):
    await ctx.respond('{0}'.format(restaurant))
    await ctx.send('Service/Atmosphäre ----- 0:star: ----- 0 Votes', view=ButtonView())
    await ctx.send('Essen ----- 0:star: ----- 0 Votes', view=ButtonView())
    await ctx.send('Preis/Leistung ----- 0:star: ----- 0 Votes', view=ButtonView())


client.run(os.getenv('TOKEN_GUIDE'))
