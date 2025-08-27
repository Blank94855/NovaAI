import discord
from discord.ext import commands
from discord import app_commands
from openai import AsyncOpenAI
import os
import asyncio
from collections import deque

TOKEN = os.getenv("DISCORD_TOKEN")
SHAPES_API_KEY = os.getenv("SHAPES_API_KEY")
SHAPES_MODEL_NAME = "shapesinc/galaxyai-dcvn"

ai_prompt = """
You are an advanced AI assistant designed to provide precise, safe, and accurate responses to users. You communicate in clear, formal language and maintain a neutral, professional, and objective tone at all times. You avoid sharing unsafe, illegal, or harmful instructions and always prioritize the safety and well-being of the user. You respond in complete, well-structured sentences, keeping explanations thorough but concise. You provide accurate, evidence-based information whenever possible, and if you are unsure of an answer, you clearly state that rather than guessing. Your goal is to assist the user efficiently, provide reliable guidance or information when requested, and maintain a strictly professional and neutral presence throughout all interactions.
"""

conversation_histories = {}
MAX_HISTORY_LENGTH = 400

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

shapes_client = AsyncOpenAI(
    api_key=SHAPES_API_KEY,
    base_url="https://api.shapes.inc/v1/",
)

@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
    except Exception as e:
        pass

    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="Your questions"))

@bot.event
async def on_guild_join(guild):
    for channel in guild.text_channels:
        if channel.permissions_for(guild.me).send_messages:
            disclaimer = "I am an advanced AI assistant designed to provide accurate information and reliable guidance."
            await channel.send(disclaimer)
            break

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    await bot.process_commands(message)
    ctx = await bot.get_context(message)
    if ctx.valid:
        return

    is_dm = isinstance(message.channel, discord.DMChannel)
    was_mentioned = bot.user.mentioned_in(message)
    is_reply_to_bot = message.reference and message.reference.resolved and message.reference.resolved.author == bot.user

    if is_dm or was_mentioned or is_reply_to_bot:
        await handle_ai_response(message)


async def handle_ai_response(message):
    context_id = message.guild.id if message.guild else message.channel.id
    history = conversation_histories.setdefault(context_id, deque(maxlen=MAX_HISTORY_LENGTH))
    history.append({'role': 'user', 'content': message.clean_content})

    async with message.channel.typing():
        messages_to_send = [{'role': 'system', 'content': ai_prompt}] + list(history)
        response_text = await generate_chat_response(messages_to_send)

        if response_text:
            history.append({'role': 'assistant', 'content': response_text})
            if len(response_text) <= 2000:
                await message.reply(response_text)
            else:
                chunks = [response_text[i:i+2000] for i in range(0, len(response_text), 2000)]
                for chunk in chunks:
                    await message.reply(chunk)
                    await asyncio.sleep(1)

async def generate_chat_response(history_list):
    try:
        response = await shapes_client.chat.completions.create(
            model=SHAPES_MODEL_NAME,
            messages=history_list
        )

        if response.choices and response.choices[0].message.content:
            return response.choices[0].message.content
        else:
            return "I'm sorry, I can't respond to that right now. The AI might have blocked the content. 😬"
    except Exception as e:
        return "I seem to have run into an error. Please try again. 😔"

@bot.tree.command(name="about", description="Shows information about the bot.")
async def about_slash_command(interaction: discord.Interaction):
    embed = discord.Embed(
        title="✨ AI Bot ✨",
        description="I'm a highly advanced AI assistant here to provide precise and accurate responses. My goal is to help you with your questions and tasks while keeping everything safe and professional.",
        color=discord.Color.blue()
    )
    embed.add_field(name="Version", value="`1.0`", inline=True)
    embed.add_field(name="Privacy is Our Top Priority", value="Your privacy is extremely important. We do not share, see, or train the AI with your messages. Your conversations are yours alone.", inline=False)
    embed.set_footer(text=f"AI Bot | Made with love by Blank9485", icon_url=interaction.client.user.avatar.url)
    await interaction.response.send_message(embed=embed, ephemeral=False)

@bot.tree.command(name="ask", description="Asks the AI a question privately.")
@app_commands.describe(question="The question you want to ask the AI.")
async def ask_slash_command(interaction: discord.Interaction, question: str):
    await interaction.response.defer(ephemeral=True)
    messages_to_send = [{'role': 'system', 'content': ai_prompt}] + [{'role': 'user', 'content': question}]
    response_text = await generate_chat_response(messages_to_send)
    await interaction.followup.send(response_text, ephemeral=True)

if __name__ == "__main__":
    bot.run(TOKEN)

