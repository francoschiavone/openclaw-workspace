# Real-Time Voice Conversations with AI Assistants: Comprehensive Research Report

**Research Date:** February 17, 2026  
**Focus:** OpenClaw voice features and alternative voice AI solutions

---

## Executive Summary

Real-time voice conversations with AI assistants are now achievable with latencies ranging from **600ms to 2+ seconds** depending on the solution. OpenClaw offers native voice support through **Talk Mode** and **Voice Wake** features on macOS/iOS/Android using ElevenLabs TTS. For phone-based conversations, dedicated platforms like **Vapi**, **Retell AI**, and **Bland AI** offer enterprise-grade solutions with Twilio integration. OpenAI's **Realtime API** provides the most integrated speech-to-speech experience for developers building custom solutions.

---

## 1. OpenClaw Voice Features

### Voice Wake
- **Purpose:** Global wake word detection across all connected devices
- **How it works:** Wake words are stored centrally on the Gateway (`~/.openclaw/settings/voicewake.json`)
- **Default triggers:** "openclaw", "claude", "computer"
- **Platform support:** macOS app, iOS node, Android node
- **Protocol:** WebSocket-based sync via `voicewave.get`/`voicewake.set` methods
- **Configuration:** Any node/app UI can edit the trigger list; changes sync everywhere instantly

### Talk Mode
- **Purpose:** Continuous voice conversation loop
- **Flow:** Listen → Transcribe → Send to LLM → Speak via TTS
- **TTS Provider:** ElevenLabs (streaming API)
- **Key Features:**
  - **Interrupt on speech:** User can interrupt AI mid-sentence (default: ON)
  - **Voice directives:** Assistant can change voice/mid-conversation via JSON prefix
  - **Phase indicators:** Listening → Thinking → Speaking with visual overlay (macOS)
  - **Low-latency playback:** Uses PCM streaming for real-time audio

### Configuration (Talk Mode)
```json5
{
  talk: {
    voiceId: "elevenlabs_voice_id",
    modelId: "eleven_v3",
    outputFormat: "mp3_44100_128",  // or pcm_* for lower latency
    apiKey: "elevenlabs_api_key",
    interruptOnSpeech: true,
  },
}
```

### Platform Support Matrix

| Feature | macOS | iOS | Android | Web |
|---------|-------|-----|---------|-----|
| Voice Wake | ✅ | ✅ | ✅ | ❌ |
| Talk Mode | ✅ | ✅ | ✅ | ❌ |
| Push-to-Talk | ✅ | ❌ | ❌ | ❌ |
| Overlay UI | ✅ | ❌ | ❌ | ❌ |
| PCM Streaming | ✅ (44100) | ✅ (44100) | ✅ (16000-44100) | ❌ |

### What Voice Features Does NOT OpenClaw Currently Support
- **No phone calling:** Cannot receive or make actual phone calls (no Twilio/telephony integration)
- **No WebChat voice:** Voice only works through native apps (macOS/iOS/Android)
- **No Windows/Linux voice:** Only macOS, iOS, and Android nodes support voice
- **No multi-user voice:** Designed for single-user personal assistant

---

## 2. Latency Analysis

### Typical Voice AI Pipeline Latency

| Component | Typical Latency | Notes |
|-----------|-----------------|-------|
| **STT (Speech-to-Text)** | 100-500ms | Depends on provider (Groq Whisper: ~100ms, OpenAI Whisper: ~300-500ms) |
| **LLM Inference** | 200-2000ms | Varies wildly by model; GPT-4o: 500-1500ms, Claude: 300-800ms |
| **TTS (Text-to-Speech)** | 100-400ms | ElevenLabs streaming: ~100ms first chunk |
| **Network** | 50-200ms | WebSocket overhead + API latency |

### Round-Trip Latency by Solution

| Solution | Estimated Total Latency | Conversational? |
|----------|------------------------|-----------------|
| **Retell AI** | ~600ms | ✅ Excellent |
| **ElevenLabs Conversational AI** | <1000ms (sub-100ms TTS) | ✅ Excellent |
| **Vapi AI** | <500ms (sub-500ms claimed) | ✅ Excellent |
| **OpenAI Realtime API** | 300-800ms | ✅ Very Good |
| **OpenClaw Talk Mode** | 800-2000ms | ⚠️ Good to Acceptable |
| **Self-built (STT+LLM+TTS)** | 1500-3000ms | ⚠️ Variable |

### What Affects Latency Most?
1. **LLM inference time** (biggest factor) - Use faster models (GPT-4o-mini, Claude Haiku)
2. **Streaming vs. batching** - Streaming TTS/STT reduces perceived latency significantly
3. **Network distance** - Use edge endpoints, consider Groq for STT
4. **Audio format** - PCM streaming is faster than MP3 decoding

---

## 3. OpenClaw Talk Mode - Setup Guide

### Prerequisites
1. OpenClaw Gateway installed (`npm install -g openclaw@latest`)
2. macOS app, iOS app, or Android app installed
3. ElevenLabs API key

### Step-by-Step Setup

1. **Get ElevenLabs API Key:**
   - Go to [elevenlabs.io](https://elevenlabs.io/app/sign-up)
   - Sign up (Free tier: 10k credits/month)
   - Navigate to Profile → API Keys → Create

2. **Configure OpenClaw:**
   Edit `~/.openclaw/openclaw.json`:
   ```json5
   {
     talk: {
       voiceId: "your-voice-id",  // Get from ElevenLabs Voice Library
       modelId: "eleven_v3",
       apiKey: "xi-xxxxxxxxxx",   // Your ElevenLabs API key
       interruptOnSpeech: true,
     },
   }
   ```

3. **On macOS:**
   - Open OpenClaw.app
   - Click menu bar icon
   - Toggle "Talk" mode
   - Grant microphone permission when prompted

4. **On iOS/Android:**
   - Install OpenClaw node app
   - Pair with Gateway (Bonjour auto-discovery)
   - Grant microphone permission
   - Enable Talk Mode in settings

### Estimated Monthly Cost for Personal Use

| Usage | ElevenLabs Plan | Monthly Cost |
|-------|-----------------|--------------|
| Light (30 min/day) | Creator ($22) | $22 |
| Moderate (1 hr/day) | Pro ($99) | $99 |
| Heavy (3+ hrs/day) | Scale ($330) | $330 |

---

## 4. OpenClaw Voice Call Plugin - Phone Integration

### Current Status
**OpenClaw does NOT currently support phone calls.** There is no native voice call plugin or Twilio integration for receiving/making actual phone calls.

### What Would Be Required
To add phone calling capability to OpenClaw:

1. **Telephony Provider Integration:**
   - Twilio (most common)
   - Telnyx
   - Plivo
   - SignalWire

2. **Required Components:**
   - Webhook endpoint for incoming calls
   - TwiML/programmable voice handling
   - Media stream for real-time audio
   - SIP trunking or WebRTC

3. **Reference Implementation:**
   See [Twilio ConversationRelay](https://www.twilio.com/blog/conversationrelay-voice-ai-made-human) or ElevenLabs Twilio integration docs.

---

## 5. Alternative Voice Solutions

### A. Dedicated Voice AI Platforms

#### Vapi.ai
- **What it is:** API-first voice AI platform for developers
- **Latency:** Sub-500ms claimed
- **Pricing:** Pay-per-minute (varies by components)
- **Integrations:** 40+ apps including Twilio, HubSpot, Zapier
- **Scale:** 300M+ calls, 500K+ developers
- **Best for:** Developers building custom voice apps

#### Retell AI
- **What it is:** Enterprise voice AI for call centers
- **Latency:** ~600ms (independently benchmarked)
- **Key Features:**
  - Proprietary turn-taking model
  - Streaming RAG for knowledge
  - Simulation testing before deployment
- **Compliance:** HIPAA, SOC2 Type II, GDPR
- **Best for:** Enterprise call centers, appointment scheduling

#### Bland AI
- **What it is:** Enterprise voice AI with custom models
- **Key Differentiator:** Uses own fine-tuned models (no OpenAI/Anthropic dependency)
- **Scale:** Up to 1 million concurrent calls
- **Features:**
  - Custom trained models
  - Dedicated infrastructure
  - Voice cloning
- **Best for:** Enterprises wanting data sovereignty

#### ElevenLabs Conversational AI
- **What it is:** Full conversational AI platform
- **Latency:** Sub-100ms TTS
- **Languages:** 32+ supported
- **Key Features:**
  - Bring your own LLM (Claude, GPT, Gemini)
  - Tool calling / MCP support
  - RAG integration
  - Telephony integrations (Twilio, Genesys, Vonage)
- **Pricing:** Starting at $0.08/minute on annual plans
- **Best for:** High-quality natural conversations

### B. Developer APIs

#### OpenAI Realtime API
- **What it is:** Native speech-to-speech API
- **Models:** `gpt-realtime`, `gpt-realtime-mini`
- **Connection types:** WebRTC (browser), WebSocket (server), SIP (telephony)
- **Pricing:**
  - `gpt-realtime`: $4/1M input tokens, $16/1M output tokens
  - `gpt-realtime-mini`: $0.60/1M input, $2.40/1M output
- **Best for:** Developers wanting tight OpenAI integration

#### Groq (Fast Inference)
- **What it is:** Ultra-fast inference platform
- **Why relevant:** Fast Whisper STT (~100ms transcription)
- **Pricing:** Very competitive (e.g., Llama models ~$0.20/1M tokens)
- **Best for:** Minimizing STT latency

### C. Self-Hosted / Home Assistant Options

#### Home Assistant + Whisper + Piper
- **Components:** Whisper (STT), Piper (TTS), any LLM
- **Pros:** Full local control, privacy
- **Cons:** Higher latency (2-5 seconds typical)
- **Hardware:** Requires capable hardware (GPU recommended)

#### Local Whisper + LLM + Coqui TTS
- **Components:** Local Whisper, any local LLM, Coqui/XTTS
- **Pros:** No API costs, privacy
- **Cons:** Significant latency, hardware requirements

---

## 6. Pricing Comparison

### TTS Pricing (per minute)

| Provider | Price/Minute | Notes |
|----------|--------------|-------|
| **ElevenLabs** | $0.06 - $0.30 | Depends on plan volume |
| **OpenAI TTS** | $0.015 | Standard quality |
| **OpenAI TTS HD** | $0.030 | High definition |
| **Google Cloud TTS** | $0.006 - $0.016 | Varies by voice type |

### STT Pricing (per minute)

| Provider | Price/Minute | Notes |
|----------|--------------|-------|
| **Groq Whisper** | ~$0.0036 | Extremely fast |
| **OpenAI Whisper** | $0.006 | Standard API |
| **Deepgram** | $0.0043 | Nova-2 model |
| **Google Speech-to-Text** | $0.006 - $0.009 | Varies by model |

### Telephony Pricing (US, per minute)

| Provider | Inbound | Outbound |
|----------|---------|----------|
| **Twilio Local** | ~$0.0085 | ~$0.013 |
| **Twilio Toll-Free** | ~$0.022 | ~$0.013 |
| **Telnyx** | ~$0.005 | ~$0.005 |
| **Plivo** | ~$0.0085 | ~$0.007 |

### Voice AI Platform Pricing

| Platform | Model | Starting Price |
|----------|-------|----------------|
| **ElevenLabs Conversational** | Per minute | $0.08/min |
| **Vapi** | Per minute | Contact for pricing |
| **Retell AI** | Per minute | $0.07-0.12/min |
| **Bland AI** | Enterprise | Custom pricing |

---

## 7. Cost Estimation Scenarios

### Scenario 1: Personal Assistant (OpenClaw Talk Mode)

**Usage:** 1 hour/day voice conversation

| Component | Monthly Cost |
|-----------|--------------|
| ElevenLabs Creator Plan | $22 |
| Claude/Anthropic (via OpenClaw subscription) | Already included |
| **Total** | **$22/month** |

### Scenario 2: Phone-Based AI Assistant (Twilio + ElevenLabs)

**Usage:** 30 minutes/day of phone conversations

| Component | Monthly Cost |
|-----------|--------------|
| Twilio Voice (inbound) | $7.65 (900 min × $0.0085) |
| ElevenLabs (TTS) | ~$27 (Pro plan covers ~500 min) |
| Groq Whisper (STT) | ~$3.24 |
| LLM (Claude Haiku) | ~$5-10 |
| **Total** | **$43-48/month** |

### Scenario 3: Enterprise Call Center (1000 calls/day, 5 min avg)

**Usage:** ~150,000 minutes/month

| Component | Monthly Cost |
|-----------|--------------|
| Retell AI ($0.08/min) | $12,000 |
| Twilio Voice | $1,275 |
| Phone Numbers (50) | $57.50 |
| **Total** | **$13,332.50/month** |

---

## 8. User Experience & Reviews Summary

### What Users Say About Latency

> "For an AI agent to feel human, latency matters as much as voice quality."  
> — Debojyoti Chakraborty, Sr. Engineering Manager at Funding Societies

> "Using the voice really added a nice punchy feel to it, without it, it gets lost in the shuffle as just another chat bot."  
> — Felix Su, Head of Engineering at Scale AI

### Key User Feedback Themes

1. **Latency threshold:** Users notice anything above 1.5-2 seconds
2. **Interruption support:** Critical for natural conversation flow
3. **Voice quality:** ElevenLabs consistently rated highest
4. **Natural prosody:** Emotion and pacing matter as much as speed
5. **Turn-taking:** Knowing when to speak vs. listen is crucial

### Common Complaints
- Latency spikes during peak hours (cloud services)
- Interruption handling feels "robotic"
- Background noise handling is still imperfect
- Cost escalates quickly with heavy usage

---

## 9. Recommendations

### For OpenClaw Users Wanting Voice Conversations

**Best Path:** Use OpenClaw Talk Mode with ElevenLabs

1. **Get ElevenLabs Creator plan** ($22/month) - sufficient for moderate personal use
2. **Configure Talk Mode** in `~/.openclaw/openclaw.json`
3. **Use macOS app** for best experience (visual overlay, push-to-talk)
4. **Enable interrupt-on-speech** for natural conversation flow
5. **Consider Groq Whisper** if OpenClaw supports it for faster STT

### For Phone-Based AI Assistant

**Best Path:** ElevenLabs Conversational AI + Twilio

1. **Sign up for ElevenLabs Business plan** ($1,320/month for scale)
2. **Configure Twilio integration** via ElevenLabs dashboard
3. **Set up webhook** for incoming calls
4. **Test with friends/family** before production

**Alternative:** Use Vapi or Retell for more control

### For Maximum Privacy/Self-Hosting

**Best Path:** Home Assistant + Local Models

1. **Hardware:** NVIDIA GPU with 12GB+ VRAM
2. **STT:** Whisper-large-v3 (local)
3. **LLM:** Llama 3.1 8B or Mistral
4. **TTS:** Piper or Coqui XTTS
5. **Accept:** 2-4 second latency

---

## 10. Quick Reference: Action Items

### To Enable Voice in OpenClaw TODAY:

1. Sign up at [elevenlabs.io](https://elevenlabs.io) → Get API key
2. Edit `~/.openclaw/openclaw.json`:
   ```json5
   { talk: { apiKey: "xi-your-key", voiceId: "21m00Tcm4TlvDq8ikWAM" } }
   ```
3. Install OpenClaw macOS/iOS/Android app
4. Enable Talk Mode in app settings
5. Say "openclaw" or your wake word to start

### Minimum Budget for Personal Voice AI:

| Option | Monthly Cost | Quality |
|--------|--------------|---------|
| OpenClaw + ElevenLabs Starter | $5 | Good |
| OpenClaw + ElevenLabs Creator | $22 | Excellent |
| Vapi/Retell (phone calls) | $50-100 | Excellent |

---

## Appendix: Key Links

- **OpenClaw GitHub:** https://github.com/openclaw/openclaw
- **ElevenLabs:** https://elevenlabs.io
- **Vapi:** https://vapi.ai
- **Retell AI:** https://retellai.com
- **Bland AI:** https://bland.ai
- **OpenAI Realtime API:** https://platform.openai.com/docs/guides/realtime
- **Groq:** https://groq.com
- **Twilio Voice:** https://twilio.com/voice

---

*Report generated by research sub-agent. Information current as of February 2026.*
