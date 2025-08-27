# Nova AI

Nova AI is an open-source Discord bot built on discord.py that leverages a conversational AI to provide helpful and accurate responses to user inquiries. Designed for seamless integration into any server, this bot is engineered to manage contextual conversations, understand user commands, and deliver reliable information.

Key Features

- Advanced AI Integration: Built to connect with a powerful AI model, allowing for intelligent, context-aware conversations.
- Contextual Memory: The bot remembers the recent conversation history in each channel, enabling natural, flowing dialogue without losing track of the topic.
- Slash Commands: Utilizes modern Discord slash commands for a clean, user-friendly experience.
- Private Q&A: The /ask command allows users to get private responses from the AI without cluttering the public chat.
- Highly Configurable: Easily customize the bot's persona and behavior by modifying the main AI prompt.

- Chat System: When the bot is mentioned or replied to in a server (or in a DM), the on_message event is triggered. It stores the message and the bot's response in a deque (a double-ended queue) for that specific channel. This queue has a fixed size, ensuring the conversation context is maintained without using excessive memory.

- Slash Commands: Commands like /about and /ask use the Discord slash command API, which is more reliable and user-friendly. The /ask command is designed to respond ephemerally, ensuring the conversation remains private between the user and the bot.

