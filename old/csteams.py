from __future__ import annotations
from typing import List, Dict, Any
import discord
import random
import copy

tags = [
"Headshot Hero",
"AWP Master",
"Pistol Prodigy",
"Bomb Defuser",
"Rusher Extraordinaire",
"Clutch King",
"Knife Ninja",
"Grenade God",
"Spray and Pray",
"Flawless Victory",
"One Tap Wonder",
"Smoke Expert",
"Flash Master",
"Mind Game Master",
"Spray Control Savant",
"Eco Warrior",
"Aimbot Ace",
"Tactical Titan",
"Cover Fire Captain",
"Sniper Specialist",
"Piston Pumper",
"Wallbang Wizard",
"Heist Hero",
"C4 Destroyer",
"Counter-Terrorist Crusader",
"Terrorist Termination",
"Bulletproof Beast",
"Spawn Slayer",
"Nade Nailer",
"Recoil Reducer",
"Wall of Bullets",
"Target Tracker",
"Pistol Pro",
"Clutch Commander",
"Stealth Striker",
"Flanker",
"Trigger Happy",
"Bomb Planner",
"Flash Freak",
"Tactician",
"Mindbender",
"Grenade Guru",
"Sharpshooter",
"Assault Ace",
"Fragger Fiend",
"Pointman",
"Spray and Pray Slayer",
"Cover Master",
"Demolition Demon",
"Hostage Hero",
"Headshot Hunter",
"Blade Master",
"Smoke Screen Commander",
"Flashbang Force",
"Mind Games Guru",
"Recoil Rebel",
"Kill Confirmer",
"Wallbang Warrior",
"Terrorist Takedown",
"Counter-Terrorism Captain",
"Stealth Sniper",
"AWP Assassin",
"Tactical Tactician",
"Pistol Prodigy",
"Firepower Freak",
"Bomb Defusal Expert",
"Grenade Genius",
"Spray Control Specialist",
"Eco Executive",
"Flawless Finisher",
"One Tap Terminator",
"Smoke Signal Sergeant",
"Flashbang Fighter",
"Mind Game Maven",
"Cover Fire Chief",
"Sniper Savior",
"Piston Punisher",
"Wallbang Wonder",
"Heist Hunter",
"C4 Connoisseur",
"Counter-Terrorist Champion",
"Terrorist Toppler",
"Bulletproof Bruiser",
"Spawn Suppressor",
"Nade Ninja",
"Recoil Ruler",
"Target Terminator",
"Pistol Perfectionist",
"Clutch Conqueror",
"Stealth Slayer",
"Flanker Fiend",
"Trigger Triumph",
"Bomb Builder",
"Flashbang Fiend",
"Tactician Titan",
"Mind Manipulator",
"Grenade Great",
"Sharpshooter Supreme",
"Assault Artist",
"Fragger Frontline",
"Fucking Idiot",
"The Useless"
]

teams = {}
memberInTeamSet = {}
class Team:
    def __init__(self, guild, name: str, captain: str, maxPlayers = 5):
        self.name = name
        self.captain = captain
        self.players = {}
        self.max_players = maxPlayers
        self.guild = guild
        self.activeChannel = None

    async def add_player(self, channel, player):
        # if full
        if len(self.players) == self.max_players:
            return
        
        memberInTeamSet[player.id] = self
        self.players[str(player)] = player

        if len(self.players) == self.max_players:
            at_string = ""
            for player in self.players.values():
                at_string += f"\n ***{random.choice(tags)},*** <@{player.id}> , "
            
            await channel.send(f"> All spaces filled!.")
            await channel.send(f"> CSGOmers Assemble!" + at_string)
            return

    async def remove_player(self, player):
        if str(player) in self.players.keys():
            del self.players[str(player)]
            del memberInTeamSet[player.id]
            #await player.move_to(None)
            return True
        return False
    
    @property
    def free_count(self) -> int:
        return self.max_players - len(self.players)
    
    @property
    def count(self) -> str:
        return len(self.players)


    async def createVoiceChannel(self, name):
        try:
            channel = await self.guild.create_voice_channel(name, limit=self.max_players)
            self.activeChannel = channel
            # for player in self.players.values():
            #     #member = discord.utils.get(self.guild.members, name=str(player).split("#")[0])
            #     await player.move_to(channel)
        except Exception as e:
            print(e)

def get_team_choices(ctx: discord.AutocompleteContext):
    captains = [team.captain for team in teams.values() if team.guild == ctx.guild]
    return [f"<@{captain.id}>" for captain in captains]

async def try_create_team(ctx):
    team_name = str(ctx.author.id)
    team = Team(ctx.guild, team_name, ctx.author)
    teams[str(ctx.guild)+str(team_name)] = team
    await team.add_player(ctx.channel, ctx.author)
    return f'> {team.captain} created a team. Use `/cs join @{ctx.author}` to join.'

async def try_create_newteam(ctx, limit):
    team_name = str(ctx.author.id)
    team = Team(ctx.guild, team_name, ctx.author, limit)
    teams[str(ctx.guild)+str(team_name)] = team
    await team.add_player(ctx.channel, ctx.author)
    return f'> {team.captain} created a {limit} man limited team. Use `/cs join @{ctx.author}` to join.'


async def try_join_team(ctx, member: discord.Member):
    team_name = str(member.id)
    team_ref = str(ctx.guild)+team_name

    if ctx.author.id in memberInTeamSet:
        return f'> You are already in a team.'
    if team_ref not in teams:
        return f'> {member.name} has not created a team. Use `/csnow` to create a team. Or talk to people like a normal person.'
        
    team: Team = teams[team_ref]

    if str(ctx.author) in team.players.keys():
        return f"> You are already in a {member.name}'s team."
    if team.free_count == 0:
        return f"> {member.name}'s team is full"
    
    await team.add_player(ctx.channel, ctx.author)
    return f"> {ctx.author} joined a {member.name}'s team. Need {team.free_count} more spaces ({team.count}/{team.max_players})."

async def try_leave_team(ctx):
    if ctx.author.id not in memberInTeamSet:
        return f'> You are not in a team.'
    team: Team = memberInTeamSet[ctx.author.id]
    if team.captain == ctx.author:
        return f'> You are the captain of the team. Use `/cs disband` to disband the team.'
    
    await team.remove_player(ctx.author)

async def try_disband_team(ctx):
    if ctx.author.id not in memberInTeamSet:
        return f'> You are not in a team.'
    team: Team = memberInTeamSet[ctx.author.id]
    if team.captain != ctx.author:
        return f'> You are not the captain of the team. Use `/cs leave` to leave the team.'
    
    players = team.players.values()
    for player in players:
        del memberInTeamSet[player.id]

    del teams[str(ctx.guild)+str(team.name)]

    return f'> {ctx.author}\'s team disbanded.'