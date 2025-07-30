"""
gdd_generator.py
################

Content generation pipeline for converting GDD session data into structured markdown documents.
Handles template-based document generation with tech stack integration.
"""

# Imports
import re
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path

from .gdd_session import GDDState, GDDSessionManager, SectionStatus


class GDDContentGenerator:
    """
    Handles final GDD document assembly from LangGraph session state.
    Converts conversation outputs into structured markdown document.
    """
    
    def __init__(self, tech_stack: str, language: str):
        """
        Initialize the content generator.
        
        Args:
            tech_stack (str): The game development tech stack being used
            language (str): The programming language being used
        """
        self.tech_stack = tech_stack
        self.language = language
        self.base_template = self._get_base_template()
    
    def _get_base_template(self) -> str:
        """Get the base GDD markdown template."""
        return """# Game Design Document

**Project:** {project_name}  
**Tech Stack:** {tech_stack} / {language}  
**Created:** {created_date}  
**Last Updated:** {updated_date}  

---

## 1. Core Vision

{core_vision_content}

---

## 2. MDA Breakdown

{mda_breakdown_content}

---

## 3. Core Gameplay Loop

{core_gameplay_loop_content}

---

## 4. MVP Feature Set

{mvp_feature_set_content}

---

## 5. Vertical Slice Definition

{vertical_slice_definition_content}

---

## 6. Visual Style & Assets

{visual_style_assets_content}

---

## 7. Technical Overview

{technical_overview_content}

---

## 8. Development Roadmap

{development_roadmap_content}

---

*Generated with Antigine GDD Creator Agent*  
*Session ID: {session_id}*
"""
    
    def generate_gdd_document(self, state: GDDState, project_name: str = None) -> str:
        """
        Generate final markdown document from GDD session state.
        
        Args:
            state (GDDState): The completed or in-progress GDD session state
            project_name (str, optional): Override project name, otherwise inferred
            
        Returns:
            str: Complete GDD markdown document
        """
        if not project_name:
            project_name = f"{self.tech_stack} Game Project"
        
        # Extract content from each section
        section_contents = {}
        for section_num in range(1, 9):
            section_data = state["sections"][str(section_num)]
            section_key = self._get_section_key(section_num)
            section_contents[section_key] = self._format_section_content(section_data)
        
        # Format dates
        created_date = datetime.fromisoformat(state["created_at"]).strftime("%B %d, %Y")
        updated_date = datetime.fromisoformat(state["last_updated"]).strftime("%B %d, %Y at %I:%M %p")
        
        # Fill template
        return self.base_template.format(
            project_name=project_name,
            tech_stack=self.tech_stack,
            language=self.language,
            created_date=created_date,
            updated_date=updated_date,
            session_id=state["session_id"],
            **section_contents
        )
    
    def _get_section_key(self, section_num: int) -> str:
        """Map section number to template key."""
        section_keys = {
            1: "core_vision_content",
            2: "mda_breakdown_content", 
            3: "core_gameplay_loop_content",
            4: "mvp_feature_set_content",
            5: "vertical_slice_definition_content",
            6: "visual_style_assets_content",
            7: "technical_overview_content",
            8: "development_roadmap_content"
        }
        return section_keys.get(section_num, f"section_{section_num}_content")
    
    def _format_section_content(self, section_data: Dict[str, Any]) -> str:
        """
        Format individual section content based on its data and status.
        
        Args:
            section_data: The section data from GDD state
            
        Returns:
            str: Formatted markdown content for the section
        """
        if section_data["status"] == SectionStatus.COMPLETED.value:
            return self._format_completed_section(section_data)
        elif section_data["status"] == SectionStatus.IN_PROGRESS.value:
            return self._format_in_progress_section(section_data)
        else:
            return self._format_pending_section(section_data)
    
    def _format_completed_section(self, section_data: Dict[str, Any]) -> str:
        """Format content for a completed section."""
        content = section_data.get("content", {})
        
        # If structured content exists, format it nicely
        if content:
            return self._structure_section_content(section_data["number"], content)
        
        # Fallback to conversation-based content extraction
        return self._extract_content_from_conversation(section_data)
    
    def _format_in_progress_section(self, section_data: Dict[str, Any]) -> str:
        """Format content for a section in progress."""
        partial_content = self._extract_content_from_conversation(section_data)
        
        if partial_content.strip():
            return f"{partial_content}\n\n*[Section in progress...]*"
        else:
            return "*[Section in progress...]*"
    
    def _format_pending_section(self, section_data: Dict[str, Any]) -> str:
        """Format content for a pending section."""
        return "*[To be completed]*"
    
    def _structure_section_content(self, section_num: int, content: Dict[str, Any]) -> str:
        """
        Structure content based on section-specific requirements.
        
        Args:
            section_num (int): Section number (1-8)
            content (Dict[str, Any]): Structured content data
            
        Returns:
            str: Formatted markdown content
        """
        if section_num == 1:  # Core Vision
            return self._structure_core_vision(content)
        elif section_num == 2:  # MDA Breakdown
            return self._structure_mda_breakdown(content)
        elif section_num == 3:  # Core Gameplay Loop
            return self._structure_gameplay_loop(content)
        elif section_num == 4:  # MVP Feature Set
            return self._structure_mvp_features(content)
        elif section_num == 5:  # Vertical Slice
            return self._structure_vertical_slice(content)
        elif section_num == 6:  # Visual Style & Assets
            return self._structure_visual_style(content)
        elif section_num == 7:  # Technical Overview
            return self._structure_technical_overview(content)
        elif section_num == 8:  # Development Roadmap
            return self._structure_development_roadmap(content)
        else:
            return self._generic_content_structure(content)
    
    def _structure_core_vision(self, content: Dict[str, Any]) -> str:
        """Structure Core Vision section content."""
        parts = []
        
        if "game_hook" in content:
            parts.append(f"**Game Hook:** {content['game_hook']}")
        
        if "design_pillars" in content:
            parts.append("**Design Pillars:**")
            for i, pillar in enumerate(content["design_pillars"], 1):
                parts.append(f"{i}. {pillar}")
        
        if "timeline" in content:
            parts.append(f"**Development Timeline:** {content['timeline']}")
        
        if "platform" in content:
            parts.append(f"**Target Platform:** {content['platform']}")
        
        if "audience" in content:
            parts.append(f"**Target Audience:** {content['audience']}")
        
        return "\n\n".join(parts) if parts else self._generic_content_structure(content)
    
    def _structure_mda_breakdown(self, content: Dict[str, Any]) -> str:
        """Structure MDA Breakdown section content."""
        parts = []
        
        if "mechanics" in content:
            parts.append("### Mechanics")
            if isinstance(content["mechanics"], list):
                for mechanic in content["mechanics"]:
                    parts.append(f"- {mechanic}")
            else:
                parts.append(f"- {content['mechanics']}")
        
        if "dynamics" in content:
            parts.append("\n### Dynamics")
            if isinstance(content["dynamics"], list):
                for dynamic in content["dynamics"]:
                    parts.append(f"- {dynamic}")
            else:
                parts.append(f"- {content['dynamics']}")
        
        if "aesthetics" in content:
            parts.append("\n### Aesthetics")
            if isinstance(content["aesthetics"], list):
                for aesthetic in content["aesthetics"]:
                    parts.append(f"- {aesthetic}")
            else:
                parts.append(f"- {content['aesthetics']}")
        
        return "\n".join(parts) if parts else self._generic_content_structure(content)
    
    def _structure_gameplay_loop(self, content: Dict[str, Any]) -> str:
        """Structure Core Gameplay Loop section content."""
        parts = []
        
        if "loop_steps" in content:
            parts.append("### Core Loop Steps")
            if isinstance(content["loop_steps"], list):
                for i, step in enumerate(content["loop_steps"], 1):
                    parts.append(f"{i}. {step}")
            else:
                parts.append(content["loop_steps"])
        
        if "fun_moment" in content:
            parts.append(f"\n**Key Fun Moment:** {content['fun_moment']}")
        
        if "progression" in content:
            parts.append(f"\n**Progression Element:** {content['progression']}")
        
        return "\n".join(parts) if parts else self._generic_content_structure(content)
    
    def _structure_mvp_features(self, content: Dict[str, Any]) -> str:
        """Structure MVP Feature Set section content."""
        parts = []
        
        if "essential_features" in content:
            parts.append("### Essential Features (MVP)")
            if isinstance(content["essential_features"], list):
                for feature in content["essential_features"]:
                    parts.append(f"- {feature}")
            else:
                parts.append(f"- {content['essential_features']}")
        
        if "parking_lot" in content:
            parts.append("\n### Post-Release Features (Parking Lot)")
            if isinstance(content["parking_lot"], list):
                for feature in content["parking_lot"]:
                    parts.append(f"- {feature}")
            else:
                parts.append(f"- {content['parking_lot']}")
        
        if "excluded_features" in content:
            parts.append("\n### Explicitly Excluded from v1.0")
            if isinstance(content["excluded_features"], list):
                for feature in content["excluded_features"]:
                    parts.append(f"- {feature}")
            else:
                parts.append(f"- {content['excluded_features']}")
        
        return "\n".join(parts) if parts else self._generic_content_structure(content)
    
    def _structure_vertical_slice(self, content: Dict[str, Any]) -> str:
        """Structure Vertical Slice section content."""
        parts = []
        
        if "demo_content" in content:
            parts.append(f"**Demo Content:** {content['demo_content']}")
        
        if "success_criteria" in content:
            parts.append(f"\n**Success Criteria:** {content['success_criteria']}")
        
        if "duration" in content:
            parts.append(f"\n**Expected Duration:** {content['duration']}")
        
        return "\n".join(parts) if parts else self._generic_content_structure(content)
    
    def _structure_visual_style(self, content: Dict[str, Any]) -> str:
        """Structure Visual Style & Assets section content."""
        parts = []
        
        if "art_style" in content:
            parts.append(f"**Art Style:** {content['art_style']}")
        
        if "reference_images" in content:
            parts.append("\n**Reference Images:**")
            if isinstance(content["reference_images"], list):
                for ref in content["reference_images"]:
                    parts.append(f"- {ref}")
            else:
                parts.append(f"- {content['reference_images']}")
        
        if "asset_plan" in content:
            parts.append(f"\n**Asset Acquisition Plan:** {content['asset_plan']}")
        
        if "technical_constraints" in content:
            parts.append(f"\n**Technical Constraints:** {content['technical_constraints']}")
        
        return "\n".join(parts) if parts else self._generic_content_structure(content)
    
    def _structure_technical_overview(self, content: Dict[str, Any]) -> str:
        """Structure Technical Overview section content."""
        parts = []
        
        if "tech_rationale" in content:
            parts.append(f"**Technology Choice Rationale:** {content['tech_rationale']}")
        
        if "platform_targets" in content:
            parts.append(f"\n**Platform Targets:** {content['platform_targets']}")
        
        if "technical_risks" in content:
            parts.append("\n**Technical Risks & Mitigation:**")
            if isinstance(content["technical_risks"], list):
                for risk in content["technical_risks"]:
                    parts.append(f"- {risk}")
            else:
                parts.append(f"- {content['technical_risks']}")
        
        if "performance_targets" in content:
            parts.append(f"\n**Performance Targets:** {content['performance_targets']}")
        
        return "\n".join(parts) if parts else self._generic_content_structure(content)
    
    def _structure_development_roadmap(self, content: Dict[str, Any]) -> str:
        """Structure Development Roadmap section content."""
        parts = []
        
        if "hours_per_week" in content:
            parts.append(f"**Available Development Time:** {content['hours_per_week']} hours per week")
        
        if "milestones" in content:
            parts.append("\n**Development Milestones:**")
            if isinstance(content["milestones"], list):
                for milestone in content["milestones"]:
                    parts.append(f"- {milestone}")
            else:
                parts.append(f"- {content['milestones']}")
        
        if "first_milestone" in content:
            parts.append(f"\n**First Milestone Goal:** {content['first_milestone']}")
        
        return "\n".join(parts) if parts else self._generic_content_structure(content)
    
    def _generic_content_structure(self, content: Dict[str, Any]) -> str:
        """Generic content structuring for unknown formats."""
        if not content:
            return "*[No content available]*"
        
        parts = []
        for key, value in content.items():
            if isinstance(value, list):
                parts.append(f"**{key.replace('_', ' ').title()}:**")
                for item in value:
                    parts.append(f"- {item}")
            else:
                parts.append(f"**{key.replace('_', ' ').title()}:** {value}")
        
        return "\n\n".join(parts)
    
    def _extract_content_from_conversation(self, section_data: Dict[str, Any]) -> str:
        """
        Extract meaningful content from conversation history when structured content isn't available.
        
        Args:
            section_data: The section data with conversation history
            
        Returns:
            str: Extracted content as markdown
        """
        user_responses = section_data.get("user_responses", [])
        
        if not user_responses:
            return ""
        
        # Combine all user responses with some basic formatting
        content_parts = []
        for i, response in enumerate(user_responses, 1):
            # Clean up the response
            cleaned_response = self._clean_user_response(response)
            if cleaned_response:
                if len(user_responses) > 1:
                    content_parts.append(f"**Response {i}:** {cleaned_response}")
                else:
                    content_parts.append(cleaned_response)
        
        return "\n\n".join(content_parts)
    
    def _clean_user_response(self, response: str) -> str:
        """Clean and format user response for inclusion in GDD."""
        if not response or not response.strip():
            return ""
        
        # Remove excessive whitespace
        cleaned = re.sub(r'\s+', ' ', response.strip())
        
        # Ensure proper sentence ending
        if cleaned and not cleaned.endswith(('.', '!', '?', ':')):
            cleaned += "."
        
        return cleaned
    
    def validate_content_completeness(self, state: GDDState) -> List[str]:
        """
        Validate that all required content is present for GDD generation.
        
        Args:
            state (GDDState): The GDD session state to validate
            
        Returns:
            List[str]: List of missing or incomplete content issues
        """
        issues = []
        
        for section_num in range(1, 9):
            section_data = state["sections"][str(section_num)]
            section_name = section_data["name"]
            
            if section_data["status"] == SectionStatus.PENDING.value:
                issues.append(f"Section {section_num} ({section_name}) has not been started")
            elif section_data["status"] == SectionStatus.IN_PROGRESS.value:
                # Check if there's any content
                if not section_data.get("content") and not section_data.get("user_responses"):
                    issues.append(f"Section {section_num} ({section_name}) is in progress but has no content")
            elif section_data["status"] == SectionStatus.COMPLETED.value:
                # Completed sections should have some content
                if not section_data.get("content") and not section_data.get("user_responses"):
                    issues.append(f"Section {section_num} ({section_name}) is marked complete but has no content")
        
        return issues
    
    def generate_progress_summary_markdown(self, state: GDDState) -> str:
        """
        Generate a markdown summary of the current progress.
        
        Args:
            state (GDDState): The GDD session state
            
        Returns:
            str: Markdown progress summary
        """
        progress = GDDSessionManager.get_progress_summary(state)
        section_statuses = GDDSessionManager.get_section_status_list(state)
        
        summary = f"""# GDD Creation Progress Summary

**Session ID:** {progress['session_id']}  
**Tech Stack:** {progress['tech_stack']} / {progress['language']}  
**Style:** {progress['style']}  
**Progress:** {progress['completed_sections']}/{progress['total_sections']} sections complete ({progress['completion_percentage']:.1f}%)

## Section Status

"""
        
        for section in section_statuses:
            status_emoji = {
                "completed": "✅",
                "in_progress": "🔄", 
                "pending": "⏳",
                "skipped": "⏭️"
            }.get(section["status"], "❓")
            
            summary += f"{status_emoji} **Section {section['number']}: {section['name']}** - {section['status'].title()}\n"
            
            if section['interaction_count'] > 0:
                summary += f"   - {section['interaction_count']} interactions\n"
            
            if section['started']:
                started = datetime.fromisoformat(section['started']).strftime("%m/%d %I:%M %p")
                summary += f"   - Started: {started}\n"
            
            if section['completed']:
                completed = datetime.fromisoformat(section['completed']).strftime("%m/%d %I:%M %p")
                summary += f"   - Completed: {completed}\n"
            
            summary += "\n"
        
        if progress['is_completed']:
            summary += "🎉 **GDD Creation Complete!**\n"
        else:
            summary += f"🎯 **Next:** Continue with Section {progress['current_section']}: {progress['current_section_name']}\n"
        
        return summary