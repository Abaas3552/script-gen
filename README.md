# Comic-to-YouTube Script Agent System

A three-agent AI pipeline that transforms comic book files (CBR/CBZ) into optimized YouTube scripts through quality-assured processing and competitive intelligence integration.

## 🎯 Overview

**Input:** CBR comic files + competitor analysis CSV  
**Output:** 60-90 second YouTube script optimized for engagement  
**Method:** 3-agent pipeline with competitive intelligence using OpenAI's Vision and Text APIs  

## 🏗️ System Architecture

```
CBR File → Agent 1 → Agent 2 → Agent 3 → Final Script
           ↓        ↓        ↓
         Extract   Review   Integrate
         & Create  & Analyze & Optimize
```

### Agent 1: Comic Processor & Script Creator
- **Function:** Extract text/images from CBR files using OpenAI Vision
- **Output:** Initial YouTube script + comprehensive story analysis
- **Features:** 
  - Page-by-page vision analysis
  - Story structure identification
  - Script generation with timing cues
  - Character and plot extraction

### Agent 2: Script Editor & Competitive Analyst  
- **Function:** Review scripts against source material and competitor benchmarks
- **Output:** Detailed feedback and improvement recommendations
- **Features:**
  - Competitive pattern analysis from CSV data
  - Script accuracy verification
  - Engagement optimization suggestions
  - Quality assurance metrics

### Agent 3: Final Integration Specialist
- **Function:** Synthesize feedback into final optimized script
- **Output:** Production-ready script with titles and validation
- **Features:**
  - Conflict resolution between accuracy and engagement
  - Title generation and A/B testing options
  - Quality validation and success prediction
  - Production notes and implementation guidance

## 📋 Prerequisites

### Required Dependencies
```bash
pip install openai
```

### Required Files
- **OpenAI API Key** - Get from https://platform.openai.com/api-keys
- **Competitor Data CSV** - YouTube Shorts performance data (included: `Comics Data - sf.comics_shorts.csv`)
- **CBR/CBZ Files** - Comic book archives to process

### API Requirements
- OpenAI API access with Vision capabilities (GPT-4o model)
- Sufficient API credits for image processing

## 🚀 Quick Start

### Option 1: Full Pipeline (Recommended)
```bash
python pipeline_coordinator.py "comic.cbr" "Comics Data - sf.comics_shorts.csv" "sk-your-api-key" 75
```

### Option 2: Individual Agents
```bash
# Agent 1: Process comic and create initial script
python agent_1_comic_processor.py "comic.cbr" "sk-your-api-key" 75

# Agent 2: Review and analyze (requires Agent 1 output)
python agent_2_script_editor.py "agent_1_output_123.json" "Comics Data - sf.comics_shorts.csv" "sk-your-api-key"

# Agent 3: Final integration (requires Agent 2 output)
python agent_3_final_integrator.py "agent_2_output_456.json" "sk-your-api-key" 75
```

## 📊 Example Outputs

### Agent 1 Output Example
```json
{
  "story_analysis": {
    "story_summary": {
      "summary": "Comprehensive story breakdown with character analysis..."
    },
    "total_pages": 22,
    "analyzed_pages": 6
  },
  "script": {
    "script": "[00:00] Hook: What happens when Spider-Man faces his greatest fear?\n[00:15] Setup: Peter Parker discovers...",
    "target_duration": 75,
    "word_count": 187
  }
}
```

### Final Script Example
```
[00:00] What happens when Deadpool takes Spider-Man to HELL?
[00:03] While Spider-Man fights the boring villain Hydroman, Deadpool crashes the party...
[00:15] After giving Spidey a hug, Wade teleports them both straight to Hell...
[00:30] Where they're immediately captured by the demon lord Dormammu!
[00:45] But when Deadpool's constant jokes drive everyone insane...
[01:00] He ends the battle by giving the mindless demons actual brains!
[01:15] Thinking this must be a nightmare, Spider-Man demands they go home immediately!
```

## 🔧 Configuration Options

### Target Duration
- **Default:** 75 seconds
- **Range:** 60-90 seconds recommended for YouTube Shorts
- **Usage:** Add as final parameter to any agent

### Quality Settings
Each agent includes built-in quality controls:
- **Agent 1:** Story fidelity and script coherence
- **Agent 2:** Competitive benchmarking and accuracy verification  
- **Agent 3:** Final validation and success prediction

## 📁 File Structure

```
script-gen/
├── agent_1_comic_processor.py      # CBR processing & script creation
├── agent_2_script_editor.py        # Review & competitive analysis
├── agent_3_final_integrator.py     # Final optimization & integration
├── pipeline_coordinator.py         # Full pipeline orchestration
├── Comics Data - sf.comics_shorts.csv  # Competitor performance data
├── README.md                       # This documentation
└── Civil War II 003 (2016) GetComics.INFO.cbr  # Example comic file
```

## 🎛️ Advanced Usage

### Custom Competitor Data
Replace the CSV file with your own data using this format:
```csv
Video ID,Title,Description,Transcript,URL
XnFHna_gwK4,"Deadpool Takes Spider-Man To Hell #spiderman #shorts","Description...","Full transcript...","https://..."
```

### Error Handling
The pipeline includes comprehensive error handling:
- **Input validation** before processing
- **Timeout protection** (10 minutes per agent)
- **Graceful failure** with detailed error messages
- **Results preservation** in case of partial completion

### Output Management
- **Timestamped files** prevent overwrites
- **Results directory** for organized storage
- **Detailed reports** for pipeline analysis
- **JSON outputs** for programmatic access

## 🏆 Success Metrics

### Technical Implementation
- ✅ OpenAI Vision API integration for CBR processing
- ✅ Three-agent pipeline with proper data flow
- ✅ Error handling and timeout protection
- ✅ Competitive intelligence integration

### Content Quality
- ✅ Story integrity preservation from source material
- ✅ 60-90 second timing optimization
- ✅ Engagement-driven script optimization
- ✅ A/B testing title generation

### System Reliability  
- ✅ Consistent high-quality outputs
- ✅ Comprehensive validation and quality checks
- ✅ Production-ready script delivery
- ✅ Pipeline monitoring and reporting

## 🐛 Troubleshooting

### Common Issues

**"No images found in CBR file"**
- Ensure file is valid CBR/CBZ format
- Check file isn't corrupted
- Try renaming .cbr to .zip and extracting manually

**"API call failed"**
- Verify OpenAI API key is valid and has credits
- Check internet connection
- Ensure API key has Vision access

**"Agent timed out"**
- Large comic files may take longer
- Consider reducing target duration
- Check system resources

**"Could not find output file"**
- Agents save timestamped files in current directory
- Check for permission issues
- Verify previous agent completed successfully

### Performance Optimization
- **Image Sampling:** Agents sample key pages for efficiency
- **Rate Limiting:** Built-in delays respect API limits
- **Batch Processing:** Optimize multiple comics by running pipeline sequentially

## 📈 Expected Performance

### Processing Times
- **Agent 1:** 2-5 minutes (depends on comic length and page count)
- **Agent 2:** 1-3 minutes (depends on competitor data size)
- **Agent 3:** 1-2 minutes (script optimization and validation)
- **Total Pipeline:** 5-10 minutes per comic

### API Costs (Approximate)
- **Agent 1:** $2-5 per comic (Vision API for page analysis)
- **Agent 2:** $0.50-1 per review (Text API for analysis)
- **Agent 3:** $0.50-1 per integration (Text API for optimization)
- **Total:** $3-7 per comic processed

## 🤝 Contributing

This system is designed for extensibility:
- **Add new agents** by following the established interface patterns
- **Customize prompts** in each agent for different content types
- **Extend competitor analysis** with additional data sources
- **Integrate new APIs** for enhanced processing capabilities

## 📄 License

This project is provided as-is for educational and commercial use. Ensure compliance with OpenAI's usage policies and comic book copyright laws.

---

**🎬 Ready to transform comics into viral YouTube content? Start with the Quick Start guide above!**# script-gen
# script-gen
