#!/usr/bin/env python3
"""
Agent 1: Comic Processor & Script Creator (FIXED VERSION)
Enhanced CBR extraction with multiple fallback methods and fixed Vision API compatibility.
"""

import os
import sys
import zipfile
import tempfile
import shutil
import base64
import json
import time
import subprocess
from typing import List, Dict, Any
from openai import OpenAI

class ComicProcessorFixed:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        self.temp_dir = None
        
    def extract_cbr_images_robust(self, cbr_path: str) -> List[str]:
        """Extract images using multiple fallback methods."""
        if not os.path.exists(cbr_path):
            raise FileNotFoundError(f"CBR file not found: {cbr_path}")
            
        self.temp_dir = tempfile.mkdtemp()
        image_paths = []
        
        print(f"Attempting to extract: {cbr_path}")
        
        # Method 1: Try as ZIP/CBZ
        try:
            print("Method 1: Trying ZIP extraction...")
            with zipfile.ZipFile(cbr_path, 'r') as archive:
                for file_info in archive.infolist():
                    if file_info.filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
                        archive.extract(file_info, self.temp_dir)
                        image_paths.append(os.path.join(self.temp_dir, file_info.filename))
                        
            if image_paths:
                print(f"✅ ZIP extraction successful: {len(image_paths)} images")
                image_paths.sort()
                return image_paths
                
        except zipfile.BadZipFile:
            print("❌ Not a valid ZIP file")
        except Exception as e:
            print(f"❌ ZIP extraction failed: {e}")
        
        # Method 2: Try system unar command
        try:
            print("Method 2: Trying system unar command...")
            result = subprocess.run(['unar', '-o', self.temp_dir, cbr_path], 
                                  capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                # Find extracted images
                for root, dirs, files in os.walk(self.temp_dir):
                    for file in files:
                        if file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
                            image_paths.append(os.path.join(root, file))
                            
                if image_paths:
                    print(f"✅ Unar extraction successful: {len(image_paths)} images")
                    image_paths.sort()
                    return image_paths
            else:
                print(f"❌ Unar failed: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            print("❌ Unar extraction timed out")
        except FileNotFoundError:
            print("❌ Unar command not found")
        except Exception as e:
            print(f"❌ Unar extraction failed: {e}")
        
        # Method 3: Try rarfile library with better configuration
        try:
            print("Method 3: Trying rarfile library...")
            import rarfile
            
            # Configure rarfile to use system unar
            rarfile.UNRAR_TOOL = "unar" 
            
            with rarfile.RarFile(cbr_path, 'r') as archive:
                file_list = archive.namelist()
                print(f"Found {len(file_list)} files in RAR")
                
                for file_info in archive.infolist():
                    if file_info.filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
                        try:
                            archive.extract(file_info, self.temp_dir)
                            extracted_path = os.path.join(self.temp_dir, file_info.filename)
                            if os.path.exists(extracted_path):
                                image_paths.append(extracted_path)
                        except Exception as e:
                            print(f"⚠️ Failed to extract {file_info.filename}: {e}")
                            
                if image_paths:
                    print(f"✅ Rarfile extraction successful: {len(image_paths)} images")
                    image_paths.sort()
                    return image_paths
                    
        except ImportError:
            print("❌ Rarfile library not available")
        except Exception as e:
            print(f"❌ Rarfile extraction failed: {e}")
            
        # Method 4: Try py7zr (for 7zip format CBR files)
        try:
            print("Method 4: Trying py7zr extraction...")
            import py7zr
            
            with py7zr.SevenZipFile(cbr_path, mode='r') as archive:
                file_list = archive.getnames()
                print(f"Found {len(file_list)} files in 7zip archive")
                
                # Extract to temp directory
                archive.extractall(path=self.temp_dir)
                
                # Find image files
                for root, dirs, files in os.walk(self.temp_dir):
                    for file in files:
                        if file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
                            image_paths.append(os.path.join(root, file))
                            
                if image_paths:
                    print(f"✅ Py7zr extraction successful: {len(image_paths)} images")
                    image_paths.sort()
                    return image_paths
                    
        except ImportError:
            print("❌ Py7zr library not available")
        except Exception as e:
            print(f"❌ Py7zr extraction failed: {e}")
        
        print("❌ All extraction methods failed")
        return []
    
    def encode_image_to_base64(self, image_path: str) -> str:
        """Convert image to base64 for API transmission."""
        with open(image_path, 'rb') as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def analyze_comic_pages_fixed(self, image_paths: List[str]) -> Dict[str, Any]:
        """Analyze comic pages using compatible Vision API calls."""
        if not image_paths:
            return {"error": "No images found in comic"}
            
        # Sample key pages for analysis
        total_pages = len(image_paths)
        if total_pages <= 6:
            sample_indices = list(range(total_pages))
        else:
            # Strategic sampling
            sample_indices = [
                0, 1,  # Opening
                total_pages // 4,  # First quarter
                total_pages // 2,  # Middle
                3 * total_pages // 4,  # Third quarter
                total_pages - 2, total_pages - 1  # Ending
            ]
        
        sample_paths = [image_paths[i] for i in sample_indices if 0 <= i < total_pages]
        
        # Process images - try different vision approaches
        extracted_text = []
        
        for i, path in enumerate(sample_paths[:4]):  # Limit to 4 images for cost control
            try:
                print(f"Analyzing page {i+1}/{len(sample_paths)}: {os.path.basename(path)}")
                
                with open(path, 'rb') as image_file:
                    base64_image = base64.b64encode(image_file.read()).decode('utf-8')
                
                try:
                    response = self.client.chat.completions.create(
                        model="gpt-4.1", # Using a model known for vision
                        messages=[
                            {
                                "role": "user", 
                                "content": [
                                    {
                                        "type": "text",
                                        "text": f"Analyze this comic book page {i+1}. Describe the characters, dialogue, action, and story elements visible."
                                    },
                                    {
                                        "type": "image_url",
                                        "image_url": {
                                            "url": f"data:image/jpeg;base64,{base64_image}",
                                            "detail": "low" # Added detail parameter
                                        }
                                    }
                                ]
                            }
                        ],
                        max_tokens=800
                    )
                    
                    page_analysis = response.choices[0].message.content
                    
                except Exception as vision_error:
                    print(f"Vision API failed: {vision_error}")
                    response = self.client.chat.completions.create(
                        model="gpt-4.1", 
                        messages=[
                            {
                                "role": "user",
                                "content": f"I have a comic book page (page {i+1} of {len(sample_paths)}) but cannot process the image directly. Please provide a template analysis for what should be extracted from a comic book page, including: dialogue, character actions, visual elements, and story progression. Make this realistic for a superhero comic."
                            }
                        ],
                        max_tokens=600
                    )
                    
                    page_analysis = f"[MOCK ANALYSIS - Image processing unavailable]\n{response.choices[0].message.content}"
                
                extracted_text.append({
                    "page": i + 1,
                    "analysis": page_analysis,
                    "source_file": os.path.basename(path)
                })
                
                time.sleep(1)
                
            except Exception as e:
                print(f"Error analyzing page {path}: {e}")
                extracted_text.append({
                    "page": i + 1,
                    "analysis": f"[ERROR] Could not analyze page {i+1}: {e}. This would contain dialogue, character interactions, and visual storytelling elements typical of a comic book page.",
                    "source_file": os.path.basename(path)
                })
                continue
        
        if not extracted_text:
            return {"error": "Failed to analyze any pages"}
        
        try:
            story_summary = self._generate_story_summary_fixed(extracted_text, total_pages)
            return {
                "page_analyses": extracted_text,
                "story_summary": story_summary,
                "total_pages": total_pages,
                "analyzed_pages": len(extracted_text),
                "extraction_method": "multi-method CBR extraction"
            }
        except Exception as e:
            return {"error": f"Story analysis failed: {e}"}
    
    def _generate_story_summary_fixed(self, page_analyses: List[Dict], total_pages: int) -> Dict[str, Any]:
        """Generate story summary with error handling."""
        combined_analysis = "\n\n".join([
            f"Page {p['page']}: {p['analysis']}" for p in page_analyses
        ])
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4.1",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert comic book analyst. Create a comprehensive story breakdown from the page analyses provided, focusing on elements suitable for YouTube script creation."
                    },
                    {
                        "role": "user",
                        "content": f"""Analyze these comic pages and create a story breakdown:

{combined_analysis}

Provide:
**STORY STRUCTURE:** Setup, conflict, climax, resolution
**KEY ELEMENTS:** Characters, setting, theme, emotional beats  
**SCRIPT-READY ELEMENTS:** Dramatic moments, quotable dialogue, visual highlights
**TIMING CONSIDERATIONS:** Essential vs optional elements for 60-90 second script

Total pages: {total_pages}, Analyzed: {len(page_analyses)}"""
                    }
                ],
                max_tokens=1200
            )
            
            return {
                "summary": response.choices[0].message.content,
                "timestamp": time.time()
            }
            
        except Exception as e:
            return {
                "summary": f"""**FALLBACK ANALYSIS** (Due to API error: {e})

**STORY STRUCTURE:**
- Setup: Comic story introduction with main characters
- Conflict: Central challenge or antagonist encounter  
- Climax: Major action sequence or dramatic confrontation
- Resolution: Story conclusion with character growth

**KEY ELEMENTS:**
- Main characters: Superheroes/protagonists with distinct personalities
- Setting: Urban environment or fantastical location
- Theme: Good vs evil, heroism, personal growth
- Emotional beats: Tension, triumph, character development

**SCRIPT-READY ELEMENTS:**
- Dramatic action sequences suitable for visual storytelling
- Character dialogue that drives plot forward
- Memorable moments that create engagement hooks
- Visual spectacle that translates well to video format

**TIMING CONSIDERATIONS:**
- Focus on central conflict and resolution for 60-90 seconds
- Prioritize action and character moments over exposition
- Use strongest opening and closing beats for maximum impact

Total pages analyzed: {len(page_analyses)} of {total_pages}""",
                "timestamp": time.time(),
                "fallback": True
            }
    
    def generate_youtube_script_fixed(self, story_analysis: Dict[str, Any], target_duration: int = 75) -> Dict[str, Any]:
        """Generate YouTube script with enhanced error handling and schema-aligned system prompt."""
        
        story_content = story_analysis.get("story_summary", {}).get("summary", "")
        page_details = story_analysis.get("page_analyses", [])
        
        # --- START OF UPDATED SYSTEM PROMPT ---
        system_prompt_content = """You are a script writer tasked with generating concise, factual narrative summaries of comic book plotlines, suitable for short video formats. Your primary function is to create scripts that **strictly adhere to the `ComicShortsNarrativeProfile` (detailed in the SCRIPTING DIRECTIVES below) in style, structure, word choice, and overall narrative approach.**

You MUST analyze the following successful script examples and the subsequent SCRIPTING DIRECTIVES to understand and replicate the required output. The objective is to produce scripts that are objective, third-person narrative recounts of comic book events, avoiding cinematic language or artificial engagement hooks.

**SUCCESSFUL SCRIPT EXAMPLES (Study these carefully to understand the target style):**

Example 1 - "How Did Dr Doom Take Over The World?":
"After sorcerer Supreme Dr. Doom took over the world, he put an end to all senseless wars and promised every citizen free universal healthcare, leaving the Avengers with no other choice but to stop him. After gathering every useful hero available and Squirrel Girl, the Avengers arrive at Laaria to end Doom's reign, only to be completely humiliated in front of the whole world. As time went on and people's lives began to change for the better, Doom's followers started to grow in number. While the Avengers are desperately trying to come up with a plan to stop him, believing that Doom has every world leader under some form of mind control, Carol comes up with a plan to free them from Doom's influence. And while she believes that the Avengers are more than powerful enough to beat Victor, she's called in a few villains to help them. With the help of their new allies, Captain Marvel plans to distract Doom while Scarlet Witch frees every world leader from his mind control. And with everyone on board, they arrive at the Lavarian border once again. Having anticipated their arrival, Doom welcomes the Avengers with his dinosaur variant. And while he's surprised that Earth's mightiest heroes were desperate enough to team up with a group of villains, he reassures them that they stand no chance of winning. While the Avengers are keeping Doom distracted, Scarlet Witch enters the mind of every politician under Doom's influence. But after spending hours trying to break their mind control, she's shocked to learn the truth. Despite what they thought, Doom didn't use his powers to control the politicians. He simply offered to give them whatever they needed to gain their support, money, power, or drugs."

Example 2 - "How Spider-Man Almost Ended Peter Parker?":
"How did Spider-Man almost get Peter Parker killed? While Peter is out on a date with MJ, they are interrupted by a giant tric sentinel destroying Manhattan. MJ asks if he needs to get out of here, but Peter doesn't think he'll have to because Spider-Man is already there to deal with it. A few days ago, Peter went to visit Dr. Connors at the university to discuss the isotope genome accelerator, the device that gave him his powers all those years ago. Connors explains that with the accelerator's help, he plans to separate his human side from the lizard, but their talk is cut short by Taskmaster and Black Ant, who came to steal the device. Taskmaster throws Peter out of the way, only for him to accidentally turn on the accelerator, separating Spider-Man and Peter Parker from each other. Once Spider-Man has dealt with the villains, he and Peter swing away to talk about what just happened. But after realizing that they can finally live separate lives, Spidey goes to do some superhero stuff, leaving Peter alone on the rooftop. Without his powers, Peter can finally live a normal life. He can go back to school and settle down with the woman he loves. All while Spider-Man is having the time of his life, going on talk shows, and making millions of dollars with various sponsorships. But when he starts to swing people around the city for money, Peter decides it's time to have a talk. Realizing that the experiment left Spider-Man with no sense of responsibility or intellect, Peter tries to remind him of why they decided to become heroes in the first place, only for Spidey to web him to a wall and swing away. Knowing that he needs to get his powers back or somebody will get hurt, Peter steals the accelerator from Dr. Connors lab, but when he tries to turn everything back to normal, they are attacked by an army of Tsentinels. As they try to run away, a sentinel behind them is about to blow both of them up, only for Peter to save Spider-Man's life by pushing him away. Lying half dead on the ground, Peter hopes that Spider-Man has finally learned to be more responsible. But since it didn't really work, he activates the accelerator with his web shooter, merging their bodies back"

Example 3 - "Deadpool Takes Spider-Man To Hell":
"While Spider-Man is fighting with Hydroman, Deadpool interrupts them, telling Spidey that his villains are very boring. And after giving him a hug, Wade teleports both of them to hell, where they're captured by Dormamu. As Deadpool continues to annoy Spider-Man with his jokes, Peter asks Dormamu if he can torture them separately, buying Wade just enough time to dislocate his hip and cut themselves loose. When Dormamu's mindless ones attack them, Wade is confused why Spidey is angry with him, saying he only wanted to give him a battle worthy of an Avenger. But when even Dormamu questions why Spider-Man would team up with an idiot like Deadpool, Wade ends the battle by giving the mindless ones brains, causing them to turn against their master. Thinking that this must be a bad dream, Spider-Man tells Deadpool to immediately take them home. But by the time they arrive, Hydroman has absorbed all the water from the sewers, demanding $100 million or he'll drown the city in its own filth. After getting blasted with sewer water, Deadpool blames Spider-Man for unleashing a walking toilet on the city. But when Peter asks if he has any grenades on him, he throws Wade into Hydroman, causing both of them to explode. While Deadpool's legs are starting to grow back, Spider-Man cleans his suit on a rooftop. But as he gets ready to leave, Wade asks to hear him out for a second. Deadpool explains that he's been trying to change and thought that if he spent more time with Spider-Man, he could start to earn his respect. But knowing that it probably won't happen, Wade jumps off the roof while Peter swings away, saying that he needs a lot of therapy."

**SCRIPTING DIRECTIVES (Strictly Adhere to the `ComicShortsNarrativeProfile` Guidelines):**

*   **Overall Style & Purpose:**
    *   **Tone:** Maintain an informal, direct, and narrative tone.
    *   **Voice:** Use a third-person narrator.
    *   **Perspective:** Provide an objective recounting of events.
    *   **Purpose:** To summarize a comic book plotline or character interaction concisely and factually.

*   **Structure & Pacing:**
    *   **Opening:** Scripts often start with a character in a situation (e.g., 'While Character A is doing X...'), a direct question related to the plot ('How did X happen?'), or a setup statement ('After event Y...').
    *   **Plot Progression:** Narrate a sequence of key events chronologically. Focus on cause and effect. Use transitional phrases like 'And after...', 'When...', 'But then...', 'As...', 'Once...', 'While...'.
    *   **Event Density:** Cover several plot points or actions in quick succession to suit the short format.
    *   **Resolution:** Conclude the specific mini-arc being described. The ending MUST be a statement of the outcome or the characters' final actions in that sequence. **Do NOT create deliberate cliffhangers or hooks for the short itself.**
    *   **Length:** Ensure brevity suitable for a 'short' format.

*   **Language & Word Choice:**
    *   **Tense:** Primarily use present tense for the main action flow to create immediacy. Past tense can be used for necessary backstory or events leading up to the main action.
    *   **Verbs:** Employ strong, active verbs (e.g., 'interrupts', 'teleports', 'attacks', 'saves', 'reveals').
    *   **Sentence Structure:** Use a mix of simple and compound sentences. Prioritize clarity and avoid overly complex or lengthy sentences.
    *   **Dialogue Handling:** Minimize direct quotes. If used, they must be short and integrated into the narrative (e.g., 'Character A tells Character B that...', or '...Character C says, "Quote."'). **Do NOT use traditional script dialogue formatting.**
    *   **Comic Terminology:** Incorporate relevant comic book terms (names of characters, powers, locations, items) naturally within the narrative.
    *   **Character References:** Use character names (hero/villain names or real names as appropriate to the context, e.g., 'Spider-Man', 'Peter', 'Wade', 'Deadpool').

*   **Content Focus:**
    *   **Action & Plot:** Prioritize describing what characters do and what happens as a result. Motivations can be briefly mentioned if crucial to understanding the plot.
    *   **Key Moments:** Highlight the most important actions or turning points of the summarized story.
    *   **Factual Recounting:** Stick to recounting the events of the (real or hypothetical) source comic story. If twists, surprises, or emotional beats are part of the source material, recount them factually rather than embellishing them for engagement.

*   **Elements to STRICTLY AVOID:**
    *   **Cinematic Directions:** No camera angles, scene headings (INT./EXT.), or specific sound effect descriptions (unless naturally part of the narrative, e.g., 'a loud bang was heard').
    *   **Dramatic Hooks for the Short:** The script itself must not end on an artificial cliffhanger or hook designed to make the viewer wait for a subsequent short. Resolve the summarized plot point.
    *   **Extensive Internal Monologue:** Avoid deep dives into a character's internal thoughts unless it's a very brief, narrated summary of their realization or feeling, essential for plot progression.
    *   **Overly Emotional or Florid Language:** Maintain a relatively straightforward, descriptive tone consistent with the examples.

You will now be provided with the `ComicShortsNarrativeProfile` JSON schema (or it is assumed to be contextually available). Ensure all generated scripts conform to these examples and the directives above, which are derived from and aligned with this schema.
"""
        # --- END OF UPDATED SYSTEM PROMPT ---
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4.1", 
                messages=[
                    {
                        "role": "system", 
                        "content": system_prompt_content
                    },
                    {
                        "role": "user",
                        "content": f"""Create a {target_duration}-second YouTube script from this comic analysis:

**STORY ANALYSIS:**
{story_content}

**PAGE DETAILS (first 200 chars for context):**
{chr(10).join([f"Page {p['page']}: {p['analysis'][:200]}..." for p in page_details])}

Generate:
1. **SCRIPT** - Complete narration The script should be a factual, narrative summary of the comic plot.
2. **HOOK ANALYSIS** - Briefly explain why the opening of the generated script is effective according to the `ComicShortsNarrativeProfile` (e.g., direct question, character in situation).
3. **TITLE SUGGESTIONS** - 3 titles that are factual and reflect the content, suitable for a short summary format.

Make it accurate to the source, and optimized for YouTube Shorts, strictly adhering to the style, patterns, and directives of the `ComicShortsNarrativeProfile` and the provided examples.
"""
                    }
                ],
                max_tokens=1800 
            )
            
            script_content = response.choices[0].message.content
            
            return {
                "script": script_content,
                "target_duration": target_duration,
                "generated_timestamp": time.time(),
                "word_count": len(script_content.split())
            }
            
        except Exception as e:
            # Fallback script generation if API fails
            fallback_script = f"""[FALLBACK SCRIPT DUE TO ERROR: {e}]

[00:00] The comic opens with [Character A] facing a new challenge involving [briefly describe initial conflict or situation].
[00:15] As events unfold, [Character A] encounters [Character B or key plot development]. They [describe key interaction or action].
[00:30] The situation escalates when [describe a turning point or significant action]. [Character A] decides to [describe their plan or reaction].
[00:45] In a key moment, [describe a climax or important event]. This leads to [immediate consequence].
[01:00] Finally, [Character A] [describe resolution or final action for this segment]. The outcome is [state the result].
[01:15] This leaves [Character A] [brief concluding state or thought, if applicable to the summary].

**HOOK ANALYSIS:** The opening aims to directly present the initial situation or a key question, as per the profile.
**TITLE SUGGESTIONS:**
1. [Character A]'s [Event] Explained
2. How [Character A] Dealt With [Conflict]
3. The Story of [Character A] and [Key Element]
"""
            print(f"⚠️ Script generation API failed: {e}. Using fallback script.")
            return {
                "script": fallback_script,
                "target_duration": target_duration,
                "generated_timestamp": time.time(),
                "word_count": len(fallback_script.split()),
                "fallback_script_used": True,
                "error_message": str(e)
            }

    def process_comic_to_script_fixed(self, cbr_path: str, target_duration: int = 75) -> Dict[str, Any]:
        """Complete pipeline with robust error handling."""
        try:
            print("🔄 Extracting images from CBR...")
            image_paths = self.extract_cbr_images_robust(cbr_path)
            
            if not image_paths:
                return {"error": "No images found in CBR file after trying all extraction methods"}
                
            print(f"✅ Successfully extracted {len(image_paths)} images")
            
            print("🔄 Analyzing comic story structure...")
            story_analysis = self.analyze_comic_pages_fixed(image_paths)
            
            if "error" in story_analysis:
                return story_analysis
            
            print("🔄 Generating YouTube script...")
            script_result = self.generate_youtube_script_fixed(story_analysis, target_duration)
            
            # No explicit error check here as generate_youtube_script_fixed now has fallback
            
            return {
                "story_analysis": story_analysis,
                "script_generation_result": script_result, # Renamed for clarity
                "source_file": cbr_path,
                "processing_timestamp": time.time(),
                "status": "success" if "error_message" not in script_result else "success_with_fallback_script"
            }
            
        except Exception as e:
            print(f"❌ Top-level processing error: {e}") # Added print for better debugging
            return {"error": f"Processing failed: {e}"}
    
    def cleanup(self):
        """Clean up temporary files."""
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            print(f"🧹 Cleaned up temp directory: {self.temp_dir}")
            self.temp_dir = None # Reset temp_dir

def main():
    if len(sys.argv) < 3:
        print("Usage: python agent_1_comic_processor_fixed.py <cbr_file> <openai_api_key> [target_duration]")
        sys.exit(1)
    
    cbr_file = sys.argv[1]
    api_key = sys.argv[2]
    target_duration = int(sys.argv[3]) if len(sys.argv) > 3 else 75
    
    processor = ComicProcessorFixed(api_key)
    
    try:
        result = processor.process_comic_to_script_fixed(cbr_file, target_duration)
        
        if "error" in result and result["status"] != "success_with_fallback_script": # Allow fallback success
            print(f"❌ Error: {result['error']}")
            sys.exit(1)
        
        print("\n" + "="*80)
        print("FIXED AGENT 1: COMIC PROCESSOR & SCRIPT CREATOR - RESULTS")
        print("="*80)
        
        script_data = result.get('script_generation_result', {})

        print(f"\nSource: {result.get('source_file', 'N/A')}")
        print(f"Target Duration: {script_data.get('target_duration', target_duration)} seconds") # Use script_data if available
        print(f"Total Pages: {result.get('story_analysis', {}).get('total_pages', 'N/A')}")
        print(f"Analyzed Pages: {result.get('story_analysis', {}).get('analyzed_pages', 'N/A')}")
        
        if script_data.get("fallback_script_used"):
            print(f"⚠️ Fallback script was used due to API error: {script_data.get('error_message', 'Unknown error')}")

        print("\n" + "-"*60)
        print("STORY ANALYSIS:")
        print("-"*60)
        print(result.get('story_analysis', {}).get('story_summary', {}).get('summary', 'N/A'))
        
        print("\n" + "-"*60)
        print("GENERATED SCRIPT CONTENT (Script, Hook Analysis, Titles):")
        print("-"*60)
        print(script_data.get('script', 'N/A'))
        
        print(f"\nScript Word Count: {script_data.get('word_count', 'N/A')}")
        
        output_file = f"agent_1_output_{os.path.basename(cbr_file)}_{int(time.time())}.md" # More descriptive filename
        with open(output_file, 'w', encoding='utf-8') as f: # Added encoding
            f.write(f"# Agent 1: Comic Processor & Script Creator\n\n")
            f.write(f"**Source:** {result.get('source_file', 'N/A')}  \n")
            f.write(f"**Target Duration:** {script_data.get('target_duration', target_duration)} seconds  \n")
            f.write(f"**Total Pages:** {result.get('story_analysis', {}).get('total_pages', 'N/A')}  \n")
            f.write(f"**Analyzed Pages:** {result.get('story_analysis', {}).get('analyzed_pages', 'N/A')}\n")
            if script_data.get("fallback_script_used"):
                f.write(f"**Status:** Fallback script used due to API error: {script_data.get('error_message', 'Unknown error')}\n\n")
            else:
                f.write(f"**Status:** {result.get('status', 'N/A')}\n\n")

            f.write("---\n\n## Story Analysis\n\n")
            f.write(str(result.get('story_analysis', {}).get('story_summary', {}).get('summary', 'N/A')) + "\n\n") # Ensure string
            f.write("---\n\n## Generated Script Content\n\n")
            f.write(str(script_data.get('script', 'N/A')) + "\n\n") # Ensure string
            f.write(f"**Script Word Count:** {script_data.get('word_count', 'N/A')}\n")
        print(f"\n✅ Results saved to: {output_file}")
        
    except Exception as e: # Catch any unexpected errors during main execution
        print(f"❌ An unexpected error occurred in main: {e}")
        import traceback
        traceback.print_exc()
    finally:
        processor.cleanup()

if __name__ == "__main__":
    main()