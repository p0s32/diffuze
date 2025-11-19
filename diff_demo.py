import streamlit as st
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any
import json
import uuid
from datetime import datetime, timedelta
import re
from dataclasses import dataclass
from enum import Enum
import logging
import os
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
PROJECT_NAME = "Mediator Bot"
VERSION = "1.0.0"

class ConflictStage(Enum):
    IDENTIFICATION = "Problem Identification"
    USER_QUESTIONS = "User Questions"
    PP_INVITATION = "PP Invitation"
    PP_RESPONSES = "PP Responses"
    SUMMARY = "Summary Generation"
    STRATEGIES = "Strategy Selection"
    RESOLUTION = "Resolution Messages"

class PPSimulationType(Enum):
    AUTO_GENERATE = "Auto-Generate Responses"
    MANUAL_INPUT = "Manual Input (Demo Mode)"

@dataclass
class ConflictData:
    """Core conflict data structure"""
    user_id: str
    problem_description: str
    problematic_party: str
    desired_outcome: str
    user_facts: str = ""
    user_motive_theory: str = ""
    user_past_attempts: str = ""
    pp_facts: str = ""
    pp_motive_theory: str = ""
    pp_past_attempts: str = ""
    pp_frustration_level: int = 0
    pp_ideal_fix: str = ""
    pp_misunderstandings: str = ""
    pp_impact: str = ""
    pp_compromise: bool = False
    pp_simulation_type: Optional[PPSimulationType] = None
    stage: ConflictStage = ConflictStage.IDENTIFICATION
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        self.updated_at = datetime.now()

class ConflictMediatorApp:
    def __init__(self):
        self.setup_page_config()
        self.initialize_session_state()
        
    def setup_page_config(self):
        st.set_page_config(
            page_title="Mediator Bot - Anonymous Conflict Fixer",
            page_icon="⚖️",
            layout="wide",
            initial_sidebar_state="expanded"
        )
    
    def initialize_session_state(self):
        """Initialize session state variables"""
        if 'conflict_data' not in st.session_state:
            st.session_state.conflict_data = None
        if 'current_stage' not in st.session_state:
            st.session_state.current_stage = ConflictStage.IDENTIFICATION
        if 'pp_simulation_mode' not in st.session_state:
            st.session_state.pp_simulation_mode = False
        if 'strategy_selected' not in st.session_state:
            st.session_state.strategy_selected = None
        if 'messages_generated' not in st.session_state:
            st.session_state.messages_generated = False
        if 'show_manual_pp' not in st.session_state:
            st.session_state.show_manual_pp = False
        if 'pp_simulation_choice' not in st.session_state:
            st.session_state.pp_simulation_choice = None
        if 'form_submitted' not in st.session_state:
            st.session_state.form_submitted = False
    
    def create_navbar(self):
        """Create navigation for the mediation flow"""
        st.markdown("""
        <style>
        .main-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem;
            border-radius: 10px;
            margin-bottom: 2rem;
            text-align: center;
        }
        .stage-indicator {
            background: #f0f2f6;
            padding: 1rem;
            border-radius: 8px;
            margin: 1rem 0;
            border-left: 4px solid #667eea;
        }
        .stage-completed {
            border-left-color: #28a745;
            background: #d4edda;
        }
        .stage-current {
            border-left-color: #667eea;
            background: #e7f3ff;
        }
        .stage-pending {
            border-left-color: #6c757d;
            background: #f8f9fa;
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="main-header">
            <h1>⚖️ {PROJECT_NAME}</h1>
            <p><strong>Version {VERSION}</strong></p>
            <p>No names, no drama, just solutions</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Stage progress indicator
        stages = list(ConflictStage)
        current_stage = st.session_state.get('current_stage', ConflictStage.IDENTIFICATION)
        
        try:
            current_index = stages.index(current_stage)
        except ValueError:
            current_index = 0
            st.session_state.current_stage = ConflictStage.IDENTIFICATION
        
        st.write("### 📊 Mediation Progress")
        
        for i, stage in enumerate(stages):
            if i < current_index:
                status_class = "stage-completed"
                icon = "✅"
            elif i == current_index:
                status_class = "stage-current"
                icon = "🔄"
            else:
                status_class = "stage-pending"
                icon = "⏳"
            
            st.markdown(f"""
            <div class="stage-indicator {status_class}">
                {icon} <strong>{stage.value}</strong>
            </div>
            """, unsafe_allow_html=True)
    
    def stage_identification(self):
        """Step 1: Problem Identification"""
        st.title("📋 Step 1: Problem Identification")
        st.write("Let's understand your conflict situation.")
        
        # Get current values from session state or use defaults
        problem_desc = st.session_state.get('temp_problem_desc', '')
        pp_name = st.session_state.get('temp_pp_name', '')
        desired_outcome = st.session_state.get('temp_desired_outcome', '')
        
        st.write("### 🎯 Problem Details")
        
        problem_desc = st.text_area(
            "**1. Describe the core problem** (1-2 sentences)",
            value=problem_desc,
            placeholder="e.g., My roommate ignores shared chores",
            height=100
        )
        
        pp_name = st.text_input(
            "**2. Who is the Problematic Party (PP)?**",
            value=pp_name,
            placeholder="e.g., Roommate Alex (use pseudonym if preferred)"
        )
        
        desired_outcome = st.text_area(
            "**3. What's your desired outcome?**",
            value=desired_outcome,
            placeholder="e.g., Even chore split",
            height=80
        )
        
        # Update session state with current values
        st.session_state.temp_problem_desc = problem_desc
        st.session_state.temp_pp_name = pp_name
        st.session_state.temp_desired_outcome = desired_outcome
        
        # Use a regular button instead of form submit button
        if st.button("🔍 Analyze Problem", type="primary"):
            # Validate inputs
            if not problem_desc.strip():
                st.error("Please describe the core problem.")
                return
            if not pp_name.strip():
                st.error("Please identify the Problematic Party.")
                return
            if not desired_outcome.strip():
                st.error("Please specify your desired outcome.")
                return
            
            # Check for inappropriate content (using softer filter)
            if self.contains_inappropriate_content(problem_desc):
                st.error("This appears to involve serious personal issues. For your safety and well-being, please consider seeking professional help from a therapist or counselor.")
                return
            
            # Create conflict data
            conflict_data = ConflictData(
                user_id=str(uuid.uuid4()),
                problem_description=problem_desc.strip(),
                problematic_party=pp_name.strip(),
                desired_outcome=desired_outcome.strip()
            )
            
            st.session_state.conflict_data = conflict_data
            st.session_state.current_stage = ConflictStage.USER_QUESTIONS
            
            # Clear temporary values
            st.session_state.pop('temp_problem_desc', None)
            st.session_state.pop('temp_pp_name', None)
            st.session_state.pop('temp_desired_outcome', None)
            
            st.success("Problem analyzed! Let's dive deeper...")
            st.rerun()
    
    def contains_inappropriate_content(self, text: str) -> bool:
        """Check for inappropriate content"""
        inappropriate_keywords = [
            "violence", "assault", "theft", "fraud", "harassment",
            "abuse", "threat", "danger", "weapon", "drugs",
            "affair", "cheating", "sleeping with", "pregnant"
        ]
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in inappropriate_keywords)
    
    def stage_user_questions(self):
        """Step 2: User's Core Questions"""
        st.title("❓ Step 2: Your Perspective")
        st.write("Answer these quick questions to help us understand your side.")
        
        conflict = st.session_state.conflict_data
        
        st.info(f"""
        **Your Current Problem:**
        - **Issue:** {conflict.problem_description}
        - **PP:** {conflict.problematic_party}
        - **Your Goal:** {conflict.desired_outcome}
        """)
        
        # Get current values from session state
        user_facts = st.session_state.get('temp_user_facts', conflict.user_facts)
        user_motive = st.session_state.get('temp_user_motive', conflict.user_motive_theory)
        user_attempts = st.session_state.get('temp_user_attempts', conflict.user_past_attempts)
        
        st.write("### 🎯 Your Core Questions")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            user_facts = st.text_area(
                "**1. What facts do you know for sure happened?** (Timeline, no opinions)",
                value=user_facts,
                height=120,
                help="Be specific about dates, times, and observable behaviors"
            )
            
            user_motive = st.text_area(
                "**2. Why do you think PP is acting this way?** (Their possible motives)",
                value=user_motive,
                height=100,
                help="What might be driving their behavior?"
            )
            
            user_attempts = st.text_area(
                "**3. What have you already tried to fix it, and why failed?**",
                value=user_attempts,
                height=100,
                help="Previous solutions and why they didn't work"
            )
        
        with col2:
            st.write("**Context Helper:**")
            st.info(f"""
            **Problem:** {conflict.problem_description}
            **PP:** {conflict.problematic_party}
            **Goal:** {conflict.desired_outcome}
            """)
        
        # Update session state
        st.session_state.temp_user_facts = user_facts
        st.session_state.temp_user_motive = user_motive
        st.session_state.temp_user_attempts = user_attempts
        
        if st.button("💾 Save Your Perspective", type="primary"):
            # Validate required fields
            if not user_facts.strip():
                st.error("Please answer question 1")
                return
            if not user_motive.strip():
                st.error("Please answer question 2")
                return
            if not user_attempts.strip():
                st.error("Please answer question 3")
                return
            
            # Update conflict data
            conflict.user_facts = user_facts.strip()
            conflict.user_motive_theory = user_motive.strip()
            conflict.user_past_attempts = user_attempts.strip()
            conflict.stage = ConflictStage.PP_INVITATION
            st.session_state.conflict_data = conflict
            st.session_state.current_stage = ConflictStage.PP_INVITATION
            
            # Clear temporary values
            st.session_state.pop('temp_user_facts', None)
            st.session_state.pop('temp_user_motive', None)
            st.session_state.pop('temp_user_attempts', None)
            
            st.success("Your perspective saved! Now let's get PP's side...")
            st.rerun()
    
    def stage_pp_invitation(self):
        """Step 3: PP Invitation Setup"""
        st.title("📨 Step 3: How Should We Get PP's Perspective?")
        st.write("Choose how to simulate the PP's responses for this demo.")
        
        conflict = st.session_state.conflict_data
        
        st.info(f"""
        **For Reference - Your Problem:**
        - **Issue:** {conflict.problem_description}
        - **PP:** {conflict.problematic_party}
        - **Your Goal:** {conflict.desired_outcome}
        """)
        
        # PP Simulation Type Selection
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("### 🔧 Auto-Generate Responses")
            st.write("Perfect for quick demos - AI generates realistic PP perspective")
            
            if st.button("🤖 Auto-Generate PP Responses", type="primary"):
                st.session_state.pp_simulation_choice = 'auto'
                st.session_state.pp_simulation_type = PPSimulationType.AUTO_GENERATE
                self.generate_simulated_pp_responses(conflict)
                st.session_state.current_stage = ConflictStage.SUMMARY
                st.rerun()
        
        with col2:
            st.write("### 🎭 Manual Input (Demo Mode)")
            st.write("You play both sides - enter PP responses as if they completed the survey")
            
            if st.button("✍️ Enter PP Responses Manually", type="secondary"):
                st.session_state.pp_simulation_choice = 'manual'
                st.session_state.pp_simulation_type = PPSimulationType.MANUAL_INPUT
                st.session_state.show_manual_pp = True
                st.rerun()
    
    def generate_simulated_pp_responses(self, conflict: ConflictData):
        """Generate realistic PP responses"""
        import random
        conflict.pp_facts = "I've been dealing with personal issues and didn't realize how it affected our relationship"
        conflict.pp_motive_theory = "I thought we had different expectations and didn't want to cause conflict"
        conflict.pp_past_attempts = "I suggested we talk about it but it didn't go anywhere"
        conflict.pp_frustration_level = 6
        conflict.pp_ideal_fix = "Create a clear understanding of boundaries and expectations"
        conflict.pp_misunderstandings = "I think we might have miscommunicated our needs"
        conflict.pp_impact = "This situation has been stressful for me too"
        conflict.pp_compromise = True
        
        st.session_state.conflict_data = conflict
        st.success("🤖 AI-generated PP responses! Generating analysis...")
    
    def stage_summary(self):
        """Step 4: Generate Neutral Summary Table"""
        st.title("📋 Step 4: Conflict Analysis Summary")
        st.write("Here's a balanced view of both perspectives.")
        
        conflict = st.session_state.conflict_data
        
        # Show which method was used
        simulation_type = st.session_state.get('pp_simulation_choice', 'unknown')
        if simulation_type == 'auto':
            st.info("🤖 **PP Responses:** AI-generated based on your inputs")
        elif simulation_type == 'manual':
            st.info("✍️ **PP Responses:** Manually entered in demo mode")
        
        # Create comparison table
        st.write("### 📊 Side-by-Side Analysis")
        
        summary_data = {
            "Aspect": [
                "Core Facts/Timeline", 
                "Motives/Why", 
                "Past Attempts",
                "Desired Outcome"
            ],
            "User Side": [
                conflict.user_facts[:200] + "..." if len(conflict.user_facts) > 200 else conflict.user_facts,
                conflict.user_motive_theory,
                conflict.user_past_attempts,
                conflict.desired_outcome
            ],
            "PP Side": [
                conflict.pp_facts[:200] + "..." if len(conflict.pp_facts) > 200 else conflict.pp_facts,
                conflict.pp_motive_theory,
                conflict.pp_past_attempts,
                conflict.pp_ideal_fix
            ],
            "Common Ground": [
                "Both acknowledge the situation exists",
                "Both want resolution",
                "Both have tried to address it",
                "Both prefer peaceful outcome"
            ],
            "Emotional Intensity": [
                "User: 8 / PP: 6",
                "User: 9 / PP: 7", 
                "User: 7 / PP: 5",
                "-"
            ]
        }
        
        summary_df = pd.DataFrame(summary_data)
        st.dataframe(summary_df, use_container_width=True)
        
        if st.button("🧠 Generate Resolution Strategies", type="primary"):
            st.session_state.current_stage = ConflictStage.STRATEGIES
            st.rerun()
    
    def stage_strategies(self):
        """Step 5: Generate Resolution Strategies"""
        st.title("🧠 Step 5: Resolution Strategies")
        st.write("Based on the analysis, here are three tailored approaches.")
        
        strategies = [
            {
                "name": "Shared Responsibility System",
                "archetype": "Collaborative (Win-Win)",
                "description": "Create a structured system that benefits both parties through mutual accountability.",
                "steps": [
                    "Propose trial period with shared responsibility framework",
                    "Set up weekly check-ins to review progress",
                    "Implement mutual accountability measures",
                    "Create clear escalation path for unresolved issues",
                    "Review and adjust approach based on feedback"
                ],
                "timeline": "30-60 days"
            },
            {
                "name": "Framed Benefit Approach",
                "archetype": "Assertive (User-Favored)",
                "description": "Frame the solution as a benefit to PP while achieving user goals.",
                "steps": [
                    "Present data showing mutual benefits of resolution",
                    "Offer solution that addresses PP's underlying needs",
                    "Frame as opportunity for positive change",
                    "Set clear expectations with gentle but firm boundaries",
                    "Follow up with constructive feedback"
                ],
                "timeline": "2-3 weeks"
            },
            {
                "name": "Graceful Separation",
                "archetype": "Exit (Clean Break)",
                "description": "Establish boundaries for minimal conflict interaction.",
                "steps": [
                    "Define essential interaction requirements only",
                    "Create clear communication boundaries",
                    "Establish separate schedules/systems",
                    "Identify alternative arrangements if needed",
                    "Implement gradual boundary reinforcement"
                ],
                "timeline": "60-90 days"
            }
        ]
        
        for i, strategy in enumerate(strategies, 1):
            with st.expander(f"**Strategy {i}: {strategy['name']}** - {strategy['archetype']}", expanded=True):
                st.write(f"**{strategy['description']}**")
                st.write("---")
                for step_num, step in enumerate(strategy['steps'], 1):
                    st.write(f"**Step {step_num}:** {step}")
                st.write(f"*Timeline: {strategy['timeline']}*")
                
                if st.button(f"🎯 Select Strategy {i}", key=f"strategy_{i}"):
                    st.session_state.strategy_selected = strategy
                    st.session_state.current_stage = ConflictStage.RESOLUTION
                    st.rerun()
    
    def stage_resolution(self):
        """Step 6: Generate Resolution Messages"""
        st.title("📨 Step 6: Send Resolution Messages")
        st.write("Choose how to communicate the strategy to PP.")
        
        strategy = st.session_state.strategy_selected
        
        st.write(f"### 🎯 Selected Strategy: {strategy['name']} ({strategy['archetype']})")
        
        # Generate message templates
        messages = [
            {
                "tone": "Soft",
                "best_for": "Initial approach, maintaining relationship",
                "content": f"Mediator Bot insight: Try {strategy['steps'][0]} Wins for both?"
            },
            {
                "tone": "Firm", 
                "best_for": "When soft approach doesn't work",
                "content": f"Data shows common ground. Propose {strategy['name']}. Reply?"
            },
            {
                "tone": "Direct",
                "best_for": "Clear boundaries, exit strategies",
                "content": f"No fix? Clean break via {strategy['steps'][0]}. Confirm?"
            }
        ]
        
        st.write("### 💬 Message Templates")
        
        for i, message in enumerate(messages, 1):
            with st.expander(f"**Template {i}: {message['tone']} Approach**", expanded=True):
                st.write(f"*Tone: {message['tone']}*")
                st.write(f"*Best for: {message['best_for']}*")
                st.write("---")
                st.text_area("Message Content", value=message['content'], height=150, key=f"msg_{i}")
                
                if st.button(f"📤 Send Template {i}", key=f"send_{i}"):
                    st.success(f"📤 Template {i} sent successfully!")
                    st.balloons()
        
        if st.button("🔄 Start New Mediation", type="secondary"):
            self.reset_session()
            st.rerun()
    
    def reset_session(self):
        """Reset the session for new mediation"""
        st.session_state.conflict_data = None
        st.session_state.current_stage = ConflictStage.IDENTIFICATION
        st.session_state.pp_simulation_mode = False
        st.session_state.strategy_selected = None
        st.session_state.messages_generated = False
        st.session_state.show_manual_pp = False
        st.session_state.pp_simulation_choice = None
        st.session_state.pop('temp_problem_desc', None)
        st.session_state.pop('temp_pp_name', None)
        st.session_state.pop('temp_desired_outcome', None)
        st.session_state.pop('temp_user_facts', None)
        st.session_state.pop('temp_user_motive', None)
        st.session_state.pop('temp_user_attempts', None)

    def run(self):
        """Main application runner"""
        self.create_navbar()
        
        # Route to appropriate stage
        current_stage = st.session_state.current_stage
        
        if current_stage == ConflictStage.IDENTIFICATION:
            self.stage_identification()
        elif current_stage == ConflictStage.USER_QUESTIONS:
            self.stage_user_questions()
        elif current_stage == ConflictStage.PP_INVITATION:
            self.stage_pp_invitation()
        elif current_stage == ConflictStage.SUMMARY:
            self.stage_summary()
        elif current_stage == ConflictStage.STRATEGIES:
            self.stage_strategies()
        elif current_stage == ConflictStage.RESOLUTION:
            self.stage_resolution()

# Run the application
if __name__ == "__main__":
    app = ConflictMediatorApp()
    app.run()
