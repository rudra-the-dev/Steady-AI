# Replit.md

## Overview

This is a Streamlit-based AI chat application that integrates with OpenAI's API through Replit's AI Integrations. The application provides a conversational interface powered by GPT-5, with built-in retry logic for handling rate limits and error conditions.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit serves as both the UI framework and web server
- **Design Pattern**: Single-file application structure for simplicity
- **Rationale**: Streamlit was chosen for rapid prototyping and built-in components for chat interfaces without requiring separate frontend/backend code

### Backend Architecture
- **API Integration**: OpenAI client library with custom base URL for Replit AI Integrations
- **Error Handling**: Tenacity library provides exponential backoff retry logic for rate limit errors
- **Model**: Uses GPT-5 as the default language model
- **Rationale**: The retry decorator pattern handles transient failures gracefully without manual intervention

### Configuration Management
- **Environment Variables**: API keys and base URLs are loaded from environment variables
- **Constants**: `AI_INTEGRATIONS_OPENAI_API_KEY` and `AI_INTEGRATIONS_OPENAI_BASE_URL` are required
- **Rationale**: Keeps sensitive credentials out of source code

## External Dependencies

### Third-Party Services
- **OpenAI API**: Primary AI service accessed through Replit AI Integrations proxy
- **Replit AI Integrations**: Provides managed access to OpenAI with built-in authentication and billing

### Python Packages
- **streamlit**: Web application framework and UI components
- **openai**: Official OpenAI Python client library
- **tenacity**: Retry logic with exponential backoff for API resilience

### Environment Requirements
- `AI_INTEGRATIONS_OPENAI_API_KEY`: API key for OpenAI access
- `AI_INTEGRATIONS_OPENAI_BASE_URL`: Base URL for Replit's AI proxy service