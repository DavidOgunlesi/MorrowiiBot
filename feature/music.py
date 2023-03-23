import wavelink
import random
import discord
import settings

str_not_nowplaying = '> **Now playing: {}**'
str_added_to_queue = '> **Added to queue: {}**'
str_added_to_queue_next = '> **Added to play next in queue: {}**'
str_member_not_connected = "> You are not connected to a voice channel"
str_self_not_connected = "> I am not connected to a voice channel :("
str_not_connected_to_your_channel = "> I am not connected to your voice channel :("
str_now_connected = "> Connected to the voice channel"
str_left_channel = "> I left the voice channel :)"
str_member_no_control = "> You don't have control of the music"
str_empty_queue = "> The queue is empty"
str_queue = '> Queue:\n{}'
str_queue_format = '> ***{}. {} {}***'
str_skipped_song = "> Skipped the song for you!"
str_paused_song = "> Paused the song for you!"
str_resumed_song = "> Resumed the song for you!"
str_skipped_song_queue_empty = "> Skipped the song for you! The queue is now empty."
str_nothing_playing = "> The bot is not playing anything at the moment."
str_queue_cleared = "> Cleared the queue for you!"
str_queue_shuffled = "> Shuffled the queue for you!"
str_resume_failed = "> The bot was not playing anything before this. Use `/music play` command"
str_music_stopped = "> Stopped the music for you!"
str_music_volume_correction = "> The volume must be between 0 and 200"
str_music_volume_changed = "> Changed volume to ***{}%***"
str_member_alone_in_voice_channel = "> You are the only one in the voice channel. You already have control of the bot."
str_vote = "> <@{}> wants to take control of the bot. {} votes needed. Type `/vote` to vote."
str_has_control = "> <@{}> now has control of the bot."
str_no_vote_in_progress = "> There is no vote in progress."
str_relinquish_control = "> <@{}> relinquished control of the bot. No one has control of the bot now."

control = {} # Dict[guild, member]
votes = {} # Dict[guild, int]

def has_control(ctx):
    if ctx.guild not in control:
        return True
    if ctx.author.id == control[ctx.guild]:
        return True
    else:
        return False

async def on_song_end(trackEventPayload):
    """
    Play the next song in the queue
    """
    player: wavelink.Player = trackEventPayload.player
    track = await player.queue.get_wait()
    await player.play(track)
    channel = discord.utils.get(player.guild.channels, name=settings.BOTCHANNEL)
    if channel is None:
        await player.channel.send(settings.STR_NOBOTCHANNEL)
        await player.channel.send(str_not_nowplaying.format(track.title))
    else:
        await channel.send(str_not_nowplaying.format(track.title))

async def join(ctx):
    """
    Join the voice channel
    """
    if not ctx.author.voice:
        return str_member_not_connected

    if not ctx.voice_client:
        await ctx.author.voice.channel.connect(cls=wavelink.Player)

    return str_now_connected

async def leave(ctx):
    """
    Leave the voice channel
    """
    voice_client = ctx.guild.voice_client
    if voice_client is not None:
        await voice_client.disconnect()
        return str_left_channel
    else:
        return str_self_not_connected
    
async def queueplay(ctx, search: str):
    """
    Add a song to the queue
    """
    if not ctx.author.voice:
        return str_member_not_connected
    
    if has_control(ctx) == False:
        return str_member_no_control
    
    if not ctx.voice_client:
        player: wavelink.Player = await ctx.author.voice.channel.connect(cls=wavelink.Player)
    else:
        player: wavelink.Player = ctx.voice_client

    track = await wavelink.YouTubeTrack.search(search, return_first=True)
    # Add the first track to the queue
    await player.queue.put_wait(track)
    
    if not player.is_playing():
        player.queue.get()
        await player.play(track, False)
        return str_not_nowplaying.format(track.title)
    else:
        return str_added_to_queue.format(track.title)
    
async def playnext(ctx, search: str):
    """
    Play a song next in the queue
    """
    if not ctx.author.voice:
        return str_member_not_connected
    
    if has_control(ctx) == False:
        return str_member_no_control

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

    return str_added_to_queue_next.format(track.title)

async def playlist(ctx):
    """
    Show the list of tracks in the queue
    """
    if not ctx.voice_client:
        player: wavelink.Player = await ctx.author.voice.channel.connect(cls=wavelink.Player)
    else:
        player: wavelink.Player = ctx.voice_client
    # Get the list of tracks in the queue
    queue = player.queue

    # Send a message with the list of tracks in the queue
    if not queue:
        return str_empty_queue
    else:
        track_list = '\n'.join([str_queue_format.format(1, track.title, "[Up Next]" if i == 0  else "") for i, track in enumerate(queue)])
        return str_queue.format(track_list)
    
async def skip(ctx):
    if not ctx.author.voice:
        return str_member_not_connected
        
    # Get the player for the current guild
    if not ctx.voice_client:
        player: wavelink.Player = await ctx.author.voice.channel.connect(cls=wavelink.Player)
    else:
        player: wavelink.Player = ctx.voice_client

    if has_control(ctx) == False:
        return str_member_no_control
    
    voice_client = ctx.guild.voice_client
    if voice_client.is_playing():
        # Skip the current track and play the next one in the queue
        await player.stop()
        if player.queue:
            return str_skipped_song
        else:
            return str_skipped_song_queue_empty
    else:
        return str_nothing_playing
    
async def clear(ctx):
    if not ctx.author.voice:
        return str_member_not_connected
    
    if has_control(ctx) == False:
        return str_member_no_control

    if not ctx.voice_client:
        vc: wavelink.Player = await ctx.author.voice.channel.connect(cls=wavelink.Player)
    else:
        vc: wavelink.Player = ctx.voice_client
    
    # Clear the queue
    vc.queue.reset()

    # Send a message confirming that the queue has been cleared
    return str_queue_cleared

async def shuffle(ctx):
    if not ctx.author.voice:
        return str_member_not_connected
    
    if has_control(ctx) == False:
        return str_member_no_control

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
    return str_queue_shuffled

async def pause(ctx):
    if has_control(ctx) == False:
        return str_member_no_control
    
    voice_client = ctx.guild.voice_client

    if voice_client.is_playing():
        await voice_client.pause()
        return str_paused_song
    else:
        return str_nothing_playing
    
async def resume(ctx):
    if has_control(ctx) == False:
        return str_member_no_control

    voice_client = ctx.guild.voice_client
    if voice_client.is_paused():
        await voice_client.resume()
        return str_resumed_song
    else:
        return str_resume_failed

async def stop(ctx):
    if has_control(ctx) == False:
        return str_member_no_control
    
    voice_client = ctx.guild.voice_client
    if voice_client.is_playing():
        # Get the player for the current guild
        if not ctx.voice_client:
            player: wavelink.Player = await ctx.author.voice.channel.connect(cls=wavelink.Player)
        else:
            player: wavelink.Player = ctx.voice_client
        player.queue.reset()

        await voice_client.stop()
        return str_music_stopped
    else:
        return str_nothing_playing

async def volume(ctx, volume: int):
    """Changes the player's volume"""

    if has_control(ctx) == False:
        return str_member_no_control
    
    if not 0 < volume < 201:
        return str_music_volume_correction
    if ctx.voice_client is None:
        return str_self_not_connected
    vc: wavelink.Player = ctx.voice_client
    await vc.set_volume(volume)
    return str_music_volume_changed.format(volume)

async def takecontrol(ctx):
    if not ctx.author.voice:
        return str_member_not_connected

    if ctx.voice_client is None:
        return str_self_not_connected
    
    # check if bot is in your voice channel
    if ctx.author.voice.channel != ctx.voice_client.channel:
        return str_not_connected_to_your_channel

    votes_needed = len(ctx.author.voice.channel.members)-2
    if votes_needed == 0:
        return str_member_alone_in_voice_channel
    
    votes[ctx.author.guild.id] = 0
    return str_vote.format(ctx.author.id, votes_needed)

async def givecontrol(ctx, member: discord.Member):
    if not ctx.author.voice:
        return str_member_not_connected

    if ctx.voice_client is None:
        return str_self_not_connected

    # check if bot is in your voice channel
    if ctx.author.voice.channel != ctx.voice_client.channel:
        return str_not_connected_to_your_channel

    control[ctx.author.guild.id] = member.id
    return str_has_control.format(member.id)

async def vote(ctx):
    if not ctx.author.voice:
        return str_member_not_connected
    
    # check if bot is your voice channel
    if ctx.voice_client is None:
        return str_self_not_connected
    
    # check if bot is in your voice channel
    if ctx.author.voice.channel != ctx.voice_client.channel:
        return str_not_connected_to_your_channel
    
    if ctx.author.guild.id not in votes:
        return str_no_vote_in_progress
    
    votes[ctx.author.guild.id] += 1

    votes_needed = len(ctx.author.voice.channel.members)-1

    if votes[ctx.author.guild.id] >= votes_needed:
        del votes[ctx.author.guild.id]
        control[ctx.author.guild.id] = ctx.author.id
        return str_has_control.format(ctx.author.id)
    
async def relinquish_control(member, before):
    if member.guild.id in control and control[member.guild.id] == member.id:
        del control[member.guild.id]
        return str_relinquish_control.format(member.id)
