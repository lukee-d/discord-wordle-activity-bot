const express = require('express');
const WebSocket = require('ws');
const http = require('http');
const path = require('path');
const crypto = require('crypto');
require('dotenv').config();

const app = express();
const server = http.createServer(app);
const wss = new WebSocket.Server({ server });

// Word list (same as your bot)
const WORD_LIST = [
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
];

// Game state
const activePlayers = new Map();
const userStats = new Map(); // Store user statistics
const dailyResults = new Map(); // Store daily game results

// Middleware
app.use(express.json());
app.use(express.static(path.join(__dirname, '../public')));

// Get daily word (same logic as bot)
function getDailyWord() {
    const today = new Date();
    const seed = today.getFullYear() * 10000 + (today.getMonth() + 1) * 100 + today.getDate();
    
    // Simple seeded random using crypto
    const hash = crypto.createHash('sha256').update(seed.toString()).digest('hex');
    const index = parseInt(hash.substring(0, 8), 16) % WORD_LIST.length;
    
    return WORD_LIST[index];
}

function getTodayString() {
    const today = new Date();
    return today.toISOString().split('T')[0];
}

// API Routes
app.get('/api/today-word', (req, res) => {
    const word = getDailyWord();
    res.json({ word, date: getTodayString() });
});

app.post('/api/validate-word', (req, res) => {
    const { word } = req.body;
    const valid = WORD_LIST.includes(word.toLowerCase());
    res.json({ valid });
});

app.get('/api/daily-results', (req, res) => {
    const today = getTodayString();
    const results = dailyResults.get(today) || [];
    res.json({ results, date: today });
});

// Stats sync API for Discord bot integration
app.post('/api/sync-stats', (req, res) => {
    const { userId, stats } = req.body;
    if (!userId || !stats) {
        return res.status(400).json({ error: 'Missing userId or stats' });
    }
    
    // Store/update user stats (in production, use a database)
    userStats.set(userId, {
        ...stats,
        lastUpdated: new Date().toISOString()
    });
    
    res.json({ success: true, message: 'Stats synced successfully' });
});

app.get('/api/user-stats/:userId', (req, res) => {
    const { userId } = req.params;
    const stats = userStats.get(userId) || {
        gamesPlayed: 0,
        gamesWon: 0,
        currentStreak: 0,
        maxStreak: 0,
        guessDistribution: { 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0 }
    };
    
    res.json({ stats, userId });
});

// WebSocket handling
wss.on('connection', (ws) => {
    console.log('New player connected');
    
    ws.on('message', (message) => {
        try {
            const data = JSON.parse(message);
            handlePlayerMessage(ws, data);
        } catch (error) {
            console.error('Invalid message format:', error);
        }
    });
    
    ws.on('close', () => {
        // Remove player from active list
        for (const [playerId, playerData] of activePlayers) {
            if (playerData.ws === ws) {
                activePlayers.delete(playerId);
                broadcastPlayersUpdate();
                break;
            }
        }
        console.log('Player disconnected');
    });
});

function handlePlayerMessage(ws, data) {
    switch (data.type) {
        case 'player_joined':
            handlePlayerJoined(ws, data.player);
            break;
        case 'guess_update':
            handleGuessUpdate(ws, data);
            break;
        case 'game_complete':
            handleGameComplete(ws, data);
            break;
    }
}

function handlePlayerJoined(ws, player) {
    activePlayers.set(player.id, {
        ...player,
        ws,
        guesses: 0,
        complete: false,
        joinedAt: Date.now()
    });
    
    broadcastPlayersUpdate();
    console.log(`Player ${player.username} joined`);
}

function handleGuessUpdate(ws, data) {
    const player = activePlayers.get(data.player.id);
    if (player) {
        player.guesses = data.guesses;
        player.complete = data.complete;
        broadcastPlayersUpdate();
    }
}

function handleGameComplete(ws, data) {
    const player = activePlayers.get(data.player.id);
    if (player) {
        player.complete = true;
        player.won = data.won;
        player.finalGuesses = data.guesses;
        
        // Save to daily results
        saveDailyResult(data.player, data.won, data.guesses, data.result);
        
        broadcastPlayersUpdate();
        console.log(`Player ${data.player.username} completed game: ${data.won ? 'won' : 'lost'} in ${data.guesses} guesses`);
    }
}

function saveDailyResult(player, won, guesses, result) {
    const today = getTodayString();
    if (!dailyResults.has(today)) {
        dailyResults.set(today, []);
    }
    
    const results = dailyResults.get(today);
    const existingIndex = results.findIndex(r => r.playerId === player.id);
    
    const resultData = {
        playerId: player.id,
        username: player.username,
        avatar: player.avatar,
        won,
        guesses,
        result,
        timestamp: Date.now()
    };
    
    if (existingIndex >= 0) {
        results[existingIndex] = resultData;
    } else {
        results.push(resultData);
    }
}

function broadcastPlayersUpdate() {
    const players = Array.from(activePlayers.values()).map(p => ({
        id: p.id,
        username: p.username,
        avatar: p.avatar,
        guesses: p.guesses,
        complete: p.complete
    }));
    
    const message = JSON.stringify({
        type: 'players_update',
        players
    });
    
    // Broadcast to all connected clients
    wss.clients.forEach(client => {
        if (client.readyState === WebSocket.OPEN) {
            client.send(message);
        }
    });
}

// Serve the main page
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, '../public/index.html'));
});

// Health check
app.get('/health', (req, res) => {
    res.json({ status: 'ok', players: activePlayers.size });
});

const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
    console.log(`Discord Wordle Activity server running on port ${PORT}`);
    console.log(`Today's word: ${getDailyWord()}`);
});
