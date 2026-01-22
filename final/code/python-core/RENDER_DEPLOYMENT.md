# AI Music Backend - Render Deployment Guide

## Overview
This is a lightweight Flask API backend for the AI Music Composition application. It does NOT run ML inference locally - instead, it forwards music generation requests to an external Colab/Gradio service.

## What This Backend Does
✅ **User Authentication** - signup, signin endpoints  
✅ **Music History** - saves and retrieves user music generations  
✅ **API Gateway** - forwards music generation requests to external ML service  
✅ **Health Check** - `/health` endpoint for monitoring  

## What This Backend Does NOT Do
❌ No ML model inference (torch, transformers, sklearn, etc.)  
❌ No ML libraries installed  
❌ No mood analysis or audio processing  
❌ RAM usage: ~50-80 MB (fits in 512 MB free tier)  

## Dependencies
```
flask==2.3.0          # Web framework
flask-cors==4.0.0     # CORS support
requests==2.31.0      # HTTP requests to external service
gunicorn==21.2.0      # Production WSGI server
```

## Local Development

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Locally
```bash
python studio_api.py
```
API will be available at `http://localhost:8000`

### 3. Test Health Check
```bash
curl http://localhost:8000/health
```

## Render Deployment

### 1. Connect GitHub Repository
- Push code to GitHub
- Connect your GitHub repo to Render

### 2. Create Web Service on Render
- **Name**: `ai-music-backend`
- **Region**: Choose your region
- **Branch**: `main`
- **Build Command**: `pip install -r python-core/requirements.txt`
- **Start Command**: `gunicorn -w 1 --threads 2 --timeout 300 python-core/studio_api:app`
- **Environment Variables**: (none required for basic setup)
- **Tier**: Free tier (512 MB RAM)

### 3. Important Configuration
- **Root Directory**: Leave blank (default)
- **Python Version**: 3.10 or higher
- **Gunicorn Settings**:
  - Workers: `1` (free tier limitation)
  - Threads: `2` (for concurrent requests)
  - Timeout: `300` seconds (for long music generation requests)
  - Max requests: `1000` (memory leak prevention)

### 4. Frontend Configuration
Set environment variable in Vercel:
```
VITE_API_URL = https://your-render-domain.onrender.com
```

## API Endpoints

### Authentication

**POST /signup**
```json
{
  "fullName": "John Doe",
  "username": "johndoe",
  "email": "john@example.com",
  "password": "password123"
}
```

**POST /signin**
```json
{
  "username": "johndoe",
  "password": "password123"
}
```

### Music Generation

**POST /studio-generate**
```json
{
  "prompt": "Calm ambient music",
  "duration": 20,
  "mood": "Happy",
  "tempo": 120,
  "instruments": "piano",
  "username": "johndoe",
  "use_colab": true,
  "colab_url": "https://your-colab-endpoint.com/api/generate"
}
```
Response: Audio MP3 file (binary)

**POST /save-history**
```json
{
  "username": "johndoe",
  "prompt": "Calm music",
  "mood": "Happy",
  "instruments": "piano",
  "tempo": 120,
  "duration": 20
}
```

**GET /get-history/<username>**
Returns: Array of music generation history

### Monitoring

**GET /health**
Returns: `{"status": "ok", "service": "AI Music Backend"}`

## Performance Optimizations

1. **No ML Libraries**: Saves ~500MB RAM
2. **Single Worker**: Prevents memory issues on free tier
3. **Gunicorn Threads**: Handles multiple concurrent requests
4. **Request Timeout**: 300 seconds for long music generations
5. **SQLite**: Lightweight database (no PostgreSQL needed)
6. **BytesIO**: Streams audio without disk I/O

## External ML Service Integration

The `/studio-generate` endpoint expects an external ML service (Colab/Gradio) that:

1. Accepts POST request with JSON body:
```json
{
  "prompt": "string",
  "duration": "int",
  "mood": "string",
  "tempo": "int",
  "instruments": "string"
}
```

2. Returns HTTP 200 with audio/mp3 content

Example Colab setup:
```python
import gradio as gr
from music_generation_model import generate_music

def generate(prompt, duration, mood, tempo, instruments):
    return generate_music(prompt, duration, mood, tempo, instruments)

gr.Interface(generate, ...).launch(share=True)
```

## Troubleshooting

**Memory Issue on Render**
- Already optimized! No ML libraries = ~50MB base usage
- Gunicorn with 1 worker handles this automatically

**Slow Music Generation**
- This is normal for ML models
- Colab/Gradio endpoint may take 30-120 seconds
- Frontend should show loading indicator

**Database Lock Errors**
- SQLite + concurrent requests = rare locks
- Render uses ephemeral filesystem (data cleared on redeploy)
- Use external database (PostgreSQL) for production

**External Service Timeout**
- Default: 300 seconds
- Increase in Procfile if needed: `--timeout 600`

## Database Notes

- **users.db**: Stored in `/tmp` (ephemeral on Render)
- **music_history.db**: Also in `/tmp`
- **On Redeploy**: Data is cleared (expected behavior for free tier)
- **For Production**: Migrate to external PostgreSQL

## Next Steps

1. ✅ Push to GitHub
2. ✅ Deploy on Render
3. ✅ Get Render backend URL (e.g., `https://ai-music-backend.onrender.com`)
4. ✅ Set `VITE_API_URL` in Vercel frontend
5. ✅ Test signup → signin → music generation flow
