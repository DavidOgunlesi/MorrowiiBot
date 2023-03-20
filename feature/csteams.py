from __future__ import annotations
from typing import List, Dict, Any
import globals
import discord

teams = {}

class Team:
    def __init__(self, guild, name: str, captain: str):
        self.name = name
        self.captain = captain
        self.players = {}
        self.max_players = 5
        self.guild = guild
        self.activeChannel = None

    async def add_player(self, channel, player):
        self.players[str(player)] = player
        if len(self.players) == self.max_players:
            vcname = self.name + " Team"
            await self.createVoiceChannel(vcname)
            channel.send(f"> All spaces filled in {self.name}, moving all to voice channel '{vcname}'")

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

async def handle_response(message, tokens: List[str]):
    msg = None
    msg = try_create_team(message, tokens) or msg
    msg = await try_join_team(message, tokens) or msg
    msg = await try_start_team(message, tokens) or msg
    return msg

async def try_start_team(message, tokens:List[str]):
    data = parse_command_string("\start {team_name:str}", tokens)
    if data != None:
        team_name = data['team_name']
        
        if str(message.guild)+team_name not in teams:
            return None
        
        team: Team = teams[str(message.guild)+team_name]

        if message.author != team.captain:
            return f'> Only the captain can start a team ***"{team.name}"***.'
        
        await team.createVoiceChannel(team.name + " Team")
    
    return None

def try_create_team(message, tokens:List[str]):
    data = parse_command_string("\letsplaycs {team_name:str}", tokens)
    if data != None:
        team_name = data['team_name']
        team = Team(message.guild, team_name, message.author)
        teams[str(message.guild)+team_name] = team
        return f'> {team.captain} created a team ***"{team.name}"***.'
    
    return None

async def try_join_team(message, tokens:List[str]):
    data = parse_command_string("\join {team_name:str}", tokens)
    if data != None:
        team_name = data['team_name']

        if str(message.guild)+team_name not in teams:
            return None
        
        team: Team = teams[str(message.guild)+team_name]

        if str(message.author) in team.players.keys():
            return f'> You are already in a ***"{team.name}"*** team.'
        if team.free_count == 0:
            return f'> `Team *"{team.name}"* is full.`'
        
        await team.add_player(message.channel, message.author)
        return f'> {message.author} joined a ***"{team.name}"*** team. Need {team.free_count} more spaces ({team.count}/{team.max_players}).'
    
    return None

def parse_command_string(cmd_string: str, tokens: List[str]):
    "example letsplaycs {team_name:str}"
    match = cmd_string.split(" ")

    if len(match) != len(tokens):
        print(f"length of match {len(match)} does not match length of tokens {len(tokens)}")
        return None
    data = {}
    for i in range(len(match)):
        if match[i][0] != '{' and match[i] != tokens[i]:
            print(f"`{match[i]}` did not match `{tokens[i]}` in tokens")
            return None
        if match[i][0] == '{' and match[i][-1] != '}':
            print(f"{match[i]}_<- does not have a closing bracket")
            return None
        else:
            match_parse = match[i][1:][:-1].split(":")
            if len(match_parse) != 2:
                continue
            name = match_parse[0]
            _type = match_parse[1]
            
            type_match = False
            type_match = (_type == "str" and type(tokens[i]) == str) or type_match
            type_match =  (_type == "int" and type(tokens[i]) == int) or type_match
            if type_match:
                data[name] = tokens[i]

    return data