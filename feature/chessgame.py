# python -m pip install chess python -m pip install cairosvg, python -m pip install pipwin, pipwin install cairocffi    
import chess
import chess.svg
from cairosvg import svg2png
import discord
import random
import asyncio
import settings
import chess.engine

engine = chess.engine.SimpleEngine.popen_uci("stockfish/stockfish-windows-2022-x86-64-avx2.exe")
engine.configure({"UCI_elo": settings.CHESS_ELO})
requests = {}
games = {}
draws = {}
class ChessGame:
    def __init__(self, black: discord.Member, white: discord.Member, board):
        self.black = black
        self.white = white
        self.board: chess.Board = board
        self.turn = white

    async def embed_board(self, ctx):
        if len (self.board.move_stack) > 0:
            lastmove = self.board.peek()
        else:
            lastmove = None
        svg = chess.svg.board(self.board, lastmove = lastmove)  
        svg2png(bytestring=svg, write_to='board.png')
        embed = discord.Embed(title="Chess", description=f"White: {self.white.name} | Black: {self.black.name}", color=0x00ff00)
        embed.set_image(url="attachment://board.png")
        await ctx.send(file=discord.File('board.png'), embed=embed)
        #await ctx.send(file=discord.File('board.png'))
    
    async def do_move(self, ctx, from_square, to_square):
        try:
            move = chess.Move.from_uci(f"{from_square}{to_square}")
        except ValueError:
            return -1
        
        if move not in self.board.legal_moves:
            return -2
        
        self.board.push(move)
        await self.embed_board(ctx)
        self.ChangeTurn()

    async def do_engine_move(self, ctx):
        if self.turn.id == APPLICATION_ID:
            async with ctx.channel.typing():
                type_time = random.randint(0, 5)
                await asyncio.sleep(type_time)
                limit = chess.engine.Limit(time=2.0)
                result = engine.play(self.board, limit) 
                self.board.push(result.move)
                await ctx.send(f"My turn :P")
                await self.embed_board(ctx)
                gameover = await self.check_for_game_over(ctx)
                if gameover:
                    ctx.send(f"Game over!")
                self.ChangeTurn()

    async def check_for_game_over(self, ctx):
        if self.board.is_game_over():
            if self.board.is_checkmate():
                winner = self.white if self.board.turn == chess.BLACK else self.black
                await ctx.send(f"Checkmate! <@{winner.id}> wins!")
            else:
                await ctx.send("Draw!")
            del games[self.white.id]
            del games[self.black.id]
            return True
        return False
    
    def ChangeTurn(self):
        self.turn = self.white if self.turn == self.black else self.black

class MyView(discord.ui.View): # Create a class called MyView that subclasses discord.ui.View
    @discord.ui.button(label="Accept Challenge!", style=discord.ButtonStyle.primary, emoji="😎") 
    async def button_callback(self, button, interaction: discord.Interaction):
        if interaction.user.id in games:
            return await interaction.response.send_message("You are already in a game!", ephemeral=True)
        if button.view.id not in requests:
            return await interaction.response.send_message("The challenge has expired!", ephemeral=True)
        if interaction.user.id == requests[button.view.id].author.id:
            return await interaction.response.send_message("You can't play yourself!", ephemeral=True)
        
        await interaction.response.send_message("You accepted the challenge!", ephemeral=True) 
        # (ctx, opponent: discord.Member):
        await start_game(requests[button.view.id], interaction.user)

async def request_game(ctx):
    if ctx.author.id in games:
        return await ctx.respond("You are already in a game!")
    view:discord.ui.View  = MyView()
    requests[view.id] = ctx
    return await ctx.respond("Waiting for opponent to accept...", view=view)

async def play_bot(ctx, bot: discord.Member):
    if ctx.author.id in games:
        return await ctx.respond("You are already in a game!")
    return await start_game(ctx, bot)

async def start_game(ctx, opponent: discord.Member):
    board = chess.Board()
    players = [ctx.author, opponent]
    white = random.choice(players)
    black = players[0] if white == players[1] else players[1]
    game = ChessGame(black, white, board)
    games[ctx.author.id] = game
    games[opponent.id] = game
    await game.embed_board(ctx)

    await game.do_engine_move(ctx)
    gameover = await game.check_for_game_over(ctx)
    if gameover:
        return await ctx.respond(f"Game over!")

    return await ctx.respond(f"Game started! <@{white.id}> is white. Make your move with `/chess move <from> <to>`")


async def move(ctx, from_square, to_square):
    if ctx.author.id not in games:
        await ctx.respond("You are not in a game!")
        return
    
    game: ChessGame = games[ctx.author.id]

    if ctx.author.id == game.black.id:
        if game.board.turn != chess.BLACK:
            await ctx.respond("It's not your turn!")
            return
    else:
        if game.board.turn != chess.WHITE:
            await ctx.respond("It's not your turn!")
            return
        
    res = await game.do_move(ctx, from_square, to_square)

    if res == -1:
        await ctx.respond("Invalid move!")
        return
    elif res == -2:
        await ctx.respond("Illegal move!")
        return
    
    gameover = await game.check_for_game_over(ctx)
    if gameover:
        await ctx.respond(f"Game over!")
        return
    
    # do engine move if playing against bot
    await ctx.respond(f"{ctx.author.name}'s turn. Now it's {game.turn.name}'s time to shine!")

    await game.do_engine_move(ctx)

async def resign(ctx):
    if ctx.author.id not in games:
        return "You are not in a game!"
    
    game: ChessGame = games[ctx.author.id]
    winner = game.white if ctx.author.id == game.black.id else game.black
    del games[game.white.id]
    del games[game.black.id]
    return f"{ctx.author.name} resigned! <@{winner.id}> wins!"

async def draw(ctx):
    if ctx.author.id not in games:
        return "You are not in a game!"
    opponent = games[ctx.author.id].black if ctx.author.id == games[ctx.author.id].white.id else games[ctx.author.id].white

    if opponent.id == settings.APPLICATION_ID:
        game: ChessGame = games[ctx.author.id]
        del games[game.white.id]
        del games[game.black.id]
        return "Draw! Game over!"

    draws[opponent.id] = ctx.author
    return f"{opponent.name} has been offered a draw! They have 30 seconds to accept with `/chess acceptdraw`"

async def accept_draw(ctx):
    if ctx.author.id not in games:
        return "You are not in a game!"
    if ctx.author.id not in draws:
        return "You haven't been offered a draw!"
    opponent = draws[ctx.author.id]
    game: ChessGame = games[ctx.author.id]
    del games[game.white.id]
    del games[game.black.id]
    del draws[ctx.author.id]
    return f"{opponent.name} offered a draw! Game over!"

async def print_board(ctx, board):
    svg = chess.svg.board(board)  
    svg2png(bytestring=svg, write_to='board.png')
    await ctx.send(file=discord.File('board.png'))
    return "Your turn!"

def list_chess_positions():
    positions = []
    for row in range(1, 9):
        for col in ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']:
            positions.append(col + str(row))
    return positions