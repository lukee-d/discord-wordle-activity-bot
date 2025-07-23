# Discord Wordle Bot

A Discord bot that brings the popular Wordle game to your Discord server with all the social features of the official Discord Wordle app.

## Features

- 🎯 **Daily Wordle**: Everyone gets the same word each day
- 🔒 **Private Gameplay**: Your guesses are private, only results are shared
- 📊 **Public Results**: Share your completion status with the server
- 🔥 **Streak Tracking**: Keep track of your server's daily completion streak
- 🔴 **Live Progress**: See who's currently playing in real-time
- 📈 **Server Stats**: View completion rates and leaderboards
- ⏰ **Daily Summaries**: Automatic midnight recaps of the previous day

## Setup

### Prerequisites
- Python 3.8 or higher
- A Discord bot token (get one from [Discord Developer Portal](https://discord.com/developers/applications))

### Installation

1. Clone or download this repository
2. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project directory:
   ```
   DISCORD_BOT_TOKEN=your_bot_token_here
   ```

5. Run the bot:
   ```bash
   python app.py
   ```

### Discord Bot Setup

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application
3. Go to "Bot" section and create a bot
4. Copy the bot token and put it in your `.env` file
5. Under "OAuth2" > "URL Generator", select:
   - Scope: `bot` and `applications.commands`
   - Bot Permissions: `Send Messages`, `Use Slash Commands`, `Embed Links`
6. Use the generated URL to invite the bot to your server

## Commands

- `/wordlebot` - Start today's Wordle game
- `/results` - View today's server results

## How to Play

1. Use `/wordlebot` to start a new game
2. Click "Make Guess" to enter your 5-letter word
3. Get feedback with colored squares:
   - 🟩 Green: Correct letter in correct position
   - 🟨 Yellow: Correct letter in wrong position
   - ⬜ White: Letter not in the word
4. You have 6 attempts to guess the word
5. Your progress is shared live (without revealing letters)
6. Results are posted publicly when you complete the game

## File Structure

- `app.py` - Main bot code
- `requirements.txt` - Python dependencies
- `.env` - Environment variables (not committed to git)
- `wordle_data.json` - Game data storage (created automatically)
- `.gitignore` - Files to exclude from git

## Security Note

Never commit your `.env` file or bot token to version control. The `.gitignore` file is set up to prevent this.
