import os
from dotenv import load_dotenv
import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain_anthropic import ChatAnthropic
from crewai import LLM
from langchain_openai.chat_models.base import BaseChatOpenAI
from litellm import completion
from typing import Optional

def load_secrets_from_env():
    load_dotenv(override=True)
    if "env_vars" not in st.session_state:
        st.session_state.env_vars = {
            "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
            "OPENAI_API_BASE": os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1/"),
            "GROQ_API_KEY": os.getenv("GROQ_API_KEY"),
            "LMSTUDIO_API_BASE": os.getenv("LMSTUDIO_API_BASE"),
            "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY"),
            "OLLAMA_HOST": os.getenv("OLLAMA_HOST"),
            "XAI_API_KEY": os.getenv("XAI_API_KEY"),
            "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY"),
            "AZURE_OPENAI_API_KEY": os.getenv("AZURE_OPENAI_API_KEY"),
            "AZURE_OPENAI_ENDPOINT": os.getenv("AZURE_OPENAI_ENDPOINT"),
            "AZURE_OPENAI_DEPLOYMENT_NAME": os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
            "AZURE_OPENAI_API_VERSION": os.getenv("AZURE_OPENAI_API_VERSION"),
            "AWS_ACCESS_KEY_ID": os.getenv("AWS_ACCESS_KEY_ID"),
            "AWS_SECRET_ACCESS_KEY": os.getenv("AWS_SECRET_ACCESS_KEY"),
            "AWS_SESSION_TOKEN": os.getenv("AWS_SESSION_TOKEN"),
            "AWS_REGION": os.getenv("AWS_REGION"),
        }
    else:
        st.session_state.env_vars = st.session_state.env_vars

def switch_environment(new_env_vars):
    for key, value in new_env_vars.items():
        if value is not None:
            os.environ[key] = value
            st.session_state.env_vars[key] = value

def restore_environment():
    for key, value in st.session_state.env_vars.items():
        if value is not None:
            os.environ[key] = value
        elif key in os.environ:
            del os.environ[key]

def safe_pop_env_var(key):
    os.environ.pop(key, None)

def create_openai_llm(model, temperature):
    switch_environment({
        "OPENAI_API_KEY": st.session_state.env_vars["OPENAI_API_KEY"],
        "OPENAI_API_BASE": st.session_state.env_vars["OPENAI_API_BASE"],
    })
    api_key = os.getenv("OPENAI_API_KEY")
    api_base = os.getenv("OPENAI_API_BASE")

    if api_key:
        return LLM(model=model, temperature=temperature, base_url=api_base)
    else:
        raise ValueError("OpenAI API key not set in .env file")

def create_anthropic_llm(model, temperature):
    switch_environment({
        "ANTHROPIC_API_KEY": st.session_state.env_vars["ANTHROPIC_API_KEY"],
    })
    api_key = os.getenv("ANTHROPIC_API_KEY")

    if api_key:
        return ChatAnthropic(
            anthropic_api_key=api_key,
            model_name=model,
            temperature=temperature,
            max_tokens=4095,
        )
    else:
        raise ValueError("Anthropic API key not set in .env file")

def create_groq_llm(model, temperature):
    switch_environment({
        "GROQ_API_KEY": st.session_state.env_vars["GROQ_API_KEY"],
    })
    api_key = os.getenv("GROQ_API_KEY")

    if api_key:
        return ChatGroq(groq_api_key=api_key, model_name=model, temperature=temperature, max_tokens=4095)
    else:
        raise ValueError("Groq API key not set in .env file")

def create_ollama_llm(model, temperature):
    host = st.session_state.env_vars["OLLAMA_HOST"]
    if host:
        switch_environment({
            "OPENAI_API_KEY": "ollama",  # Nastaví OpenAI API klíč na "ollama"
            "OPENAI_API_BASE": host,    # Nastaví OpenAI API Base na hodnotu OLLAMA_HOST
        })
        return LLM(model=model, temperature=temperature, base_url=host)
    else:
        raise ValueError("Ollama Host is not set in .env file")


def create_xai_llm(model, temperature):
    host = "https://api.x.ai/v1"
    api_key = st.session_state.env_vars.get("XAI_API_KEY")

    if not api_key:
        raise ValueError("XAI_API_KEY must be set in .env file")

    switch_environment({
        "OPENAI_API_KEY": api_key,
        "OPENAI_API_BASE": host,
    })

    return LLM(
        model=model,
        temperature=temperature,
        api_key=api_key,
        base_url=host
    )


def create_gemini_llm(model: str, temperature: Optional[float]):
    api_key = st.session_state.env_vars.get("GEMINI_API_KEY")

    if not api_key:
        raise ValueError("GEMINI_API_KEY must be set in .env file")

    if not model.startswith("gemini/"):
        raise ValueError(f"Model must start with 'gemini/', got: {model}")

    switch_environment({"GEMINI_API_KEY": api_key})

    return LLM(
        model=model,
        temperature=temperature,
        api_key=api_key,
        provider="gemini",
    )


def create_azure_openai_llm(model: str, temperature: Optional[float]):
    api_key = st.session_state.env_vars.get("AZURE_OPENAI_API_KEY")
    endpoint = st.session_state.env_vars.get("AZURE_OPENAI_ENDPOINT")
    deployment = st.session_state.env_vars.get("AZURE_OPENAI_DEPLOYMENT_NAME") or model
    api_version = st.session_state.env_vars.get("AZURE_OPENAI_API_VERSION")

    if not api_key or not endpoint:
        raise ValueError("AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT must be set in .env file")

    switch_environment(
        {
            "AZURE_OPENAI_API_KEY": api_key,
            "AZURE_OPENAI_ENDPOINT": endpoint,
            "AZURE_OPENAI_DEPLOYMENT_NAME": deployment,
            "AZURE_OPENAI_API_VERSION": api_version,
        }
    )

    deployment_base = f"{endpoint.rstrip('/')}/openai/deployments/{deployment}"

    return LLM(
        model=deployment,
        temperature=temperature,
        api_key=api_key,
        base_url=deployment_base,
        api_version=api_version,
        provider="azure",
    )


def create_bedrock_llm(model: str, temperature: Optional[float]):
    region = st.session_state.env_vars.get("AWS_REGION")
    aws_access_key_id = st.session_state.env_vars.get("AWS_ACCESS_KEY_ID")
    aws_secret_access_key = st.session_state.env_vars.get("AWS_SECRET_ACCESS_KEY")
    aws_session_token = st.session_state.env_vars.get("AWS_SESSION_TOKEN")

    if not region:
        raise ValueError("AWS_REGION must be set in .env file for Bedrock models")

    switch_environment(
        {
            "AWS_REGION": region,
            "AWS_ACCESS_KEY_ID": aws_access_key_id,
            "AWS_SECRET_ACCESS_KEY": aws_secret_access_key,
            "AWS_SESSION_TOKEN": aws_session_token,
        }
    )

    return LLM(
        model=model,
        temperature=temperature,
        provider="bedrock",
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        aws_session_token=aws_session_token,
        region_name=region,
    )

def create_lmstudio_llm(model, temperature):
    switch_environment({
        "OPENAI_API_KEY": "lm-studio",
        "OPENAI_API_BASE": st.session_state.env_vars["LMSTUDIO_API_BASE"],
    })
    api_base = os.getenv("OPENAI_API_BASE")

    if api_base:
        return ChatOpenAI(
            openai_api_key="lm-studio",
            openai_api_base=api_base,
            temperature=temperature,
            max_tokens=4095,
        )
    else:
        raise ValueError("LM Studio API base not set in .env file")

LLM_CONFIG = {
    "OpenAI": {
        "models": os.getenv("OPENAI_PROXY_MODELS", "").split(",") if os.getenv("OPENAI_PROXY_MODELS") else [
            "gpt-4.1",
            "gpt-4.1-mini",
            "gpt-4.1-nano",
            "gpt-4o",
            "gpt-4o-mini",
            "gpt-4-turbo",
            "o3-mini",
            "o1-mini",
            "o1",
            "gpt-3.5-turbo",
        ],
        "create_llm": create_openai_llm,
    },
    "Groq": {
        "models": ["groq/llama3-8b-8192", "groq/llama3-70b-8192", "groq/mixtral-8x7b-32768"],
        "create_llm": create_groq_llm,
    },
    "Ollama": {
        "models": os.getenv("OLLAMA_MODELS", "").split(",") if os.getenv("OLLAMA_MODELS") else [],
        "create_llm": create_ollama_llm,
    },
    "Anthropic": {
        "models": [
            "claude-3-5-sonnet-20240620",
            "claude-3-7-sonnet-20250219",
            "claude-sonnet-4-20250514",
            "claude-sonnet-4-5-20250929",
        ],
        "create_llm": create_anthropic_llm,
    },
    "LM Studio": {
        "models": ["lms-default"],
        "create_llm": create_lmstudio_llm,
    },
     "Xai": {
        "models": ["xai/grok-2-1212", "xai/grok-beta"],
        "create_llm": create_xai_llm,
    },
    "Gemini": {
        "models": [
            "gemini/gemini-2.5-flash",
            "gemini/gemini-2.5-pro",
            "gemini/gemini-2.0-flash",
        ],
        "create_llm": create_gemini_llm,
    },
    "Azure OpenAI": {
        "models": [
            "gpt-4o",
            "gpt-4.1",
            "gpt-4.1-mini",
            "gpt-4-turbo",
        ],
        "create_llm": create_azure_openai_llm,
    },
    "Bedrock": {
        "models": [
            "anthropic.claude-3-7-sonnet-20250219-v1:0",
            "meta.llama3-1-70b-instruct-v1:0",
            "amazon.nova-pro-v1:0",
            "mistral.mistral-large-2402-v1:0",
            "cohere.command-r-plus-v1:0",
            "deepseek.r1-v1:0",
        ],
        "create_llm": create_bedrock_llm,
    },
}

def llm_providers_and_models():
    return [f"{provider}: {model}" for provider in LLM_CONFIG.keys() for model in LLM_CONFIG[provider]["models"]]

def create_llm(provider_and_model, temperature=0.15):
    # Rozdělit pouze na první výskyt ': ', aby model mohl obsahovat dvojtečku
    if ": " not in provider_and_model:
        raise ValueError("Input string must be in format 'Provider: Model'")
    provider, model = provider_and_model.split(": ", 1)
    create_llm_func = LLM_CONFIG.get(provider, {}).get("create_llm")

    if create_llm_func:
        llm = create_llm_func(model, temperature)
        restore_environment()  # Obnoví původní prostředí po vytvoření LLM
        return llm
    else:
        raise ValueError(f"LLM provider {provider} is not recognized or not supported")
