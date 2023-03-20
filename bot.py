import discord
import responses
import brain
import globals
APPLICATION_ID = 1087034256838111383
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
    TOKEN = "null"
    client = discord.Client(intents=discord.Intents.all())
    globals.CLIENT = client
    #conversation = brain.init_morrowii_brain()
    @client.event
    async def on_ready():
        print(f"{client.user} has connected to Discord!")

    @client.event
    async def on_message(message):
        # stops execution if the message is from the bot itself
        if message.author == client.user:
            return
        
        username = str(message.author)
        user_message = str(message.content)
        channel = str(message.channel)

        print(f"{username} sent a message in {channel}: {user_message}")

        if len(user_message) == 0:
            return
        
        invoke_string = f"<@{APPLICATION_ID}>"

        if not invoke_string in user_message:
            return
        print(user_message.replace(invoke_string, ''))
        user_message = user_message.replace(invoke_string, '')
        if len(user_message) > 0 and user_message.strip()[0] ==" ~":
            await send_message(message, user_message.strip(), True)
        if len(user_message) > 0 and user_message.strip()[0] =="\\":
            await send_message(message, user_message.strip(), False)
        # elif user_message == " ":
        #     await send_ai_message(message, "I'm shy...", conversation)
        # elif len(user_message) > 0:
        #     await send_ai_message(message, user_message, conversation)
        # else:
        #     await send_ai_message(message, "hey!", conversation)

    client.run(TOKEN)