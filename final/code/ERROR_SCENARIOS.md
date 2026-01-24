# Exact Error Scenarios & How They're Fixed

## Scenario 1: HF Returns Nested Object Format ❌ → ✅

### What Happens (Original Code)
```python
# HF Response:
# {
#   "data": [
#     {
#       "name": "audio.wav",
#       "data": "UklGRiY4AABXQVZFZm10..."
#     }
#   ]
# }

result = response.json()  # OK
audio_bytes = base64.b64decode(result["data"][0])  # ❌ CRASH!
# result["data"][0] = {"name": "audio.wav", "data": "..."}
# Can't base64 decode a dict!
```

**Error in Render logs:**
```
TypeError: string argument without an encoding
Traceback:
  File "studio_api.py", line 178, in studio_generate
    audio_bytes = base64.b64decode(result["data"][0])
TypeError: string argument without an encoding
```

**Response to client:** 500 (caught by generic except)

---

### How It's Fixed (New Code)
```python
audio_b64, extraction_error = extract_audio_from_hf_response(result)
# extract_audio_from_hf_response() checks:
# 1. Is result a dict? ✓
# 2. Does result have "data" key? ✓
# 3. Is data a non-empty list? ✓
# 4. Is data[0] a dict with "data" field? ✓ → Extract it!
# 5. Or is data[0] a string? → Use it directly!

if extraction_error:
    print(f"Cannot extract audio: {extraction_error}")
    return jsonify({"error": "Invalid audio data from music service"}), 502

try:
    audio_bytes = base64.b64decode(audio_b64)  # ✓ Works!
except Exception as e:
    print(f"Base64 decode failed: {e}")
    return jsonify({"error": "Failed to decode audio data"}), 502
```

**Response to client:** 502 (Bad Gateway) with clear error message

---

## Scenario 2: Malformed Base64 String ❌ → ✅

### What Happens (Original Code)
```python
result = response.json()  # {"data": ["not-valid-base64!!!!"]}
audio_bytes = base64.b64decode(result["data"][0])  # ❌ CRASH!
# binascii.Error: Incorrect padding
```

**Error in Render logs:**
```
binascii.Error: Incorrect padding
```

**Response to client:** 500

---

### How It's Fixed (New Code)
```python
try:
    # Remove data URI prefix if present
    if "," in audio_b64:
        audio_b64 = audio_b64.split(",", 1)[1]
    
    audio_bytes = base64.b64decode(audio_b64)
    print(f"✅ Decoded audio: {len(audio_bytes)} bytes")
    
except Exception as e:
    print(f"Base64 decode failed: {e}")  # ← Logs the exact error
    return jsonify({"error": "Failed to decode audio data"}), 502  # ← Returns 502
```

**Response to client:** 502 (Bad Gateway)

---

## Scenario 3: HF API Timeout (Default 120s) ❌ → ✅

### What Happens (Original Code)
```python
# Render free tier may be slow
response = requests.post(
    hf_url,
    json={"data": [prompt, duration]},
    timeout=120  # Waits 2 minutes!
)
# After 120 seconds:
# requests.exceptions.ConnectTimeout
```

**Error in Render logs:**
```
ConnectTimeout: HTTPConnection pool is full, discarding connection
```

**Response to client:** 500 (caught by generic except)

**Problem:** By the time timeout happens, user is waiting 2 minutes + API still processing!

---

### How It's Fixed (New Code)
```python
max_retries = 2
for attempt in range(max_retries):
    try:
        response = requests.post(
            hf_url,
            json={"data": [prompt, duration]},
            timeout=60,  # ← Only wait 60 seconds
            headers={"Content-Type": "application/json"}
        )
        # ... process response ...
        
    except requests.Timeout:
        print(f"[Attempt {attempt + 1}] Request timeout after 60s")
        if attempt < max_retries - 1:
            time.sleep(2)  # Wait 2 seconds before retry
            continue  # ← Retry once
        return jsonify({"error": "Music generation timed out"}), 504  # ← Returns 504
    except requests.RequestException as e:
        # ... handle other request errors ...
```

**Benefits:**
1. First attempt fails at 60s (not 120s)
2. Automatically retries once (user gets another chance)
3. Returns **504 Gateway Timeout** (not 500)
4. Frontend can show "Service busy, please try again"

---

## Scenario 4: Missing HF_API_URL Environment Variable ❌ → ✅

### What Happens (Original Code)
```python
hf_url = os.environ.get("HF_API_URL")
if not hf_url:
    return jsonify({"error": "HF_API_URL not set"}), 500  # ❌ Wrong status code
```

**Response to client:** 500 (implies Flask code error, not infrastructure issue)

**Frontend gets confused:** "Is the backend broken?" vs "Is the service not configured?"

---

### How It's Fixed (New Code)
```python
hf_url = os.environ.get("HF_API_URL")
if not hf_url:
    print("ERROR: HF_API_URL environment variable not set")
    return jsonify({"error": "Music service not configured"}), 503  # ✅ Service Unavailable
```

**Response to client:** 503 (clearly indicates service not ready)

**Frontend knows:** "Service isn't configured, check deployment"

---

## Scenario 5: HF API Returns Invalid JSON ❌ → ✅

### What Happens (Original Code)
```python
result = response.json()  # ❌ Crash if not JSON!
# JSONDecodeError: Expecting value: line 1 column 1
```

**Error in Render logs:**
```
json.decoder.JSONDecodeError: Expecting value: line 1 column 1
```

**Response to client:** 500

---

### How It's Fixed (New Code)
```python
try:
    result = response.json()
    print(f"HF Response keys: {result.keys() if isinstance(result, dict) else 'not a dict'}")
except Exception as e:
    print(f"Failed to parse HF response as JSON: {e}")
    return jsonify({"error": "Invalid response from music service"}), 502  # ✅ Returns 502
```

**Response to client:** 502 (Bad Gateway)

---

## Scenario 6: Invalid Duration Parameter ❌ → ✅

### What Happens (Original Code)
```python
duration = int(data.get("duration", 12))  # Could be 1000, 0, negative!
# No validation!

response = requests.post(
    hf_url,
    json={"data": [prompt, duration]},  # ← HF might silently fail or timeout
    timeout=120
)
# HF returns an error, or takes too long
```

**Response to client:** 500 or timeout

---

### How It's Fixed (New Code)
```python
duration = int(data.get("duration", 12))

# ✅ Validate input BEFORE calling HF
if duration < 5 or duration > 30:
    return jsonify({"error": "Duration must be between 5-30 seconds"}), 400  # ✅ Returns 400

# Now we know duration is safe for HF API
response = requests.post(
    hf_url,
    json={"data": [prompt, duration]},
    timeout=60
)
```

**Benefits:**
1. Invalid input caught immediately (not sent to HF)
2. Returns **400 Bad Request** (not 500)
3. Frontend can validate on client-side too

---

## Scenario 7: Audio Response Missing Content-Length Header ❌ → ✅

### What Happens (Original Code)
```python
return send_file(
    BytesIO(audio_bytes),
    mimetype="audio/wav",
    as_attachment=False
)
# Browser doesn't know audio size
# Streaming playback may fail
# Progress bar shows unknown length
```

**Browser behavior:**
- Audio player shows "0:00 / Unknown" duration
- May struggle to play if length unknown
- Seeking might not work

---

### How It's Fixed (New Code)
```python
audio_io = BytesIO(audio_bytes)
audio_io.seek(0)
response_obj = send_file(
    audio_io,
    mimetype="audio/wav",
    as_attachment=False,
    download_name="generated_music.wav"
)
response_obj.headers["Content-Length"] = len(audio_bytes)  # ✅ Add header
response_obj.headers["Cache-Control"] = "no-cache"  # ✅ Don't cache
return response_obj
```

**Benefits:**
1. Browser knows exact audio size
2. Progress bar shows correct duration
3. Seeking works properly
4. Audio plays reliably

---

## Scenario 8: Generic Exception Logging ❌ → ✅

### What Happens (Original Code)
```python
except Exception as e:
    print("Studio generate error:", e)  # Just prints error message
    return jsonify({"error": str(e)}), 500

# If error is: "list index out of range"
# Render logs show: "Studio generate error: list index out of range"
# Unclear where this is happening!
```

**In Render logs:**
```
Studio generate error: list index out of range
```

**Problem:** Can't debug where the error occurred!

---

### How It's Fixed (New Code)
```python
except ValueError as e:
    print(f"Validation error: {e}")
    return jsonify({"error": f"Invalid input: {str(e)}"}), 400
except Exception as e:
    print(f"❌ Studio generate error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()  # ← Full traceback!
    return jsonify({"error": "An unexpected error occurred"}), 500
```

**In Render logs:**
```
❌ Studio generate error: TypeError: unsupported operand type(s) for +: 'int' and 'str'
Traceback (most recent call last):
  File "studio_api.py", line 156, in studio_generate
    prompt = f"... {tempo + " BPM"} ..."
TypeError: unsupported operand type(s) for +: 'int' and 'str'
```

**Benefits:**
1. Error type clearly shown (TypeError, IndexError, etc.)
2. Full traceback shows line number
3. Can immediately identify and fix the bug

---

## Summary: 500 Error Status Code Distribution (After Fix)

| Original Behavior | Fixed Behavior | Improvement |
|---|---|---|
| 500 from HF response error | 502 Bad Gateway | ✅ Clearer error type |
| 500 from timeout | 504 Gateway Timeout | ✅ Retry + clearer error |
| 500 from config error | 503 Service Unavailable | ✅ Clearer error type |
| 500 from invalid input | 400 Bad Request | ✅ Validation added |
| 500 from JSON parse error | 502 Bad Gateway | ✅ Clearer error type |
| 500 from base64 error | 502 Bad Gateway | ✅ Clearer error type |
| Random 500 from generic except | Specific status code | ✅ Meaningful response |

**Result:** 500 errors replaced with meaningful status codes and better logging! 🎉
