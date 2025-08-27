import discord
from discord import app_commands
from typing import Callable, Awaitable, Optional
import asyncio

def setup(bot, generate_ai_response_func: Callable[[str, str], Awaitable[str]]):

    @bot.tree.command(name="about", description="Shows information about this bot.")
    async def about_command(interaction: discord.Interaction):
        bot_name = "AI Bot"
        bot_version = "1.0.2"
        
        embed = discord.Embed(
            title=f"About {bot_name}",
            description="Hey there! I'm your friendly AI assistant on Discord.",
            color=discord.Color.from_rgb(46, 204, 113)
        )
        
        embed.set_thumbnail(url="https://i.imgur.com/G4hA8yV.png")
        
        embed.add_field(name="Version", value=f"`{bot_version}`", inline=True)
        embed.add_field(name="Developer", value="Blank9485", inline=True)
        
        embed.set_footer(text="Thanks for using me! ✨", icon_url=bot.user.avatar.url if bot.user else discord.Embed.Empty)
        embed.timestamp = discord.utils.utcnow()

        await interaction.response.send_message(embed=embed)


    @bot.tree.command(name="ask", description="Ask AI a question privately.")
    @app_commands.describe(
        question="The question you want to ask the AI."
    )
    async def ask_command(interaction: discord.Interaction, question: str):
        await interaction.response.defer(ephemeral=True)

        prompt = """
You are an advanced AI assistant designed to provide precise, safe, and accurate responses to users. You communicate in clear, formal language and maintain a neutral, professional, and objective tone at all times. You avoid sharing unsafe, illegal, or harmful instructions and always prioritize the safety and well-being of the user. You respond in complete, well-structured sentences, keeping explanations thorough but concise. You provide accurate, evidence-based information whenever possible, and if you are unsure of an answer, you clearly state that rather than guessing. Your goal is to assist the user efficiently, provide reliable guidance or information when requested, and maintain a strictly professional and neutral presence throughout all interactions.
        """

        try:
            async with interaction.channel.typing():
                response = await generate_ai_response_func(prompt, question)
                await interaction.followup.send(f"**Your Question:** `{question}`\n\n**AI's Answer:**\n{response}", ephemeral=True)
        except Exception as e:
            await interaction.followup.send("Oops! I hit a snag trying to answer that. Please try again later. 😅", ephemeral=True)


    @bot.event
    async def on_ready():
        try:
            await bot.tree.sync()
        except Exception as e:
            pass

