class WordleActivity {
    constructor() {
        console.log('WordleActivity constructor called');
        this.currentRow = 0;
        this.currentCol = 0;
        this.gameComplete = false;
        this.gameWon = false;
        this.currentGuess = '';
        this.guesses = [];
        this.answer = '';
        this.stats = {
            gamesPlayed: 0,
            gamesWon: 0,
            currentStreak: 0,
            maxStreak: 0
        };
        this.discordSDK = null;
        this.websocket = null;
        
        console.log('Starting initialization...');
        this.init();
    }

    async init() {
        try {
            // Initialize Discord SDK
            await this.initDiscordSDK();
            
            // Connect to game server
            this.connectWebSocket();
            
            // Set up event listeners
            this.setupEventListeners();
            
            // Display current date
            this.displayDate();
            
            // Load stats
            this.loadStats();
            
            // Get today's word
            await this.getTodaysWord();
            
        } catch (error) {
            console.error('Failed to initialize Wordle Activity:', error);
            this.showMessage('Failed to connect to game server', 'error');
        }
    }

    async initDiscordSDK() {
        // Initialize Discord Embedded App SDK (optional)
        try {
            // Skip Discord SDK for now to avoid blocking
            console.log('Discord SDK disabled for local testing');
            this.discordSDK = null;
        } catch (error) {
            console.log('Discord SDK not available, running in standalone mode');
            this.discordSDK = null;
        }
    }

    connectWebSocket() {
        try {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}/ws`;
            
            this.websocket = new WebSocket(wsUrl);
            
            this.websocket.onopen = () => {
                console.log('Connected to game server');
                this.sendPlayerJoined();
            };
            
            this.websocket.onmessage = (event) => {
                const data = JSON.parse(event.data);
                this.handleServerMessage(data);
            };
            
            this.websocket.onclose = () => {
                console.log('Disconnected from game server');
                setTimeout(() => this.connectWebSocket(), 3000);
            };
            
            this.websocket.onerror = (error) => {
                console.log('WebSocket error (non-critical):', error);
            };
        } catch (error) {
            console.log('WebSocket connection failed (running offline mode)');
            this.websocket = null;
        }
    }

    setupEventListeners() {
        console.log('Setting up event listeners...');
        
        // Keyboard event listeners
        document.addEventListener('keydown', (e) => {
            console.log('Key pressed:', e.key);
            this.handleKeyPress(e.key);
        });
        
        // Virtual keyboard
        const keyButtons = document.querySelectorAll('.key');
        console.log('Found', keyButtons.length, 'keyboard buttons');
        
        keyButtons.forEach(key => {
            key.addEventListener('click', () => {
                const keyValue = key.dataset.key;
                console.log('Button clicked:', keyValue);
                this.handleKeyPress(keyValue);
            });
        });
        
        console.log('Event listeners set up successfully');
    }

    displayDate() {
        const today = new Date();
        const dateStr = today.toLocaleDateString('en-US', {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
        document.getElementById('date-display').textContent = dateStr;
    }

    async getTodaysWord() {
        try {
            const response = await fetch('/api/today-word');
            const data = await response.json();
            this.answer = data.word.toLowerCase();
            console.log('Today\'s word loaded');
        } catch (error) {
            console.error('Failed to get today\'s word, using fallback:', error);
            // Fallback word for offline testing
            this.answer = 'house';
            console.log('Using fallback word for testing');
        }
    }

    handleKeyPress(key) {
        if (this.gameComplete) return;

        key = key.toUpperCase();

        if (key === 'ENTER') {
            this.submitGuess();
        } else if (key === 'BACKSPACE') {
            this.deleteLetter();
        } else if (key.match(/^[A-Z]$/) && this.currentCol < 5) {
            this.addLetter(key);
        }
    }

    addLetter(letter) {
        console.log('addLetter called, gameComplete:', this.gameComplete);
        if (this.gameComplete) return;
        if (this.currentCol >= 5) return;

        // Find the correct tile: row with data-row, then tile with data-col within that row
        const row = document.querySelector(`[data-row="${this.currentRow}"]`);
        const tile = row.querySelector(`[data-col="${this.currentCol}"]`);
        
        if (!tile) {
            console.error('Could not find tile at row', this.currentRow, 'col', this.currentCol);
            return;
        }
        
        tile.textContent = letter;
        tile.classList.add('filled');
        
        this.currentGuess += letter;
        this.currentCol++;
    }

    deleteLetter() {
        if (this.gameComplete) return;
        if (this.currentCol <= 0) return;

        this.currentCol--;
        const row = document.querySelector(`[data-row="${this.currentRow}"]`);
        const tile = row.querySelector(`[data-col="${this.currentCol}"]`);
        
        if (!tile) {
            console.error('Could not find tile at row', this.currentRow, 'col', this.currentCol);
            return;
        }
        
        tile.textContent = '';
        tile.classList.remove('filled');
        
        this.currentGuess = this.currentGuess.slice(0, -1);
    }

    async submitGuess() {
        if (this.gameComplete) return;
        if (this.currentCol !== 5) {
            this.showMessage('Not enough letters', 'error');
            this.shakeRow();
            return;
        }

        // Check if word is valid
        if (!await this.isValidWord(this.currentGuess)) {
            this.showMessage('Not in word list', 'error');
            this.shakeRow();
            return;
        }

        // Check if already guessed
        if (this.guesses.includes(this.currentGuess)) {
            this.showMessage('Already guessed', 'error');
            this.shakeRow();
            return;
        }

        // Process the guess
        this.processGuess();
        this.updateKeyboard();
        this.sendGuessUpdate();

        // Check win condition
        console.log('Checking win condition:', this.currentGuess, 'vs', this.answer);
        if (this.currentGuess.toLowerCase() === this.answer) {
            console.log('WIN DETECTED! Setting gameComplete to true');
            this.gameWon = true;
            this.gameComplete = true;
            this.showMessage('Congratulations! 🎉', 'success');
            this.updateStats(true);
            this.sendGameComplete();
        } else if (this.currentRow >= 5) {
            this.gameComplete = true;
            this.showMessage(`The word was: ${this.answer.toUpperCase()}`, 'info');
            this.updateStats(false);
            this.sendGameComplete();
        } else {
            this.currentRow++;
            this.currentCol = 0;
            this.currentGuess = '';
        }
    }

    async isValidWord(word) {
        try {
            const response = await fetch('/api/validate-word', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ word: word.toLowerCase() })
            });
            const data = await response.json();
            return data.valid;
        } catch (error) {
            console.error('Word validation failed:', error);
            return true; // Allow word if validation fails
        }
    }

    processGuess() {
        const guess = this.currentGuess.toLowerCase();
        const answer = this.answer;
        const result = [];
        
        // Create arrays for processing
        const answerArray = answer.split('');
        const guessArray = guess.split('');
        const answerLetterCount = {};
        
        // Count letters in answer
        answerArray.forEach(letter => {
            answerLetterCount[letter] = (answerLetterCount[letter] || 0) + 1;
        });
        
        // First pass: mark correct positions
        for (let i = 0; i < 5; i++) {
            if (guessArray[i] === answerArray[i]) {
                result[i] = 'correct';
                answerLetterCount[guessArray[i]]--;
            }
        }
        
        // Second pass: mark present letters
        for (let i = 0; i < 5; i++) {
            if (result[i] !== 'correct') {
                if (answerLetterCount[guessArray[i]] > 0) {
                    result[i] = 'present';
                    answerLetterCount[guessArray[i]]--;
                } else {
                    result[i] = 'absent';
                }
            }
        }
        
        // Apply results to tiles
        const row = document.querySelector(`[data-row="${this.currentRow}"]`);
        for (let i = 0; i < 5; i++) {
            const tile = row.querySelector(`[data-col="${i}"]`);
            setTimeout(() => {
                tile.classList.add(result[i]);
            }, i * 200);
        }
        
        this.guesses.push(this.currentGuess);
    }

    updateKeyboard() {
        const guess = this.currentGuess.toLowerCase();
        const answer = this.answer;
        
        for (let i = 0; i < guess.length; i++) {
            const letter = guess[i].toUpperCase();
            const key = document.querySelector(`[data-key="${letter}"]`);
            
            if (!key) continue;
            
            let status = 'absent';
            if (answer[i] === guess[i]) {
                status = 'correct';
            } else if (answer.includes(guess[i])) {
                status = 'present';
            }
            
            // Only update if it's not already correct
            if (!key.classList.contains('correct')) {
                key.classList.remove('present', 'absent');
                key.classList.add(status);
            }
        }
    }

    shakeRow() {
        const row = document.querySelector(`[data-row="${this.currentRow}"]`);
        row.classList.add('shake');
        setTimeout(() => row.classList.remove('shake'), 500);
    }

    showMessage(text, type = 'info') {
        const messageEl = document.getElementById('message');
        messageEl.textContent = text;
        messageEl.className = type;
        
        setTimeout(() => {
            messageEl.textContent = '';
            messageEl.className = '';
        }, 3000);
    }

    updateStats(won) {
        this.stats.gamesPlayed++;
        if (won) {
            this.stats.gamesWon++;
            this.stats.currentStreak++;
            this.stats.maxStreak = Math.max(this.stats.maxStreak, this.stats.currentStreak);
        } else {
            this.stats.currentStreak = 0;
        }
        
        this.saveStats();
        this.displayStats();
    }

    displayStats() {
        const winPercentage = this.stats.gamesPlayed > 0 
            ? Math.round((this.stats.gamesWon / this.stats.gamesPlayed) * 100) 
            : 0;
            
        document.getElementById('games-played').textContent = this.stats.gamesPlayed;
        document.getElementById('win-percentage').textContent = winPercentage;
        document.getElementById('current-streak').textContent = this.stats.currentStreak;
        document.getElementById('max-streak').textContent = this.stats.maxStreak;
    }

    saveStats() {
        localStorage.setItem('wordle-stats', JSON.stringify(this.stats));
    }

    loadStats() {
        const saved = localStorage.getItem('wordle-stats');
        if (saved) {
            this.stats = JSON.parse(saved);
        }
        this.displayStats();
    }

    // WebSocket message handlers
    sendPlayerJoined() {
        if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
            this.websocket.send(JSON.stringify({
                type: 'player_joined',
                player: this.getPlayerInfo()
            }));
        }
    }

    sendGuessUpdate() {
        if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
            this.websocket.send(JSON.stringify({
                type: 'guess_update',
                player: this.getPlayerInfo(),
                guesses: this.currentRow + 1,
                complete: this.gameComplete
            }));
        }
    }

    sendGameComplete() {
        if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
            this.websocket.send(JSON.stringify({
                type: 'game_complete',
                player: this.getPlayerInfo(),
                won: this.gameWon,
                guesses: this.currentRow + 1,
                result: this.getShareableResult()
            }));
        }
    }

    getPlayerInfo() {
        if (this.discordSDK && this.discordSDK.user) {
            return {
                id: this.discordSDK.user.id,
                username: this.discordSDK.user.username,
                avatar: this.discordSDK.user.avatar
            };
        }
        return {
            id: 'guest',
            username: 'Guest Player',
            avatar: null
        };
    }

    handleServerMessage(data) {
        switch (data.type) {
            case 'players_update':
                this.updateLivePlayers(data.players);
                break;
            case 'player_progress':
                this.updatePlayerProgress(data.player, data.progress);
                break;
        }
    }

    updateLivePlayers(players) {
        const playersList = document.getElementById('players-list');
        playersList.innerHTML = '';
        
        players.forEach(player => {
            const playerEl = document.createElement('div');
            playerEl.className = 'player';
            playerEl.innerHTML = `
                <div class="player-avatar" style="background-image: url('${player.avatar || ''}')"></div>
                <span>${player.username}</span>
                <span class="player-progress">${player.guesses}/6</span>
            `;
            playersList.appendChild(playerEl);
        });
    }

    getShareableResult() {
        const today = new Date().toLocaleDateString('en-US', {
            month: 'numeric',
            day: 'numeric',
            year: 'numeric'
        });
        
        let result = `Wordle ${today} `;
        result += this.gameWon ? `${this.currentRow + 1}/6\n\n` : 'X/6\n\n';
        
        // Add emoji grid
        this.guesses.forEach((guess, rowIndex) => {
            const answer = this.answer;
            for (let i = 0; i < guess.length; i++) {
                if (guess[i] === answer[i]) {
                    result += '🟩';
                } else if (answer.includes(guess[i])) {
                    result += '🟨';
                } else {
                    result += '⬜';
                }
            }
            result += '\n';
        });
        
        return result;
    }
}

// Initialize the game when the page loads
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM loaded, initializing Wordle Activity...');
    try {
        new WordleActivity();
    } catch (error) {
        console.error('Failed to initialize WordleActivity:', error);
    }
});
