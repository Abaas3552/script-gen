
"""
Agent 2: Script Editor & Competitive Analyst
Reviews generated scripts against original comic content and competitor benchmarks
to provide improvement recommendations, aligning with the ComicShortsNarrativeProfile.
Handles output path for JSON results.
"""

import os
import sys
import json
import csv
import time
from typing import List, Dict, Any
from openai import OpenAI

class ScriptEditor:
    def __init__(self, api_key: str, competitor_data_path: str):
        self.client = OpenAI(api_key=api_key)
        self.competitor_data = self._load_competitor_data(competitor_data_path)

    def _load_competitor_data(self, csv_path: str) -> List[Dict[str, str]]:
        """Load competitor YouTube shorts data from CSV."""
        competitor_data = []
        if not csv_path or not os.path.exists(csv_path):
            print(f"Warning: Competitor data file not found or path not provided: {csv_path}. Competitive analysis will be limited.")
            return competitor_data
        try:
            with open(csv_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    competitor_data.append({
                        'video_id': row.get('Video ID', ''),
                        'title': row.get('Title', ''),
                        'description': row.get('Description', ''),
                        'transcript': row.get('Transcript', ''),
                        'url': row.get('URL', '')
                    })
            print(f"Loaded {len(competitor_data)} competitor videos for analysis from {csv_path}")
        except Exception as e:
            print(f"Warning: Could not load competitor data from {csv_path}: {e}")

        return competitor_data

    def analyze_competitor_patterns(self) -> Dict[str, Any]:
        """Analyze competitor data to identify successful patterns, benchmarked against ComicShortsNarrativeProfile."""
        if not self.competitor_data:
            return {"info": "No competitor data available or loaded for analysis.", "competitive_analysis": "Not performed."}

        competitor_examples = []
        for i, video in enumerate(self.competitor_data[:10]):
            competitor_examples.append(f"""
VIDEO {i+1}:
Title: {video['title']}
Description: {video['description'][:200]}...
Transcript: {video['transcript'][:500]}...
""")

        combined_examples = "\n".join(competitor_examples)

        system_prompt_content = """You are a competitive content analyst specializing in YouTube Shorts for comic book content. Your primary goal is to identify how competitor content aligns with or deviates from the **`ComicShortsNarrativeProfile`** style, which emphasizes factual, third-person narrative summaries.

**REFERENCE `ComicShortsNarrativeProfile` STYLE (Derived from successful examples - this is the target style):**
- **Tone:** Informal, direct, narrative.
- **Voice:** Third-person narrator.
- **Perspective:** Objective recounting of events.
- **Purpose:** To summarize a comic book plotline concisely and factually.
- **Structure:** Often starts with a character in a situation or a direct question. Chronological plot progression. Concludes the specific mini-arc without artificial cliffhangers for the short itself.
- **Language:** Primarily present tense. Strong, active verbs. Minimized direct quotes, integrated into narration. No cinematic directions.

**SUCCESSFUL SCRIPT EXAMPLES (These embody the `ComicShortsNarrativeProfile`):**
[Examples as in original file - omitted for brevity here but should be included]
Example 1 - "How Did Dr Doom Take Over The World?": ...
Example 2 - "How Spider-Man Almost Ended Peter Parker?": ...
Example 3 - "Deadpool Takes Spider-Man To Hell": ...

Your task is to analyze competitor content and identify patterns specifically in relation to this `ComicShortsNarrativeProfile` style. Focus on how they achieve engagement while adhering to, or deviating from, these factual narrative summary principles.
"""
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
                        "content": f"""Analyze these YouTube Shorts about comic books. Identify key patterns in their titles, content structure, narrative techniques, and engagement optimization, **specifically in relation to the `ComicShortsNarrativeProfile` style (factual, narrative summary) described in the system prompt and exemplified by the provided successful scripts.**

{combined_examples}

Provide detailed analysis covering:

**TITLE PATTERNS (in relation to factual summary style):**
- How titles reflect the narrative summary approach.
- Use of questions vs. statements for factual summaries.
- Character name placement in titles for direct summaries.

**CONTENT STRUCTURE (for narrative summaries):**
- How videos open to establish the summary's scope.
- Pacing and information delivery for concise factual recounting.
- How the summarized arc is concluded.

**NARRATIVE TECHNIQUES (for factual summaries):**
- Storytelling approaches that effectively summarize comic plots.
- How characters and conflicts are introduced in a summary format.

**ENGAGEMENT OPTIMIZATION (within the factual summary framework):**
- How hooks are created for factual summaries (e.g., intriguing questions about plot points).
- Elements that drive retention in narrative summaries.

**COMPETITIVE INSIGHTS (benchmarked against `ComicShortsNarrativeProfile`):**
- What makes competitor summaries stand out while remaining factual.
- Common weaknesses in competitor summaries (e.g., deviation from factual recounting, unnecessary embellishments).
- How audience preferences are indicated for this type of factual summary content.

Provide specific, actionable recommendations for creating or improving scripts to better align with the `ComicShortsNarrativeProfile` style, based on observed competitor strategies that are compatible with this factual narrative approach.
"""
                    }
                ],
                max_tokens=2000
            )

            return {
                "competitive_analysis": response.choices[0].message.content,
                "videos_analyzed": len(self.competitor_data[:10]),
                "analysis_timestamp": time.time()
            }

        except Exception as e:
            return {"error": f"Competitive analysis failed: {e}"}

    def review_script_accuracy(self, agent_1_output: Dict[str, Any]) -> Dict[str, Any]:
        """Review script accuracy against original comic content and adherence to ComicShortsNarrativeProfile."""
        story_analysis = agent_1_output.get("story_analysis", {})
        script_generation_result = agent_1_output.get("script_generation_result", {})
        comic_filename = story_analysis.get("comic_filename", "the comic")


        story_summary = story_analysis.get("story_summary", {}).get("summary", "")
        page_analyses = story_analysis.get("page_analyses", [])
        raw_script_output = script_generation_result.get("script", "")

        generated_script_content = raw_script_output
        if "SCRIPT" in raw_script_output.upper(): # More robust check for "SCRIPT"
            try:
                # Find "SCRIPT" then find "HOOK ANALYSIS" or "TITLE SUGGESTIONS"
                script_start_keyword = "SCRIPT"
                script_end_keywords = ["HOOK ANALYSIS", "TITLE SUGGESTIONS"]

                script_text_upper = raw_script_output.upper()
                script_start_index = script_text_upper.find(script_start_keyword)

                if script_start_index != -1:
                    actual_script_start = script_start_index + len(script_start_keyword)
                    # Find the earliest end keyword after the script start
                    script_end_index = len(raw_script_output) # Default to end of string
                    for end_keyword in script_end_keywords:
                        found_end_index = script_text_upper.find(end_keyword, actual_script_start)
                        if found_end_index != -1:
                            script_end_index = min(script_end_index, found_end_index)
                    
                    generated_script_content = raw_script_output[actual_script_start:script_end_index].strip()
                else: # "SCRIPT" keyword not found, use the whole thing but log it
                    print("Warning: 'SCRIPT' keyword not found in Agent 1 output, using raw output for script content.")


            except Exception as e:
                print(f"Could not parse script from Agent 1 output, using raw output. Error: {e}")
                generated_script_content = raw_script_output


        detailed_story_from_pages = "\n".join([
            f"Comic Page {p.get('page_number_in_comic', 'N/A')} (Sample {p.get('sample_index', 'N/A')} of '{comic_filename}'):\n{p.get('analysis', 'N/A')}" for p in page_analyses
        ])

        system_prompt_content = f"""You are an expert script editor specializing in comic book adaptations for '{comic_filename}'. Your role is to evaluate scripts not only for accuracy against source material but also for strict adherence to the **`ComicShortsNarrativeProfile` style.**

**`ComicShortsNarrativeProfile` KEY CHARACTERISTICS (This is the target style):**
- **Tone & Voice:** Informal, direct, third-person narrative.
- **Perspective & Purpose:** Objective recounting of events to concisely summarize a comic plot.
- **Structure:** Often starts with a character in a situation or a direct question. Chronological plot progression. Concludes the specific mini-arc factually, avoiding artificial cliffhangers for the short itself.
- **Language:** Primarily present tense. Strong, active verbs. Minimized direct quotes, integrated into narration. No cinematic directions (camera angles, scene headings).
- **Content Focus:** Prioritize describing what characters do and what happens. Factual recounting of the source comic story.

**QUALITY STANDARDS (against `ComicShortsNarrativeProfile`):**
- **Accuracy to Source:** Story events match source material (9/10+ expected).
- **Adherence to Profile Style:** Script strictly follows the `ComicShortsNarrativeProfile` characteristics (e.g., tense, voice, no cinematic hooks, factual summary) (9/10+ expected).
- **Completeness of Summary:** Core narrative arc of the summarized segment is preserved (8/10+ expected).
- **Clarity of Summary:** Viewers understand the summarized story without prior knowledge (9/10+ expected).

You have a keen eye for detail and deep understanding of storytelling principles as they apply to factual narrative summaries in the style of the `ComicShortsNarrativeProfile`.
"""
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
                        "content": f"""Review this YouTube script for the comic '{comic_filename}'. Evaluate its accuracy against the original comic content AND its adherence to the `ComicShortsNarrativeProfile` style (factual, third-person narrative summary, present tense, no cinematic hooks, etc.).

**ORIGINAL COMIC STORY ANALYSIS (Source Material Summary for '{comic_filename}'):**
{story_summary}

**DETAILED PAGE CONTENT (Source Material Details from analyzed pages of '{comic_filename}'):**
{detailed_story_from_pages}

**GENERATED SCRIPT (to be evaluated for '{comic_filename}'):**
{generated_script_content}

Provide comprehensive review covering:

**ACCURACY ASSESSMENT (vs. Source Material for '{comic_filename}'):**
- Story events: Are key plot points from the source represented correctly in the script?
- Character portrayal: Are characters depicted accurately as per the source?
- Dialogue adaptation: Is important dialogue from the source preserved or adapted well into the narrative?

**ADHERENCE TO `ComicShortsNarrativeProfile` STYLE:**
- **Narrative Voice & Tense:** Is it consistently third-person, primarily present tense?
- **Factual Recounting:** Does it stick to summarizing events without adding interpretation or embellishment?
- **Structure & Pacing:** Does it follow the expected structure for a factual summary (e.g., clear beginning of the summarized arc, chronological flow, factual conclusion of the arc)?
- **Language & Word Choice:** Is the language direct, with active verbs? Are direct quotes minimized and integrated?
- **Avoidance of Cinematic Elements:** Are there any cinematic directions, scene headings, or artificial hooks for the short itself?

**COMPLETENESS & CLARITY OF SUMMARY:**
- Essential elements: Are crucial components of the summarized comic segment missing?
- Plot coherence: Does the script tell a coherent summary of the intended comic segment?
- Clarity: Will viewers understand the summarized events?

**IMPROVEMENT RECOMMENDATIONS (for closer alignment with source and `ComicShortsNarrativeProfile`):**
- Specific additions/corrections for accuracy to the source material of '{comic_filename}'.
- Edits to improve adherence to the `ComicShortsNarrativeProfile` (e.g., tense changes, removing subjective language, ensuring factual conclusion).
- Suggestions for clarity or completeness of the summary.

Rate overall accuracy to source (1-10) AND overall adherence to `ComicShortsNarrativeProfile` style (1-10). Provide specific action items.
"""
                    }
                ],
                max_tokens=2000
            )

            return {
                "accuracy_review": response.choices[0].message.content,
                "source_pages_analyzed_count": len(page_analyses),
                "comic_filename_reviewed": comic_filename,
                "review_timestamp": time.time()
            }

        except Exception as e:
            return {"error": f"Accuracy review failed for '{comic_filename}': {e}"}

    def generate_improvement_recommendations(self, accuracy_review: Dict[str, Any],
                                           competitive_analysis: Dict[str, Any],
                                           original_script_output: str,
                                           comic_filename: str = "the comic") -> Dict[str, Any]:
        """Generate specific improvement recommendations based on reviews, focusing on ComicShortsNarrativeProfile."""

        accuracy_content = accuracy_review.get("accuracy_review", "")
        competitive_content = competitive_analysis.get("competitive_analysis", "")

        current_script_content = original_script_output
        if "SCRIPT" in original_script_output.upper(): # More robust check
            try:
                script_start_keyword = "SCRIPT"
                script_end_keywords = ["HOOK ANALYSIS", "TITLE SUGGESTIONS"]
                script_text_upper = original_script_output.upper()
                script_start_index = script_text_upper.find(script_start_keyword)

                if script_start_index != -1:
                    actual_script_start = script_start_index + len(script_start_keyword)
                    script_end_index = len(original_script_output)
                    for end_keyword in script_end_keywords:
                        found_end_index = script_text_upper.find(end_keyword, actual_script_start)
                        if found_end_index != -1:
                            script_end_index = min(script_end_index, found_end_index)
                    current_script_content = original_script_output[actual_script_start:script_end_index].strip()
                else:
                    print("Warning: 'SCRIPT' keyword not found in original script output for recommendations, using raw output.")
            except Exception as e:
                print(f"Could not parse script from original output for recommendations. Error: {e}")
                pass

        system_prompt_content = f"""You are an expert script optimization consultant for comic book content, specifically for '{comic_filename}'. Your goal is to synthesize accuracy reviews and competitive intelligence to provide actionable recommendations for improving scripts to **strictly align with the `ComicShortsNarrativeProfile` style (factual, third-person narrative summary).**

**`ComicShortsNarrativeProfile` KEY CHARACTERISTICS (The Target Style):**
- **Tone & Voice:** Informal, direct, third-person narrative.
- **Perspective & Purpose:** Objective recounting of events to concisely summarize a comic plot.
- **Structure:** Often starts with a character in a situation or a direct question. Chronological plot progression. Concludes the specific mini-arc factually, avoiding artificial cliffhangers for the short itself.
- **Language:** Primarily present tense. Strong, active verbs. Minimized direct quotes, integrated into narration. No cinematic directions.
- **Content Focus:** Prioritize describing what characters do and what happens. Factual recounting of the source comic story.

Focus on practical, specific recommendations that can be directly applied to elevate the script to meet the standards of the `ComicShortsNarrativeProfile`, using insights from competitor analysis only where they support this specific style.
"""
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
                        "content": f"""Based on the accuracy review (which includes adherence to the `ComicShortsNarrativeProfile`) and competitive analysis (benchmarked against this profile), provide optimization recommendations for the script for '{comic_filename}'. The primary goal is to ensure the script is an excellent example of the `ComicShortsNarrativeProfile` style.

**ACCURACY & PROFILE ADHERENCE REVIEW FINDINGS (for '{comic_filename}'):**
{accuracy_content}

**COMPETITIVE ANALYSIS INSIGHTS (Relevant to `ComicShortsNarrativeProfile` style):**
{competitive_content}

**CURRENT SCRIPT (to be improved for '{comic_filename}'):**
{current_script_content}

Generate a comprehensive improvement plan with:

**PRIORITY 1 - CRITICAL FIXES FOR ACCURACY & PROFILE ALIGNMENT:**
- Accuracy issues (deviations from source material of '{comic_filename}') that must be addressed.
- Deviations from `ComicShortsNarrativeProfile` style (e.g., wrong tense, subjective language, cinematic elements, artificial hooks) that must be corrected.
- Missing essential story elements for a complete summary of the comic segment from '{comic_filename}'.
- Clarity problems that confuse viewers of the summary.

**PRIORITY 2 - ENHANCING THE FACTUAL NARRATIVE SUMMARY (within `ComicShortsNarrativeProfile`):**
- Strengthening the opening of the summary (e.g., clearer setup of the summarized situation/question).
- Improving pacing for a concise and effective factual recount.
- Enhancing clarity of the summarized plot progression.
- Ensuring the ending provides a factual conclusion to the summarized arc.
- Word choice and narration style refinements to better fit the direct, objective, present-tense narrative style.

**PRIORITY 3 - CONSIDERING COMPATIBLE COMPETITIVE INSIGHTS:**
- Ways to make the factual summary more engaging *without* deviating from the `ComicShortsNarrativeProfile` (e.g., more vivid verbs, better transitions if supported by profile-compatible competitor examples).

**SPECIFIC EDITS (Illustrative examples for `ComicShortsNarrativeProfile` alignment):**
- Line-by-line suggestions for key improvements (e.g., changing "He felt sad" to "He looks down," if the former is too interpretive for the profile).
- Alternative phrasing for better factual recounting.
- Stronger transition phrases suitable for narrative summaries.
- Edits to ensure the ending is a factual resolution of the segment, not a hook.

**IMPLEMENTATION NOTES:**
- How changes ensure both source accuracy for '{comic_filename}' and strict adherence to the `ComicShortsNarrativeProfile`.
- Rationale for why suggestions improve the script as a factual narrative summary.

Provide specific, actionable recommendations with clear rationale, always prioritizing alignment with the `ComicShortsNarrativeProfile`.
"""
                    }
                ],
                max_tokens=2500
            )

            return {
                "improvement_recommendations": response.choices[0].message.content,
                "recommendation_timestamp": time.time(),
                "priority_breakdown": "Critical Fixes (Accuracy & Profile Alignment) → Enhancing Factual Summary → Compatible Competitive Insights"
            }

        except Exception as e:
            return {"error": f"Recommendation generation failed for '{comic_filename}': {e}"}

    def perform_complete_review(self, agent_1_output_path: str) -> Dict[str, Any]:
        """Perform complete script review and analysis."""
        try:
            with open(agent_1_output_path, 'r', encoding='utf-8') as f:
                agent_1_output = json.load(f)

            comic_filename_from_agent1 = agent_1_output.get("story_analysis", {}).get("comic_filename", "UnknownComic")
            print(f"Starting Agent 2 review for comic: {comic_filename_from_agent1}")

            print("Performing competitive analysis (benchmarked against ComicShortsNarrativeProfile)...")
            competitive_analysis = self.analyze_competitor_patterns()

            if "error" in competitive_analysis:
                print(f"Warning: Competitive analysis error - {competitive_analysis['error']}")
            if "info" in competitive_analysis: # Handle no data case
                print(f"Info: {competitive_analysis['info']}")


            print("Reviewing script accuracy and adherence to ComicShortsNarrativeProfile...")
            accuracy_review = self.review_script_accuracy(agent_1_output)

            if "error" in accuracy_review:
                return accuracy_review

            print("Generating improvement recommendations for ComicShortsNarrativeProfile alignment...")
            original_script_output_str = agent_1_output.get("script_generation_result", {}).get("script", "")

            recommendations = self.generate_improvement_recommendations(
                accuracy_review, competitive_analysis, original_script_output_str, comic_filename_from_agent1
            )

            if "error" in recommendations:
                return recommendations

            complete_review = {
                "comic_filename_reviewed": comic_filename_from_agent1,
                "original_agent_1_output_path": agent_1_output_path,
                "competitive_analysis_results": competitive_analysis,
                "accuracy_and_profile_review": accuracy_review,
                "improvement_recommendations_for_profile": recommendations,
                "review_timestamp": time.time(),
                "reviewer": "Agent 2: Script Editor & Competitive Analyst (Profile-Focused)"
            }

            return complete_review

        except FileNotFoundError:
            return {"error": f"Agent 1 output file not found: {agent_1_output_path}"}
        except json.JSONDecodeError:
            return {"error": f"Error decoding JSON from Agent 1 output file: {agent_1_output_path}"}
        except Exception as e:
            import traceback
            print(f"Unexpected error in perform_complete_review: {e}")
            traceback.print_exc()
            return {"error": f"Complete review failed due to an unexpected error: {e}"}

def main():
    if len(sys.argv) < 5:
        print("Usage: python agent_2_script_editor.py <agent_1_output.json> <competitor_data.csv> <openai_api_key> <output_json_path>")
        print("Example: python agent_2_script_editor.py agent_1.json competitors.csv sk-... /path/to/output/agent_2.json")
        sys.exit(1)

    agent_1_output_path_arg = sys.argv[1]
    competitor_data_path_arg = sys.argv[2]
    api_key_arg = sys.argv[3]
    output_json_path_arg = sys.argv[4]

    if not os.path.exists(agent_1_output_path_arg):
        print(f"Error: Agent 1 output file not found: {agent_1_output_path_arg}")
        sys.exit(1)

    # Competitor data is optional, ScriptEditor handles missing file
    if not os.path.exists(competitor_data_path_arg):
        print(f"Warning: Competitor data file not found: {competitor_data_path_arg}. Competitive analysis will be limited.")
        # Pass the path anyway; constructor will handle it.

    # Ensure output directory exists
    output_dir = os.path.dirname(output_json_path_arg)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
        print(f"Created output directory: {output_dir}")

    editor = ScriptEditor(api_key_arg, competitor_data_path_arg)

    try:
        result = editor.perform_complete_review(agent_1_output_path_arg)

        if "error" in result:
            print(f"❌ Error during review process: {result['error']}")
            # Still save the error information to the JSON file
            with open(output_json_path_arg, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2)
            print(f"Error details saved to: {output_json_path_arg}")
            sys.exit(1)

        print("\n" + "="*80)
        print(f"AGENT 2: SCRIPT EDITOR & COMPETITIVE ANALYST (Profile-Focused) - RESULTS for '{result.get('comic_filename_reviewed', 'UnknownComic')}'")
        print("="*80)

        comp_analysis_results = result.get('competitive_analysis_results', {})
        acc_profile_review_results = result.get('accuracy_and_profile_review', {})
        recommendations_results = result.get('improvement_recommendations_for_profile', {})

        print("\n" + "-"*60)
        print("COMPETITIVE ANALYSIS (Benchmarked against ComicShortsNarrativeProfile):")
        print("-"*60)
        comp_analysis_text = comp_analysis_results.get('competitive_analysis', 'No analysis available or error.')
        if "info" in comp_analysis_results: # Handle no data case
             comp_analysis_text = comp_analysis_results.get('info', comp_analysis_text)
        print(comp_analysis_text)

        print("\n" + "-"*60)
        print("ACCURACY & PROFILE ADHERENCE REVIEW:")
        print("-"*60)
        acc_review_text = acc_profile_review_results.get('accuracy_review', 'No review available or error.')
        print(acc_review_text)

        print("\n" + "-"*60)
        print("IMPROVEMENT RECOMMENDATIONS (for ComicShortsNarrativeProfile Alignment):")
        print("-"*60)
        improvements_text = recommendations_results.get('improvement_recommendations', 'No recommendations available or error.')
        print(improvements_text)

        with open(output_json_path_arg, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2)
        print(f"\n✅ Complete review (JSON) saved to: {output_json_path_arg}")

        # Optional: Save a Markdown summary if needed for quick human review
        output_file_basename = os.path.splitext(os.path.basename(agent_1_output_path_arg))[0]
        md_summary_path = os.path.join(os.path.dirname(output_json_path_arg), f"agent_2_summary_{output_file_basename}_{int(time.time())}.md")
        try:
            with open(md_summary_path, 'w', encoding='utf-8') as f_md:
                f_md.write(f"# Agent 2: Review Summary for {result.get('comic_filename_reviewed', 'UnknownComic')}\n\n")
                f_md.write(f"**Reviewed Agent 1 Output:** `{agent_1_output_path_arg}`\n\n")
                f_md.write("## Competitive Analysis\n\n")
                f_md.write(str(comp_analysis_text) + "\n\n")
                f_md.write("---\n\n## Accuracy & Profile Adherence Review\n\n")
                f_md.write(str(acc_review_text) + "\n\n")
                f_md.write("---\n\n## Improvement Recommendations\n\n")
                f_md.write(str(improvements_text) + "\n")
            print(f"ℹ️  Readable summary (Markdown) saved to: {md_summary_path}")
        except Exception as md_e:
            print(f"Warning: Could not save Markdown summary: {md_e}")


    except Exception as e:
        print(f"❌ Unexpected error in main execution: {e}")
        import traceback
        traceback.print_exc()
        # Try to save error to output file if possible
        error_result = {"error": f"Main execution failed: {str(e)}", "traceback": traceback.format_exc()}
        try:
            with open(output_json_path_arg, 'w', encoding='utf-8') as f:
                json.dump(error_result, f, indent=2)
            print(f"Error details saved to: {output_json_path_arg}")
        except Exception as save_err:
            print(f"Could not save error details to {output_json_path_arg}: {save_err}")
        sys.exit(1)

if __name__ == "__main__":
    main()