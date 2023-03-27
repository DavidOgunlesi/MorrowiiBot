import discord
import feature.egirl as egirl
from dotenv import load_dotenv, dotenv_values
import wavelink
import settings
import feature.csteams as csteams
import feature.music as music
import feature.egirl as egirl
import feature.chessgame as chessgame

APPLICATION_ID = 1087034256838111383

load_dotenv()
config = dotenv_values(".env")

# async def send_message(message, user_message, is_private):
#     try:
#         response = await responses.handle_response(message, user_message)
#         if is_private:
#             await message.author.send(response) 
#         else: 
#             await message.channel.send(response)

#     except Exception as e:
#         print(e)


def run_discord_bot(do_music: bool = True, do_egirl: bool = True):
    TOKEN = config['DISCORD_TOKEN']
    bot = discord.Bot(intents=discord.Intents.all())
    
    if do_egirl:
        conversation = egirl.init_morrowii_brain()

    @bot.event
    async def on_ready() -> None:
        print(f'{bot.user} | {bot.user.id} has connected to Discord!')
        if do_music:
            node: wavelink.Node = wavelink.Node(uri='http://localhost:3000', password='youshallnotpass')
            await wavelink.NodePool.connect(client=bot, nodes=[node])
            print('Wavelink has been setup.')
        else:
            print('Music has been disabled. Skipping wavelink setup. Media player will not be available.')

    @bot.command(name="ping",description="Sends the bot's latency.") # this decorator makes a slash command
    async def ping(ctx): # a slash command will be created with the name "ping"
        channel = discord.utils.get(ctx.guild.channels, name=settings.BOTCHANNEL)
        if channel is None:
            await ctx.respond("I don't have a home yet! Please use `/houseme` to create a channel for me.")
        await ctx.respond(f"Pong! Latency is {bot.latency}")

    @bot.command(name="houseme", description="Create channel for bot") # this decorator makes a slash command
    async def houseme(ctx): # a slash command will be created with the name "ping"
        channel = discord.utils.get(ctx.guild.channels, name=settings.BOTCHANNEL)
        if channel is None:
            channel = await ctx.guild.create_text_channel(settings.BOTCHANNEL)
        await channel.send("I finally have a home!")
        await ctx.respond(f"> Created channel for Morrowii at {channel.mention}")

    """ 
    ---------------
    COUNTERSTRIKE COMMANDS 
    ---------------
    """ 

    cs_comm = discord.SlashCommandGroup("cs", "CS:GO commands")

    # newteam [num] or join 
    @bot.command(description="Creates a new team, or joins an existing one.")
    async def csnow(ctx):
        res = await csteams.try_create_team(ctx)
        await ctx.respond(res)

    @cs_comm.command(description="Creates a new team")
    async def newteam(ctx, limit: discord.Option(int)):
        res = await csteams.try_create_newteam(ctx, limit)
        await ctx.respond(res)

    @cs_comm.command(description="Join a team ")
    async def join(ctx, member: discord.Option(discord.Member, autocomplete=discord.utils.basic_autocomplete(csteams.get_team_choices))):
        res = await csteams.try_join_team(ctx, member)
        await ctx.respond(res)

    @cs_comm.command(description="Leave a team")
    async def leave(ctx):
        res = await csteams.try_leave_team(ctx)
        await ctx.respond(res)

    @cs_comm.command(description="Disband a team")
    async def disband(ctx):
        res = await csteams.try_disband_team(ctx)
        await ctx.respond(res)

    bot.add_application_command(cs_comm)


    """ 
    ---------------
    MUSIC COMMANDS 
    ---------------
    """ 

    music_comm = discord.SlashCommandGroup("music", "Music commands")

    @bot.event
    async def on_wavelink_track_end(trackEventPayload):
        await music.on_song_end(trackEventPayload)

    @music_comm.command(name='join', description='Tells the bot to join the voice channel')
    async def m_join(ctx):
        res = await music.join(ctx)
        await ctx.respond(res)

    @music_comm.command(name='leave', description='To make the bot leave the voice channel')
    async def m_leave(ctx):
        res = await music.leave(ctx)
        await ctx.respond(res)


    @music_comm.command(name='queueplay', description='Play a song')
    async def m_queueplay(ctx, *, search: str):
        res = await music.queueplay(ctx, search)
        await ctx.respond(res)

    @music_comm.command(name='playnext', description='Play a song next in the queue')
    async def m_playnext(ctx, *, search: str):
        res = await music.playnext(ctx, search)
        await ctx.respond(res)

    @music_comm.command(name='forceplay', description='Override current playlist and force play a song')
    async def m_forceplay(ctx, *, search: str):
        await m_playnext(ctx, search=search)
        await m_skip(ctx)


    @music_comm.command(name='playlist', description='List the queue')
    async def m_playlist(ctx):
        res = await music.playlist(ctx)
        await ctx.respond(res)

    @music_comm.command(name='skip', description='Skip a song')
    async def m_skip(ctx):
        res = await music.skip(ctx)
        await ctx.respond(res)

    @music_comm.command(name='clear', description='Clear the queue')
    async def m_clear(ctx):
        res = await music.clear(ctx)
        await ctx.respond(res)

    @music_comm.command(name='shuffle', description='Shuffle the queue')
    async def m_shuffle(ctx):
        res = await music.shuffle(ctx)
        await ctx.respond(res)

    @music_comm.command(name='pause', description='Pauses a song')
    async def m_pause(ctx):
        res = await music.pause(ctx)
        await ctx.respond(res)
        
    @music_comm.command(name='resume', description='Resumes a song')
    async def m_resume(ctx):
        res = await music.resume(ctx)
        await ctx.respond(res)

    @music_comm.command(name='stop', description='Stops all songs')
    async def m_stop(ctx):
        res = await music.stop(ctx)
        await ctx.respond(res)

    @music_comm.command(name= 'volume', description = 'Change the volume of the bot (0-200)')
    async def m_volume(ctx, volume: int):
        res = await music.volume(ctx, volume)
        await ctx.respond(res)

    @music_comm.command(name = 'takecontrol', description = 'Take control of the bot')
    async def m_takecontrol(ctx):
        res = await music.takecontrol(ctx)
        await ctx.respond(res)

    @music_comm.command(name = 'givecontrol', description = 'Give control of the bot')
    async def m_givecontrol(ctx):
        res = await music.givecontrol(ctx)
        await ctx.respond(res)

    @music_comm.command(name = 'vote', description = 'Vote to give control of the bot')
    async def m_vote(ctx):
        res = await music.vote(ctx)
        await ctx.respond(res)

    @bot.event
    async def on_voice_state_update(member, before, after):
        if member == bot.user:
            return
        if after.channel == None:
            res = await music.relinquish_control(member, before)
            channel = discord.utils.get(member.guild.channels, name=settings.BOTCHANNEL)
            if channel is None:
                await before.channel.send("I don't have a home yet! Please use `/houseme` to create a channel for me.")
                await before.channel.send(res)
            else:
                await channel.send(res)

    @music_comm.command(name = 'ban', description = 'Ban a song')
    async def m_ban(ctx, *, search: str):
        if not ctx.author.top_role.permissions.administrator:
            await ctx.respond("You can't ban songs unless you are a admin!")
            return
        res = await music.ban(ctx, search)
        await ctx.respond(res)

    @music_comm.command(name = 'unban', description = 'Unban a song')
    async def m_unban(ctx, *, search: str):
        if not ctx.author.top_role.permissions.administrator:
            await ctx.respond("You can't ban songs unless you are a admin!")
            return
        res = await music.unban(ctx, search)
        await ctx.respond(res)

    @music_comm.command(name = 'listbans', description = 'List banned songs')
    async def m_listbans(ctx):
        res = await music.listbans(ctx)
        await ctx.respond(res)

    bot.add_application_command(music_comm)

    """ 
    ---------------
    CHESS COMMANDS 
    ---------------
    """ 

    chess_comm = discord.SlashCommandGroup("chess", "Chess commands")

    @chess_comm.command(name = 'test', description = 'Play Morrowii at Chess!')
    async def chess_test(ctx):
        res = await chessgame.test(ctx)
        await ctx.respond(res)

    @chess_comm.command(name = 'play', description = 'Challenge someone at Chess!')
    async def chess_play(ctx, member: discord.Option(discord.Member)):
        res = await chessgame.start_game(ctx, member)
        await ctx.respond(res)

    @chess_comm.command(name = 'move', description = 'Make a chess move!') # , autocomplete= discord.utils.basic_autocomplete(chessgame.list_chess_positions()
    async def chess_move(ctx, movefrom: discord.Option(str), moveto: discord.Option(str)):
        movefrom = movefrom.lower()
        moveto = moveto.lower()
        await chessgame.move(ctx, movefrom, moveto)

    @chess_comm.command(name = 'resign', description = 'End a game!')
    async def chess_resign(ctx):
        res = await chessgame.resign(ctx)
        await ctx.respond(res)

    @chess_comm.command(name = 'draw', description = 'Offer a draw!')
    async def chess_draw(ctx):
        res = await chessgame.draw(ctx)
        await ctx.respond(res)

    bot.add_application_command(chess_comm)

    

    @bot.event
    async def on_message(ctx):
        # stops execution if the message is from the bot itself
        if ctx.author == bot.user:
            return
        
        username = str(ctx.author)
        user_message = str(ctx.content)
        channel = str(ctx.channel)

        print(f"{username} sent a message in {channel}: {user_message}")

        if len(user_message) == 0:
            return
        
        invoke_string = f"<@{APPLICATION_ID}>"

        if not invoke_string in user_message:
            return
        print(user_message.replace(invoke_string, ''))
        user_message = user_message.replace(invoke_string, '')

        if not do_egirl:
            return
        
        if user_message == " ":
            await egirl.send_morrowii_message(ctx, "I'm shy...", conversation)
        if len(user_message) > 0:
            await egirl.send_morrowii_message(ctx, user_message, conversation)
        else:
            await egirl.send_morrowii_message(ctx, "hey!", conversation)

    bot.run(TOKEN)
    #bot.run(TOKEN)