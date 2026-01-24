# Fix for /studio-generate 500 Error on Render

## Summary of Issues Fixed

### 1. **Incorrect HF Response Format Handling** ⚠️ CRITICAL
**Problem:** The original code assumed `result["data"][0]` would be a base64 string, but HF Gradio actually returns nested objects.

**HF Response Formats (actual):**
```json
// Format 1: Nested object (most common)
{
  "data": [
    {
      "name": "audio.wav",
      "data": "UklGRiY..."  // base64 string
    }
  ]
}

// Format 2: Direct array
{
  "data": ["UklGRiY..."]
}
```

**Original code crashed on Format 1** because `result["data"][0]` returns a dict, not a string.

**Fix:** Added `extract_audio_from_hf_response()` helper that handles both formats safely.

---

### 2. **No Base64 Decoding Error Handling**
**Problem:** If the base64 string is malformed, `base64.b64decode()` crashes without catching it.

**Fix:** Wrapped in try/except block with detailed logging:
```python
try:
    # Remove data URI prefix if present (e.g., "data:audio/wav;base64,")
    if "," in audio_b64:
        audio_b64 = audio_b64.split(",", 1)[1]
    
    audio_bytes = base64.b64decode(audio_b64)
    print(f"✅ Decoded audio: {len(audio_bytes)} bytes")
    
    # Validate audio data (WAV files start with RIFF)
    if not audio_bytes.startswith(b'RIFF'):
        print(f"⚠️ Warning: Audio doesn't start with RIFF, may not be valid WAV")
        
except Exception as e:
    print(f"Base64 decode failed: {e}")
    return jsonify({"error": "Failed to decode audio data"}), 502
```

---

### 3. **Missing HF Response Validation**
**Problem:** No validation that the JSON response has the expected structure before trying to access keys.

**Fix:** 
- Check `response.status_code != 200` and return 502 (Bad Gateway)
- Check `response.json()` doesn't throw an exception
- Use helper function to safely extract nested values
- Log HF response details for debugging

---

### 4. **Timeout Too Long for Render Free Tier**
**Problem:** 120-second timeout is too long on Render free tier. May cause dyno hibernation.

**Fix:**
- Reduced timeout from **120s → 60s**
- Added **retry logic** (max 2 attempts with 2-second wait)
- Handles `requests.Timeout` and `requests.RequestException` separately
- Returns 504 (Gateway Timeout) if both retries fail

```python
for attempt in range(max_retries):
    try:
        response = requests.post(
            hf_url,
            json={"data": [prompt, duration]},
            timeout=60,  # Reduced from 120
            headers={"Content-Type": "application/json"}
        )
```

---

### 5. **Missing send_file Content-Length Header**
**Problem:** `send_file(BytesIO())` may not include `Content-Length` header, causing streaming issues.

**Fix:**
```python
response_obj = send_file(
    audio_io,
    mimetype="audio/wav",
    as_attachment=False,
    download_name="generated_music.wav"
)
response_obj.headers["Content-Length"] = len(audio_bytes)
response_obj.headers["Cache-Control"] = "no-cache"
return response_obj
```

---

### 6. **Missing Environment Variable Validation**
**Problem:** If `HF_API_URL` is missing, error message was vague.

**Fix:** Returns 503 (Service Unavailable) with clear message:
```python
hf_url = os.environ.get("HF_API_URL")
if not hf_url:
    print("ERROR: HF_API_URL environment variable not set")
    return jsonify({"error": "Music service not configured"}), 503
```

---

### 7. **No Input Validation**
**Problem:** No checks on duration, which could cause HF API errors.

**Fix:** Added duration validation:
```python
if duration < 5 or duration > 30:
    return jsonify({"error": "Duration must be between 5-30 seconds"}), 400
```

---

### 8. **Poor Error Logging**
**Problem:** Original catch-all exception just prints to console, no useful debugging info.

**Fix:** Added comprehensive logging:
```python
except ValueError as e:
    print(f"Validation error: {e}")
    return jsonify({"error": f"Invalid input: {str(e)}"}), 400
except Exception as e:
    print(f"❌ Studio generate error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    return jsonify({"error": "An unexpected error occurred"}), 500
```

---

## Testing Checklist

### On Render (Production)
```bash
# 1. Check logs for startup
# Go to Render dashboard → Logs tab

# 2. Test /health endpoint
curl https://your-render-url/health

# 3. Test /studio-generate with valid inputs
curl -X POST https://your-render-url/studio-generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Calm piano",
    "duration": 10,
    "mood": "Relaxing",
    "tempo": 80,
    "instruments": "piano",
    "username": "test"
  }'
```

### Environment Variables Required
In Render dashboard, set:
```
HF_API_URL=https://api-inference.huggingface.co/models/[MODEL]/run/predict
```

Replace `[MODEL]` with your Hugging Face Gradio Space URL.

---

## HTTP Status Codes Now Returned

| Endpoint | Status | Meaning |
|----------|--------|---------|
| `/studio-generate` | 200 | ✅ Audio generated successfully |
| `/studio-generate` | 400 | ❌ Invalid input (duration out of range) |
| `/studio-generate` | 502 | ❌ HF API returned non-200 or invalid response |
| `/studio-generate` | 503 | ❌ `HF_API_URL` environment variable not set |
| `/studio-generate` | 504 | ❌ Request timeout (HF service slow/overloaded) |
| `/studio-generate` | 500 | ❌ Unexpected error in Flask code |

---

## Debug Render Logs

When `/studio-generate` returns 500, check **Render logs**:

```
[Attempt 1] Calling HF API: https://api-inference.huggingface.co/models/...
HF Response Status: 200
HF Response keys: dict_keys(['data'])
✅ Decoded audio: 44100 bytes
✅ Saved history for user: test_user
```

If you see errors:
```
Cannot extract audio: 'data' is not a non-empty list
Failed to parse HF response as JSON: ...
Base64 decode failed: ...
Request timeout after 60s
```

These are **caught and logged** — they return proper 502/504 status codes instead of 500.

---

## Performance Tuning for Render Free Tier

1. **Timeout:** 60s (down from 120s) ✅
2. **Retry:** 2 attempts with 2s backoff ✅
3. **Duration validation:** 5-30 seconds ✅
4. **Database:** SQLite in `/tmp` (ephemeral storage) ✅
5. **No dependencies:** No TensorFlow, large ML models ✅

---

## Frontend Integration

Your frontend can now properly handle these status codes:

```javascript
async function generateMusic(params) {
  try {
    const response = await fetch('/studio-generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params)
    });

    if (response.status === 200) {
      // Audio blob is ready
      const audioBlob = await response.blob();
      // Play or download
      const url = URL.createObjectURL(audioBlob);
      return url;
    } else if (response.status === 503) {
      // Service not configured
      console.error('Music service not available');
    } else if (response.status === 504) {
      // Retry with longer timeout or different duration
      console.error('Music generation timeout - try shorter duration');
    } else if (response.status === 502) {
      // HF API error
      console.error('Music service error');
    } else if (response.status === 400) {
      const error = await response.json();
      console.error('Invalid input:', error.error);
    }
  } catch (error) {
    console.error('Network error:', error);
  }
}
```

---

## Related Files Modified
- `python-core/studio_api.py` — Fixed `/studio-generate` endpoint
- No changes needed to `requirements.txt` (all dependencies present)

---

## Next Steps
1. Deploy updated `studio_api.py` to Render
2. Verify `HF_API_URL` environment variable is set
3. Test `/studio-generate` endpoint
4. Monitor Render logs for any residual issues
5. Check that audio files are valid WAV format
