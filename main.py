import discord
from discord import app_commands, Interaction
from string import ascii_lowercase
from random import randint
from discord.ui import Button, Select, TextInput, View, Modal
from time import sleep

intents = discord.Intents.all()
intents.members = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
AFK_Members = {}


@client.event
async def on_message(message: discord.Message):
    global AFK_Members
    mentions = message.mentions
    if AFK_Members is not None:
        if len(mentions) != 0:
            for mention in mentions:
                if mention.id in AFK_Members.keys():
                    await message.channel.send(f'{mention.name} está AFK. Motivo: {AFK_Members[mention.id]}')
        else:
            if message.author.id in AFK_Members.keys():
                AFK_Members.pop(message.author.id)
                await message.channel.send(f'Perfecto **{message.author.name}**, ya no estas AFK.')


@tree.command(name='choice', description='Test', guild=discord.Object(
    id=998108250153160704))
async def select_test(interaction: Interaction):
    members = [member for member in interaction.guild.members if not member.bot]
    print(members)
    select = None
    for member in members:
        if not member.bot:
            select = Select(options=[discord.SelectOption(label=f'{member.name} #{member.discriminator}')])

    async def my_callback(interaction: Interaction):
        await interaction.response.send_message(f'Elegiste: {select.values[0]}')

    select.callback = my_callback
    view = View()
    view.add_item(select)

    await interaction.response.send_message('Select member:', view=view)
    select.disabled = True


@tree.command(name='input',
              description='InputText Test',
              guild=discord.Object(id=998108250153160704))
async def input_text_test(interaction: Interaction):
    text_input = TextInput(label='Hola', required=True)

    async def my_callback(interaction: Interaction):
        await interaction.response.send_message(f'Elegiste: {str(text_input)}')

    text_input.callback = my_callback
    view = View()
    view.add_item(text_input)
    await interaction.response.send_message('Choose:', view=view)


@tree.command(name='buttons',
              description='Button Test',
              guild=discord.Object(id=998108250153160704))
async def ButtonTest(interaction: Interaction):
    btn = Button(label='Aceptar', style=discord.ButtonStyle.green, emoji='🔥')
    btn2 = Button(label='Rechazar', style=discord.ButtonStyle.red, emoji='🔥')

    async def my_callback(interaction: Interaction):
        await interaction.response.defer()
        await interaction.delete_original_response()
        for member in interaction.guild.members:
            if not member.bot:
                await interaction.followup.send(f'{member.name} #{member.discriminator}')

    btn.callback = my_callback
    view = View()
    view.add_item(btn)
    await interaction.response.send_message('Choose:', view=view)


@tree.command(name='modal',
              description='Popup a modal',
              guild=discord.Object(id=998108250153160704))
async def modal(interaction: Interaction):
    class auth_modal(Modal, title='Auth Modal'):
        username = TextInput(label='Type your username',
                             placeholder='Ej.: Terma',
                             style=discord.TextStyle.short,
                             required=True,
                             min_length=2)
        password = TextInput(label='Type your password',
                             placeholder='Ej.: 123',
                             style=discord.TextStyle.short,
                             required=True,
                             min_length=2)

        async def on_submit(self, interaction: Interaction):
            embed = discord.Embed(title='Information of Auth', color=discord.Color.dark_purple())
            embed.add_field(name='Username', value=self.username, inline=False)
            embed.add_field(name='Username', value=self.password, inline=False)
            await interaction.response.send_message(embed=embed)

        async def on_error(self, interaction: Interaction, error: Exception, /):
            await interaction.response.send_message(error=error)
            print(error)

    await interaction.response.send_modal(auth_modal())


@tree.command(name='gen',
              description='Generates a random key (only numbers) or serial (numbers, letters and special characters)',
              guild=discord.Object(id=998108250153160704))
@app_commands.choices(choice=[
    discord.app_commands.Choice(name='Serial', value=0),
    discord.app_commands.Choice(name='Serial with special chars ($, @, &, %...)', value=1),
    discord.app_commands.Choice(name='Key', value=2)
])
async def Random_Key(interaction: Interaction, length: int, choice: app_commands.Choice[int]):
    def Gen_key(key_length: int, method: int):
        key, serial = '', ''
        symbols = {27: '~', 28: ':', 29: "'", 30: '+', 31: '[', 32: '\\', 33: '@', 34: '^', 35: '{', 36: '%',
                   37: '(', 38: '-', 39: '"', 40: '*', 41: '|', 42: ',', 43: '&', 44: '<', 45: '`', 46: '}',
                   47: '.', 48: '_', 49: '=', 50: ']', 51: '!', 52: '>', 53: ';', 54: '?', 55: '#', 56: '$',
                   57: ')', 58: '/'}
        alphabet = dict(enumerate(ascii_lowercase, 1))

        if method == 2:
            for i in range(key_length):
                key += str(randint(0, 9))
            return key
        elif method == 0:
            for i in range(key_length):
                r = randint(0, 2)
                if r == 0:
                    serial += str(alphabet[randint(1, 26)])
                elif r == 1:
                    serial += str(alphabet[randint(1, 26)].upper())
                elif r == 2:
                    serial += str(randint(0, 9))
            return serial
        elif method == 1:
            alphabet.update(symbols)
            for i in range(key_length):
                r = randint(0, 2)
                if r == 0:
                    serial += str(alphabet[randint(1, 58)])
                elif r == 1:
                    serial += str(alphabet[randint(1, 58)].upper())
                elif r == 2:
                    serial += str(randint(0, 9))
            return serial
        else:
            return 'Invalid method.'

    gen = Gen_key(int(length), choice.value)
    if len(gen) > 40:
        await interaction.response.send_message('La generación es muy larga. Maximo 40')
        raise Exception('Key muy larga.')
    else:

        embed = discord.Embed(color=discord.Color.red())
        embed.add_field(name='Key', value=gen)
        print(f'Generated key: {gen}')
        await interaction.response.send_message(embed=embed)


@tree.command(name='afk',
              description='Establece el modo AFK: Cuando te mencionen les avisare que estás AFK.',
              guild=discord.Object(id=998108250153160704))
async def set_afk(interaction: Interaction, reason: str):
    global AFK_Members
    member_id = interaction.user.id
    if reason is None:
        reason = 'No se ha dado un motivo.'
    AFK_Members[member_id] = reason
    await interaction.response.send_message('Listo! Si vuelves a hablar se te irá el AFK')


@client.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=998108250153160704))
    print("Ready!")


client.run('MTAzMDI4OTIwOTE1Nzc2NzIxOQ.GzO_Ak.ELZ_mQIPFBFyue-yXjnw8996X_n2A8LOFjd0Vc')
