import discord
from discord.ext import commands, tasks
import random
import asyncio
import datetime
import json
import os
import aiohttp
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Activity URL (set this after you deploy to Railway)
ACTIVITY_URL = os.getenv('ACTIVITY_URL', 'https://your-app.railway.app')

# Expanded list of 5-letter words (you can expand this much more)
WORD_LIST = [
    "about", "above", "abuse", "actor", "acute", "admit", "adopt", "adult", "after", "again",
    "agent", "agree", "ahead", "alarm", "album", "alert", "alien", "align", "alike", "alive",
    "allow", "alone", "along", "alter", "among", "anger", "angle", "angry", "apart", "apple",
    "apply", "arena", "argue", "arise", "array", "aside", "asset", "avoid", "awake", "award",
    "aware", "badly", "baker", "bases", "basic", "beach", "began", "begin", "being", "below",
    "bench", "billy", "birth", "black", "blame", "blind", "block", "blood", "board", "boost",
    "booth", "bound", "brain", "brand", "brass", "brave", "bread", "break", "breed", "brief",
    "bring", "broad", "broke", "brown", "build", "built", "buyer", "cable", "calif", "carry",
    "catch", "cause", "chain", "chair", "chaos", "charm", "chart", "chase", "cheap", "check",
    "chest", "chief", "child", "china", "chose", "civil", "claim", "class", "clean", "clear",
    "click", "climb", "clock", "close", "cloud", "coach", "coast", "could", "count", "court",
    "cover", "craft", "crash", "crazy", "cream", "crime", "cross", "crowd", "crown", "crude",
    "curve", "cycle", "daily", "dance", "dated", "dealt", "death", "debut", "delay", "depth",
    "doing", "doubt", "dozen", "draft", "drama", "drank", "dream", "dress", "drill", "drink",
    "drive", "drove", "dying", "eager", "eagle", "early", "earth", "eight", "elite", "empty",
    "enemy", "enjoy", "enter", "entry", "equal", "error", "event", "every", "exact", "exist",
    "extra", "faith", "false", "fault", "fiber", "field", "fifth", "fifty", "fight", "final",
    "first", "fixed", "flash", "fleet", "floor", "fluid", "focus", "force", "forth", "forty",
    "forum", "found", "frame", "frank", "fraud", "fresh", "front", "fruit", "fully", "funny",
    "giant", "given", "glass", "globe", "going", "grace", "grade", "grand", "grant", "grass",
    "grave", "great", "green", "gross", "group", "grown", "guard", "guess", "guest", "guide",
    "happy", "harry", "heart", "heavy", "hence", "henry", "horse", "hotel", "house", "human",
    "ideal", "image", "index", "inner", "input", "issue", "japan", "jimmy", "joint", "jones",
    "judge", "known", "label", "large", "laser", "later", "laugh", "layer", "learn", "lease",
    "least", "leave", "legal", "level", "lewis", "light", "limit", "links", "lives", "local",
    "logic", "loose", "lower", "lucky", "lunch", "lying", "magic", "major", "maker", "march",
    "maria", "match", "maybe", "mayor", "meant", "media", "metal", "might", "minor", "minus",
    "mixed", "model", "money", "month", "moral", "motor", "mount", "mouse", "mouth", "moved",
    "movie", "music", "needs", "never", "newly", "night", "noise", "north", "noted", "novel",
    "nurse", "occur", "ocean", "offer", "often", "order", "other", "ought", "paint", "panel",
    "paper", "party", "peace", "peter", "phase", "phone", "photo", "piano", "piece", "pilot",
    "pitch", "place", "plain", "plane", "plant", "plate", "point", "pound", "power", "press",
    "price", "pride", "prime", "print", "prior", "prize", "proof", "proud", "prove", "queen",
    "quick", "quiet", "quite", "radio", "raise", "range", "rapid", "ratio", "reach", "ready",
    "realm", "rebel", "refer", "relax", "repay", "reply", "right", "rigid", "river", "robot",
    "roger", "roman", "rough", "round", "route", "royal", "rural", "scale", "scene", "scope",
    "score", "sense", "serve", "setup", "seven", "shall", "shape", "share", "sharp", "sheet",
    "shelf", "shell", "shift", "shine", "shirt", "shock", "shoot", "short", "shown", "side",
    "sight", "simon", "since", "sixth", "sixty", "sized", "skill", "sleep", "slide", "small",
    "smart", "smile", "smith", "smoke", "snake", "snow", "social", "solid", "solve", "sorry",
    "sound", "south", "space", "spare", "speak", "speed", "spend", "spent", "split", "spoke",
    "sport", "staff", "stage", "stake", "stand", "start", "state", "steam", "steel", "stick",
    "still", "stock", "stone", "stood", "store", "storm", "story", "strip", "stuck", "study",
    "stuff", "style", "sugar", "suite", "super", "sweet", "table", "taken", "taste", "taxes",
    "teach", "teeth", "terry", "texas", "thank", "theft", "their", "theme", "there", "these",
    "thick", "thing", "think", "third", "those", "three", "threw", "throw", "thumb", "tiger",
    "tight", "timer", "tired", "title", "today", "topic", "total", "touch", "tough", "tower",
    "track", "trade", "train", "treat", "trend", "trial", "tribe", "trick", "tried", "tries",
    "truck", "truly", "trunk", "trust", "truth", "twice", "uncle", "under", "undue", "union",
    "unity", "until", "upper", "upset", "urban", "usage", "usual", "valid", "value", "video",
    "virus", "visit", "vital", "vocal", "voice", "waste", "watch", "water", "wheel", "where",
    "which", "while", "white", "whole", "whose", "woman", "women", "world", "worry", "worse",
    "worst", "worth", "would", "write", "wrong", "wrote", "young", "youth"
]

# Game state management
active_games = {}  # Maps user ID to game data
daily_results = {}  # Maps guild_id -> {date: {user_id: result}}
guild_settings = {}  # Maps guild_id -> {wordle_channel_id: channel_id, streak: count, last_activity: date}
DATA_FILE = "wordle_data.json"

def load_data():
    """Load saved game data"""
    global daily_results, guild_settings
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                data = json.load(f)
                daily_results = data.get('daily_results', {})
                guild_settings = data.get('guild_settings', {})
        except:
            daily_results = {}
            guild_settings = {}

def save_data():
    """Save game data"""
    with open(DATA_FILE, 'w') as f:
        json.dump({
            'daily_results': daily_results,
            'guild_settings': guild_settings
        }, f, indent=2)

def get_daily_word():
    """Get the word for today (same for everyone)"""
    today = datetime.date.today()
    # Use date as seed for consistent daily word
    random.seed(today.toordinal())
    word = random.choice(WORD_LIST)
    # Reset random seed
    random.seed()
    return word, today.strftime("%Y-%m-%d")

def get_today_string():
    """Get today's date as string"""
    return datetime.date.today().strftime("%Y-%m-%d")

def get_yesterday_string():
    """Get yesterday's date as string"""
    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    return yesterday.strftime("%Y-%m-%d")

class WordleGame:
    def __init__(self, answer, user_id, channel, guild_id):
        self.answer = answer.lower()
        self.guesses = []
        self.max_guesses = 6
        self.completed = False
        self.won = False
        self.user_id = user_id
        self.channel = channel
        self.guild_id = guild_id
        self.live_message = None  # Store the live progress message
    
    def make_guess(self, guess):
        guess = guess.lower()
        if len(guess) != 5:
            return False, "Guess must be 5 letters!"
        
        if guess in [g[0] for g in self.guesses]:
            return False, "You already guessed that word!"
        
        feedback = self.get_feedback(guess)
        self.guesses.append((guess, feedback))
        
        if guess == self.answer:
            self.completed = True
            self.won = True
        elif len(self.guesses) >= self.max_guesses:
            self.completed = True
            self.won = False
        
        return True, feedback
    
    def get_feedback(self, guess):
        feedback = []
        answer_chars = list(self.answer)
        guess_chars = list(guess)
        
        # First pass: mark correct positions
        for i in range(5):
            if guess_chars[i] == answer_chars[i]:
                feedback.append("🟩")
                answer_chars[i] = None  # Mark as used
                guess_chars[i] = None   # Mark as processed
            else:
                feedback.append(None)
        
        # Second pass: mark wrong positions
        for i in range(5):
            if feedback[i] is None:  # Not already green
                if guess_chars[i] in answer_chars:
                    feedback[i] = "🟨"
                    answer_chars[answer_chars.index(guess_chars[i])] = None  # Mark as used
                else:
                    feedback[i] = "⬜"
        
        return "".join(feedback)
    
    def get_board_display(self):
        board = ""
        for guess, feedback in self.guesses:
            board += f"`{guess.upper()}` {feedback}\n"
        
        # Add empty rows
        for i in range(len(self.guesses), self.max_guesses):
            board += "`_____` ⬜⬜⬜⬜⬜\n"
        
        return board
    
    def get_live_progress_display(self):
        """Get just the emoji grid for live progress (no letters)"""
        progress = ""
        for guess, feedback in self.guesses:
            progress += feedback + "\n"
        
        # Add empty rows
        for i in range(len(self.guesses), self.max_guesses):
            progress += "⬜⬜⬜⬜⬜\n"
        
        return progress.strip()
    
    def get_result_string(self):
        """Get the shareable result string like real Wordle"""
        if not self.completed:
            return None
        
        result = f"Wordle {get_today_string()} "
        if self.won:
            result += f"{len(self.guesses)}/6\n\n"
        else:
            result += "X/6\n\n"
        
        # Add just the emoji grid
        for guess, feedback in self.guesses:
            result += feedback + "\n"
        
        return result

class GuessModal(discord.ui.Modal, title='Make a Guess'):
    def __init__(self, game):
        super().__init__()
        self.game = game

    guess = discord.ui.TextInput(
        label='Enter your 5-letter guess',
        placeholder='Type your guess here...',
        max_length=5,
        min_length=5,
    )

    async def on_submit(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        guess_word = self.guess.value.lower()
        
        # Validate the guess - if invalid, show error in modal and keep it open
        if guess_word not in WORD_LIST:
            # Create a new modal with error message and keep the user's input
            error_modal = GuessModal(self.game)
            error_modal.guess.label = '❌ Invalid word! Enter a valid 5-letter word'
            error_modal.guess.default = self.guess.value  # Keep their input
            error_modal.guess.placeholder = 'That word is not in our dictionary...'
            await interaction.response.send_modal(error_modal)
            return
        
        success, feedback = self.game.make_guess(guess_word)
        
        if not success:
            await interaction.response.send_message(feedback, ephemeral=True)
            return
        
        # Update live progress message
        await self.update_live_progress(interaction.user)
        
        # Create the updated board display
        embed = discord.Embed(title="🎯 Wordle Bot", color=0x2F3136)
        embed.add_field(name="Your Progress", value=self.game.get_board_display(), inline=False)
        embed.add_field(name=f"Guesses: {len(self.game.guesses)}/{self.game.max_guesses}", value="\u200b", inline=False)
        
        if self.game.completed:
            # Update streak tracking
            await self.update_guild_streak()
            
            # Save result to daily results
            guild_id = str(self.game.guild_id)
            today = get_today_string()
            
            if guild_id not in daily_results:
                daily_results[guild_id] = {}
            if today not in daily_results[guild_id]:
                daily_results[guild_id][today] = {}
            
            daily_results[guild_id][today][str(user_id)] = {
                'won': self.game.won,
                'guesses': len(self.game.guesses),
                'result_string': self.game.get_result_string(),
                'username': interaction.user.display_name
            }
            save_data()
            
            if self.game.won:
                embed.add_field(name="🎉 Congratulations!", value=f"You got it in {len(self.game.guesses)} guesses!", inline=False)
                embed.color = 0x57F287  # Green
            else:
                embed.add_field(name="😔 Game Over", value=f"The word was: **{self.game.answer.upper()}**", inline=False)
                embed.color = 0xED4245  # Red
            
            # Remove the game from active games
            if user_id in active_games:
                del active_games[user_id]
            
            # Update the private message
            await interaction.response.edit_message(embed=embed, view=None)
            
            # Delete the live progress message
            if self.game.live_message:
                try:
                    await self.game.live_message.delete()
                except:
                    pass
            
            # Send public result to the channel
            public_embed = discord.Embed(title="🎯 Wordle Complete!", color=0x57F287 if self.game.won else 0xED4245)
            public_embed.add_field(name=f"{interaction.user.display_name}'s Result", value=f"```{self.game.get_result_string()}```", inline=False)
            
            # Add a "Share Results" button
            view = ShareResultsView(guild_id, today)
            await self.game.channel.send(embed=public_embed, view=view)
            
        else:
            view = WordleView(self.game)
            await interaction.response.edit_message(embed=embed, view=view)
    
    async def update_live_progress(self, user):
        """Update or create the live progress message"""
        embed = discord.Embed(title="🔴 Live Wordle Progress", color=0x5865F2)
        embed.add_field(name=f"{user.display_name} is playing", value=f"```{self.game.get_live_progress_display()}```", inline=False)
        embed.add_field(name="Progress", value=f"{len(self.game.guesses)}/6 guesses", inline=True)
        
        try:
            if self.game.live_message:
                await self.game.live_message.edit(embed=embed)
            else:
                self.game.live_message = await self.game.channel.send(embed=embed)
        except:
            # If editing fails, send a new message
            try:
                self.game.live_message = await self.game.channel.send(embed=embed)
            except:
                pass  # Channel might not allow sending messages
    
    async def update_guild_streak(self):
        """Update the guild's daily streak"""
        guild_id = str(self.game.guild_id)
        today = get_today_string()
        
        if guild_id not in guild_settings:
            guild_settings[guild_id] = {
                'wordle_channel_id': self.game.channel.id,
                'streak': 0,
                'last_activity': None
            }
        
        settings = guild_settings[guild_id]
        
        # Check if this is the first completion today
        if guild_id not in daily_results or today not in daily_results[guild_id]:
            # First person to complete today
            if settings['last_activity'] == get_yesterday_string():
                # Consecutive day - increase streak
                settings['streak'] += 1
            else:
                # Streak broken or new streak
                settings['streak'] = 1
        
        settings['last_activity'] = today
        settings['wordle_channel_id'] = self.game.channel.id
        save_data()

class ShareResultsView(discord.ui.View):
    def __init__(self, guild_id, date):
        super().__init__(timeout=86400)  # 24 hours timeout
        self.guild_id = guild_id
        self.date = date

    @discord.ui.button(label='View Today\'s Results', style=discord.ButtonStyle.secondary, emoji='📊')
    async def view_results(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = await self.get_daily_results_embed()
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    async def get_daily_results_embed(self):
        guild_id = str(self.guild_id)
        today = self.date
        
        embed = discord.Embed(title=f"📊 Daily Wordle Results - {today}", color=0x5865F2)
        
        if guild_id not in daily_results or today not in daily_results[guild_id]:
            embed.add_field(name="No Results Yet", value="No one has completed today's Wordle yet!", inline=False)
            return embed
        
        results = daily_results[guild_id][today]
        
        # Sort by completion status, then by number of guesses
        sorted_results = sorted(results.items(), key=lambda x: (not x[1]['won'], x[1]['guesses'] if x[1]['won'] else 999))
        
        completed_users = []
        failed_users = []
        
        for user_id, result in sorted_results:
            username = result['username']
            if result['won']:
                completed_users.append(f"✅ **{username}** - {result['guesses']}/6")
            else:
                failed_users.append(f"❌ **{username}** - X/6")
        
        if completed_users:
            embed.add_field(name="✅ Completed", value="\n".join(completed_users), inline=True)
        
        if failed_users:
            embed.add_field(name="❌ Failed", value="\n".join(failed_users), inline=True)
        
        total_players = len(results)
        completed_count = len(completed_users)
        success_rate = round((completed_count / total_players) * 100) if total_players > 0 else 0
        
        embed.add_field(name="📈 Server Stats", 
                       value=f"**Players:** {total_players}\n**Success Rate:** {success_rate}%", 
                       inline=False)
        
        return embed

class WordleView(discord.ui.View):
    def __init__(self, game):
        super().__init__(timeout=300)  # 5 minutes timeout
        self.game = game

    @discord.ui.button(label='Make Guess', style=discord.ButtonStyle.primary, emoji='✏️')
    async def make_guess(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = GuessModal(self.game)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label='Give Up', style=discord.ButtonStyle.danger, emoji='❌')
    async def give_up(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_id = interaction.user.id
        
        # Save failed result
        guild_id = str(self.game.guild_id)
        today = get_today_string()
        
        if guild_id not in daily_results:
            daily_results[guild_id] = {}
        if today not in daily_results[guild_id]:
            daily_results[guild_id][today] = {}
        
        # Create a failed result
        failed_result = self.game.get_result_string() or f"Wordle {today} X/6\n\n" + "".join([guess[1] + "\n" for guess in self.game.guesses])
        
        daily_results[guild_id][today][str(user_id)] = {
            'won': False,
            'guesses': 6,
            'result_string': failed_result,
            'username': interaction.user.display_name
        }
        save_data()
        
        embed = discord.Embed(title="🎯 Wordle - Game Over", color=0xED4245)
        embed.add_field(name="You gave up!", value=f"The word was: **{self.game.answer.upper()}**", inline=False)
        embed.add_field(name="Your Progress", value=self.game.get_board_display(), inline=False)
        
        # Remove the game from active games
        if user_id in active_games:
            del active_games[user_id]
        
        await interaction.response.edit_message(embed=embed, view=None)
        
        # Send public result to the channel
        public_embed = discord.Embed(title="🎯 Wordle Complete!", color=0xED4245)
        public_embed.add_field(name=f"{interaction.user.display_name}'s Result", value=f"```{failed_result}```", inline=False)
        
        view = ShareResultsView(guild_id, today)
        await self.game.channel.send(embed=public_embed, view=view)

    async def on_timeout(self):
        # Disable all buttons when the view times out
        for item in self.children:
            item.disabled = True

@tasks.loop(hours=24)
async def daily_summary():
    """Send daily summary at midnight"""
    yesterday = get_yesterday_string()
    
    for guild_id, settings in guild_settings.items():
        if 'wordle_channel_id' not in settings:
            continue
            
        try:
            channel = bot.get_channel(settings['wordle_channel_id'])
            if not channel:
                continue
            
            # Check if anyone played yesterday
            if (guild_id in daily_results and 
                yesterday in daily_results[guild_id] and 
                daily_results[guild_id][yesterday]):
                
                results = daily_results[guild_id][yesterday]
                
                # Create yesterday's summary
                embed = discord.Embed(title="🎯 Wordle Daily Summary", color=0x5865F2)
                
                # Show streak
                streak = settings.get('streak', 0)
                if streak > 0:
                    streak_emoji = "🔥" if streak > 1 else "✨"
                    embed.add_field(name=f"{streak_emoji} Group Streak", 
                                   value=f"Your group is on a **{streak} day** streak!", 
                                   inline=False)
                
                # Show yesterday's results
                completed_users = []
                failed_users = []
                
                # Sort by completion status, then by number of guesses
                sorted_results = sorted(results.items(), key=lambda x: (not x[1]['won'], x[1]['guesses'] if x[1]['won'] else 999))
                
                for user_id, result in sorted_results:
                    username = result['username']
                    if result['won']:
                        if result['guesses'] == 1:
                            completed_users.append(f"🏆 **{username}** - {result['guesses']}/6")
                        elif result['guesses'] <= 3:
                            completed_users.append(f"🥇 **{username}** - {result['guesses']}/6")
                        else:
                            completed_users.append(f"✅ **{username}** - {result['guesses']}/6")
                    else:
                        failed_users.append(f"❌ **{username}** - X/6")
                
                if completed_users:
                    embed.add_field(name=f"🎉 Yesterday's Results ({yesterday})", 
                                   value="\n".join(completed_users), inline=False)
                
                if failed_users:
                    embed.add_field(name="😔 Didn't Complete", 
                                   value="\n".join(failed_users), inline=False)
                
                # Add today's reminder
                embed.add_field(name="🆕 Today's Wordle", 
                               value="Ready for today's challenge? Use `/wordlebot` to start playing!", 
                               inline=False)
                
                await channel.send(embed=embed)
            
            else:
                # No one played yesterday - streak is broken
                if settings.get('streak', 0) > 0:
                    embed = discord.Embed(title="💔 Streak Broken", color=0xED4245)
                    embed.add_field(name="Oh no!", 
                                   value=f"Your group's {settings['streak']} day streak was broken yesterday.\nStart a new streak today with `/wordlebot`!", 
                                   inline=False)
                    settings['streak'] = 0
                    save_data()
                    await channel.send(embed=embed)
                    
        except Exception as e:
            print(f"Error sending daily summary to guild {guild_id}: {e}")

@daily_summary.before_loop
async def before_daily_summary():
    await bot.wait_until_ready()
    # Calculate time until next midnight
    now = datetime.datetime.now()
    tomorrow = now.replace(hour=0, minute=0, second=0, microsecond=0) + datetime.timedelta(days=1)
    await asyncio.sleep((tomorrow - now).total_seconds())

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    print(f"Bot ID: {bot.user.id}")
    print(f"Connected to {len(bot.guilds)} guilds")
    
    load_data()  # Load saved data
    daily_summary.start()  # Start the daily summary task
    
    # Sync commands with better error handling
    try:
        print("Attempting to sync slash commands...")
        synced = await bot.tree.sync()
        print(f"✅ Successfully synced {len(synced)} command(s)")
        
        # List all synced commands
        for command in synced:
            print(f"  - /{command.name}")
            
    except Exception as e:
        print(f"❌ Failed to sync commands: {e}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()

@bot.event
async def on_disconnect():
    print("Bot disconnected - will attempt to reconnect...")

@bot.event
async def on_resumed():
    print("Bot connection resumed!")

# Error handler for slash command errors
@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
    print(f"Command error: {error}")
    
    try:
        if interaction.response.is_done():
            await interaction.followup.send("An error occurred while processing your command.", ephemeral=True)
        else:
            await interaction.response.send_message("An error occurred while processing your command.", ephemeral=True)
    except:
        # If we can't send an error message, just log it
        print("Failed to send error message to user")

@bot.tree.command(name="wordlebot", description="Start today's Wordle game!")
async def wordle_slash(interaction: discord.Interaction):
    user_id = interaction.user.id
    guild_id = interaction.guild_id
    channel = interaction.channel
    
    # Check if user already has an active game
    if user_id in active_games:
        await interaction.response.send_message("You already have an active game! Finish it first or use the 'Give Up' button.", ephemeral=True)
        return
    
    # Check if user already completed today's Wordle
    today = get_today_string()
    if (str(guild_id) in daily_results and 
        today in daily_results[str(guild_id)] and 
        str(user_id) in daily_results[str(guild_id)][today]):
        
        result = daily_results[str(guild_id)][today][str(user_id)]
        embed = discord.Embed(title="🎯 Already Completed!", color=0x5865F2)
        embed.add_field(name="You've already played today!", 
                       value=f"Your result:\n```{result['result_string']}```", inline=False)
        embed.add_field(name="Come back tomorrow!", value="A new Wordle will be available in the next daily cycle.", inline=False)
        
        view = ShareResultsView(str(guild_id), today)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        return
    
    # Get today's word (same for everyone)
    word, date_str = get_daily_word()
    game = WordleGame(word, user_id, channel, guild_id)
    active_games[user_id] = game
    
    # Create initial embed and respond immediately (within 3 seconds)
    embed = discord.Embed(title="🎯 Daily Wordle", color=0x2F3136)
    embed.add_field(name="Your Progress", value=game.get_board_display(), inline=False)
    embed.add_field(name=f"Guesses: {len(game.guesses)}/{game.max_guesses}", value="\u200b", inline=False)
    embed.add_field(name="How to Play", value="Click 'Make Guess' to enter your 5-letter word!\n🟩 = Correct letter and position\n🟨 = Correct letter, wrong position\n⬜ = Letter not in word", inline=False)
    embed.add_field(name="Daily Word", value=f"Everyone gets the same word today!\nDate: {date_str}", inline=False)
    embed.add_field(name="Live Progress", value="Your progress is being shared live in the channel (without revealing your guesses)!", inline=False)
    
    view = WordleView(game)
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    # Create live progress message after responding (to avoid timeout)
    try:
        live_embed = discord.Embed(title="🔴 Live Wordle Progress", color=0x5865F2)
        live_embed.add_field(name=f"{interaction.user.display_name} is playing", value=f"```{game.get_live_progress_display()}```", inline=False)
        live_embed.add_field(name="Progress", value="0/6 guesses", inline=True)
        game.live_message = await channel.send(embed=live_embed)
    except:
        pass  # Channel might not allow sending messages

@bot.tree.command(name="results", description="View today's Wordle results for this server")
async def results_slash(interaction: discord.Interaction):
    guild_id = str(interaction.guild_id)
    today = get_today_string()
    
    embed = discord.Embed(title=f"📊 Daily Wordle Results - {today}", color=0x5865F2)
    
    if guild_id not in daily_results or today not in daily_results[guild_id]:
        embed.add_field(name="No Results Yet", value="No one has completed today's Wordle yet!\nUse `/wordlebot` to start playing!", inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    results = daily_results[guild_id][today]
    
    # Sort by completion status, then by number of guesses
    sorted_results = sorted(results.items(), key=lambda x: (not x[1]['won'], x[1]['guesses'] if x[1]['won'] else 999))
    
    completed_users = []
    failed_users = []
    
    for user_id, result in sorted_results:
        username = result['username']
        if result['won']:
            completed_users.append(f"✅ **{username}** - {result['guesses']}/6")
        else:
            failed_users.append(f"❌ **{username}** - X/6")
    
    if completed_users:
        embed.add_field(name="✅ Completed", value="\n".join(completed_users), inline=True)
    
    if failed_users:
        embed.add_field(name="❌ Failed", value="\n".join(failed_users), inline=True)
    
    total_players = len(results)
    completed_count = len(completed_users)
    success_rate = round((completed_count / total_players) * 100) if total_players > 0 else 0
    
    embed.add_field(name="📈 Server Stats", 
                   value=f"**Players:** {total_players}\n**Success Rate:** {success_rate}%", 
                   inline=False)
    
    await interaction.response.send_message(embed=embed)

# Commands to help users choose between bot and activity versions
@bot.tree.command(name="wordle-help", description="Learn about both Wordle options: bot commands and interactive activity")
async def wordle_help(interaction: discord.Interaction):
    """Help users understand both the bot and activity options"""
    embed = discord.Embed(
        title="🎯 Discord Wordle - Two Ways to Play!",
        description="Choose your preferred Wordle experience:",
        color=0x00ff00
    )
    
    embed.add_field(
        name="🤖 Bot Commands (Classic)",
        value=(
            "• `/wordlebot` - Play Wordle with Discord slash commands\n"
            "• Private gameplay, public results sharing\n"
            "• Text-based interface\n"
            "• Cross-platform stats\n"
            "• Perfect for any channel"
        ),
        inline=False
    )
    
    embed.add_field(
        name="🎮 Discord Activity (Interactive)",
        value=(
            "• Launch from voice channels (Activities button)\n"
            "• Visual game board with clicking\n"
            "• Real-time multiplayer viewing\n"
            "• Modern web interface\n"
            "• Best experienced in voice channels"
        ),
        inline=False
    )
    
    embed.add_field(
        name="📊 Shared Features",
        value="Both versions track your daily streaks and statistics!",
        inline=False
    )
    
    embed.set_footer(text="Choose the experience that works best for you!")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="launch-activity", description="Get instructions to launch the interactive Wordle activity")
async def launch_activity(interaction: discord.Interaction):
    """Help users launch the Discord Activity"""
    embed = discord.Embed(
        title="🚀 Launch Interactive Wordle Activity",
        description="Here's how to access the visual Wordle game:",
        color=0x5865f2
    )
    
    embed.add_field(
        name="Step 1: Join a Voice Channel",
        value="Connect to any voice channel in this server",
        inline=False
    )
    
    embed.add_field(
        name="Step 2: Find Activities",
        value="Look for the 🚀 **Activities** button in the voice channel",
        inline=False
    )
    
    embed.add_field(
        name="Step 3: Select Discord Wordle",
        value="Click on **Discord Wordle** from the activities list",
        inline=False
    )
    
    embed.add_field(
        name="Step 4: Play Together!",
        value="Enjoy the interactive game with friends watching live",
        inline=False
    )
    
    embed.add_field(
        name="🔗 Direct Link",
        value=f"[Open Activity in Browser]({ACTIVITY_URL})",
        inline=False
    )
    
    embed.set_footer(text="Can't find the activity? Make sure it's properly configured in Discord Developer Portal")
    await interaction.response.send_message(embed=embed)

# Admin command to force sync commands
@bot.tree.command(name="sync-commands", description="Force sync slash commands (admin only)")
async def sync_commands(interaction: discord.Interaction):
    """Force sync slash commands - useful for testing"""
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Only administrators can use this command.", ephemeral=True)
        return
        
    try:
        synced = await bot.tree.sync()
        await interaction.response.send_message(f"✅ Successfully synced {len(synced)} command(s)!", ephemeral=True)
        print(f"Manual sync: {len(synced)} commands synced by {interaction.user}")
    except Exception as e:
        await interaction.response.send_message(f"❌ Failed to sync commands: {str(e)}", ephemeral=True)
        print(f"Manual sync failed: {e}")

@bot.tree.command(name="bot-info", description="Show bot information and permissions")
async def bot_info(interaction: discord.Interaction):
    """Show bot status and permissions"""
    embed = discord.Embed(title="🤖 Bot Information", color=0x00ff00)
    
    # Bot basic info
    embed.add_field(
        name="Bot Status", 
        value=f"✅ Online\n🏓 Latency: {round(bot.latency * 1000)}ms", 
        inline=True
    )
    
    # Guild info
    embed.add_field(
        name="Server Info",
        value=f"📊 Guilds: {len(bot.guilds)}\n👥 Users: {len(bot.users)}",
        inline=True
    )
    
    # Check permissions
    permissions = interaction.app_permissions
    embed.add_field(
        name="Key Permissions",
        value=(
            f"Send Messages: {'✅' if permissions.send_messages else '❌'}\n"
            f"Use Slash Commands: {'✅' if permissions.use_slash_commands else '❌'}\n"
            f"Embed Links: {'✅' if permissions.embed_links else '❌'}\n"
            f"Read Message History: {'✅' if permissions.read_message_history else '❌'}"
        ),
        inline=False
    )
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

# Keep the old commands for backwards compatibility
@bot.command()
async def start(ctx):
    """Legacy command - use /wordlebot instead"""
    await ctx.send("Please use the `/wordlebot` slash command instead for a better experience!")

@bot.command()
async def guess(ctx, word: str = None):
    """Legacy command - use /wordlebot instead"""
    await ctx.send("Please use the `/wordlebot` slash command instead for a better experience!")

# Get bot token from environment variable
TOKEN = os.getenv('DISCORD_BOT_TOKEN')
if not TOKEN:
    print("Error: DISCORD_BOT_TOKEN environment variable not set!")
    print("Please set it with: export DISCORD_BOT_TOKEN=your_token_here")
    exit(1)

bot.run(TOKEN)
