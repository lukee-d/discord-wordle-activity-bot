# Discord Wordle Activity

A Discord Activity version of the Wordle game that runs directly inside Discord voice channels and DMs.

## Features

- 🎯 **Interactive Wordle Gameplay**: Full Wordle experience with visual board and keyboard
- 🔄 **Real-time Multiplayer**: See other players' progress live
- 📱 **Responsive Design**: Works on desktop and mobile
- 🎨 **Beautiful UI**: Modern glass-morphism design with animations
- 📊 **Statistics Tracking**: Personal stats with localStorage
- 🔗 **Discord Integration**: Native Discord SDK integration
- ⚡ **WebSocket Updates**: Real-time player updates

## Setup

### Prerequisites
- Node.js 16+ 
- Discord Developer Application with Activity enabled

### Installation

1. Install dependencies:
   ```bash
   npm install
   ```

2. Configure environment:
   ```bash
   cp .env.example .env
   # Edit .env with your Discord application details
   ```

3. Run development server:
   ```bash
   npm run dev
   ```

4. Run production server:
   ```bash
   npm start
   ```

## Discord Developer Setup

### Creating a Discord Activity

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application or use existing one
3. Go to "Activities" tab
4. Click "New Activity"
5. Fill in details:
   - **Name**: "Wordle"
   - **Description**: "Play Wordle together!"
   - **Target URL**: Your hosted URL (e.g., `https://your-domain.com`)
   - **Supported Platforms**: Web
6. Set up OAuth2 redirects if needed
7. Copy your Client ID to `.env` file

### Local Development with ngrok

For local testing, use ngrok to expose your local server:

```bash
# Install ngrok
npm install -g ngrok

# In one terminal, start your server
npm run dev

# In another terminal, expose port 3000
ngrok http 3000

# Use the ngrok URL as your Discord Activity Target URL
```

## Deployment

### Recommended Platforms

1. **Vercel** (easiest)
   ```bash
   npm install -g vercel
   vercel
   ```

2. **Railway**
   - Connect your GitHub repo
   - Set environment variables
   - Deploy automatically

3. **Heroku**
   ```bash
   git push heroku main
   ```

4. **DigitalOcean App Platform**
   - Connect repository
   - Configure build settings

### Environment Variables for Production

```bash
PORT=3000
NODE_ENV=production
DISCORD_CLIENT_ID=your_client_id
DISCORD_CLIENT_SECRET=your_client_secret
```

## File Structure

```
discord-activity/
├── public/
│   ├── index.html      # Main HTML file
│   ├── styles.css      # CSS styles
│   └── script.js       # Frontend JavaScript
├── src/
│   └── server.js       # Node.js server
├── package.json        # Dependencies
├── .env               # Environment variables
└── README.md          # This file
```

## API Endpoints

- `GET /` - Serve the main Activity page
- `GET /api/today-word` - Get today's Wordle word
- `POST /api/validate-word` - Validate if a word exists
- `GET /api/daily-results` - Get today's completion results
- `GET /health` - Health check endpoint
- `WebSocket /ws` - Real-time player updates

## WebSocket Events

### Client → Server
- `player_joined` - Player joins the Activity
- `guess_update` - Player makes a guess
- `game_complete` - Player completes the game

### Server → Client
- `players_update` - Updated list of active players
- `player_progress` - Individual player progress update

## How It Works

1. **Player joins**: Opens Activity in Discord, connects via WebSocket
2. **Game loads**: Fetches today's word, displays board and keyboard
3. **Real-time updates**: Other players see live progress (without spoilers)
4. **Game completion**: Results shared with other players
5. **Statistics**: Personal stats saved locally

## Differences from Bot Version

| Feature | Bot Version | Activity Version |
|---------|-------------|------------------|
| Interface | Discord embeds/modals | Full HTML/CSS/JS |
| Real-time | Limited updates | Full WebSocket sync |
| Multiplayer | Separate games | Shared experience |
| Platform | Any Discord channel | Voice channels/DMs only |
| Setup | Invite bot | Configure Activity |

## Development

### Running locally
```bash
npm run dev
```

### Testing with Discord
1. Use ngrok to expose local server
2. Update Discord Activity URL to ngrok URL
3. Test in Discord voice channel

### Adding features
- Modify `public/script.js` for frontend features
- Modify `src/server.js` for backend/WebSocket features
- Update `public/styles.css` for styling

## Security Notes

- Never commit `.env` files
- Use HTTPS in production
- Validate all user inputs
- Rate limit API endpoints for production use

## Troubleshooting

### Activity not loading
- Check Discord Developer Portal Activity URL
- Ensure server is accessible via HTTPS
- Check browser console for errors

### WebSocket connection issues
- Verify WebSocket endpoint is accessible
- Check firewall/proxy settings
- Ensure proper CORS configuration

### Word not loading
- Check API endpoints are working
- Verify word list is properly loaded
- Check server logs for errors
