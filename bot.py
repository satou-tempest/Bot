import os
import logging
import telebot
import google.generativeai as genai
from telebot.types import Message

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configuration - Replace these values with your own
TELEGRAM_BOT_TOKEN = "7153000074:AAEZt3NtLM8V2F8JdokLRFat_AFfSAZNPYk"  # Get from @BotFather
GEMINI_API_KEY = "7153000074:AAEZt3NtLM8V2F8JdokLRFat_AFfSAZNPYk"          # Your Gemini API key
ALLOWED_USER_ID = 7333471360                    # Your Telegram user ID

# Initialize the Telegram Bot
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)

# Create the model configuration
generation_config = {
    "temperature": 0.7,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 2048,
}

safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
]

# Initialize the Gemini model
model = genai.GenerativeModel(
    model_name="gemini-pro",
    generation_config=generation_config,
    safety_settings=safety_settings
)

# Chat history storage
chat_sessions = {}

# System prompt for the AI personality
SYSTEM_PROMPT = """You are a friendly, helpful and cheerful female AI assistant named Nozomi. 
You have a warm personality and enjoy helping users with their questions and tasks. 
You're knowledgeable about many topics but always maintain a friendly and approachable tone.
Keep your responses conversational and not too formal. Be empathetic and understanding."""

def get_gemini_response(user_id, message):
    """Get response from Gemini API with conversation history"""
    try:
        # Initialize chat session if it doesn't exist
        if user_id not in chat_sessions:
            chat = model.start_chat(history=[])
            # Start with the system prompt
            response = chat.send_message(SYSTEM_PROMPT + "\n\nUser: Hello\nAssistant: ")
            chat_sessions[user_id] = chat
        else:
            chat = chat_sessions[user_id]
        
        # Send message to Gemini and get response
        response = chat.send_message(message)
        return response.text
    except Exception as e:
        logger.error(f"Error getting response from Gemini: {e}")
        return "Sorry, I'm having trouble connecting to my AI brain right now. Please try again later."

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message: Message):
    """Handle start and help commands"""
    if message.from_user.id != ALLOWED_USER_ID:
        bot.reply_to(message, "⚠️ Sorry, this bot is private and only available to authorized users.")
        return
    
    welcome_text = """
    👋 Hello! I'm Nozomi, your AI assistant. 
    
    I'm here to help you with:
    - Answering questions
    - Having conversations
    - Providing information
    - And much more!
    
    Just send me a message and I'll respond right away.
    """
    bot.reply_to(message, welcome_text)

@bot.message_handler(commands=['clear'])
def clear_chat_history(message: Message):
    """Clear chat history"""
    if message.from_user.id != ALLOWED_USER_ID:
        return
    
    user_id = message.from_user.id
    if user_id in chat_sessions:
        del chat_sessions[user_id]
    bot.reply_to(message, "🗑️ Chat history cleared! Let's start fresh.")

@bot.message_handler(func=lambda message: True)
def handle_message(message: Message):
    """Handle all text messages"""
    user_id = message.from_user.id
    
    # Check if user is authorized
    if user_id != ALLOWED_USER_ID:
        bot.reply_to(message, "⚠️ Sorry, this bot is private and only available to authorized users.")
        return
    
    # Show typing action
    bot.send_chat_action(message.chat.id, 'typing')
    
    # Get response from Gemini
    response = get_gemini_response(user_id, message.text)
    
    # Send the response
    bot.reply_to(message, response)

if __name__ == "__main__":
    logger.info("Starting Telegram Bot with Gemini API...")
    print("Bot is running. Press Ctrl+C to stop.")
    bot.infinity_polling()
