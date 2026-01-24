# Deploy /studio-generate Fix to Render

## Quick Deployment Steps

### 1. Update Code on Render

**Option A: Git Push**
```bash
# In your local workspace
cd d:\Internship Project\AI-MUSIC-COMPOSITION\final\code

# Commit changes
git add python-core/studio_api.py
git commit -m "Fix 500 error in /studio-generate: handle HF response format, add retry logic, improve error handling"
git push origin main
# Render auto-deploys
```

**Option B: Manual Upload (if no git)**
- Go to Render Dashboard → Services → Your Python Backend Service
- Click "Manual Deploy" if git is not connected
- Upload updated `python-core/studio_api.py`

### 2. Verify Environment Variables in Render

In Render Dashboard:
1. Go to your service
2. Settings → Environment
3. Ensure `HF_API_URL` is set correctly

**Example value:**
```
HF_API_URL=https://api-inference.huggingface.co/models/facebook/musicgen-small/run/predict
```

Or if using a custom Gradio Space:
```
HF_API_URL=https://huggingface.co/spaces/[USERNAME]/[SPACE-NAME]/run/predict
```

### 3. Monitor Deployment

```bash
# Via Render CLI
render logs --service=your-service-name

# Or watch logs in Dashboard: Services → Logs
```

**Expected success log:**
```
2026-01-24 10:30:45 python-core/studio_api.py loaded
2026-01-24 10:30:46 Starting server on 0.0.0.0:PORT
2026-01-24 10:30:50 [Attempt 1] Calling HF API: https://...
2026-01-24 10:30:52 HF Response Status: 200
2026-01-24 10:30:52 ✅ Decoded audio: 44100 bytes
```

### 4. Test Endpoint (After Deploy)

```bash
curl -X POST https://your-service.render.com/studio-generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Calm electronic music",
    "duration": 10,
    "mood": "Relaxing",
    "tempo": 90,
    "instruments": "synth",
    "username": "test"
  }'
```

**Expected response:**
- Status: **200**
- Body: **Binary WAV audio file** (can play in browser)

**If still getting 500:**
- Check Render logs for specific error
- Verify `HF_API_URL` is correct and accessible
- Test HF API manually: `curl HF_API_URL` with test data

---

## What Changed

### Before (Broken)
```python
result = response.json()
audio_bytes = base64.b64decode(result["data"][0])  # ❌ Crashes if result["data"][0] is a dict
```

### After (Fixed)
```python
result = response.json()
audio_b64, error = extract_audio_from_hf_response(result)  # ✅ Handles dict or string
if error:
    return jsonify({"error": "..."}), 502

try:
    audio_bytes = base64.b64decode(audio_b64)  # ✅ Wrapped in try/except
except Exception as e:
    print(f"Base64 decode failed: {e}")
    return jsonify({"error": "..."}), 502
```

---

## Key Improvements

| Issue | Old | New |
|-------|-----|-----|
| **Response parsing** | No validation | Safe extraction with helper function |
| **Base64 decoding** | No error handling | Try/except + validation |
| **Timeout** | 120s (too long) | 60s + retry logic |
| **Logging** | Generic `str(e)` | Detailed error types and context |
| **Input validation** | None | Duration 5-30s range check |
| **Status codes** | All errors = 500 | 400/502/503/504 for specific issues |
| **HTTP headers** | Missing Content-Length | Added Content-Length + Cache-Control |

---

## Rollback (If Needed)

If the update causes issues:
1. In Render Dashboard, click "Redeploy" on previous build
2. Or revert git commit and push

---

## Support

If `/studio-generate` still returns 500 after deployment:
1. Check Render logs for exact error message
2. Verify HF API is accessible (test directly)
3. Ensure duration parameter is 5-30 seconds
4. Check that `HF_API_URL` environment variable is set
