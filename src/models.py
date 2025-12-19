from pydantic import BaseModel, Field
from typing import List

class IncidentReport(BaseModel):
    """Structured output for the SRE investigation."""
    
    incident_type: str = Field(description="The category of the issue (e.g., Database, Network, API)")
    root_cause: str = Field(description="A concise technical explanation of what went wrong.")
    confidence_score: int = Field(description="Confidence level between 0-100.")
    remediation_steps: List[str] = Field(description="List of actionable steps to fix the issue.")
    
    def to_markdown(self):
        """Helper to format this as a nice string for the UI."""
        # We build the string line-by-line to guarantee NO leading spaces
        lines = []
        lines.append(f"### 🚨 Incident Report: {self.incident_type}")
        lines.append(f"**Confidence:** {self.confidence_score}%")
        lines.append("") # explicit blank line
        lines.append("**🔴 Root Cause:**")
        lines.append(self.root_cause.strip()) # strip removes accidental spaces from LLM
        lines.append("") # explicit blank line
        lines.append("**🛠️ Recommended Fixes:**")
        
        for step in self.remediation_steps:
            lines.append(f"- {step.strip()}")
            
        return "\n".join(lines)