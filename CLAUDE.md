# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

KindCoach is an AI-powered coaching platform for kindergarten teachers, designed to help them communicate more effectively with children through AI analysis of teacher-child interactions.

**Tech Stack:**
- **Frontend:** Streamlit for web interface (mobile-optimized)
- **AI Services:** AssemblyAI for Korean speech recognition + speaker diarization, OpenAI GPT-4o-mini for conversation analysis and coaching recommendations
- **Backend:** Python 3.10+
- **Data:** JSON file-based result persistence in `data/analysis_results/`
- **Infrastructure:** Python virtual environment, Git version control

## Development Commands

### Quick Start (Recommended)
```bash
# One-click setup and run
./run.sh
```

The `run.sh` script provides automated deployment with:
- **Port Management**: Automatically kills any processes using port 8501
- **Environment Setup**: Creates `.venv` virtual environment if it doesn't exist  
- **Dependency Installation**: Installs/updates packages from `requirements.txt`
- **Application Launch**: Activates environment and starts Streamlit server

This is the **fastest way to get KindCoach running** from a fresh clone.

### Manual Environment Setup
```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt
```

### Running the Application
```bash
# Start Streamlit app (default port 8501)
streamlit run src/main.py

# Run on custom port
STREAMLIT_SERVER_PORT=8502 streamlit run src/main.py
```

### Environment Variables
Copy `env_example` to `.env` and configure:
- `ASSEMBLYAI_API_KEY`: AssemblyAI API key for speech recognition and speaker diarization
- `OPENAI_API_KEY`: OpenAI API key for conversation analysis using GPT-4o-mini
- `STREAMLIT_SERVER_PORT`: Port for Streamlit server (default: 8501)
- `ADMIN_USERNAME`: Admin login username (default: admin)
- `ADMIN_PASSWORD`: Admin login password for authentication

### Testing and Verification
```bash
# Test module imports
python -c "import src.main; print('All modules imported successfully')"

# Run end-to-end test with sample audio
python test_audio.py

# The app will be available at http://localhost:8501
```

## Architecture

### Core Application Structure
The application follows a single-page Streamlit architecture with modular backend services:

- `KindCoachApp` class in `src/main.py` orchestrates the entire user experience
- Session state management handles multi-step workflows and caching
- Mobile-first responsive UI using custom CSS and Streamlit columns
- File upload validation with 50MB limit and format checking

### Key Modules
- **`src/audio_processor.py`**: AssemblyAI wrapper for speech-to-text and speaker diarization
- **`src/ai_analyzer.py`**: OpenAI client for multiple analysis types (comprehensive, quick feedback, child development, coaching tips)  
- **`src/utils.py`**: Shared utilities for environment loading, file validation, data formatting, and UI helpers
- **`src/auth.py`**: Authentication system with bcrypt password hashing and session management
- **`src/prompt_manager.py`**: Dynamic prompt management system for domain experts to modify AI prompts
- **`src/prompt_editor.py`**: Streamlit UI components for prompt editing and management
- **`src/analysis_manager.py`**: Comprehensive analysis result storage, loading, and management system
- **`src/metadata_form.py`**: UI components for collecting structured metadata during analysis requests
- **`src/dashboard.py`**: Personal dashboard with user-specific analysis statistics and insights
- **`config/prompts.py`**: Legacy centralized AI prompt templates (being migrated to JSON-based system)
- **`config/prompts.json`**: JSON-based prompt template system with versioning and backup support

### Data Flow
1. **Authentication** → Login validation with bcrypt → Session state management → Auto-logout after 30 mins
2. **Metadata Collection** → Structured input form for child/teacher information → Session state storage
3. **File Upload** → Validation (format, size) → Store in session state
4. **Audio Processing** → AssemblyAI transcription → Speaker diarization → Teacher/child role detection
5. **AI Analysis** → Multiple OpenAI calls with dynamic prompts from JSON templates → Structured JSON responses  
6. **Results Display** → Tabbed interface with summary, transcript, analysis, and visualizations
7. **Persistence** → Analysis results auto-saved to user-specific directories in `data/analysis_results/` as JSON with unique conversation IDs
8. **Dashboard Analytics** → Personal statistics and insights based on historical analysis data

### Speaker Analysis Logic
- Identifies teacher vs child based on speaking time ratios, word counts, and conversation patterns
- Calculates balance metrics (teacher dominance, child participation)
- Provides statistical breakdowns for coaching insights

### Analysis Types Architecture
- **Comprehensive**: Full 10-point scoring system with detailed feedback
- **Quick Feedback**: Immediate insights for rapid review
- **Child Development**: Developmental psychology perspective  
- **Coaching Tips**: Situational improvement recommendations

### Prompt Management System
The application features a dynamic prompt management system allowing domain experts to modify AI analysis prompts:

- **JSON-based Templates**: Prompts stored in `config/prompts.json` with metadata and versioning
- **Live Editing**: Web-based prompt editor accessible through the admin interface
- **Backup System**: Automatic versioning with timestamps in `config/backups/`
- **Template Variables**: Support for dynamic content insertion (transcript, metadata, etc.)
- **Hot Reloading**: Changes take effect immediately without application restart

## Development Notes

### Audio File Handling
- Supported formats: WAV, MP3, M4A, FLAC, OGG, WMA, AAC
- Maximum file size: 50MB
- File validation occurs before processing to prevent API errors
- Sample audio file available at `data/sample_audio/sample_audio.m4a` for testing

### Session State Management
Session state keys used throughout the application:
- `authenticated`: Boolean flag for login status
- `login_time`: Timestamp for session timeout tracking
- `uploaded_file`: Current audio file
- `transcription_result`: AssemblyAI response data  
- `analysis_results`: All AI analysis responses
- `conversation_id`: Unique identifier for saving results
- `show_additional_analysis`: UI state for expanded analysis options
- `prompt_manager`: PromptManager instance for dynamic prompt access
- `analysis_metadata`: Structured metadata collected from user input forms
- `current_username`: Active user for personalized data storage and dashboard

### Error Handling Patterns
- API failures gracefully handled with user-friendly error messages
- Environment variable validation occurs at startup
- File processing errors display specific guidance (file format, size limits)
- Network timeouts and rate limits handled with retry logic

### Mobile Optimization
- Custom CSS for touch-friendly interfaces
- Responsive column layouts that stack on mobile
- Optimized font sizes and button spacing
- Progress indicators for long-running operations

### Data Storage Architecture
- **User-specific Storage**: Analysis results stored in `data/analysis_results/{username}/` directories
- **Shared Results**: Legacy results in `data/analysis_results/` for backward compatibility  
- **Prompt Versioning**: Automated backups in `config/backups/` with timestamps
- **Structured Metadata**: Rich metadata collection including child/teacher information, session context
- **JSON Format**: All data persisted as JSON with unique conversation IDs for easy access

### Production Readiness
- Environment variables required for API keys and authentication
- Results automatically persist to local JSON files with unique IDs
- No database dependencies - uses file system for simplicity
- Secure authentication with bcrypt password hashing
- Session timeout for security (30 minutes)
- User-specific data isolation for multi-user deployments
- Ready for deployment with proper API key and admin credential configuration

## Security Considerations

### Authentication System
- Admin login required to access application
- Passwords hashed using bcrypt with salt
- Session timeout after 30 minutes of inactivity
- Session state stored securely in Streamlit's session management

### API Key Management
- All API keys stored in environment variables, never in code
- Environment validation at application startup
- Clear error messages for missing configurations without exposing sensitive data

### File Security
- Uploaded files validated for type and size before processing
- Temporary file handling with proper cleanup
- Analysis results stored locally with unique identifiers to prevent conflicts