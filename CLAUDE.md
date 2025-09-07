# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

KindCoach is an AI-powered coaching platform for kindergarten teachers, designed to help them communicate more effectively with children through AI analysis of teacher-child interactions.

**Tech Stack:**
- **Frontend:** Streamlit for web interface
- **AI Services:** AssemblyAI for Korean speech recognition + speaker diarization, OpenAI GPT-4o-mini for conversation analysis and coaching recommendations
- **Backend:** Python 3.10+
- **Infrastructure:** Python virtual environment, Git version control

## Development Commands

### Environment Setup
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
# Start Streamlit app
streamlit run src/main.py
```

### Environment Variables
Copy `env_example` to `.env` and configure:
- `ASSEMBLYAI_API_KEY`: AssemblyAI API key for speech recognition and speaker diarization
- `OPENAI_API_KEY`: OpenAI API key for conversation analysis using GPT-4o-mini
- `STREAMLIT_SERVER_PORT`: Port for Streamlit server (default: 8501)

### Testing and Verification
```bash
# Test that all modules can be imported
source .venv/bin/activate
python -c "import src.main; print('All modules imported successfully')"

# Run the application
streamlit run src/main.py

# The app will be available at http://localhost:8501
```

## Architecture

The project follows a modular structure designed around real-time audio processing and AI analysis:

**Implemented Module Structure:**
- `src/main.py`: Streamlit main application with mobile-optimized UI
- `src/audio_processor.py`: AssemblyAI integration for speech recognition and speaker diarization
- `src/ai_analyzer.py`: OpenAI GPT-4o-mini integration for conversation analysis and coaching
- `src/utils.py`: Common utility functions for file handling, data processing, and mobile layout
- `config/prompts.py`: Comprehensive AI prompt templates for different analysis types

**Implemented Workflow:**
1. **File Upload**: Mobile-optimized drag-and-drop interface with file validation
2. **Audio Processing**: AssemblyAI transcription with Korean language support and speaker diarization
3. **Speaker Analysis**: Automatic teacher-child role detection based on speaking patterns
4. **AI Analysis**: Multiple analysis types using OpenAI GPT-4o-mini:
   - Comprehensive coaching analysis (conversation quality, strengths, improvement areas)
   - Quick feedback for immediate insights
   - Child development analysis from developmental psychology perspective
   - Situation-specific coaching tips
   - Sentiment analysis interpretation
5. **Results Display**: Tabbed interface with:
   - Summary with key metrics and speaker statistics
   - Full transcript with speaker labels and timestamps
   - AI analysis with expandable sections
   - Interactive charts and statistical visualizations
6. **Data Persistence**: Automatic saving of analysis results as JSON files

## Project Status

✅ **FULLY IMPLEMENTED** - The KindCoach platform is complete and functional:

### Implemented Features
1. ✅ Complete project structure with all core modules
2. ✅ Mobile-optimized Streamlit web interface
3. ✅ AssemblyAI integration for Korean speech recognition and speaker diarization
4. ✅ OpenAI GPT-4o-mini integration for comprehensive conversation analysis
5. ✅ Teacher-child interaction analysis and coaching feedback
6. ✅ Multiple analysis types: comprehensive, quick feedback, child development, coaching tips
7. ✅ Audio file upload with validation (50MB limit, multiple formats)
8. ✅ Results visualization with interactive charts and statistics
9. ✅ Session state management and result persistence
10. ✅ Environment configuration with API key validation

### Key Implementation Notes
- All modules are functional and tested
- Korean language support throughout
- Comprehensive error handling for API integrations
- Mobile-first responsive design
- File-based result storage system
- Speaker balance analysis and conversation insights

### Usage
The application is ready for production use. Users can upload teacher-child conversation audio files and receive detailed AI-powered coaching feedback.