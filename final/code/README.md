MuseAI Frontend v3 — Enhanced visuals & Studio page

## Quick Start

### Local Development
1. Clone the repository
2. `cd` into this folder (`final/code`)
3. Copy `.env.example` to `.env.local` and configure API URLs:
   ```bash
   cp .env.example .env.local
   # Edit .env.local with your local backend URLs
   ```
4. `npm install`
5. `npm run dev`

### Production Deployment (Vercel)
1. Push to your GitHub repository
2. Connect to Vercel and set environment variables:
   - `VITE_API_URL`: Your production API domain
   - `VITE_AUTH_API_URL`: Your production auth domain
3. Deploy: `vercel deploy`

## Pages & Features
- **Home**: minimal hero + featured grid (20 items)
- **Studio** (`/studio`): music generation with mood selection, tempo control, instrument choice, history management
- **About**: workflow overview, 20 features list
- **History**: music library with generated tracks
- **Profile**: user account and settings
- **Sign Up/Sign In**: user authentication

## Environment Variables

Create a `.env.local` file with:
```
VITE_API_URL=http://127.0.0.1:8000
VITE_AUTH_API_URL=http://127.0.0.1:5000
```

See `ENV_CONFIGURATION.md` for detailed setup instructions.

## API Endpoints

**Music & History** (VITE_API_URL):
- `POST /studio-generate` - Generate music
- `POST /save-history` - Save to history
- `GET /get-history/:username` - Retrieve history

**Authentication** (VITE_AUTH_API_URL):
- `POST /signup` - Register user
- `POST /signin` - Login user

## Build & Deploy
```bash
npm run build        # Build for production
npm run preview      # Preview production build locally
```

For more information, see `DEPLOYMENT_SUMMARY.md` and `ENV_CONFIGURATION.md`
