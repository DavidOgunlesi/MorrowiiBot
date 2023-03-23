import discord
import responses
import brain
from dotenv import load_dotenv, dotenv_values
import feature.csteams as csteams
import wavelink
from wavelink import TrackEventPayload
import random

APPLICATION_ID = 1087034256838111383

load_dotenv()
config = dotenv_values(".env")

async def send_message(message, user_message, is_private):
    try:
        response = await responses.handle_response(message, user_message)
        if is_private:
            await message.author.send(response) 
        else: 
            await message.channel.send(response)

    except Exception as e:
        print(e)

async def send_ai_message(message, user_message, conversation):
    try:
        response = brain.send_morrowii_message(user_message, conversation)
        await message.channel.send(response)
    except Exception as e:
        print(e)

def run_discord_bot():
    TOKEN = config['DISCORD_TOKEN']
    bot = discord.Bot(intents=discord.Intents.all())#commands.Bot(intents=discord.Intents.all(), command_prefix='/')
    #conversation = brain.init_morrowii_brain()

    # async def on_event_hook(event):
    #     if isinstance(event, (wavelink.TrackEnd, wavelink.TrackException)):
    #         play_next_song.set()
    

    @bot.event
    async def on_ready() -> None:
        print(f'{bot.user} | {bot.user.id} has connected to Discord!')
        node: wavelink.Node = wavelink.Node(uri='http://localhost:8080', password='youshallnotpass')
        await wavelink.NodePool.connect(client=bot, nodes=[node])
        print('Wavelink has been setup.')

    @bot.command(description="Sends the bot's latency.") # this decorator makes a slash command
    async def ping(ctx): # a slash command will be created with the name "ping"
        await ctx.respond(f"Pong! Latency is {bot.latency}")

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

    music = discord.SlashCommandGroup("music", "Music commands")

    @bot.event
    async def on_wavelink_track_end(trackEventPayload):
        player: wavelink.Player = trackEventPayload.player
        track = await player.queue.get_wait()
        await player.play(track)
        await player.channel.send(f'> **Now playing: {track.title}**')

    @music.command(name='join', description='Tells the bot to join the voice channel')
    async def m_join(ctx):
        if not ctx.author.voice:
            await ctx.respond("> {} is not connected to a voice channel".format(ctx.author.name))
            return
        else:
            channel = ctx.author.voice.channel
        await channel.connect()
        await ctx.respond("> Connected to the voice channel")

    @music.command(name='leave', description='To make the bot leave the voice channel')
    async def m_leave(ctx):
        voice_client = ctx.guild.voice_client
        if voice_client is not None:
            await voice_client.disconnect()
            await ctx.respond("> The bot has left the voice channel")
        else:
            await ctx.respond("> The bot is not connected to a voice channel.")


    @music.command(name='queueplay', description='Play a song')
    async def m_queueplay(ctx, *, search: str):
        if not ctx.author.voice:
            await ctx.respond("> {} is not connected to a voice channel".format(ctx.author.name))
            return
        
        if not ctx.voice_client:
            player: wavelink.Player = await ctx.author.voice.channel.connect(cls=wavelink.Player)
        else:
            player: wavelink.Player = ctx.voice_client

        track = await wavelink.YouTubeTrack.search(search, return_first=True)
        # Add the first track to the queue
        await player.queue.put_wait(track)
        
        if not player.is_playing():
            print("Playingasdasd")
            player.queue.get()
            await player.play(track, False)
            await ctx.respond(f'> **Now playing: {track.title}**')
        else:
            await ctx.respond(f'> **Added to queue: {track.title}**')

    @music.command(name='playnext', description='Play a song next in the queue')
    async def m_playnext(ctx, *, search: str):
        if not ctx.author.voice:
            await ctx.respond("> {} is not connected to a voice channel".format(ctx.author.name))
            return
        
        if not ctx.voice_client:
            player: wavelink.Player = await ctx.author.voice.channel.connect(cls=wavelink.Player)
        else:
            player: wavelink.Player = ctx.voice_client

        track = await wavelink.YouTubeTrack.search(search, return_first=True)

        if len (player.queue) > 0:
            # Add the first track to the queue
            player.queue.put_at_index(0, track)
        else:
            await player.queue.put_wait(track)

        await ctx.respond(f'> **Added to play next in queue: {track.title}**')

    @music.command(name='forceplay', description='Override current playlist and force play a song')
    async def m_forceplay(ctx, *, search: str):
        await m_playnext(ctx, search=search)
        await m_skip(ctx)


    @music.command(name='playlist', description='List the queue')
    async def m_playlist(ctx):
        if not ctx.voice_client:
            player: wavelink.Player = await ctx.author.voice.channel.connect(cls=wavelink.Player)
        else:
            player: wavelink.Player = ctx.voice_client
        # Get the list of tracks in the queue
        queue = player.queue

        # Send a message with the list of tracks in the queue
        if not queue:
            await ctx.respond('> The queue is empty.')
        else:
            track_list = '\n'.join([f'> ***{i+1}. {track.title} {"[Up Next]" if i == 0  else ""}***' for i, track in enumerate(queue)])
            await ctx.respond(f'> Queue:\n{track_list}')

    @music.command(name='skip', description='Skip a song')
    async def m_skip(ctx):
        if not ctx.author.voice:
            await ctx.respond("> {} is not connected to a voice channel".format(ctx.author.name))
            return
         
        # Get the player for the current guild
        if not ctx.voice_client:
            player: wavelink.Player = await ctx.author.voice.channel.connect(cls=wavelink.Player)
        else:
            player: wavelink.Player = ctx.voice_client

        voice_client = ctx.guild.voice_client
        if voice_client.is_playing():
            # Skip the current track and play the next one in the queue
            await player.stop()
            if player.queue:
                await ctx.respond("> Skipped the song for you!")
            else:
                await ctx.respond("> Skipped the song for you! The queue is now empty.")
        else:
            await ctx.respond("> The bot is not playing anything at the moment.")

    @music.command(name='clear', description='Clear the queue')
    async def clear(ctx):
        if not ctx.author.voice:
            await ctx.respond("> {} is not connected to a voice channel".format(ctx.author.name))
            return
        
        if not ctx.voice_client:
            vc: wavelink.Player = await ctx.author.voice.channel.connect(cls=wavelink.Player)
        else:
            vc: wavelink.Player = ctx.voice_client

        # Clear the queue
        vc.queue.reset()

        # Send a message confirming that the queue has been cleared
        await ctx.respond('> Queue cleared.')

    @music.command(name='shuffle', description='Shuffle the queue')
    async def shuffle(ctx):
        if not ctx.author.voice:
            await ctx.respond("> {} is not connected to a voice channel".format(ctx.author.name))
            return
        
        if not ctx.voice_client:
            player: wavelink.Player = await ctx.author.voice.channel.connect(cls=wavelink.Player)
        else:
            player: wavelink.Player = ctx.voice_client
            
        queuetemp = []
        for i in range(0, len(player.queue)):
            queuetemp.append(player.queue.get())
        # Shuffle the queue
        random.shuffle(queuetemp)

        # Clear the queue
        player.queue.clear()

        # Add the shuffled tracks back to the queue
        for track in queuetemp:
            player.queue.put(track)
        
        # Send a message confirming that the queue has been shuffled
        await ctx.respond('> Queue shuffled.')

    @music.command(name='pause', description='Pauses a song')
    async def m_pause(ctx):
        voice_client = ctx.guild.voice_client
        if voice_client.is_playing():
            await voice_client.pause()
            await ctx.respond("> Paused the song for you!")
        else:
            await ctx.respond("> The bot is not playing anything at the moment.")
        
    @music.command(name='resume', description='Resumes a song')
    async def m_resume(ctx):
        voice_client = ctx.guild.voice_client
        if voice_client.is_paused():
            await voice_client.resume()
            await ctx.respond("> Resumed the song for you!")
        else:
            await ctx.respond("> The bot was not playing anything before this. Use `/music play` command")

    @music.command(name='stop', description='Stops all songs')
    async def m_stop(ctx):
        voice_client = ctx.guild.voice_client
        if voice_client.is_playing():
            # Get the player for the current guild
            if not ctx.voice_client:
                player: wavelink.Player = await ctx.author.voice.channel.connect(cls=wavelink.Player)
            else:
                player: wavelink.Player = ctx.voice_client
            player.queue.reset()

            await voice_client.stop()
            await ctx.respond("> Music stopped!")
        else:
            await ctx.respond("> The bot is not playing anything at the moment.")

    @music.command()
    async def volume(ctx, volume: int):
        """Changes the player's volume"""
        if not 0 < volume < 201:
            return await ctx.respond("> Volume must be between 0 and 200.")
        if ctx.voice_client is None:
            return await ctx.respond("? Not connected to a voice channel.")
        vc: wavelink.Player = ctx.voice_client
        await vc.set_volume(volume)
        await ctx.respond(f"> Changed volume to ***{volume}%***")

    bot.add_application_command(music)

    # @bot.event
    # async def on_ready():
    #     print(f"> {bot.user} has connected to Discord!")

    # @client.event
    # async def on_message(message):
    #     # stops execution if the message is from the bot itself
    #     if message.author == client.user:
    #         return
        
    #     username = str(message.author)
    #     user_message = str(message.content)
    #     channel = str(message.channel)

    #     print(f"{username} sent a message in {channel}: {user_message}")

    #     if len(user_message) == 0:
    #         return
        
    #     invoke_string = f"<@{APPLICATION_ID}>"

    #     if not invoke_string in user_message:
    #         return
    #     print(user_message.replace(invoke_string, ''))
    #     user_message = user_message.replace(invoke_string, '')
    #     if len(user_message) > 0 and user_message.strip()[0] ==" ~":
    #         await send_message(message, user_message.strip(), True)
    #     if len(user_message) > 0 and user_message.strip()[0] =="\\":
    #         await send_message(message, user_message.strip(), False)
    #     # elif user_message == " ":
    #     #     await send_ai_message(message, "I'm shy...", conversation)
    #     # elif len(user_message) > 0:
    #     #     await send_ai_message(message, user_message, conversation)
    #     # else:
    #     #     await send_ai_message(message, "hey!", conversation)

    bot.run(TOKEN)
    #bot.run(TOKEN)