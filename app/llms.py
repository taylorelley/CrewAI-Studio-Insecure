import os
from typing import Optional

import streamlit as st
from crewai import LLM
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain_openai.chat_models.base import BaseChatOpenAI
from litellm import completion

def load_secrets_from_env():
    load_dotenv(override=True)
    if "env_vars" not in st.session_state:
        st.session_state.env_vars = {
            "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
            "OPENAI_API_BASE": os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1/"),
            "OPENAI_PROXY_MODELS": os.getenv("OPENAI_PROXY_MODELS"),
            "GROQ_API_KEY": os.getenv("GROQ_API_KEY"),
            "LMSTUDIO_API_BASE": os.getenv("LMSTUDIO_API_BASE"),
            "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY"),
            "OLLAMA_HOST": os.getenv("OLLAMA_HOST"),
            "OLLAMA_MODELS": os.getenv("OLLAMA_MODELS"),
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


def _get_env_var(key, default=None):
    if "env_vars" in st.session_state and st.session_state.env_vars.get(key) is not None:
        return st.session_state.env_vars.get(key)
    return os.getenv(key, default)


def _has_env_value(key):
    value = _get_env_var(key)
    return value is not None and str(value).strip() != ""

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

def get_llm_config():
    openai_models = _get_env_var("OPENAI_PROXY_MODELS")
    ollama_models = _get_env_var("OLLAMA_MODELS")

    return {
        "OpenAI": {
            "models": openai_models.split(",") if openai_models else [
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
            "models": ollama_models.split(",") if ollama_models else [],
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


def get_available_llm_config():
    config = get_llm_config()
    availability_checks = {
        "OpenAI": lambda: _has_env_value("OPENAI_API_KEY"),
        "Groq": lambda: _has_env_value("GROQ_API_KEY"),
        "Ollama": lambda: _has_env_value("OLLAMA_HOST"),
        "Anthropic": lambda: _has_env_value("ANTHROPIC_API_KEY"),
        "LM Studio": lambda: _has_env_value("LMSTUDIO_API_BASE"),
        "Xai": lambda: _has_env_value("XAI_API_KEY"),
        "Gemini": lambda: _has_env_value("GEMINI_API_KEY"),
        "Azure OpenAI": lambda: _has_env_value("AZURE_OPENAI_API_KEY") and _has_env_value("AZURE_OPENAI_ENDPOINT"),
        "Bedrock": lambda: _has_env_value("AWS_REGION"),
    }

    available_config = {}
    for provider, provider_config in config.items():
        if availability_checks.get(provider, lambda: False)():
            models = [model for model in provider_config.get("models", []) if model]
            if models:
                available_config[provider] = {**provider_config, "models": models}

    return available_config


def llm_providers_and_models():
    available_config = get_available_llm_config()
    return [f"{provider}: {model}" for provider in available_config.keys() for model in available_config[provider]["models"]]


def create_llm(provider_and_model, temperature=0.15):
    if not provider_and_model or provider_and_model == "none:none":
        raise ValueError("No LLM provider/model configured. Please update your .env with valid credentials.")

    # Rozdělit pouze na první výskyt ': ', aby model mohl obsahovat dvojtečku
    if ": " not in provider_and_model:
        raise ValueError("Input string must be in format 'Provider: Model'")
    provider, model = provider_and_model.split(": ", 1)
    create_llm_func = get_llm_config().get(provider, {}).get("create_llm")

    if create_llm_func:
        llm = create_llm_func(model, temperature)
        restore_environment()  # Obnoví původní prostředí po vytvoření LLM
        return llm
    else:
        raise ValueError(f"LLM provider {provider} is not recognized or not supported")
