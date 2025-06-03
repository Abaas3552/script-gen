#!/usr/bin/env python3
"""
Pipeline Coordinator
Orchestrates the three-agent system for comic-to-YouTube script transformation.
Handles data flow, error management, and quality assurance across the pipeline.
"""

import os
import sys
import json
import time
import subprocess
from typing import Dict, Any, Optional
from pathlib import Path

class PipelineCoordinator:
    def __init__(self, openai_api_key: str, competitor_data_path: str):
        self.openai_api_key = openai_api_key
        self.competitor_data_path = competitor_data_path
        self.pipeline_id = f"pipeline_{int(time.time())}"
        self.results_dir = f"results_{self.pipeline_id}"
        
        # Create results directory
        os.makedirs(self.results_dir, exist_ok=True)
        
    def run_agent(self, agent_script: str, args: list, stage_name: str) -> Dict[str, Any]:
        """Run an agent and handle errors."""
        print(f"\n{'='*60}")
        print(f"RUNNING {stage_name}")
        print(f"{'='*60}")
        
        try:
            # Construct command
            cmd = [sys.executable, agent_script] + args
            print(f"Command: {' '.join(cmd)}")
            
            # Run agent
            start_time = time.time()
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)  # 10 min timeout
            end_time = time.time()
            
            if result.returncode != 0:
                return {
                    "success": False,
                    "error": f"Agent failed with return code {result.returncode}",
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "duration": end_time - start_time
                }
            
            return {
                "success": True,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "duration": end_time - start_time,
                "stage": stage_name
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Agent timed out after 10 minutes",
                "stage": stage_name
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to run agent: {e}",
                "stage": stage_name
            }
    
    def find_latest_output_file(self, pattern: str) -> Optional[str]:
        """Find the most recent output file matching pattern."""
        try:
            files = [f for f in os.listdir('.') if f.startswith(pattern) and f.endswith('.json')]
            if not files:
                return None
            # Sort by modification time, return newest
            files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
            return files[0]
        except Exception as e:
            print(f"Error finding output file: {e}")
            return None
    
    def validate_inputs(self, cbr_path: str) -> Dict[str, Any]:
        """Validate all inputs before starting pipeline."""
        issues = []
        
        # Check CBR file
        if not os.path.exists(cbr_path):
            issues.append(f"CBR file not found: {cbr_path}")
        elif not cbr_path.lower().endswith(('.cbr', '.cbz', '.zip')):
            issues.append(f"Invalid file type. Expected .cbr, .cbz, or .zip: {cbr_path}")
        
        # Check competitor data
        if not os.path.exists(self.competitor_data_path):
            issues.append(f"Competitor data file not found: {self.competitor_data_path}")
        elif not self.competitor_data_path.lower().endswith('.csv'):
            issues.append(f"Invalid competitor data format. Expected .csv: {self.competitor_data_path}")
        
        # Check agent scripts
        required_agents = [
            "agent_1_comic_processor.py",
            "agent_2_script_editor.py", 
            "agent_3_final_integrator.py"
        ]
        
        for agent in required_agents:
            if not os.path.exists(agent):
                issues.append(f"Agent script not found: {agent}")
        
        # Check API key format (basic validation)
        if not self.openai_api_key.startswith('sk-'):
            issues.append("Invalid OpenAI API key format")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues
        }
    
    def run_complete_pipeline(self, cbr_path: str, target_duration: int = 75) -> Dict[str, Any]:
        """Run the complete three-agent pipeline."""
        pipeline_start = time.time()
        
        print(f"🚀 Starting Comic-to-YouTube Pipeline: {self.pipeline_id}")
        print(f"📁 Results will be saved to: {self.results_dir}")
        
        # Validate inputs
        validation = self.validate_inputs(cbr_path)
        if not validation["valid"]:
            return {
                "success": False,
                "error": "Input validation failed",
                "issues": validation["issues"]
            }
        
        print("✅ Input validation passed")
        
        pipeline_results = {
            "pipeline_id": self.pipeline_id,
            "start_time": pipeline_start,
            "cbr_file": cbr_path,
            "target_duration": target_duration,
            "stages": {}
        }
        
        # Stage 1: Comic Processor & Script Creator
        stage_1_result = self.run_agent(
            "agent_1_comic_processor.py",
            [cbr_path, self.openai_api_key, str(target_duration)],
            "AGENT 1: Comic Processor & Script Creator"
        )
        
        pipeline_results["stages"]["agent_1"] = stage_1_result
        
        if not stage_1_result["success"]:
            pipeline_results["success"] = False
            pipeline_results["failed_at"] = "Agent 1"
            return pipeline_results
        
        # Find Agent 1 output file
        agent_1_output = self.find_latest_output_file("agent_1_output_")
        if not agent_1_output:
            pipeline_results["success"] = False
            pipeline_results["error"] = "Could not find Agent 1 output file"
            return pipeline_results
        
        print(f"✅ Agent 1 completed successfully. Output: {agent_1_output}")
        
        # Stage 2: Script Editor & Competitive Analyst
        stage_2_result = self.run_agent(
            "agent_2_script_editor.py",
            [agent_1_output, self.competitor_data_path, self.openai_api_key],
            "AGENT 2: Script Editor & Competitive Analyst"
        )
        
        pipeline_results["stages"]["agent_2"] = stage_2_result
        
        if not stage_2_result["success"]:
            pipeline_results["success"] = False
            pipeline_results["failed_at"] = "Agent 2"
            return pipeline_results
        
        # Find Agent 2 output file
        agent_2_output = self.find_latest_output_file("agent_2_output_")
        if not agent_2_output:
            pipeline_results["success"] = False
            pipeline_results["error"] = "Could not find Agent 2 output file"
            return pipeline_results
        
        print(f"✅ Agent 2 completed successfully. Output: {agent_2_output}")
        
        # Stage 3: Final Integration Specialist
        stage_3_result = self.run_agent(
            "agent_3_final_integrator.py",
            [agent_2_output, self.openai_api_key, str(target_duration)],
            "AGENT 3: Final Integration Specialist"
        )
        
        pipeline_results["stages"]["agent_3"] = stage_3_result
        
        if not stage_3_result["success"]:
            pipeline_results["success"] = False
            pipeline_results["failed_at"] = "Agent 3"
            return pipeline_results
        
        # Find final output file
        final_output = self.find_latest_output_file("final_output_")
        if not final_output:
            pipeline_results["success"] = False
            pipeline_results["error"] = "Could not find final output file"
            return pipeline_results
        
        print(f"✅ Agent 3 completed successfully. Output: {final_output}")
        
        # Copy results to results directory
        try:
            import shutil
            shutil.copy(agent_1_output, os.path.join(self.results_dir, "agent_1_output.json"))
            shutil.copy(agent_2_output, os.path.join(self.results_dir, "agent_2_output.json"))
            shutil.copy(final_output, os.path.join(self.results_dir, "final_output.json"))
        except Exception as e:
            print(f"Warning: Could not copy results to results directory: {e}")
        
        # Calculate total pipeline time
        pipeline_end = time.time()
        total_duration = pipeline_end - pipeline_start
        
        pipeline_results.update({
            "success": True,
            "end_time": pipeline_end,
            "total_duration": total_duration,
            "final_output_file": final_output,
            "results_directory": self.results_dir
        })
        
        return pipeline_results
    
    def generate_pipeline_report(self, pipeline_results: Dict[str, Any]) -> str:
        """Generate a comprehensive pipeline execution report."""
        
        report = f"""
{'='*80}
COMIC-TO-YOUTUBE SCRIPT PIPELINE REPORT
{'='*80}

Pipeline ID: {pipeline_results.get('pipeline_id', 'Unknown')}
Source CBR: {pipeline_results.get('cbr_file', 'Unknown')}
Target Duration: {pipeline_results.get('target_duration', 'Unknown')} seconds

EXECUTION SUMMARY:
Status: {'SUCCESS' if pipeline_results.get('success') else 'FAILED'}
Total Duration: {pipeline_results.get('total_duration', 0):.2f} seconds
"""
        
        if not pipeline_results.get('success'):
            report += f"Failed At: {pipeline_results.get('failed_at', 'Unknown')}\n"
            if 'error' in pipeline_results:
                report += f"Error: {pipeline_results['error']}\n"
        
        report += "\nSTAGE BREAKDOWN:\n"
        
        stages = pipeline_results.get('stages', {})
        for stage_name, stage_data in stages.items():
            status = "SUCCESS" if stage_data.get('success') else "FAILED"
            duration = stage_data.get('duration', 0)
            report += f"  {stage_name}: {status} ({duration:.2f}s)\n"
            
            if not stage_data.get('success') and 'error' in stage_data:
                report += f"    Error: {stage_data['error']}\n"
        
        if pipeline_results.get('success'):
            report += f"\nFINAL OUTPUT: {pipeline_results.get('final_output_file', 'Not found')}\n"
            report += f"RESULTS SAVED TO: {pipeline_results.get('results_directory', 'Not saved')}\n"
        
        report += "\n" + "="*80
        
        return report

def main():
    if len(sys.argv) < 4:
        print("Usage: python pipeline_coordinator.py <cbr_file> <competitor_data.csv> <openai_api_key> [target_duration]")
        print("Example: python pipeline_coordinator.py comic.cbr competitor_data.csv sk-... 75")
        sys.exit(1)
    
    cbr_file = sys.argv[1]
    competitor_data = sys.argv[2]
    api_key = sys.argv[3]
    target_duration = int(sys.argv[4]) if len(sys.argv) > 4 else 75
    
    coordinator = PipelineCoordinator(api_key, competitor_data)
    
    try:
        results = coordinator.run_complete_pipeline(cbr_file, target_duration)
        
        # Generate and display report
        report = coordinator.generate_pipeline_report(results)
        print(report)
        
        # Save report
        report_file = f"pipeline_report_{coordinator.pipeline_id}.txt"
        with open(report_file, 'w') as f:
            f.write(report)
        
        print(f"\n📊 Pipeline report saved to: {report_file}")
        
        # Exit with appropriate code
        sys.exit(0 if results.get('success') else 1)
        
    except KeyboardInterrupt:
        print("\n⚠️  Pipeline interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Pipeline coordinator error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()