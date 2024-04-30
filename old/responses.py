from __future__ import annotations
import random
import old.csteams as csteams

async def handle_response(message, user_message: str):
    l_msg = user_message#.lower()
    
    tokens = parseCommand(l_msg)

    if len(tokens) == 0:
        return "I don't understand what you mean. Try !help for a list of commands."

    features = [csteams.handle_response]
    for feature in features:
        result = await feature(message, tokens)
        if result != None:
            return result
    
    if l_msg == "roll":
        rand = str(random.randint(1, 6))
        if rand > 6:
            return "You rolled a " + rand + "! What a lucky boy!"
        if rand > 1:
            return "You rolled a " + rand + "."
        if rand == 1:
            return "You rolled a " + rand + ". Maybe try again?"
        
    if l_msg == "!help":
        return """
        Here are the commands you can use:
        !help - Shows this message
        roll - Rolls a dice
        hello - Greets the bot
        """
    return "I don't understand what you mean. Try !help for a list of commands."

def parseCommand(string):
    #string = string.lower()
    strings = string.split(" ")
    return strings