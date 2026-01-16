# Vercel Deployment Guide

## Quick Deployment (5 minutes)

### Step 1: Prepare Your Code
```bash
cd final/code
git add .
git commit -m "Configure environment variables for deployment"
git push
```

### Step 2: Set Up Vercel Project

1. Go to [vercel.com](https://vercel.com)
2. Click **"Add New..." → "Project"**
3. Select your GitHub repository
4. Click **"Import"**

### Step 3: Configure Environment Variables

Before clicking **"Deploy"**:

1. Click **"Environment Variables"**
2. Add two variables:

   **Variable 1:**
   - **Name:** `VITE_API_URL`
   - **Value:** `https://your-api-domain.com` (or your production API URL)
   - **Environments:** Select all (Production, Preview, Development)

   **Variable 2:**
   - **Name:** `VITE_AUTH_API_URL`
   - **Value:** `https://your-auth-domain.com` (or your production auth URL)
   - **Environments:** Select all (Production, Preview, Development)

3. Click **"Save"**

### Step 4: Deploy

Click the **"Deploy"** button and wait for the deployment to complete.

### Step 5: Test Your Deployment

Once deployment is complete:

1. Click **"Visit"** to open your site
2. Test these features:
   - Navigate to **Sign Up** and try registering a user
   - Navigate to **Sign In** and try logging in
   - Go to **Studio** and try generating music
   - Check **History** to view generated tracks

---

## Updating Environment Variables Later

If your API URLs change:

1. Go to Vercel Dashboard
2. Select your project
3. Go to **Settings → Environment Variables**
4. Edit the values
5. All new deployments will use the updated URLs

---

## Troubleshooting

### Issue: "Backend API is not configured"

**Cause:** Environment variable not set correctly

**Solution:**
1. Check Vercel Dashboard > Settings > Environment Variables
2. Verify `VITE_API_URL` is exactly correct (include https://)
3. Redeploy or wait for the next automatic deployment

### Issue: Sign-up/Sign-in fails with 404

**Cause:** `VITE_AUTH_API_URL` not set or incorrect

**Solution:**
1. Check Vercel Dashboard > Environment Variables
2. Verify `VITE_AUTH_API_URL` is set and correct
3. Check your backend auth service is running

### Issue: Music generation fails

**Cause:** `VITE_API_URL` not set or backend unreachable

**Solution:**
1. Check Vercel Dashboard > Environment Variables
2. Verify `VITE_API_URL` is set and correct
3. Check your backend API is accessible from Vercel IPs
4. Verify CORS is configured in your backend

### Issue: Environment variables not taking effect

**Solution:**
1. Check that variables are set in the correct environment (Production)
2. Trigger a redeployment:
   - Go to Deployments tab
   - Click the latest deployment
   - Click "Redeploy"
3. Wait for the new deployment to complete

---

## Alternative Deployment Options

### Docker Deployment
```bash
# Set environment variables
export VITE_API_URL=https://your-api-domain.com
export VITE_AUTH_API_URL=https://your-auth-domain.com

# Build
npm run build

# Run locally
npm run preview
```

### Traditional Server (Apache, Nginx)
```bash
# Build
npm run build

# Copy dist/ folder to your web server
cp -r dist/* /var/www/html/

# Set environment variables in your deployment process
```

---

## Environment Variable Configuration

### For Different Environments

**Development:**
```
VITE_API_URL=http://localhost:8000
VITE_AUTH_API_URL=http://localhost:5000
```

**Staging:**
```
VITE_API_URL=https://api-staging.yourdomain.com
VITE_AUTH_API_URL=https://auth-staging.yourdomain.com
```

**Production:**
```
VITE_API_URL=https://api.yourdomain.com
VITE_AUTH_API_URL=https://auth.yourdomain.com
```

---

## Monitoring & Debugging

### View Deployment Logs
1. Go to Vercel Dashboard
2. Select your project
3. Click **Deployments**
4. Click on a deployment
5. Click **"Logs"** to see build and runtime logs

### Check Runtime Environment
1. Open browser DevTools (F12)
2. Go to **Console** tab
3. Look for any warnings about unconfigured APIs
4. Check **Network** tab to verify correct API endpoints

---

## Performance Tips

1. **CDN:** Vercel automatically uses Vercel Edge Network
2. **Caching:** Static assets are cached globally
3. **Analytics:** Enable Web Analytics in Vercel Dashboard to monitor performance

---

## Next Steps

1. ✅ Set environment variables
2. ✅ Deploy to Vercel
3. ✅ Test all functionality
4. ✅ Monitor error logs
5. ✅ Set up domain (custom domain setup in Vercel Settings)

---

## Need Help?

- **Vercel Docs:** https://vercel.com/docs
- **Vite Docs:** https://vitejs.dev
- **Your Backend API:** Ensure it's accessible from Vercel IPs and has CORS configured

---

**Happy Deploying! 🚀**
