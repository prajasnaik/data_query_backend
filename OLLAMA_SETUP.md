# Ollama Setup Guide for Data Query Agent

## Overview

This project uses **Ollama with Qwen2.5:14b** instead of Google Gemini for LLM capabilities. This provides several advantages:

- ✅ **No API costs** - Runs locally
- ✅ **No rate limits** - Unlimited usage
- ✅ **Privacy-friendly** - Data stays local
- ✅ **Tool calling support** - Native function calling
- ✅ **Open source** - Full control and transparency

---

## Installation

### 1. Install Ollama

**Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**macOS:**
```bash
brew install ollama
```

**Windows:**
Download from [https://ollama.com/download](https://ollama.com/download)

### 2. Start Ollama Service

```bash
# Start Ollama (runs on port 11434 by default)
ollama serve
```

**For background service:**
```bash
# Linux (systemd)
sudo systemctl enable ollama
sudo systemctl start ollama

# macOS (launchd)
brew services start ollama
```

### 3. Pull Qwen2.5:14b Model

```bash
# Download the model (one-time, ~8GB)
ollama pull qwen2.5:14b

# Verify it works
ollama run qwen2.5:14b "Write a SQL query to create a users table"
```

---

## Configuration

### Environment Variables

**Backend `.env`:**
```env
# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:14b
```

**If Ollama is on a different server:**
```env
OLLAMA_BASE_URL=http://192.168.1.100:11434
```

---

## Why Qwen2.5:14b?

### Model Characteristics:
- **14 billion parameters** - Good balance of speed and quality
- **Strong reasoning** - Excellent for SQL and schema generation
- **Tool calling** - Native support for function calling
- **JSON mode** - Reliable structured output
- **Multilingual** - English, Chinese, and 25+ languages

### Performance:
- **Speed:** ~20-50 tokens/sec on GPU (RTX 3090/4090)
- **Speed:** ~5-10 tokens/sec on CPU (modern Intel/AMD)
- **Memory:** ~8-10GB RAM/VRAM
- **Context:** 32K tokens (plenty for CSV analysis)

### Comparison with Other Models:
| Model | Size | Speed | Quality | Tool Calling |
|-------|------|-------|---------|--------------|
| qwen2.5:14b | 14B | ⭐⭐⭐ | ⭐⭐⭐⭐ | ✅ |
| llama3.1:8b | 8B | ⭐⭐⭐⭐ | ⭐⭐⭐ | ✅ |
| mistral:7b | 7B | ⭐⭐⭐⭐ | ⭐⭐⭐ | ✅ |
| codellama:13b | 13B | ⭐⭐⭐ | ⭐⭐⭐⭐ | ❌ |

---

## Hardware Requirements

### Minimum (CPU Only):
- **CPU:** Modern multi-core (8+ cores recommended)
- **RAM:** 16GB (model uses ~10GB)
- **Storage:** 10GB for model
- **Speed:** 5-10 tokens/sec (acceptable for development)

### Recommended (GPU):
- **GPU:** NVIDIA RTX 3060+ (12GB VRAM) or AMD equivalent
- **RAM:** 16GB+
- **Storage:** 10GB for model
- **Speed:** 30-50 tokens/sec (smooth user experience)

### Optimal (Production):
- **GPU:** NVIDIA RTX 4090 (24GB VRAM) or A100
- **RAM:** 32GB+
- **Storage:** NVMe SSD
- **Speed:** 60-100 tokens/sec (instant responses)

---

## Testing Ollama

### 1. Basic Test
```bash
curl http://localhost:11434/api/generate -d '{
  "model": "qwen2.5:14b",
  "prompt": "Explain what SQLite is in one sentence."
}'
```

### 2. JSON Mode Test
```bash
ollama run qwen2.5:14b --format json "Generate a JSON schema for a users table with id, name, email"
```

### 3. Tool Calling Test
```python
import ollama

response = ollama.chat(
    model='qwen2.5:14b',
    messages=[{'role': 'user', 'content': 'What is 2+2?'}],
    tools=[{
        'type': 'function',
        'function': {
            'name': 'calculator',
            'description': 'Calculate math expressions',
            'parameters': {
                'type': 'object',
                'properties': {
                    'expression': {'type': 'string'}
                }
            }
        }
    }]
)

print(response)
```

---

## Integration in the Project

### Backend Service (`app/services/llm_service.py`)

```python
import ollama
from app.config import settings
import json

class LLMService:
    def __init__(self):
        self.client = ollama.Client(host=settings.OLLAMA_BASE_URL)
        self.model = settings.OLLAMA_MODEL
    
    async def generate_schema(self, csv_metadata: list[dict]) -> dict:
        """Generate database schema from CSV metadata"""
        prompt = self._build_schema_prompt(csv_metadata)
        
        response = self.client.chat(
            model=self.model,
            messages=[
                {
                    'role': 'system',
                    'content': 'You are a database architect. You must respond ONLY with valid JSON.'
                },
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            format='json',  # Force JSON output
            options={
                'temperature': 0.2,  # More deterministic
            }
        )
        
        return json.loads(response['message']['content'])
    
    def _build_schema_prompt(self, csv_metadata: list[dict]) -> str:
        # ... (see STEPS.md for full implementation)
        pass
```

### Query Agent with Tool Calling

```python
class QueryAgentService:
    def __init__(self, db, user_id: str, schema_id: str):
        self.client = ollama.Client(host=settings.OLLAMA_BASE_URL)
        self.model = settings.OLLAMA_MODEL
        
        # Define tools
        self.tools = [
            {
                'type': 'function',
                'function': {
                    'name': 'execute_sql_query',
                    'description': 'Execute SQL queries',
                    'parameters': {
                        'type': 'object',
                        'properties': {
                            'query': {'type': 'string'}
                        }
                    }
                }
            }
        ]
    
    async def stream_response(self, messages: list[dict]):
        response = self.client.chat(
            model=self.model,
            messages=messages,
            tools=self.tools,
            stream=True  # Streaming for real-time responses
        )
        
        for chunk in response:
            yield chunk
```

---

## Troubleshooting

### Issue: Ollama not responding

**Check if service is running:**
```bash
curl http://localhost:11434/api/tags
```

**Restart Ollama:**
```bash
# Linux
sudo systemctl restart ollama

# macOS
brew services restart ollama

# Manual
killall ollama
ollama serve
```

### Issue: Model not found

```bash
# List available models
ollama list

# Pull model again
ollama pull qwen2.5:14b
```

### Issue: Slow responses

**Solutions:**
1. Use GPU if available (10-20x faster)
2. Reduce model size: `ollama pull qwen2.5:7b`
3. Increase Ollama workers: `OLLAMA_NUM_PARALLEL=4 ollama serve`
4. Optimize prompt length (shorter prompts = faster)

### Issue: Out of memory

**Solutions:**
1. Close other applications
2. Use smaller model: `qwen2.5:7b` or `llama3.1:8b`
3. Increase system swap space
4. Use Ollama on a separate machine with more RAM

### Issue: JSON parsing errors

**Solution:**
```python
# Always use format='json' parameter
response = client.chat(
    model=model,
    messages=messages,
    format='json'  # Force JSON output
)

# Add validation
try:
    data = json.loads(response['message']['content'])
except json.JSONDecodeError:
    # Handle malformed JSON
    # Retry with more explicit prompt
```

---

## Performance Optimization

### 1. Enable GPU Acceleration

**NVIDIA (CUDA):**
```bash
# Check if GPU is detected
ollama list

# Should show GPU info in logs
ollama serve
# Output: "GPU detected: NVIDIA RTX 4090"
```

**AMD (ROCm):**
```bash
# Set ROCm environment
export HSA_OVERRIDE_GFX_VERSION=10.3.0
ollama serve
```

### 2. Adjust Context Size

```python
response = client.chat(
    model=model,
    messages=messages,
    options={
        'num_ctx': 4096,  # Reduce from default 32K for speed
        'num_predict': 512,  # Limit output tokens
    }
)
```

### 3. Use Quantization

```bash
# Use quantized version for faster inference
# Q4_K_M = 4-bit quantization, good balance
ollama pull qwen2.5:14b-q4_K_M
```

### 4. Parallel Requests

```bash
# Allow multiple concurrent requests
OLLAMA_NUM_PARALLEL=4 ollama serve
```

---

## Alternative Models

If Qwen2.5:14b doesn't meet your needs:

### For Faster Responses:
```bash
ollama pull qwen2.5:7b
# or
ollama pull llama3.1:8b
```

### For Better Quality (if you have hardware):
```bash
ollama pull qwen2.5:32b
# or
ollama pull llama3.1:70b  # Requires 48GB+ RAM
```

### For Code/SQL Focus:
```bash
ollama pull deepseek-coder:33b
# or
ollama pull codellama:13b
```

---

## Production Deployment

### Docker Deployment

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  ollama:
    image: ollama/ollama:latest
    container_name: ollama
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    environment:
      - OLLAMA_NUM_PARALLEL=4
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
  
  backend:
    build: ./backend
    depends_on:
      - ollama
    environment:
      - OLLAMA_BASE_URL=http://ollama:11434
      - OLLAMA_MODEL=qwen2.5:14b

volumes:
  ollama_data:
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ollama
spec:
  replicas: 1
  template:
    spec:
      containers:
      - name: ollama
        image: ollama/ollama:latest
        ports:
        - containerPort: 11434
        resources:
          limits:
            nvidia.com/gpu: 1
          requests:
            memory: "16Gi"
```

---

## Monitoring

### Check Ollama Status

```bash
# Check running models
curl http://localhost:11434/api/tags

# Check server health
curl http://localhost:11434/api/version

# Monitor logs
journalctl -u ollama -f
```

### Performance Metrics

```python
import time

start = time.time()
response = client.chat(model='qwen2.5:14b', messages=[...])
duration = time.time() - start

print(f"Response time: {duration:.2f}s")
print(f"Tokens: {len(response['message']['content'].split())}")
print(f"Speed: {len(response['message']['content'].split()) / duration:.2f} tokens/sec")
```

---

## Cost Comparison

| Aspect | Ollama (Local) | Google Gemini | OpenAI GPT-4 |
|--------|----------------|---------------|--------------|
| **Setup Cost** | $0 (use existing hardware) | $0 | $0 |
| **Per-token Cost** | $0 | $0.00125/$0.005 | $0.01/$0.03 |
| **1M tokens** | $0 | $1,250-$5,000 | $10,000-$30,000 |
| **Rate Limits** | None | 60 RPM | 10,000 TPM |
| **Privacy** | ✅ Fully local | ❌ Cloud | ❌ Cloud |
| **Latency** | 50-100ms | 200-500ms | 300-800ms |
| **Customization** | ✅ Full control | ⚠️ Limited | ⚠️ Limited |

**For this project (estimated usage):**
- **Development:** ~100K tokens/day → $0 vs $125-$500/day
- **Production (100 users):** ~1M tokens/day → $0 vs $1,250-$5,000/day

**Break-even analysis:**
- GPU server cost: ~$1,000-$2,000/month
- API costs at scale: ~$5,000-$50,000/month
- **Savings: 60-90% at scale**

---

## Resources

- **Ollama Documentation:** https://ollama.com/docs
- **Qwen2.5 Model Card:** https://ollama.com/library/qwen2.5
- **Python Client:** https://github.com/ollama/ollama-python
- **Community Discord:** https://discord.gg/ollama

---

## Quick Reference

### Common Commands

```bash
# Start Ollama
ollama serve

# Pull/update model
ollama pull qwen2.5:14b

# Run interactive chat
ollama run qwen2.5:14b

# List models
ollama list

# Remove model
ollama rm qwen2.5:14b

# Show model info
ollama show qwen2.5:14b

# Check version
ollama --version
```

### Python Client Basics

```python
import ollama

# Simple chat
response = ollama.chat(
    model='qwen2.5:14b',
    messages=[{'role': 'user', 'content': 'Hello!'}]
)

# Streaming
for chunk in ollama.chat(model='qwen2.5:14b', messages=[...], stream=True):
    print(chunk['message']['content'], end='')

# JSON mode
response = ollama.chat(
    model='qwen2.5:14b',
    messages=[...],
    format='json'
)

# Tool calling
response = ollama.chat(
    model='qwen2.5:14b',
    messages=[...],
    tools=[{...}]
)
```

---

**Ready to build with Ollama!** 🚀

No API keys, no rate limits, no cloud dependence. Your data, your model, your control.
