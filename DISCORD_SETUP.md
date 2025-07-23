# Discord Activity Setup Guide

## 1. Railway Deployment

### Deploy to Railway:
1. Push your code to GitHub
2. Go to [railway.app](https://railway.app)
3. Deploy from GitHub repo: `lukee-d/discord-wordle-activity-bot`
4. Wait for deployment to complete
5. Note your Railway app URL (e.g., `https://your-app.railway.app`)

### Set Environment Variables on Railway:
```
PORT=3000
NODE_ENV=production
DISCORD_CLIENT_ID=your_actual_client_id
DISCORD_CLIENT_SECRET=your_actual_client_secret
```

## 2. Discord Developer Portal Setup

### Create Discord Application:
1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application"
3. Name it "Discord Wordle" or similar
4. Go to "Activities" tab in the left sidebar

### Configure Activity:
1. **Activity Name**: Discord Wordle
2. **Activity Description**: Play Wordle together with friends!
3. **Activity URL**: `https://your-railway-app.railway.app`
4. **Supported Platforms**: Web
5. **Orientation**: Portrait or Landscape (your choice)

### Set OAuth2 Redirect URLs:
1. Go to "OAuth2" tab
2. Add redirect URL: `https://your-railway-app.railway.app/auth/callback`

### Get Client Credentials:
1. Copy **Application ID** (this is your CLIENT_ID)
2. Copy **Client Secret** from OAuth2 section
3. Add these to Railway environment variables

## 3. Test the Activity

### In Discord:
1. Create a voice channel or join one
2. Look for the "Activities" button (rocket icon)
3. Find "Discord Wordle" in your activities
4. Click to launch!

## 4. Publishing (Optional)

### To make it public:
1. In Developer Portal, go to "Activities" → "Distribution"
2. Fill out the store listing information
3. Submit for review

## 5. Troubleshooting

### Common Issues:
- **Activity not loading**: Check Railway logs, ensure URL is correct
- **Authentication errors**: Verify CLIENT_ID and CLIENT_SECRET
- **WebSocket issues**: Ensure Railway deployment includes WebSocket support

### Debug Steps:
1. Check Railway deployment logs
2. Test the URL directly in browser
3. Verify Discord Developer Portal settings
4. Check browser console for errors

### Railway Logs:
```bash
# View logs in Railway dashboard or CLI
railway logs
```
