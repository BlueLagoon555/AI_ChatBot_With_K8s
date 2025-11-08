# Environment Variables Documentation

This document explains the environment variables used in the AI API Gateway project.

## Provider Configuration

### AI_PROVIDER
- Description: Selects which AI provider to use
- Options: "azure" or "digitalocean"
- Example: `AI_PROVIDER=azure`

## Azure OpenAI Configuration

### AZURE_OPENAI_ENDPOINT
- Description: Your Azure OpenAI service endpoint URL
- Format: https://your-resource-name.openai.azure.com/
- Required if: AI_PROVIDER=azure

### AZURE_OPENAI_API_KEY
- Description: Your Azure OpenAI API key
- Required if: AI_PROVIDER=azure

### AZURE_OPENAI_MODEL
- Description: The deployment name of your model in Azure OpenAI
- Common values: gpt-4, gpt-35-turbo
- Required if: AI_PROVIDER=azure

### AZURE_OPENAI_API_VERSION
- Description: Azure OpenAI API version to use
- Example: 2024-02-15-preview
- Required if: AI_PROVIDER=azure

## DigitalOcean AI Configuration

### DIGITALOCEAN_INFERENCE_ENDPOINT
- Description: DigitalOcean AI API endpoint
- Format: https://api.digitalocean.com/v2/
- Required if: AI_PROVIDER=digitalocean

### DIGITALOCEAN_API_KEY
- Description: Your DigitalOcean API key
- Required if: AI_PROVIDER=digitalocean

### DIGITALOCEAN_MODEL
- Description: The model to use with DigitalOcean
- Common values: gpt-3.5-turbo
- Required if: AI_PROVIDER=digitalocean

## System Configuration

### DEFAULT_SYSTEM_PROMPT
- Description: Default system prompt for the AI
- Optional: Defaults to "You are a helpful AI assistant."

### API_HOST
- Description: Host to bind the API server
- Default: 0.0.0.0
- Optional

### API_PORT
- Description: Port for the API server
- Default: 8000
- Optional

### CORS_ORIGINS
- Description: Allowed CORS origins
- Format: Comma-separated list or "*" for all origins
- Default: *
- Note: Using "*" is not recommended for production

### LOG_LEVEL
- Description: Logging level for the application
- Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Default: INFO
- Optional

## Usage

1. Copy `.env.example` to `.env`
2. Fill in the required values based on your chosen provider
3. Optional: Adjust system configuration as needed

## Security Notes

- Never commit the `.env` file containing your actual API keys
- Keep your API keys secure and rotate them regularly
- In production, restrict CORS_ORIGINS to specific domains
