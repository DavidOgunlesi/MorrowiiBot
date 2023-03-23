import discord
from feature.music import YTDLSource as player

filename = player.from_url("https://www.youtube.com/watch?v=4JkIs37a2JE", loop=None, stream=True)
discord.FFmpegPCMAudio(executable="dll/ffmpeg.exe", source=filename)