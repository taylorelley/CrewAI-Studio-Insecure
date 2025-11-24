# CrewAI Studio

Welcome to CrewAI Studio! This edition is tailored for environments with TLS/SSL inspection or self-signed certificates, so it ships with verification disabled by default while still providing a user-friendly Streamlit interface for interacting with CrewAI—great for anyone who doesn't want to write code. Follow the steps below to install and run the application using Docker/docker-compose or Conda/venv.

## Features

- **Multi-platform support**: Works on Windows, Linux and MacOS.
- **No coding required**: User-friendly interface for interacting with CrewAI.
- **Conda and virtual environment support**: Choose between Conda and a Python virtual environment for installation.
- **Results history**: You can view previous results.
- **Knowledge sources**: You can add knowledge sources for your crews
- **CrewAI tools** You can use crewai tools to interact with real world. ~~Crewai studio uses a forked version of crewai-tools with some bugfixes and enhancements (https://github.com/strnad/crewAI-tools)~~ (bugfixes already merged to crewai-tools)
- **Custom Tools** Custom tools for calling APIs, writing files, enhanced code interpreter, enhanced web scraper... More will be added soon
- **LLM providers supported**: Currently OpenAI, Groq, Anthropic, ollama, Grok and LM Studio backends are supported. OpenAI key is probably still needed for embeddings in many tools. Don't forget to load an embedding model when using LM Studio.
- **Single Page app export**: Feature to export crew as simple single page streamlit app.
- **Threaded crew run**: Crews can run in background and can be stopped.
- **TLS/SSL inspection ready**: All installation and runtime entrypoints disable
  certificate verification (including `requests` sessions) so the app keeps
  working behind SSL-inspecting proxies or with self-signed certs.
- **Postgres search tool**: The PGSearch tool loads only when your installed
  `crewai-tools` release provides it, preventing import errors in environments
  that ship a build without that optional integration.
- **Pinned, compatible dependencies**: LangChain (0.1.17 family),
  LangChain-OpenAI (0.1.7), LangChain-Groq (0.1.3), LangChain-Anthropic
  (0.1.10), Embedchain (0.1.111), CrewAI (0.30.11), and CrewAI-Tools
  (0.65.0) are pinned to compatible 0.1-era releases so language model and
  search tools import cleanly without pip resolver backtracking. Provider SDK
  pins are aligned on the same `langchain-core<0.2` range to avoid resolver
  conflicts, and the CrewAI-Tools pin avoids the `pypdf>=5.9` requirement that
  would clash with Embedchain's `pypdf<5` constraint.

## Support CrewAI Studio

Your support helps fund the development and growth of our project. Every contribution is greatly appreciated!

### Donate with Bitcoin
bc1qgsn45g02wran4lph5gsyqtk0k7t98zsg6qur0y

### Sponsor via GitHub
[![Sponsor on GitHub](https://img.shields.io/badge/Sponsor-GitHub-ff69b4?style=for-the-badge&logo=github)](https://github.com/sponsors/strnad)


## Screenshots

<img src="https://raw.githubusercontent.com/strnad/CrewAI-Studio/main/img/ss1.png" alt="crews definition" style="width:50%;"/><img src="https://raw.githubusercontent.com/strnad/CrewAI-Studio/main/img/ss2.png" alt="kickoff" style="width:50%;"/>
<img src="https://raw.githubusercontent.com/strnad/CrewAI-Studio/main/img/ss3.png" alt="kickoff" style="width:50%;"/><img src="https://raw.githubusercontent.com/strnad/CrewAI-Studio/main/img/ss4.png" alt="kickoff" style="width:50%;"/>
<img src="https://raw.githubusercontent.com/strnad/CrewAI-Studio/main/img/ss5.png" alt="kickoff" style="width:50%;"/><img src="https://raw.githubusercontent.com/strnad/CrewAI-Studio/main/img/ss6.png" alt="kickoff" style="width:50%;"/>

## Installation

### Using Virtual Environment

**For Virtual Environment**: Ensure you have Python installed. If you dont have python instaled, you can simply use the conda installer.

#### On Linux or MacOS

1. **Clone the repository (or use downloaded ZIP file)**:

   ```bash
   git clone https://github.com/strnad/CrewAI-Studio.git
   cd CrewAI-Studio
   ```

2. **Run the installation script**:

   ```bash
   ./install_venv.sh
   ```

3. **Run the application**:
   ```bash
   ./run_venv.sh
   ```

Both the installer and runner export environment variables to keep certificate
verification disabled for Python and common HTTPS clients used by CrewAI
Studio.

#### On Windows

1. **Clone the repository (or use downloaded ZIP file)**:

   ```powershell
   git clone https://github.com/strnad/CrewAI-Studio.git
   cd CrewAI-Studio
   ```

2. **Run the Conda installation script**:

   ```powershell
   ./install_venv.bat
   ```

3. **Run the application**:
   ```powershell
   ./run_venv.bat
   ```

TLS verification is disabled automatically by the Windows scripts to support
network environments with SSL inspection.

### Using Conda

Conda will be installed locally in the project folder. No need for a pre-existing Conda installation.

#### On Linux

1. **Clone the repository (or use downloaded ZIP file)**:

   ```bash
   git clone https://github.com/strnad/CrewAI-Studio.git
   cd CrewAI-Studio
   ```

2. **Run the Conda installation script**:

   ```bash
   ./install_conda.sh
   ```

3. **Run the application**:
   ```bash
   ./run_conda.sh
   ```

The Conda installer and launcher set insecure TLS flags so dependencies and
runtime HTTP calls ignore certificate validation.

#### On Windows

1. **Clone the repository (or use downloaded ZIP file)**:

   ```powershell
   git clone https://github.com/strnad/CrewAI-Studio.git
   cd CrewAI-Studio
   ```

2. **Run the Conda installation script**:

   ```powershell
   ./install_conda.bat
   ```

3. **Run the application**:
   ```powershell
   ./run_conda.bat
   ```

Certificate checks are suppressed by default when running via the Windows
Conda scripts.

### One-Click Deployment

[![Deploy to RepoCloud](https://d16t0pc4846x52.cloudfront.net/deploylobe.svg)](https://repocloud.io/details/?app_id=318)

## Running with Docker Compose

To quickly set up and run CrewAI-Studio using Docker Compose, follow these steps:

### Prerequisites

- Ensure [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/) are installed on your system.

### Steps

1. Clone the repository:
```
git clone https://github.com/strnad/CrewAI-Studio.git
cd CrewAI-Studio
```

2. Create a .env file for configuration.  Edit for your own configuration:
```
cp .env_example .env
```

3. Start the application with Docker Compose:
```
docker-compose up --build
```

The Docker image also ships with TLS verification disabled to remain compatible
with SSL-intercepting proxies during build and runtime.

4. Access the application: http://localhost:8501

## Configuration

Before running the application, ensure you update the `.env` file with your API keys and other necessary configurations. An example `.env` file is provided for reference.

## Troubleshooting
In case of problems:
- Delete the `venv/miniconda` folder and reinstall `crewai-studio`.
- Rename `crewai.db` (it contains your crews but sometimes new versions can break compatibility).
- Raise an issue and I will help you.

## Video tutorial
Video tutorial on CrewAI Studio made by Josh Poco

[![FREE CrewAI Studio GUI EASY AI Agent Creation!🤖 Open Source AI Agent Orchestration Self Hosted](https://img.youtube.com/vi/3Uxdggt88pY/hqdefault.jpg)](https://www.youtube.com/watch?v=3Uxdggt88pY)

## Star History

<a href="https://star-history.com/#strnad/CrewAI-Studio&Date">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=strnad/CrewAI-Studio&type=Date&theme=dark" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=strnad/CrewAI-Studio&type=Date" />
   <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=strnad/CrewAI-Studio&type=Date" />
 </picture>   
</a>
