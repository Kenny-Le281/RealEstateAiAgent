# RealEstateAiAgent

## Local LLM setup

This project uses **Ollama** to run a local model. Ollama supports macOS, Windows, and Linux, and exposes a local API at `http://localhost:11434`. ([Ollama Documentation][1])

### 1. Install Ollama

On macOS, install the app and move it to `Applications`. Ollama’s macOS docs note that the app can add the `ollama` CLI to your `PATH`, and that macOS 14 Sonoma or later is required. ([Ollama Documentation][2])

On Linux:

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Ollama’s Linux docs also mention optional startup-service and GPU setup steps if needed. ([Ollama][3])

On Windows PowerShell:

```powershell
irm https://ollama.com/install.ps1 | iex
```

Ollama’s Windows docs say it installs in the user directory by default and does not require Administrator privileges. ([Ollama][4])

### 2. Start Ollama

After installation, open Ollama once so the local service starts. You can verify it is available with:

```bash
ollama
```

Ollama’s quickstart shows this opens the interactive CLI, and the local API is then available for integration. ([Ollama Documentation][5])

You can also verify the local server with:

```bash
curl http://localhost:11434/api/chat -d '{
  "model": "llama3.1",
  "messages": [{"role": "user", "content": "Hello!"}]
}'
```

That endpoint is shown in Ollama’s quickstart and model pages. ([Ollama Documentation][5])

### 3. Pull the model used by this project

This project is configured to use **Llama 3.1** through Ollama.

Pull the model:

```bash
ollama pull llama3.1
```

Or start it directly once:

```bash
ollama run llama3.1
```

Ollama’s Llama 3.1 model page documents `ollama run llama3.1` and notes that the Llama 3.1 family includes 8B, 70B, and 405B variants. ([Ollama][6])

### 4. Verify the model is installed

Run:

```bash
ollama list
```

You should see `llama3.1` in the installed models list.

Then test it:

```bash
ollama run llama3.1
```

Type a prompt such as:

```text
Hello
```

If the model responds, the local LLM is ready.

### 5. Match the project config to your installed model

In `config.py`, the project should point to the same model name you installed.

Example:

```python
OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "llama3.1"
OLLAMA_TIMEOUT_SECONDS = 180
```

If your local setup uses a different tag, update `MODEL_NAME` to match what `ollama list` shows.

### 6. Install Python dependencies

From the project root or backend directory, install the required Python packages:

```bash
pip install requests pydantic
```

If you are using a virtual environment, activate it first.

### 7. Run the chatbot

From the backend folder:

```bash
python -m app.chatbot
```

If everything is set up correctly, the chatbot should start and send prompts to the local Ollama model.

### 8. Common setup checks

If the chatbot cannot connect to the model:

* Make sure Ollama is running.
* Make sure the model in `config.py` matches the installed model name.
* Make sure `http://localhost:11434` is reachable.
* If responses time out, increase `OLLAMA_TIMEOUT_SECONDS`.

To test the local API directly:

```bash
curl http://localhost:11434/api/chat -d '{
  "model": "llama3.1",
  "messages": [{"role": "user", "content": "Test"}]
}'
```
