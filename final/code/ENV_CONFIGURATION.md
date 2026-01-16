# Environment Configuration for Deployment

## Overview
The frontend code has been updated to use environment variables for backend API URLs instead of hard-coded values. This allows for seamless deployment to different environments (local, staging, production).

## Environment Variables

### For Vite Applications
Vite uses `import.meta.env` to access environment variables. All variables must be prefixed with `VITE_` to be exposed to the client.

### Required Variables

#### 1. **VITE_API_URL** (Music Generation & History API)
- **Purpose**: Base URL for music generation, history storage, and retrieval
- **Used in**: `Studio.jsx`, `History.jsx`
- **Endpoints**:
  - `POST /studio-generate` - Generate music
  - `POST /save-history` - Save to history
  - `GET /get-history/:username` - Retrieve history
- **Example**: `https://api.yourdomain.com` or `http://127.0.0.1:8000`

#### 2. **VITE_AUTH_API_URL** (Authentication API)
- **Purpose**: Base URL for user authentication
- **Used in**: `SignUp.jsx`, `SignIn.jsx`
- **Endpoints**:
  - `POST /signup` - User registration
  - `POST /signin` - User login
- **Example**: `https://auth.yourdomain.com` or `http://127.0.0.1:5000`

## Setup Instructions

### Local Development

1. Create a `.env.local` file in the `final/code/` directory:
   ```bash
   VITE_API_URL=http://127.0.0.1:8000
   VITE_AUTH_API_URL=http://127.0.0.1:5000
   ```

2. Start your development server:
   ```bash
   npm install
   npm run dev
   ```

### Vercel Deployment

1. Go to your Vercel project settings
2. Navigate to **Settings → Environment Variables**
3. Add the following variables:
   - `VITE_API_URL`: Your production API URL
   - `VITE_AUTH_API_URL`: Your production auth API URL

4. Deploy as usual:
   ```bash
   vercel
   ```

### Other Deployment Platforms

For platforms like Netlify, AWS Amplify, etc.:

1. **Netlify**: Add environment variables in **Site settings → Build & deploy → Environment**
2. **AWS Amplify**: Add variables in **App settings → Environment variables**
3. **Docker**: Use build args or runtime env vars
4. **Traditional hosting**: Set env variables in your build process

## Files Modified

1. **src/pages/Studio.jsx**
   - Added: `const API = import.meta.env.VITE_API_URL || null;`
   - Updated 3 fetch calls to use template literals
   - Added null checks before API calls

2. **src/pages/History.jsx**
   - Added: `const API = import.meta.env.VITE_API_URL || null;`
   - Updated 1 fetch call to use template literals
   - Added null check before API call

3. **src/pages/SignUp.jsx**
   - Added: `const AUTH_API = import.meta.env.VITE_AUTH_API_URL || null;`
   - Updated 1 fetch call to use template literals
   - Added null check before API call

4. **src/pages/SignIn.jsx**
   - Added: `const AUTH_API = import.meta.env.VITE_AUTH_API_URL || null;`
   - Updated 1 fetch call to use template literals
   - Added null check before API call

## Safety Features

All API calls now include safety checks:

```javascript
if (!API) {
  console.warn("API URL not configured");
  return;
}
```

or for user-facing errors:

```javascript
if (!API) {
  setError("Backend API is not configured. Please set VITE_API_URL.");
  return;
}
```

This prevents runtime errors when environment variables are not configured.

## Testing

### Test Configuration
1. Run with local backend:
   ```bash
   VITE_API_URL=http://localhost:8000 VITE_AUTH_API_URL=http://localhost:5000 npm run dev
   ```

2. Run with production URLs:
   ```bash
   VITE_API_URL=https://api.yourdomain.com VITE_AUTH_API_URL=https://auth.yourdomain.com npm run dev
   ```

### Verify in Browser
Open browser DevTools and check:
1. Network tab to verify correct endpoints are being called
2. Console for any warnings about unconfigured APIs

## CORS Configuration

When deploying to production, ensure your backend CORS settings allow requests from your frontend domain:

```python
# Example Python/Flask
from flask_cors import CORS
CORS(app, resources={
    r"/api/*": {
        "origins": ["https://yourdomain.com", "https://www.yourdomain.com"],
        "allow_headers": ["Content-Type"],
        "methods": ["GET", "POST"]
    }
})
```

## Troubleshooting

### Issue: "Backend API is not configured"
- **Cause**: Environment variable not set
- **Solution**: Verify `VITE_API_URL` is set in your environment

### Issue: API calls failing with 404/CORS errors
- **Cause**: Incorrect API URL or CORS not configured
- **Solution**: Check environment variables and backend CORS settings

### Issue: Environment variables not loading
- **Cause**: Server not restarted after `.env` changes
- **Solution**: Restart your development server (`npm run dev`)

## Migration from Hard-Coded URLs

If you previously had hard-coded URLs:
- Old: `fetch("http://127.0.0.1:8000/studio-generate")`
- New: `fetch(\`${API}/studio-generate\`)`

This change makes the application more flexible and production-ready.
