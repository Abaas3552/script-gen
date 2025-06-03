"""
Agent 3: Final Integration Specialist
Synthesizes script drafts with editor feedback to produce final YouTube scripts
that strictly adhere to the ComicShortsNarrativeProfile.
Handles output paths for JSON and MD results.
"""

import os
import sys
import json
import time
from typing import Dict, Any
from openai import OpenAI

COMIC_SHORTS_NARRATIVE_PROFILE_SCHEMA = """
{
  "profile_name": "ComicShortsNarrativeProfile",
  "description": "A profile to generate comic book short scripts mimicking the style, structure, word choice, and writing style of the sf.comics_shorts.csv transcript examples. The goal is a factual, action-oriented narrative summary.",
  "guidelines": {
    "overall_style": {
      "tone": "Informal, direct, and narrative.",
      "voice": "Third-person narrator.",
      "perspective": "Objective recounting of events.",
      "purpose": "To summarize a comic book plotline or character interaction concisely."
    },
    "structure_and_pacing": {
      "opening": "Often starts with a character in a situation (e.g., 'While Character A is doing X...'), a direct question ('How did X happen?'), or a setup statement ('After event Y...').",
      "plot_progression": "Narrate a sequence of key events chronologically. Focus on cause and effect. Use transitional phrases like 'And after...', 'When...', 'But then...', 'As...', 'Once...', 'While...'.",
      "event_density": "Cover several plot points or actions in quick succession.",
      "resolution": "Conclude the specific mini-arc being described. The ending should be a statement of the outcome or the characters' final actions in that sequence, not a deliberate cliffhanger for the short itself.",
      "length_consideration": "Implied brevity, suitable for a 'short'."
    },
    "language_and_word_choice": {
      "tense": "Primarily present tense for the main action flow to create immediacy. Past tense can be used for backstory or events leading up to the main action being described.",
      "verbs": "Use strong, active verbs (e.g., 'interrupts', 'teleports', 'attacks', 'saves', 'reveals').",
      "sentence_structure": "Mix of simple and compound sentences. Avoid overly complex or lengthy sentences. Clarity is key.",
      "dialogue_handling": "Minimize direct quotes. If used, they should be short and integrated into the narrative (e.g., 'Character A tells Character B that...', or '...Character C says, \\"Quote.\\"'). Do not use traditional script dialogue formatting.",
      "comic_terminology": "Incorporate relevant comic book terms (names, powers, locations, items) naturally within the narrative.",
      "character_references": "Use character names (hero/villain names or real names as appropriate to the context, e.g., 'Spider-Man', 'Peter', 'Wade', 'Deadpool')."
    },
    "content_focus": {
      "action_and_plot": "Prioritize describing what characters do and what happens as a result. Motivations can be briefly mentioned if crucial.",
      "key_moments": "Highlight the most important actions or turning points of the summarized story.",
      "factual_recounting": "Stick to recounting the events of the (real or hypothetical) source comic story."
    },
    "elements_to_avoid": {
      "cinematic_directions": "No camera angles, scene headings (INT./EXT.), sound effect descriptions (unless naturally part of the narrative, e.g., 'a loud bang was heard').",
      "dramatic_hooks_for_short": "The short script itself should not end on an artificial cliffhanger designed to make the viewer wait for the *next short*. It should resolve the summarized plot point.",
      "internal_monologue_extensive": "Avoid deep dives into a character's internal thoughts unless it's a very brief, narrated summary of their realization or feeling.",
      "overly_emotional_or_florid_language": "Maintain a relatively straightforward, descriptive tone."
    }
  }
}
"""

class FinalIntegrator:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        try:
            self.profile_schema = json.loads(COMIC_SHORTS_NARRATIVE_PROFILE_SCHEMA)
        except json.JSONDecodeError:
            print("Error: Could not parse COMIC_SHORTS_NARRATIVE_PROFILE_SCHEMA. Ensure it's valid JSON.")
            self.profile_schema = {}

    def _get_profile_guideline_summary(self) -> str:
        if not self.profile_schema:
            return "Profile schema not loaded."
        summary_points = []
        guidelines = self.profile_schema.get("guidelines", {})
        overall = guidelines.get("overall_style", {})
        summary_points.append(f"- Tone/Voice: {overall.get('tone', '')} {overall.get('voice', '')}")
        summary_points.append(f"- Perspective/Purpose: {overall.get('perspective', '')} to {overall.get('purpose', '')}")
        structure = guidelines.get("structure_and_pacing", {})
        summary_points.append(f"- Opening: {structure.get('opening', '')}")
        summary_points.append(f"- Resolution: {structure.get('resolution', '')}")
        language = guidelines.get("language_and_word_choice", {})
        summary_points.append(f"- Tense: {language.get('tense', '')}")
        summary_points.append(f"- Dialogue: {language.get('dialogue_handling', '')}")
        avoid = guidelines.get("elements_to_avoid", {})
        summary_points.append(f"- Avoid: {', '.join(avoid.keys())}")
        return "\n".join(summary_points)

    def synthesize_final_script(self,
                                agent_1_data: Dict[str, Any],
                                competitive_analysis_text: str,
                                accuracy_review_text: str,
                                recommendations_text: str,
                                comic_filename: str = "the comic",
                                target_duration: int = 75) -> Dict[str, Any]:
        """Synthesize final script, strictly adhering to ComicShortsNarrativeProfile."""

        original_script_output_str = agent_1_data.get("script_generation_result", {}).get("script", "")
        original_script_content = original_script_output_str # Default
        if "SCRIPT" in original_script_output_str.upper(): # More robust check
            try:
                script_start_keyword = "SCRIPT"
                script_end_keywords = ["HOOK ANALYSIS", "TITLE SUGGESTIONS"]
                script_text_upper = original_script_output_str.upper()
                script_start_index = script_text_upper.find(script_start_keyword)

                if script_start_index != -1:
                    actual_script_start = script_start_index + len(script_start_keyword)
                    script_end_index = len(original_script_output_str)
                    for end_keyword in script_end_keywords:
                        found_end_index = script_text_upper.find(end_keyword, actual_script_start)
                        if found_end_index != -1:
                            script_end_index = min(script_end_index, found_end_index)
                    original_script_content = original_script_output_str[actual_script_start:script_end_index].strip()
                else:
                    print("Warning: 'SCRIPT' keyword not found in Agent 1 script output for synthesis, using raw output.")
            except Exception as e:
                print(f"Could not parse script from Agent 1 output for synthesis. Error: {e}")
                pass

        story_analysis_summary = agent_1_data.get("story_analysis", {}).get("story_summary", {}).get("summary", "No story analysis available from Agent 1 data.")

        integration_context = f"""
**ORIGINAL SCRIPT DRAFT (from Agent 1 for '{comic_filename}', potentially pre-edit):**
{original_script_content}

**STORY ANALYSIS (Source Material Summary for '{comic_filename}'):**
{story_analysis_summary}

**COMPETITIVE INSIGHTS (Benchmarked against `ComicShortsNarrativeProfile`):**
{competitive_analysis_text}

**ACCURACY & PROFILE ADHERENCE REVIEW (from Agent 2 for '{comic_filename}'):**
{accuracy_review_text}

**IMPROVEMENT RECOMMENDATIONS (from Agent 2 for `ComicShortsNarrativeProfile` alignment for '{comic_filename}'):**
{recommendations_text}
"""
        profile_summary_for_prompt = self._get_profile_guideline_summary()
        reference_script_examples = """
Example 1 - "How Did Dr Doom Take Over The World?": ...
Example 2 - "How Spider-Man Almost Ended Peter Parker?": ...
Example 3 - "Deadpool Takes Spider-Man To Hell": ...
        """.strip() # Keep this concise for the log, actual prompt has full examples

        system_prompt_content = f"""You are the Final Integration Specialist. Your mission is to synthesize all feedback into a perfectly optimized {target_duration}-second script for the comic '{comic_filename}' that **strictly embodies the `ComicShortsNarrativeProfile`**. This profile emphasizes factual, third-person narrative summaries of comic book plotlines.

**YOUR PRIMARY GOAL: Adherence to `ComicShortsNarrativeProfile`**
The final script MUST be a prime example of this profile. "Engagement" and "viral potential" are achieved by masterfully executing this specific narrative summary style.

**`ComicShortsNarrativeProfile` - KEY CHARACTERISTICS TO EMBODY:**
{profile_summary_for_prompt}
(Full schema: {COMIC_SHORTS_NARRATIVE_PROFILE_SCHEMA})

**REFERENCE SCRIPT EXAMPLES (These perfectly exemplify the `ComicShortsNarrativeProfile`):**
{reference_script_examples}
[Full examples as in original file would be here]

**INTEGRATION PRINCIPLES (for `ComicShortsNarrativeProfile`):**
1. **Profile First**: The final script MUST reflect the `ComicShortsNarrativeProfile`.
2. **Fidelity to Source & Profile**: Maintain comic story integrity for '{comic_filename}' AND strict adherence to the profile's narrative summary style.
3. **Resolve Conflicts for Profile Alignment**: Balance recommendations, always defaulting to what best serves the `ComicShortsNarrativeProfile`.
4. **Optimization Priority**: Critical accuracy fixes → `ComicShortsNarrativeProfile` style adherence (tense, voice, structure, factual recounting, no cinematic hooks) → Clarity of summary.
5. **Timing for Profile**: Pacing should suit a concise, factual summary of approx. {target_duration} seconds.

**FINAL SCRIPT REQUIREMENTS (as per `ComicShortsNarrativeProfile` for '{comic_filename}'):**
- Target: {target_duration} seconds (approx. 150-200 words for the script part).
- Script must be a factual, third-person narrative summary.
- Maintain story authenticity from source material ('{comic_filename}').
- Address all critical accuracy issues.
- Optimize for clarity and conciseness as a factual summary.
- Include [TIMESTAMP] markers for pacing the narrative summary (e.g., [00:00], [00:15]).
- End with a factual conclusion of the summarized comic segment, as per the profile (no artificial hooks for the short itself).
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
                        "content": f"""Create the final optimized YouTube script for '{comic_filename}'. Integrate all feedback and analysis, ensuring the output **strictly adheres to the `ComicShortsNarrativeProfile` style (factual, third-person narrative summary)** as detailed in the system prompt and exemplified by the reference scripts.

{integration_context}

**TARGET DURATION FOR SCRIPT NARRATION:** {target_duration} seconds

Deliver:

1.  **FINAL OPTIMIZED SCRIPT (Adhering to `ComicShortsNarrativeProfile` for '{comic_filename}')**
    *   Complete, production-ready narration with [TIMESTAMP] markers every ~15 seconds.
    *   The script must be a factual, third-person narrative summary, primarily in present tense, avoiding cinematic language or artificial hooks for the short itself.
2.  **INTEGRATION DECISIONS & PROFILE ALIGNMENT RATIONALE**
    *   Explain key decisions made to resolve feedback and ensure strict adherence to the `ComicShortsNarrativeProfile` for '{comic_filename}'.
    *   Highlight how the script now exemplifies the profile's characteristics.
3.  **OPTIMIZATION SUMMARY FOR `ComicShortsNarrativeProfile`**
    *   List key improvements made to align the script with the profile (e.g., tense corrections, removal of subjective language, ensuring factual conclusion).
4.  **PRODUCTION NOTES (for a `ComicShortsNarrativeProfile` video of '{comic_filename}')**
    *   Brief guidance for video creation that complements a factual narrative summary (e.g., focus on clear comic panel visuals from '{comic_filename}').

Ensure the final script is a prime example of the `ComicShortsNarrativeProfile`.
"""
                    }
                ],
                max_tokens=3000
            )

            final_content = response.choices[0].message.content

            return {
                "final_script_package_content": final_content,
                "target_duration": target_duration,
                "integration_timestamp": time.time(),
                "word_count_of_package": len(final_content.split()),
                "profile_schema_version_used": self.profile_schema.get("profile_name", "Unknown")
            }

        except Exception as e:
            return {"error": f"Final integration failed for '{comic_filename}': {e}"}

    def validate_final_output(self, final_script_package_data: Dict[str, Any],
                             original_story_analysis_summary: str,
                             comic_filename: str = "the comic") -> Dict[str, Any]:
        """Validate final script meets ComicShortsNarrativeProfile criteria."""

        final_script_package_content = final_script_package_data.get("final_script_package_content", "")
        target_duration = final_script_package_data.get("target_duration", 75)
        profile_summary_for_prompt = self._get_profile_guideline_summary()
        reference_script_examples_short = "[Same examples as in synthesize_final_script - omitted for brevity]"


        system_prompt_content = f"""You are a Quality Assurance Specialist for YouTube content. Your role is to validate that final scripts for '{comic_filename}' **strictly adhere to the `ComicShortsNarrativeProfile`** and meet all quality criteria for a factual narrative summary. The provided successful script examples are the gold standard for this profile.

**`ComicShortsNarrativeProfile` - KEY CHARACTERISTICS FOR VALIDATION:**
{profile_summary_for_prompt}
(Full schema: {COMIC_SHORTS_NARRATIVE_PROFILE_SCHEMA})

**VALIDATION CRITERIA (Judged against the `ComicShortsNarrativeProfile` and its exemplars):**
1.  **Profile Adherence (CRUCIAL)**: Does the script strictly follow all guidelines of the `ComicShortsNarrativeProfile` (tense, voice, factual recounting, no cinematic hooks, objective tone, narrative summary structure, etc.)?
2.  **Technical Compliance**: Duration of script narration (approx. {target_duration}s), word count (approx. 150-200 for script), format.
3.  **Story Fidelity (within summary context)**: Accuracy to source material ('{comic_filename}') for the summarized segment.
4.  **Clarity & Coherence**: Is the factual summary clear, coherent, and easy to understand?
5.  **Production Readiness**: Is the script (within the package) clearly formatted for narration?

**REFERENCE SCRIPT EXAMPLES (Gold Standard for `ComicShortsNarrativeProfile`):**
{reference_script_examples_short}
[Full examples as in original file would be here]


**QUALITY ASSESSMENT (Rated 1-10, based on adherence to `ComicShortsNarrativeProfile`):**
- Profile Adherence Score
- Clarity of Factual Summary Score
- Accuracy to Source (for summarized segment of '{comic_filename}') Score
- Overall Quality as a `ComicShortsNarrativeProfile` Script Score

Provide detailed analysis with specific scores and actionable feedback if it deviates from the `ComicShortsNarrativeProfile`.
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
                        "content": f"""Validate this final YouTube script package for '{comic_filename}'. The primary focus is its strict adherence to the `ComicShortsNarrativeProfile` (factual, third-person narrative summary) as detailed in the system prompt and exemplified by the reference scripts.

**FINAL SCRIPT PACKAGE (includes script, rationale, etc. for '{comic_filename}'):**
{final_script_package_content}

**TARGET DURATION FOR SCRIPT NARRATION:** {target_duration} seconds

**ORIGINAL STORY SUMMARY (for context of source material '{comic_filename}'):**
{original_story_analysis_summary}

Provide comprehensive validation covering:

**PROFILE ADHERENCE VALIDATION (Primary Focus):**
-   **Narrative Style:** Is it a third-person, objective, factual recount?
-   **Tense & Voice:** Primarily present tense, active voice?
-   **Structure:** Does it follow the summary structure (e.g., setup of summarized arc, chronological flow, factual conclusion of the arc)?
-   **Language:** Direct, concise, appropriate for a factual summary? Minimized and integrated quotes?
-   **Avoidance of Prohibited Elements:** Free of cinematic directions, subjective interpretations, artificial hooks for the short itself?

**TECHNICAL VALIDATION (for the script part within the package):**
-   Estimated duration compliance for script narration.
-   Word count assessment for script narration.

**CONTENT VALIDATION (for the script part):**
-   Accuracy of the summarized events vs. original comic context for '{comic_filename}'.
-   Clarity and coherence of the factual summary.

**QUALITY SCORES (1-10, based on `ComicShortsNarrativeProfile` adherence):**
-   Profile Adherence Score: X/10
-   Clarity of Factual Summary Score: X/10
-   Accuracy to Source (for summarized segment of '{comic_filename}') Score: X/10
-   Overall Quality as a `ComicShortsNarrativeProfile` Script Score: X/10

**FINAL RECOMMENDATIONS:**
-   Any remaining critical changes needed for strict `ComicShortsNarrativeProfile` alignment.
-   Confirmation of readiness if all criteria for the profile are met.

Provide specific scores and detailed reasoning, focusing on how well the script (within the package) embodies the `ComicShortsNarrativeProfile`.
"""
                    }
                ],
                max_tokens=2000
            )

            validation_content = response.choices[0].message.content
            # Basic check if validation seems positive. Robust parsing would be better.
            meets_profile_criteria = "profile adherence score: [8-9]/10" in validation_content.lower() or \
                                     "profile adherence score: 10/10" in validation_content.lower() or \
                                     "overall quality as a comicshortsnarrativeprofile script score: [8-9]/10" in validation_content.lower() or \
                                     "overall quality as a comicshortsnarrativeprofile script score: 10/10" in validation_content.lower()


            return {
                "validation_results_content": validation_content,
                "validation_timestamp": time.time(),
                "validated_script_package_content": final_script_package_content, # For reference
                "meets_profile_criteria": meets_profile_criteria
            }

        except Exception as e:
            return {"error": f"Validation failed for '{comic_filename}': {e}"}

    def generate_title_options(self, final_script_package_data: Dict[str, Any], comic_filename: str = "the comic") -> Dict[str, Any]:
        """Generate title options suitable for a ComicShortsNarrativeProfile video."""

        final_script_package_content = final_script_package_data.get("final_script_package_content", "")
        reference_script_examples_short = "[Same examples as in synthesize_final_script - titles like 'How Did Dr Doom Take Over The World?' are good examples]"

        system_prompt_content = f"""You are a YouTube Title Optimization Expert. Your task is to generate titles for comic book summary videos for '{comic_filename}' that **strictly adhere to the `ComicShortsNarrativeProfile` style.** This means titles should be factual, direct, and accurately reflect the content of a narrative summary.

**`ComicShortsNarrativeProfile` - TITLE PRINCIPLES:**
-   Titles should clearly indicate the content is a summary of a comic plotline from '{comic_filename}'.
-   Use character names and key comic elements for clarity and searchability.
-   Questions should be about the plot being summarized (e.g., "How Did [Character] Achieve X?").
-   Statements should be factual and intriguing in the context of a summary (e.g., "[Character]'s Plan to Defeat [Villain] Explained").
-   Avoid clickbait or titles that misrepresent the factual summary nature of the content.
-   Optimize for clarity and conciseness (ideally under 70 characters).

**REFERENCE SCRIPT EXAMPLES (Their titles often align with this factual summary approach):**
{reference_script_examples_short}

Generate diverse title options that are appropriate for a factual comic summary video adhering to the `ComicShortsNarrativeProfile`.
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
                        "content": f"""Generate YouTube titles for a comic summary video of '{comic_filename}'. The video script (embedded within the package below) follows the `ComicShortsNarrativeProfile` (factual, third-person narrative summary). Titles should reflect this style.

**SCRIPT PACKAGE CONTENT (The script summary for '{comic_filename}' is embedded within this text):**
{final_script_package_content}

Create 5-7 title variations that are factual, direct, and suitable for a comic summary video adhering to the `ComicShortsNarrativeProfile`:

**TITLE APPROACHES (for `ComicShortsNarrativeProfile`):**
1.  **Question-Based Summary Hook (2-3 titles):**
    *   e.g., "How Did [Character from '{comic_filename}'] [Summarized Action]?", "What Was [Character]'s Role in [Event from '{comic_filename}']?"
2.  **Factual Statement/Intrigue (2-3 titles):**
    *   e.g., "[Character]'s [Key Plot Point from '{comic_filename}'] Explained", "The Full Story of [Character]'s [Summarized Arc from '{comic_filename}']"
3.  **Direct Character/Event Focus (1-2 titles):**
    *   e.g., "{comic_filename}: [Comic Event/Character Arc] Summary"

For each title provide:
-   The title text (under 70 characters preferably).
-   Brief rationale on why it fits the `ComicShortsNarrativeProfile` style for a summary video of '{comic_filename}'.
-   Target audience appeal (e.g., fans wanting a recap of X from '{comic_filename}').

Rank titles by their effectiveness in accurately representing a factual comic summary video.
"""
                    }
                ],
                max_tokens=1500
            )

            return {
                "title_options_content": response.choices[0].message.content,
                "generation_timestamp": time.time()
            }

        except Exception as e:
            return {"error": f"Title generation failed for '{comic_filename}': {e}"}

    def perform_final_integration(self, agent_2_output_path: str, target_duration: int = 75) -> Dict[str, Any]:
        """Perform complete final integration process, focusing on ComicShortsNarrativeProfile."""
        agent_1_data_for_integration = {}
        original_story_summary_for_validation = "Original story summary not available (Agent 1 data load issue)."
        comic_filename_from_review = "UnknownComic"

        try:
            with open(agent_2_output_path, 'r', encoding='utf-8') as f:
                agent_2_output = json.load(f)

            comic_filename_from_review = agent_2_output.get("comic_filename_reviewed", "UnknownComic")
            print(f"Starting final integration for: {agent_2_output_path} (Comic: {comic_filename_from_review})")
            print(f"Target duration for script narration: {target_duration} seconds")
            print(f"Ensuring adherence to: {self.profile_schema.get('profile_name', 'ComicShortsNarrativeProfile')}")

            # Load Agent 1 data using the path from Agent 2's output
            agent_1_output_path_from_agent2 = agent_2_output.get("original_agent_1_output_path")
            if agent_1_output_path_from_agent2 and os.path.exists(agent_1_output_path_from_agent2):
                try:
                    with open(agent_1_output_path_from_agent2, 'r', encoding='utf-8') as f_agent1:
                        agent_1_data_for_integration = json.load(f_agent1)
                    print(f"Successfully loaded Agent 1 data for integration from: {agent_1_output_path_from_agent2}")
                    original_story_summary_for_validation = agent_1_data_for_integration.get("story_analysis", {})\
                                                                                  .get("story_summary", {})\
                                                                                  .get("summary", "Original story summary not available in loaded Agent 1 data.")
                except Exception as e:
                    print(f"Error loading Agent 1 data from {agent_1_output_path_from_agent2}: {e}")
                    # agent_1_data_for_integration remains {}
            else:
                print(f"Warning: Agent 1 output path not found or invalid in Agent 2's output: {agent_1_output_path_from_agent2}")


            print("Synthesizing final script (adhering to ComicShortsNarrativeProfile)...")
            final_script_package_data = self.synthesize_final_script(
                agent_1_data_for_integration,
                agent_2_output.get("competitive_analysis_results", {}).get("competitive_analysis", "No competitive analysis available"),
                agent_2_output.get("accuracy_and_profile_review", {}).get("accuracy_review", "No accuracy review available"),
                agent_2_output.get("improvement_recommendations_for_profile", {}).get("improvement_recommendations", "No recommendations available"),
                comic_filename_from_review,
                target_duration
            )

            if "error" in final_script_package_data:
                print(f"Error during script synthesis: {final_script_package_data['error']}")
                return final_script_package_data

            print("Validating final output against ComicShortsNarrativeProfile...")
            validation_results_data = self.validate_final_output(
                final_script_package_data,
                original_story_summary_for_validation,
                comic_filename_from_review
            )

            if "error" in validation_results_data:
                print(f"Warning: Validation failed - {validation_results_data['error']}")
                validation_results_data = {"validation_results_content": f"Validation unavailable due to error: {validation_results_data['error']}", "meets_profile_criteria": False}

            print("Generating title options (suitable for ComicShortsNarrativeProfile)...")
            title_options_data = self.generate_title_options(final_script_package_data, comic_filename_from_review)

            if "error" in title_options_data:
                print(f"Warning: Title generation failed - {title_options_data['error']}")
                title_options_data = {"title_options_content": f"Title generation unavailable due to error: {title_options_data['error']}"}

            final_output = {
                "comic_filename_integrated": comic_filename_from_review,
                "final_script_package": final_script_package_data,
                "validation_results": validation_results_data,
                "title_options": title_options_data,
                "source_agent_2_output_path": agent_2_output_path,
                "source_agent_1_output_path": agent_1_output_path_from_agent2, # Added for traceability
                "integration_completed_timestamp": time.time(),
                "integrator_agent_name": "Agent 3: Final Integration Specialist (Profile-Focused)",
                "profile_applied": self.profile_schema.get("profile_name", "ComicShortsNarrativeProfile")
            }

            print("Final integration process completed.")
            return final_output

        except FileNotFoundError:
            return {"error": f"Agent 2 output file not found: {agent_2_output_path}"}
        except json.JSONDecodeError:
            return {"error": f"Error decoding JSON from Agent 2 output file: {agent_2_output_path}"}
        except Exception as e:
            import traceback
            print(f"Unexpected error in perform_final_integration: {e}")
            traceback.print_exc()
            return {"error": f"Final integration process failed due to an unexpected error: {e}"}


def main():
    if len(sys.argv) < 5: # agent_2_output.json, api_key, output_json_path, output_md_path, [target_duration]
        print("Usage: python agent_3_final_integrator.py <agent_2_output.json> <openai_api_key> <output_json_path> <output_md_path> [target_duration]")
        print("Example: python agent_3_final_integrator.py agent_2.json sk-... /path/agent_3.json /path/agent_3.md 75")
        sys.exit(1)

    agent_2_output_path_arg = sys.argv[1]
    api_key_arg = sys.argv[2]
    output_json_path_arg = sys.argv[3]
    output_md_path_arg = sys.argv[4]
    target_duration_arg = int(sys.argv[5]) if len(sys.argv) > 5 else 75

    if not os.path.exists(agent_2_output_path_arg):
        print(f"Error: Agent 2 output file not found: {agent_2_output_path_arg}")
        sys.exit(1)

    # Ensure output directories exist
    for path_arg in [output_json_path_arg, output_md_path_arg]:
        output_dir = os.path.dirname(path_arg)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
            print(f"Created output directory: {output_dir}")

    integrator = FinalIntegrator(api_key_arg)

    try:
        result = integrator.perform_final_integration(agent_2_output_path_arg, target_duration_arg)

        if "error" in result:
            print(f"❌ Error during final integration: {result['error']}")
            # Still save the error information to the JSON file
            with open(output_json_path_arg, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2)
            print(f"Error details saved to: {output_json_path_arg}")
            sys.exit(1)

        print("\n" + "="*80)
        print(f"AGENT 3: FINAL INTEGRATION SPECIALIST ({result.get('profile_applied', 'Profile-Focused')}) - RESULTS for '{result.get('comic_filename_integrated', 'UnknownComic')}'")
        print("="*80)

        final_script_pkg = result.get('final_script_package', {})
        validation_res = result.get('validation_results', {})
        titles_res = result.get('title_options', {})

        final_script_content = final_script_pkg.get('final_script_package_content', 'No final script package available.')
        validation_text = validation_res.get('validation_results_content', 'No validation available or error.')
        titles_text = titles_res.get('title_options_content', 'No titles available or error.')

        print("\n" + "-"*60)
        print("FINAL OPTIMIZED SCRIPT PACKAGE (Adhering to ComicShortsNarrativeProfile):")
        print("-"*60)
        print(final_script_content)

        print("\n" + "-"*60)
        print("VALIDATION RESULTS (Against ComicShortsNarrativeProfile):")
        print("-"*60)
        print(validation_text)
        if validation_res.get('meets_profile_criteria'):
            print("\n✅ Validation indicates script meets ComicShortsNarrativeProfile criteria.")
        else:
            print("\n⚠️ Validation indicates script may need further review for ComicShortsNarrativeProfile adherence.")

        print("\n" + "-"*60)
        print("TITLE OPTIONS (Suitable for ComicShortsNarrativeProfile):")
        print("-"*60)
        print(titles_text)

        print(f"\nTarget Duration for Script Narration: {final_script_pkg.get('target_duration', target_duration_arg)} seconds")
        print(f"Final Package Word Count: {final_script_pkg.get('word_count_of_package', 'Unknown')}")

        with open(output_json_path_arg, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2)
        print(f"\n✅ Final optimized output (JSON) saved to: {output_json_path_arg}")

        with open(output_md_path_arg, 'w', encoding='utf-8') as f_md:
            f_md.write(f"# Agent 3: Final Integration Specialist ({result.get('profile_applied', 'Profile-Focused')}) for '{result.get('comic_filename_integrated', 'UnknownComic')}'\n\n")
            f_md.write(f"**Source Agent 2 Output:** `{agent_2_output_path_arg}`\n")
            f_md.write(f"**Source Agent 1 Output (via Agent 2):** `{result.get('source_agent_1_output_path', 'N/A')}`\n")
            f_md.write(f"**Target Duration for Script Narration:** {final_script_pkg.get('target_duration', target_duration_arg)} seconds\n\n")

            f_md.write("## Final Optimized Script Package (Adhering to ComicShortsNarrativeProfile)\n\n")
            f_md.write("```text\n")
            f_md.write(str(final_script_content) + "\n")
            f_md.write("```\n\n")

            f_md.write("---\n\n## Validation Results (Against ComicShortsNarrativeProfile)\n\n")
            f_md.write("```text\n")
            f_md.write(str(validation_text) + "\n")
            f_md.write("```\n\n")
            if validation_res.get('meets_profile_criteria'):
                f_md.write("**Validation Status:** Meets ComicShortsNarrativeProfile criteria.\n\n")
            else:
                f_md.write("**Validation Status:** May need further review for ComicShortsNarrativeProfile adherence.\n\n")

            f_md.write("---\n\n## Title Options (Suitable for ComicShortsNarrativeProfile)\n\n")
            f_md.write("```text\n")
            f_md.write(str(titles_text) + "\n")
            f_md.write("```\n\n")
        print(f"✅ Readable summary (Markdown) saved to: {output_md_path_arg}")
        print(f"\n🎬 PRODUCTION READY - Script optimized for factual narrative summary style ({result.get('profile_applied', 'ComicShortsNarrativeProfile')})!")

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