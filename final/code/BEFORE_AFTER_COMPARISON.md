# Before & After Code Comparison

## The Broken /studio-generate (Original)

```python
@app.route("/studio-generate", methods=["POST"])
def studio_generate():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON body"}), 400

        base_prompt = data.get("prompt", "Calm music")
        duration = int(data.get("duration", 12))
        mood = data.get("mood", "Happy")
        tempo = int(data.get("tempo", 120))
        instruments = data.get("instruments", "piano")
        username = data.get("username", "guest")

        prompt = (
            f"{base_prompt}. "
            f"Mood: {mood}. "
            f"Tempo: {tempo} BPM. "
            f"Instrument: {instruments}."
        )

        hf_url = os.environ.get("HF_API_URL")
        if not hf_url:
            return jsonify({"error": "HF_API_URL not set"}), 500  # ❌ Should be 503

        # ❌ PROBLEM 1: 120s timeout too long for Render free tier
        response = requests.post(
            hf_url,
            json={"data": [prompt, duration]},
            timeout=120  # ❌ TOO LONG
            # ❌ No retry logic
        )

        # ❌ PROBLEM 2: No error handling for non-200 status
        if response.status_code != 200:
            return jsonify({"error": "Hugging Face inference failed"}), 500  # ❌ Too generic

        # ❌ PROBLEM 3: Assumes result["data"][0] is a string
        #    But HF returns: {"data": [{"name": "audio.wav", "data": "base64..."}]}
        result = response.json()
        audio_bytes = base64.b64decode(result["data"][0])  # ❌ CRASHES HERE
        
        # ❌ PROBLEM 4: No error handling for base64 decode

        # save history (non-blocking)
        try:
            conn = sqlite3.connect(MUSIC_DB_PATH)
            c = conn.cursor()
            c.execute(
                """
                INSERT INTO music_history
                (username, prompt, mood, instruments, tempo, duration)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (username, base_prompt, mood, instruments, tempo, duration)
            )
            conn.commit()
            conn.close()
        except Exception as e:
            print("History save failed:", e)

        # ❌ PROBLEM 5: Missing Content-Length header
        return send_file(
            BytesIO(audio_bytes),
            mimetype="audio/wav",
            as_attachment=False
        )

    except Exception as e:
        # ❌ PROBLEM 6: Generic error logging, no details
        print("Studio generate error:", e)  # ❌ Doesn't show error type
        return jsonify({"error": str(e)}), 500  # ❌ All errors = 500
```

---

## The Fixed /studio-generate (Updated)

```python
def extract_audio_from_hf_response(result):
    """
    Safely extract base64 audio from HF Gradio response.
    Handles multiple response formats.
    ✅ NEW: Helper function to safely parse HF response
    """
    try:
        if not isinstance(result, dict):
            return None, f"Response is not a dict: {type(result)}"
        
        if "data" not in result:
            return None, f"Response missing 'data' key. Keys: {result.keys()}"
        
        data_list = result.get("data")
        if not isinstance(data_list, list) or len(data_list) == 0:
            return None, f"'data' is not a non-empty list: {type(data_list)}"
        
        data_item = data_list[0]
        
        # Format 1: {"name": "audio.wav", "data": "base64..."}
        if isinstance(data_item, dict):
            if "data" in data_item:
                return data_item["data"], None
            else:
                return None, f"Dict in 'data' has no 'data' key: {data_item.keys()}"
        
        # Format 2: ["base64..."]
        if isinstance(data_item, str):
            return data_item, None
        
        return None, f"Unexpected data format: {type(data_item)}"
    
    except Exception as e:
        return None, f"Exception extracting audio: {e}"


@app.route("/studio-generate", methods=["POST"])
def studio_generate():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON body"}), 400

        base_prompt = data.get("prompt", "Calm music")
        duration = int(data.get("duration", 12))
        mood = data.get("mood", "Happy")
        tempo = int(data.get("tempo", 120))
        instruments = data.get("instruments", "piano")
        username = data.get("username", "guest")

        # ✅ NEW: Input validation
        if duration < 5 or duration > 30:
            return jsonify({"error": "Duration must be between 5-30 seconds"}), 400

        prompt = (
            f"{base_prompt}. "
            f"Mood: {mood}. "
            f"Tempo: {tempo} BPM. "
            f"Instrument: {instruments}."
        )

        hf_url = os.environ.get("HF_API_URL")
        if not hf_url:
            print("ERROR: HF_API_URL environment variable not set")
            return jsonify({"error": "Music service not configured"}), 503  # ✅ FIXED: 503 instead of 500

        # ✅ NEW: Retry logic with reduced timeout
        max_retries = 2
        for attempt in range(max_retries):
            try:
                print(f"[Attempt {attempt + 1}] Calling HF API: {hf_url}")
                response = requests.post(
                    hf_url,
                    json={"data": [prompt, duration]},
                    timeout=60,  # ✅ FIXED: 60s instead of 120s
                    headers={"Content-Type": "application/json"}
                )
                
                print(f"HF Response Status: {response.status_code}")
                
                if response.status_code != 200:
                    error_msg = response.text[:200] if response.text else "No error details"
                    print(f"HF API Error: {error_msg}")
                    if attempt < max_retries - 1:
                        time.sleep(2)  # ✅ NEW: Wait before retry
                        continue
                    return jsonify({"error": f"Music generation failed (HTTP {response.status_code})"}), 502  # ✅ FIXED: 502 instead of 500
                
                # ✅ NEW: Parse and validate response structure
                try:
                    result = response.json()
                    print(f"HF Response keys: {result.keys() if isinstance(result, dict) else 'not a dict'}")
                except Exception as e:
                    print(f"Failed to parse HF response as JSON: {e}")
                    return jsonify({"error": "Invalid response from music service"}), 502  # ✅ FIXED: 502 instead of 500
                
                # ✅ NEW: Use safe extraction helper
                audio_b64, extraction_error = extract_audio_from_hf_response(result)
                
                if extraction_error:
                    print(f"Cannot extract audio: {extraction_error}")
                    print(f"Full response: {str(result)[:500]}")
                    return jsonify({"error": "Invalid audio data from music service"}), 502  # ✅ FIXED: 502 instead of 500
                
                # ✅ NEW: Decode base64 with error handling
                try:
                    # Remove data URI prefix if present (e.g., "data:audio/wav;base64,")
                    if "," in audio_b64:
                        audio_b64 = audio_b64.split(",", 1)[1]
                    
                    audio_bytes = base64.b64decode(audio_b64)
                    print(f"✅ Decoded audio: {len(audio_bytes)} bytes")
                    
                    # ✅ NEW: Validate audio data (WAV files start with RIFF)
                    if not audio_bytes.startswith(b'RIFF'):
                        print(f"⚠️ Warning: Audio doesn't start with RIFF, may not be valid WAV")
                    
                except Exception as e:
                    print(f"Base64 decode failed: {e}")
                    return jsonify({"error": "Failed to decode audio data"}), 502  # ✅ FIXED: 502 instead of 500
                
                # ✅ NEW: Success - save history (non-blocking)
                try:
                    conn = sqlite3.connect(MUSIC_DB_PATH)
                    c = conn.cursor()
                    c.execute(
                        """
                        INSERT INTO music_history
                        (username, prompt, mood, instruments, tempo, duration)
                        VALUES (?, ?, ?, ?, ?, ?)
                        """,
                        (username, base_prompt, mood, instruments, tempo, duration)
                    )
                    conn.commit()
                    conn.close()
                    print(f"✅ Saved history for user: {username}")
                except Exception as e:
                    print(f"⚠️ History save failed (non-blocking): {e}")
                
                # ✅ FIXED: Add Content-Length header and caching control
                audio_io = BytesIO(audio_bytes)
                audio_io.seek(0)
                response_obj = send_file(
                    audio_io,
                    mimetype="audio/wav",
                    as_attachment=False,
                    download_name="generated_music.wav"  # ✅ NEW
                )
                response_obj.headers["Content-Length"] = len(audio_bytes)  # ✅ NEW
                response_obj.headers["Cache-Control"] = "no-cache"  # ✅ NEW
                return response_obj
                
            except requests.Timeout:
                print(f"[Attempt {attempt + 1}] Request timeout after 60s")
                if attempt < max_retries - 1:
                    time.sleep(2)
                    continue
                return jsonify({"error": "Music generation timed out (service overloaded)"}), 504  # ✅ FIXED: 504 instead of 500
            except requests.RequestException as e:
                print(f"[Attempt {attempt + 1}] Request failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2)
                    continue
                return jsonify({"error": "Failed to connect to music service"}), 502  # ✅ FIXED: 502 instead of 500

    except ValueError as e:
        print(f"Validation error: {e}")
        return jsonify({"error": f"Invalid input: {str(e)}"}), 400  # ✅ NEW: 400 for validation
    except Exception as e:
        # ✅ FIXED: Better error logging with traceback
        print(f"❌ Studio generate error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": "An unexpected error occurred"}), 500
```

---

## Key Changes Summary

| Issue | Old | New | Impact |
|-------|-----|-----|--------|
| **HF response parsing** | Assumes string | Safe dict/string extraction | ❌ Crashes → ✅ 502 |
| **Base64 decoding** | No error handling | Try/except block | ❌ Crashes → ✅ 502 |
| **Timeout** | 120s | 60s + retry | ❌ Fails → ✅ 2 attempts |
| **Status codes** | All = 500 | 400/502/503/504/500 | ❌ Vague → ✅ Meaningful |
| **Error logging** | Generic `str(e)` | Detailed type + traceback | ❌ Unclear → ✅ Debuggable |
| **Input validation** | None | Duration 5-30s check | ❌ No checks → ✅ Validates |
| **Missing config** | Returns 500 | Returns 503 | ❌ Wrong code → ✅ Correct code |
| **HTTP headers** | Missing Content-Length | Added headers | ❌ Streaming issues → ✅ Proper headers |

---

## Testing Scenarios

### Scenario 1: Normal Operation ✅
```json
Request: {"prompt": "Piano", "duration": 10, "mood": "Calm", "tempo": 80, "instruments": "piano"}
HF Response: {"data": [{"name": "audio.wav", "data": "UklGRi4..."}]}
Response: 200 (audio blob)
```

### Scenario 2: HF API Returns Non-200
```
HF Returns: HTTP 500
Expected: 502 (Bad Gateway) instead of ❌ 500
```

### Scenario 3: Invalid Duration
```json
Request: {"prompt": "Piano", "duration": 60, ...}  // Too long
Response: 400 (Bad Request) instead of ❌ 500
```

### Scenario 4: HF API Timeout
```
HF Takes >60s
Attempt 1: Timeout → Retry after 2s
Attempt 2: Timeout → Return 504 (Gateway Timeout) instead of ❌ 500
```

### Scenario 5: Missing HF_API_URL
```
Environment variable not set
Response: 503 (Service Unavailable) instead of ❌ 500
```

---

## Deployment Checklist

- [ ] Update `python-core/studio_api.py` in repository
- [ ] Commit and push to git (or manually upload to Render)
- [ ] Verify `HF_API_URL` environment variable is set in Render
- [ ] Redeploy on Render (should auto-deploy if using git)
- [ ] Test `/health` endpoint returns 200
- [ ] Test `/studio-generate` with valid input
- [ ] Monitor Render logs for deployment and first requests
- [ ] Verify response headers include Content-Length
- [ ] Test audio playback in frontend
