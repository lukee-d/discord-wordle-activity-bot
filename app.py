import discord
from discord.ext import commands
import random
import datetime
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Simple word list
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

# Simple game storage
active_games = {}
daily_results = {}

def get_daily_word():
    """Get today's word"""
    today = datetime.date.today()
    random.seed(today.toordinal())
    word = random.choice(WORD_LIST)
    random.seed()
    return word

def get_feedback(guess, answer):
    """Get Wordle feedback"""
    feedback = []
    answer_chars = list(answer.lower())
    guess_chars = list(guess.lower())
    
    # First pass: mark correct positions
    for i in range(5):
        if guess_chars[i] == answer_chars[i]:
            feedback.append("🟩")
            answer_chars[i] = None
            guess_chars[i] = None
        else:
            feedback.append(None)
    
    # Second pass: mark wrong positions
    for i in range(5):
        if feedback[i] is None:
            if guess_chars[i] in answer_chars:
                feedback[i] = "🟨"
                answer_chars[answer_chars.index(guess_chars[i])] = None
            else:
                feedback[i] = "⬜"
    
    return "".join(feedback)

@bot.event
async def on_ready():
    print(f'Bot logged in as {bot.user}')
    
    # Simple sync - just try to sync and don't worry about complications
    try:
        synced = await bot.tree.sync()
        print(f'Synced {len(synced)} commands')
    except Exception as e:
        print(f'Failed to sync: {e}')

@bot.tree.command(name="wordle", description="Start a new Wordle game!")
async def wordle(interaction: discord.Interaction):
    user_id = interaction.user.id
    
    # Get today's word
    word = get_daily_word()
    
    # Initialize game
    active_games[user_id] = {
        'word': word,
        'guesses': [],
        'completed': False
    }
    
    embed = discord.Embed(title="🎯 Wordle", description="Guess the 5-letter word!", color=0x5865F2)
    embed.add_field(name="How to play:", value="Use `/guess <word>` to make guesses!\n🟩 = Right letter, right spot\n🟨 = Right letter, wrong spot\n⬜ = Letter not in word", inline=False)
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="guess", description="Make a guess in your Wordle game!")
async def guess_command(interaction: discord.Interaction, word: str):
    user_id = interaction.user.id
    
    # Check if user has active game
    if user_id not in active_games:
        await interaction.response.send_message("❌ You don't have an active game! Use `/wordle` to start.", ephemeral=True)
        return
    
    game = active_games[user_id]
    
    if game['completed']:
        await interaction.response.send_message("❌ Your game is already completed!", ephemeral=True)
        return
    
    # Validate guess
    word = word.lower().strip()
    if len(word) != 5:
        await interaction.response.send_message("❌ Word must be exactly 5 letters!", ephemeral=True)
        return
    
    if word not in WORD_LIST:
        await interaction.response.send_message("❌ That's not a valid word!", ephemeral=True)
        return
    
    # Check if already guessed
    if word in [g['word'] for g in game['guesses']]:
        await interaction.response.send_message("❌ You already guessed that word!", ephemeral=True)
        return
    
    # Make the guess
    feedback = get_feedback(word, game['word'])
    game['guesses'].append({'word': word, 'feedback': feedback})
    
    # Check if won or lost
    won = word == game['word']
    lost = len(game['guesses']) >= 6 and not won
    
    if won or lost:
        game['completed'] = True
    
    # Create response
    embed = discord.Embed(title="🎯 Wordle", color=0x5865F2)
    
    # Show all guesses
    board = ""
    for g in game['guesses']:
        board += f"`{g['word'].upper()}` {g['feedback']}\n"
    
    # Add empty rows
    for i in range(len(game['guesses']), 6):
        board += "`_____` ⬜⬜⬜⬜⬜\n"
    
    embed.add_field(name="Your Board:", value=board, inline=False)
    
    if won:
        embed.add_field(name="🎉 You won!", value=f"Got it in {len(game['guesses'])} guesses!", inline=False)
        embed.color = 0x57F287
        del active_games[user_id]
    elif lost:
        embed.add_field(name="😔 Game Over", value=f"The word was: **{game['word'].upper()}**", inline=False)
        embed.color = 0xED4245
        del active_games[user_id]
    else:
        embed.add_field(name="Keep going!", value=f"Guesses: {len(game['guesses'])}/6", inline=False)
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="stats", description="Show your Wordle statistics")
async def stats(interaction: discord.Interaction):
    embed = discord.Embed(title="📊 Your Wordle Stats", color=0x5865F2)
    embed.add_field(name="Coming Soon!", value="Stats tracking will be added in the next update!", inline=False)
    await interaction.response.send_message(embed=embed, ephemeral=True)

# Get bot token
TOKEN = os.getenv('DISCORD_BOT_TOKEN')
if not TOKEN:
    print("Error: DISCORD_BOT_TOKEN not found!")
    exit(1)

bot.run(TOKEN)
