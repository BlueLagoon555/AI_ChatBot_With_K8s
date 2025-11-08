"""
FastAPI application for AI integration
Supports multiple AI providers: Azure OpenAI, DigitalOcean AI, and OpenAI-compatible APIs
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import logging
from openai import OpenAI, AzureOpenAI
from config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI API Gateway",
    description="""
    ## Modular AI API Gateway
    
    This API provides a unified interface to multiple AI providers:
    - **Azure OpenAI** - Microsoft's enterprise AI service
    - **DigitalOcean AI** - DigitalOcean's inference API
    
    ### Quick Start
    1. Configure your provider in `.env` file
    2. Set `AI_PROVIDER` to either `azure` or `digitalocean`
    3. Add your credentials for the chosen provider
    4. Start the server with `python start.py`
    
    ### Features
    - 🔄 Easy provider switching via environment variables
    - 💬 Chat completions with conversation history
    - 🎯 Simple text completions
    - 🎛️ Customizable system prompts
    - 📊 Token usage tracking
    - 🏥 Health monitoring
    
    ### Endpoints
    - **POST /api/chat** - Multi-turn conversations
    - **POST /api/completion** - Single prompt completions
    - **GET /health** - Service health and configuration
    """,
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Initialize OpenAI client
def get_openai_client():
    """Initialize and return OpenAI client based on AI_PROVIDER setting"""
    try:
        if settings.AI_PROVIDER.lower() == "digitalocean":
            # DigitalOcean Inference API
            # DigitalOcean Inference API - use requests directly
            import requests

            class DigitalOceanClient:
                def __init__(self, endpoint, api_key):
                    self.endpoint = endpoint.rstrip("/")
                    self.api_key = api_key.replace("Bearer ", "")
                    self.chat = self.Chat(self)

                class Chat:
                    def __init__(self, parent):
                        self.parent = parent
                        self.completions = self

                    def create(self, **kwargs):
                        # Ensure endpoint ends with /chat/completions
                        if self.parent.endpoint.endswith("/chat/completions"):
                            url = self.parent.endpoint
                        else:
                            url = f"{self.parent.endpoint}/chat/completions"
                        headers = {
                            "Content-Type": "application/json",
                            "Authorization": f"Bearer {self.parent.api_key}",
                        }
                        response = requests.post(url, headers=headers, json=kwargs)
                        if response.status_code != 200:
                            logger.error(f"DigitalOcean API error: {response.text}")
                            raise Exception(f"DigitalOcean API error: {response.text}")
                        return response.json()

            client = DigitalOceanClient(
                settings.DIGITALOCEAN_INFERENCE_ENDPOINT, settings.DIGITALOCEAN_API_KEY
            )
            # Mask API key in logs for security
            masked_key = settings.DIGITALOCEAN_API_KEY
            if masked_key:
                masked_key = masked_key.replace("Bearer ", "")
                masked_key = (
                    f"Bearer {masked_key[:3]}...{masked_key[-4:]}"
                    if len(masked_key) > 7
                    else "[NOT SET]"
                )
            logger.info(f"Initialized DigitalOcean client with key {masked_key}")
            logger.info(f"Using endpoint: {settings.DIGITALOCEAN_INFERENCE_ENDPOINT}")
        elif settings.AI_PROVIDER.lower() == "azure":
            # Check if using Azure OpenAI or standard OpenAI API format
            if "azure" in settings.AZURE_OPENAI_ENDPOINT.lower():
                # Azure OpenAI format
                client = AzureOpenAI(
                    api_key=settings.AZURE_OPENAI_API_KEY,
                    api_version=settings.AZURE_OPENAI_API_VERSION,
                    azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
                )
                logger.info(f"Using Azure OpenAI: {settings.AZURE_OPENAI_ENDPOINT}")
            else:
                # Standard OpenAI API format
                client = OpenAI(
                    api_key=settings.AZURE_OPENAI_API_KEY,
                    base_url=settings.AZURE_OPENAI_ENDPOINT,
                )
                logger.info(
                    f"Using OpenAI-compatible API: {settings.AZURE_OPENAI_ENDPOINT}"
                )
        else:
            raise ValueError(
                f"Invalid AI_PROVIDER: {settings.AI_PROVIDER}. Must be 'azure' or 'digitalocean'"
            )

        return client
    except Exception as e:
        logger.error(f"Failed to initialize OpenAI client: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to initialize AI service",
        )


def get_model_name():
    """Get the model name based on the AI provider"""
    if settings.AI_PROVIDER.lower() == "digitalocean":
        return settings.DIGITALOCEAN_MODEL
    else:
        return settings.AZURE_OPENAI_MODEL


# Request/Response models
class Message(BaseModel):
    role: str = Field(
        ..., description="Role of the message sender (system, user, assistant)"
    )
    content: str = Field(..., description="Content of the message")


class ChatRequest(BaseModel):
    messages: List[Message] = Field(
        ..., description="List of messages in the conversation"
    )
    system_prompt: Optional[str] = Field(
        None, description="Optional system prompt to override default"
    )
    temperature: Optional[float] = Field(
        default=0.7, ge=0.0, le=2.0, description="Sampling temperature (0-2)"
    )
    max_tokens: Optional[int] = Field(
        default=800, ge=1, le=4000, description="Maximum tokens to generate"
    )
    top_p: Optional[float] = Field(
        default=0.95, ge=0.0, le=1.0, description="Nucleus sampling parameter"
    )


class ChatResponse(BaseModel):
    response: str = Field(..., description="AI generated response")
    model: str = Field(..., description="Model used for generation")
    usage: Dict[str, Any] = Field(..., description="Token usage information")


class CompletionRequest(BaseModel):
    prompt: str = Field(..., description="The prompt to complete")
    system_prompt: Optional[str] = Field(
        None, description="Optional system prompt to override default"
    )
    temperature: Optional[float] = Field(
        default=0.7, ge=0.0, le=2.0, description="Sampling temperature (0-2)"
    )
    max_tokens: Optional[int] = Field(
        default=800, ge=1, le=4000, description="Maximum tokens to generate"
    )


class HealthResponse(BaseModel):
    status: str
    message: str
    configuration: Dict[str, Any]


# API Endpoints
@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint - API information"""
    return {
        "service": "AI API Gateway",
        "version": "2.0.0",
        "provider": settings.AI_PROVIDER,
        "docs": "/docs",
        "health": "/health",
        "endpoints": {"chat": "/api/chat", "completion": "/api/completion"},
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    if settings.AI_PROVIDER.lower() == "digitalocean":
        config = {
            "ai_provider": settings.AI_PROVIDER,
            "endpoint_configured": bool(settings.DIGITALOCEAN_INFERENCE_ENDPOINT),
            "api_key_configured": bool(settings.DIGITALOCEAN_API_KEY),
            "model": settings.DIGITALOCEAN_MODEL,
        }
    else:
        config = {
            "ai_provider": settings.AI_PROVIDER,
            "endpoint_configured": bool(settings.AZURE_OPENAI_ENDPOINT),
            "api_key_configured": bool(settings.AZURE_OPENAI_API_KEY),
            "model": settings.AZURE_OPENAI_MODEL,
            "api_version": settings.AZURE_OPENAI_API_VERSION,
        }

    return HealthResponse(
        status="healthy", message="Service is running", configuration=config
    )


@app.post("/api/chat", response_model=ChatResponse)
async def chat_completion(request: ChatRequest):
    """
    Send a chat completion request to Azure OpenAI

    Args:
        request: ChatRequest containing messages and optional parameters

    Returns:
        ChatResponse with AI generated response
    """
    try:
        client = get_openai_client()

        # Prepare messages
        messages = []

        # Add system prompt (use custom or default)
        system_prompt = request.system_prompt or settings.DEFAULT_SYSTEM_PROMPT
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        # Add conversation messages
        for msg in request.messages:
            messages.append({"role": msg.role, "content": msg.content})

        # Call AI service
        model_name = get_model_name()
        logger.info(
            f"Calling {settings.AI_PROVIDER} AI with {len(messages)} messages using model {model_name}"
        )
        response = client.chat.completions.create(
            model=model_name,
            messages=messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            top_p=request.top_p,
        )
        # Handle both DigitalOcean (dict) and OpenAI (object) responses
        if isinstance(response, dict):
            ai_response = response["choices"][0]["message"]["content"]
            model = response.get("model", model_name)
            usage = response.get("usage", {})
        else:
            ai_response = response.choices[0].message.content
            model = response.model
            usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            }
        return ChatResponse(response=ai_response, model=model, usage=usage)

    except Exception as e:
        logger.error(f"Error in chat completion: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate response: {str(e)}",
        )


@app.post("/api/completion", response_model=ChatResponse)
async def simple_completion(request: CompletionRequest):
    """
    Send a simple completion request to Azure OpenAI

    Args:
        request: CompletionRequest containing prompt and optional parameters

    Returns:
        ChatResponse with AI generated response
    """
    try:
        client = get_openai_client()

        # Prepare messages for chat completion format
        messages = []

        # Add system prompt if provided
        system_prompt = request.system_prompt or settings.DEFAULT_SYSTEM_PROMPT
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        # Add user prompt
        messages.append({"role": "user", "content": request.prompt})

        # Call AI service
        model_name = get_model_name()
        logger.info(
            f"Calling {settings.AI_PROVIDER} AI for completion using model {model_name}"
        )
        response = client.chat.completions.create(
            model=model_name,
            messages=messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )
        # Handle both DigitalOcean (dict) and OpenAI (object) responses
        if isinstance(response, dict):
            ai_response = response["choices"][0]["message"]["content"]
            model = response.get("model", model_name)
            usage = response.get("usage", {})
        else:
            ai_response = response.choices[0].message.content
            model = response.model
            usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            }
        return ChatResponse(response=ai_response, model=model, usage=usage)
    except Exception as e:
        logger.error(f"Error in completion: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate response: {str(e)}",
        )


@app.on_event("startup")
async def startup_event():
    logger.info("Application is starting up...")
    # Debug: Print DigitalOcean API key and endpoint
    logger.info(f"DigitalOcean API Key: {settings.DIGITALOCEAN_API_KEY}")
    logger.info(f"DigitalOcean Endpoint: {settings.DIGITALOCEAN_INFERENCE_ENDPOINT}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
