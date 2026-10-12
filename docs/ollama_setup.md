# Excel AI Assistant: Ollama Integration Setup Guide

This guide explains how to set up and use the Ollama integration in Excel AI Assistant, which allows you to use local
open-source large language models instead of the OpenAI API.

## Prerequisites

1. **Ollama Installation**: You need to have Ollama installed on your system. Ollama is a tool for running large
   language models locally.

    - **Download**: Get Ollama from https://ollama.ai/download
    - **Supported Platforms**: Windows, macOS, Linux

2. **Models**: You need to have at least one language model pulled into Ollama.

## Setting Up Ollama

### 1. Install Ollama

Follow the instructions on the Ollama website for your operating system. After installation, Ollama will run as a
service at http://localhost:11434 by default.

### 2. Install a Language Model

Open a terminal/command prompt and run:

```bash
# Pull Llama 3, a great all-purpose model
ollama pull llama3

# Or for a smaller model that requires less resources
ollama pull llama3:8b

# You can also try other models
ollama pull mistral
ollama pull phi
```

### 3. Verify Ollama is Running

Check that Ollama is running by opening a terminal and entering:

```bash
ollama list
```

This should display the models you've installed.

## Configuring Excel AI Assistant for Ollama

1. **Open Excel AI Assistant**

2. **Switch to Ollama API**:
    - In the toolbar, change the API dropdown from "OpenAI" to "Ollama"
    - The interface will update to show Ollama-specific settings

3. **Verify Connection**:
    - Click the "Test API" button to verify the connection to the Ollama server
    - If successful, you should see the available models in the model dropdown

4. **Advanced Settings**:
    - Click the "Settings" button next to the Ollama URL field
    - In the dialog, you can:
        - Change the Ollama server URL (if running on a different machine)
        - View and select available models
        - Set the default model

## Using Ollama Models

Using Ollama models is similar to using OpenAI models:

1. Select a range of cells in your spreadsheet
2. Enter your prompt in the instructions area
3. Click "Run on Selected Range"

### Tips for Using Ollama Models

1. **Model Performance**: Local models may be slower than OpenAI's API, especially on less powerful hardware.

2. **Model Selection**: Different models have different strengths:
    - Llama 3 is a good all-around model
    - Smaller models (8B, 7B) use less RAM but may produce lower quality results
    - Specialized models may perform better for specific tasks

3. **Resource Usage**: Running large language models locally requires significant computing resources:
    - Minimum: 8GB RAM, modern CPU
    - Recommended: 16GB+ RAM, modern multi-core CPU
    - For larger models: 32GB+ RAM, strong CPU or GPU

## Troubleshooting

1. **Connection Failed**:
    - Ensure Ollama is running (`ollama serve` command)
    - Check the URL is correct (default is http://localhost:11434)
    - Verify no firewall is blocking the connection

2. **No Models Found**:
    - Make sure you've pulled at least one model with `ollama pull modelname`
    - Restart Ollama if needed

3. **Slow Performance**:
    - Try a smaller model (e.g., llama3:8b instead of llama3)
    - Reduce the batch size in Preferences > Advanced
    - Close other resource-intensive applications

4. **Out of Memory Errors**:
    - Switch to a smaller model
    - Restart Ollama
    - Add more RAM to your system

## Switching Between OpenAI and Ollama

You can easily switch between OpenAI and Ollama APIs:

1. Use the API dropdown in the toolbar to switch between them
2. Your settings for each API type are saved separately
3. The model dropdown automatically updates to show the appropriate models

This feature allows you to use OpenAI when you need the highest quality results and Ollama when you prefer privacy or
working offline.