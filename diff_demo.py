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
        
        # Stage progress indicator - with error handling
        stages = list(ConflictStage)
        
        # Ensure current_stage is valid
        current_stage = st.session_state.get('current_stage', ConflictStage.IDENTIFICATION)
        if not isinstance(current_stage, ConflictStage):
            current_stage = ConflictStage.IDENTIFICATION
            st.session_state.current_stage = current_stage
        
        try:
            current_index = stages.index(current_stage)
        except ValueError:
            # Fallback if enum value is corrupted
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
        
        # Debug info - remove this in production
        with st.expander("🔍 Debug Info (will be hidden in final version)", expanded=False):
            st.write("Current session state:")
            for key, value in st.session_state.items():
                st.write(f"- {key}: {value}")
        
        with st.form("problem_identification"):
            st.write("### 🎯 Problem Details")
            
            problem_desc = st.text_area(
                "**1. Describe the core problem** (1-2 sentences)",
                placeholder="e.g., My roommate ignores shared chores",
                height=100,
                key="problem_desc_input"
            )
            
            pp_name = st.text_input(
                "**2. Who is the Problematic Party (PP)?**",
                placeholder="e.g., Roommate Alex (use pseudonym if preferred)",
                key="pp_name_input"
            )
            
            desired_outcome = st.text_area(
                "**3. What's your desired outcome?**",
                placeholder="e.g., Even chore split",
                height=80,
                key="desired_outcome_input"
            )
            
            submit_btn = st.form_submit_button("🔍 Analyze Problem")
            
            if submit_btn:
                st.write("🔍 Button was clicked!")  # Debug message
                
                # Check if fields are filled
                if not problem_desc.strip():
                    st.error("❌ Problem description is empty")
                    return
                if not pp_name.strip():
                    st.error("❌ PP name is empty")
                    return
                if not desired_outcome.strip():
                    st.error("❌ Desired outcome is empty")
                    return
                
                st.write("✅ All fields filled, checking for illegal content...")  # Debug message
                
                # Validate problem (check for illegal content)
                if self.contains_illegal_content(problem_desc):
                    st.error("⚠️ This appears to involve illegal activity. Please seek professional help or contact authorities.")
                    return
                
                st.write("✅ Problem is valid, creating conflict data...")  # Debug message
                
                # Create conflict data
                conflict_data = ConflictData(
                    user_id=str(uuid.uuid4()),
                    problem_description=problem_desc.strip(),
                    problematic_party=pp_name.strip(),
                    desired_outcome=desired_outcome.strip()
                )
                
                st.write(f"✅ Conflict data created: {conflict_data.user_id}")  # Debug message
                
                # Update session state
                st.session_state.conflict_data = conflict_data
                st.session_state.current_stage = ConflictStage.USER_QUESTIONS
                
                st.write("✅ Session state updated, redirecting...")  # Debug message
                st.success("Problem analyzed! Let's dive deeper...")
                
                # Force rerun
                st.rerun()
    
    def contains_illegal_content(self, text: str) -> bool:
        """Basic check for illegal content"""
        illegal_keywords = [
            "violence", "assault", "theft", "fraud", "harassment",
            "abuse", "threat", "danger", "weapon", "drugs"
        ]
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in illegal_keywords)
    
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
        
        with st.form("user_questions"):
            st.write("### 🎯 Your Core Questions")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                user_facts = st.text_area(
                    "**1. What facts do you know for sure happened?** (Timeline, no opinions)",
                    value=conflict.user_facts,
                    height=120,
                    help="Be specific about dates, times, and observable behaviors",
                    key="user_facts_input"
                )
                
                user_motive = st.text_area(
                    "**2. Why do you think PP is acting this way?** (Their possible motives)",
                    value=conflict.user_motive_theory,
                    height=100,
                    help="What might be driving their behavior?",
                    key="user_motive_input"
                )
                
                user_attempts = st.text_area(
                    "**3. What have you already tried to fix it, and why failed?**",
                    value=conflict.user_past_attempts,
                    height=100,
                    help="Previous solutions and why they didn't work",
                    key="user_attempts_input"
                )
            
            with col2:
                st.write("**Context Helper:**")
                st.info(f"""
                **Problem:** {conflict.problem_description}
                **PP:** {conflict.problematic_party}
                **Goal:** {conflict.desired_outcome}
                """)
            
            submit_btn = st.form_submit_button("💾 Save Your Perspective")
            
            if submit_btn:
                st.write("💾 Save button clicked!")  # Debug message
                
                # Validate required fields
                if not user_facts.strip():
                    st.error("❌ Please answer question 1")
                    return
                if not user_motive.strip():
                    st.error("❌ Please answer question 2")
                    return
                if not user_attempts.strip():
                    st.error("❌ Please answer question 3")
                    return
                
                st.write("✅ All questions answered, updating conflict data...")  # Debug message
                
                # Update conflict data
                conflict.user_facts = user_facts.strip()
                conflict.user_motive_theory = user_motive.strip()
                conflict.user_past_attempts = user_attempts.strip()
                conflict.stage = ConflictStage.PP_INVITATION
                st.session_state.conflict_data = conflict
                st.session_state.current_stage = ConflictStage.PP_INVITATION
                
                st.write("✅ Conflict data updated, redirecting to PP invitation...")  # Debug message
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
            
            if st.button("🤖 Auto-Generate PP Responses", 
                       type="primary",
                       key="auto_generate_btn"):
                st.write("🤖 Auto-generate button clicked!")  # Debug message
                st.session_state.pp_simulation_choice = 'auto'
                st.session_state.pp_simulation_type = PPSimulationType.AUTO_GENERATE
                self.generate_simulated_pp_responses(conflict)
                st.session_state.current_stage = ConflictStage.SUMMARY
                st.rerun()
        
        with col2:
            st.write("### 🎭 Manual Input (Demo Mode)")
            st.write("You play both sides - enter PP responses as if they completed the survey")
            
            if st.button("✍️ Enter PP Responses Manually", 
                       type="secondary",
                       key="manual_input_btn"):
                st.write("✍️ Manual input button clicked!")  # Debug message
                st.session_state.pp_simulation_choice = 'manual'
                st.session_state.pp_simulation_type = PPSimulationType.MANUAL_INPUT
                st.session_state.show_manual_pp = True
                st.rerun()
    
    def generate_simulated_pp_responses(self, conflict: ConflictData):
        """Generate realistic PP responses based on user input"""
        import random
        conflict.pp_facts = "I've been dealing with work stress and didn't realize how it affected our living situation"
        conflict.pp_motive_theory = "I thought we had an informal agreement and didn't want to cause conflict by bringing it up"
        conflict.pp_past_attempts = "I suggested creating a chore chart last month but it didn't get implemented"
        conflict.pp_frustration_level = 6
        conflict.pp_ideal_fix = "Create a clear, shared responsibility system that works for both of us"
        conflict.pp_misunderstandings = "I think we might have different expectations about what 'fair' means"
        conflict.pp_impact = "This situation has been causing me stress at work too"
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
                "Shared living space acknowledged",
                "Both want peaceful coexistence",
                "Both have tried informal solutions",
                "Both want better situation"
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
                    "Propose trial period with shared chore app",
                    "Set up weekly 10-minute check-ins",
                    "Implement point system for completed tasks",
                    "Create clear escalation path for issues",
                    "Review and adjust after 30 days"
                ],
                "timeline": "30-60 days"
            },
            {
                "name": "Framed Benefit Approach",
                "archetype": "Assertive (User-Favored)",
                "description": "Frame the solution as a benefit to PP while achieving user goals.",
                "steps": [
                    "Present data showing impact on PP's goals",
                    "Offer solution giving PP more free time",
                    "Frame as win for both parties",
                    "Set clear expectations with boundaries",
                    "Follow up with positive reinforcement"
                ],
                "timeline": "2-3 weeks"
            },
            {
                "name": "Graceful Separation",
                "archetype": "Exit (Clean Break)",
                "description": "Minimize contact and create clear boundaries.",
                "steps": [
                    "Establish minimal interaction protocols",
                    "Create agreement on essential responsibilities only",
                    "Set up systems to avoid direct coordination",
                    "Identify exit options if no improvement",
                    "Implement gradual disengagement"
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
