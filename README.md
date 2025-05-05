# MCP Servers Collection

A collection of Model Context Protocol (MCP) servers designed for Cline, Roo, and Claude Desktop.

## Overview

This repository contains a comprehensive suite of MCP servers that enable AI assistants to interact with local and remote resources through a standardized protocol.

### Available Servers

1. **Cline MCP Server** (Port 8080)
   - Internal workflow orchestration
   - Agent task execution
   - Memory management
   - System execution capabilities

2. **Roo MCP Server** (Port 8081)
   - Web scraping and automation
   - Browser control with Playwright
   - Form filling automation
   - Screenshot/PDF capture
   - Watchdog sessions

3. **Claude Desktop MCP Server** (Port 8082)
   - Local file operations
   - Shell command execution
   - Desktop notifications
   - LLM integration (Ollama)
   - System information access

## Quick Start

### Using Docker

```bash
# Clone the repository
git clone https://github.com/mows21/mcp-servers.git
cd mcp-servers

# Start all servers
docker-compose up -d

# Check server health
docker-compose ps

# View logs
docker-compose logs -f
```

### Manual Installation

```bash
# Install requirements for each server
cd cline-mcp && pip install -r requirements.txt
cd ../roo-mcp && pip install -r requirements.txt
cd ../claude-desktop-mcp && pip install -r requirements.txt

# Start servers individually
cd cline-mcp && python main.py
cd ../roo-mcp && python main.py
cd ../claude-desktop-mcp && python main.py
```

## Configuration

### Claude Desktop Integration

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "cline-internal": {
      "command": "docker",
      "args": ["exec", "-i", "cline-mcp-server", "python", "main.py"]
    },
    "roo-automation": {
      "command": "docker",
      "args": ["exec", "-i", "roo-mcp-server", "python", "main.py"]
    },
    "claude-desktop-local": {
      "command": "docker",
      "args": ["exec", "-i", "claude-desktop-mcp-server", "python", "main.py"]
    }
  }
}
```

## Architecture

The MCP servers communicate through:
- Unified `/mcp` endpoints
- JSON-RPC protocol
- Docker network isolation
- Event-driven architecture

## API Documentation

### Cline MCP Server

- `POST /agent/run` - Execute agent tasks
- `POST /workflow` - Run workflows
- `GET/POST/DELETE /memory` - Memory management
- `POST /exec` - System command execution

### Roo MCP Server

- `POST /scrape/url` - Web scraping
- `POST /form/fill` - Form automation
- `POST /watchdog` - Session monitoring
- `POST /snapshot` - Page capture

### Claude Desktop MCP Server

- `POST /ask` - LLM interaction
- `GET /file/read` - File reading
- `POST /file/write` - File writing
- `POST /shell/run` - Shell execution
- `POST /notify` - Desktop notifications

## Security

- Network isolation through Docker
- Token-based authentication
- Input validation and sanitization
- Resource limits and health checks

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License - See [LICENSE](LICENSE) file for details

## Contact

For questions and support, please open an issue on GitHub.

## Acknowledgments

Built for the Model Context Protocol ecosystem to enhance AI agent capabilities.
