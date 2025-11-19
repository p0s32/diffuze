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
        .pp-choice-card {
            border: 2px solid #e1e5e9;
            border-radius: 10px;
            padding: 1.5rem;
            margin: 1rem 0;
            transition: all 0.3s ease;
            cursor: pointer;
        }
        .pp-choice-card:hover {
            border-color: #667eea;
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
        }
        .pp-choice-card.selected {
            border-color: #667eea;
            background: #f8f9ff;
            box-shadow: 0 4px 16px rgba(102, 126, 234, 0.3);
        }
        .auto-generate-section {
            background: #e8f5e8;
            border: 1px solid #c3e6cb;
            border-radius: 8px;
            padding: 1rem;
            margin: 1rem 0;
        }
        .manual-input-section {
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 8px;
            padding: 1rem;
            margin: 1rem 0;
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
        
        with st.form("problem_identification"):
            st.write("### 🎯 Problem Details")
            
            problem_desc = st.text_area(
                "**1. Describe the core problem** (1-2 sentences)",
                placeholder="e.g., My roommate ignores shared chores",
                height=100
            )
            
            pp_name = st.text_input(
                "**2. Who is the Problematic Party (PP)?**",
                placeholder="e.g., Roommate Alex (use pseudonym if preferred)"
            )
            
            desired_outcome = st.text_area(
                "**3. What's your desired outcome?**",
                placeholder="e.g., Even chore split",
                height=80
            )
            
            submit_btn = st.form_submit_button("🔍 Analyze Problem")
            
            if submit_btn:
                if not all([problem_desc.strip(), pp_name.strip(), desired_outcome.strip()]):
                    st.error("Please fill in all fields.")
                    return
                
                # Validate problem (check for illegal content)
                if self.contains_illegal_content(problem_desc):
                    st.error("⚠️ This appears to involve illegal activity. Please seek professional help or contact authorities.")
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
                
                st.success("Problem analyzed! Let's dive deeper...")
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
        
        with st.form("user_questions"):
            st.write("### 🎯 Your Core Questions")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                user_facts = st.text_area(
                    "**1. What facts do you know for sure happened?** (Timeline, no opinions)",
                    value=conflict.user_facts,
                    height=120,
                    help="Be specific about dates, times, and observable behaviors"
                )
                
                user_motive = st.text_area(
                    "**2. Why do you think PP is acting this way?** (Their possible motives)",
                    value=conflict.user_motive_theory,
                    height=100,
                    help="What might be driving their behavior?"
                )
                
                user_attempts = st.text_area(
                    "**3. What have you already tried to fix it, and why failed?**",
                    value=conflict.user_past_attempts,
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
            
            submit_btn = st.form_submit_button("💾 Save Your Perspective")
            
            if submit_btn:
                if not all([user_facts.strip(), user_motive.strip(), user_attempts.strip()]):
                    st.error("Please answer all questions.")
                    return
                
                # Update conflict data
                conflict.user_facts = user_facts.strip()
                conflict.user_motive_theory = user_motive.strip()
                conflict.user_past_attempts = user_attempts.strip()
                conflict.stage = ConflictStage.PP_INVITATION
                st.session_state.conflict_data = conflict
                
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
                       type="secondary" if st.session_state.get('pp_simulation_choice') != 'auto' else "primary",
                       key="auto_generate_btn"):
                st.session_state.pp_simulation_choice = 'auto'
                st.session_state.pp_simulation_type = PPSimulationType.AUTO_GENERATE
                self.generate_simulated_pp_responses(conflict)
                st.session_state.current_stage = ConflictStage.SUMMARY
                st.rerun()
        
        with col2:
            st.write("### 🎭 Manual Input (Demo Mode)")
            st.write("You play both sides - enter PP responses as if they completed the survey")
            
            if st.button("✍️ Enter PP Responses Manually", 
                       type="secondary" if st.session_state.get('pp_simulation_choice') != 'manual' else "primary",
                       key="manual_input_btn"):
                st.session_state.pp_simulation_choice = 'manual'
                st.session_state.pp_simulation_type = PPSimulationType.MANUAL_INPUT
                st.session_state.show_manual_pp = True
                st.rerun()
        
        # Manual PP Input Section
        if st.session_state.get('show_manual_pp', False) and st.session_state.get('pp_simulation_choice') == 'manual':
            self.render_manual_pp_input()
    
    def render_manual_pp_input(self):
        """Render the manual PP input form"""
        st.write("---")
        st.write("### 🎭 Manual PP Response Entry")
        st.write("You're now playing the role of the PP. Answer these questions from their perspective:")
        
        conflict = st.session_state.conflict_data
        
        # PP Survey Questions (9-question battery)
        with st.form("pp_manual_responses"):
            st.write("### 📋 PP Survey Questions")
            st.write("_Answer as if you are the PP, being honest about your perspective._")
            
            # Core Trio
            st.write("#### 🔍 Core Questions")
            
            pp_facts = st.text_area(
                "**1. What facts do you know about this situation?** (Your timeline)",
                value=conflict.pp_facts,
                height=100,
                help="What actually happened from your perspective?"
            )
            
            pp_motive = st.text_area(
                "**2. Why do you think this is happening?** (Your view of motives)",
                value=conflict.pp_motive_theory,
                height=100,
                help="What do you think is driving this conflict?"
            )
            
            pp_attempts = st.text_area(
                "**3. What have you tried to address it?**",
                value=conflict.pp_past_attempts,
                height=100,
                help="What solutions have you attempted?"
            )
            
            st.write("---")
            st.write("#### 🎯 Deep Dive Questions")
            
            col1, col2 = st.columns(2)
            
            with col1:
                pp_frustration = st.slider(
                    "**4. What's your biggest frustration here?** (1-10 intensity)",
                    min_value=1,
                    max_value=10,
                    value=conflict.pp_frustration_level or 5,
                    help="1 = Minor annoyance, 10 = Extremely frustrated"
                )
                
                pp_ideal_fix = st.text_area(
                    "**5. What's your ideal fix?**",
                    value=conflict.pp_ideal_fix,
                    height=80
                )
            
            with col2:
                pp_misunderstandings = st.text_area(
                    "**6. Any misunderstandings you suspect?**",
                    value=conflict.pp_misunderstandings,
                    height=80
                )
                
                pp_impact = st.text_area(
                    "**7. How does this impact you emotionally/financially?**",
                    value=conflict.pp_impact,
                    height=80
                )
            
            # Final question
            pp_compromise = st.checkbox(
                "**8. Would you compromise on the user's goal (if softened appropriately)?**",
                value=conflict.pp_compromise,
                help="Are you willing to find a middle ground?"
            )
            
            st.write("**9. Additional thoughts:** (Optional)")
            pp_additional = st.text_area(
                "Any other context you'd like to share?",
                height=60
            )
            
            submit_col1, submit_col2 = st.columns([1, 6])
            
            with submit_col1:
                if st.form_submit_button("💾 Save PP Responses", type="primary"):
                    # Validate required fields
                    if not all([pp_facts.strip(), pp_motive.strip(), pp_attempts.strip(), pp_ideal_fix.strip()]):
                        st.error("Please complete all core questions (1-5).")
                        return
                    
                    # Save responses
                    conflict.pp_facts = pp_facts.strip()
                    conflict.pp_motive_theory = pp_motive.strip()
                    conflict.pp_past_attempts = pp_attempts.strip()
                    conflict.pp_frustration_level = pp_frustration
                    conflict.pp_ideal_fix = pp_ideal_fix.strip()
                    conflict.pp_misunderstandings = pp_misunderstandings.strip()
                    conflict.pp_impact = pp_impact.strip()
                    conflict.pp_compromise = pp_compromise
                    
                    st.session_state.conflict_data = conflict
                    st.session_state.current_stage = ConflictStage.SUMMARY
                    
                    st.success("PP responses saved! Generating analysis...")
                    st.balloons()
                    st.rerun()
            
            with submit_col2:
                if st.form_submit_button("🗑️ Clear All", type="secondary"):
                    # Reset all PP responses
                    conflict.pp_facts = ""
                    conflict.pp_motive_theory = ""
                    conflict.pp_past_attempts = ""
                    conflict.pp_frustration_level = 0
                    conflict.pp_ideal_fix = ""
                    conflict.pp_misunderstandings = ""
                    conflict.pp_impact = ""
                    conflict.pp_compromise = False
                    
                    st.session_state.conflict_data = conflict
                    st.rerun()
    
    def generate_simulated_pp_responses(self, conflict: ConflictData):
        """Generate realistic PP responses based on user input"""
        # Simulate PP's perspective - make it reasonable but different from user
        pp_facts_options = [
            f"I did help with chores on {conflict.user_facts.split()[0]} and {conflict.user_facts.split()[3]}",
            "I've been dealing with work stress, which affected my availability",
            "I thought we had an informal agreement about rotating responsibilities",
            "I noticed some of the tasks weren't clearly defined or assigned",
            "I was under the impression you preferred handling certain tasks yourself",
            "I've been contributing in ways that might not be immediately visible"
        ]
        
        pp_motive_options = [
            "I feel overwhelmed with my current workload",
            "I didn't realize the impact my actions had on you",
            "I thought you preferred handling certain tasks yourself",
            "I was waiting for a clear discussion about expectations",
            "I've been trying to avoid conflict by not bringing it up",
            "I assumed we were managing things informally and it was working"
        ]
        
        pp_attempts_options = [
            "I suggested creating a chore chart last month",
            "I offered to handle cooking if you'd manage cleaning",
            "I tried talking about it but didn't want to cause conflict",
            "I assumed we were managing things informally",
            "I proposed a different system but it wasn't well-received",
            "I've been doing tasks when I have time, just not on a set schedule"
        ]
        
        # Randomly select responses
        import random
        conflict.pp_facts = random.choice(pp_facts_options)
        conflict.pp_motive_theory = random.choice(pp_motive_options)
        conflict.pp_past_attempts = random.choice(pp_attempts_options)
        conflict.pp_frustration_level = random.randint(4, 8)
        conflict.pp_ideal_fix = "Create a clear, shared responsibility system that works for both of us with flexibility for busy periods"
        conflict.pp_misunderstandings = "I think we might have different expectations about what 'fair' means and when to bring up concerns"
        conflict.pp_impact = "This situation has been causing me stress at work too, affecting my focus and energy levels"
        conflict.pp_compromise = random.choice([True, True, False])  # 66% chance of compromise
        
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
                self.find_common_facts(conflict),
                self.find_common_motives(conflict),
                self.find_common_attempts(conflict),
                "Both want a better living/working situation"
            ],
            "Emotional Intensity": [
                f"User: {self.estimate_user_intensity(conflict)} / PP: {conflict.pp_frustration_level}",
                f"User: {self.estimate_user_intensity(conflict)} / PP: {conflict.pp_frustration_level}", 
                f"User: {self.estimate_user_intensity(conflict)} / PP: {conflict.pp_frustration_level}",
                "-"
            ]
        }
        
        summary_df = pd.DataFrame(summary_data)
        st.dataframe(summary_df, use_container_width=True)
        
        # Key insights
        st.write("### 🔍 Key Insights")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            agreement_rate = self.calculate_agreement_rate(conflict)
            st.metric("Agreement Rate", f"{agreement_rate}%", delta="Shared facts")
        
        with col2:
            emotional_gap = abs(self.estimate_user_intensity(conflict) - conflict.pp_frustration_level)
            st.metric("Emotional Gap", f"{emotional_gap} points", delta="Intensity difference")
        
        with col3:
            st.metric("Compromise Willingness", "PP: Yes" if conflict.pp_compromise else "PP: No", delta="Resolution potential")
        
        # Summary blurb
        st.write("### 📝 Neutral Summary")
        summary_blurb = f"""
        **Context:** {conflict.problem_description}. Both parties acknowledge the situation exists but have different perspectives on responsibility and solutions.
        
        **Key Gaps:** {self.identify_key_gaps(conflict)}
        
        **Resolution Leverage:** {self.identify_leverage_points(conflict)}
        """
        st.info(summary_blurb)
        
        if st.button("🧠 Generate Resolution Strategies", type="primary"):
            st.session_state.current_stage = ConflictStage.STRATEGIES
            st.rerun()
    
    def estimate_user_intensity(self, conflict: ConflictData) -> int:
        """Estimate user's emotional intensity based on their responses"""
        # Simple heuristic based on word choice and length
        user_text = f"{conflict.user_facts} {conflict.user_motive_theory} {conflict.user_past_attempts}"
        intensity_indicators = ["frustrated", "angry", "upset", "annoyed", "tired", "stressed", "hate", "dislike"]
        
        intensity_score = 5  # Base score
        for indicator in intensity_indicators:
            if indicator in user_text.lower():
                intensity_score += 1
        
        return min(intensity_score + len(user_text.split()) // 20, 10)
    
    def find_common_facts(self, conflict: ConflictData) -> str:
        """Find common ground in facts"""
        user_words = set(conflict.user_facts.lower().split())
        pp_words = set(conflict.pp_facts.lower().split())
        common = user_words.intersection(pp_words)
        
        if len(common) > 3:
            return f"Both mention: {', '.join(list(common)[:3])}"
        return "Shared living/working space acknowledged"
    
    def find_common_motives(self, conflict: ConflictData) -> str:
        return "Both want a peaceful, functional relationship"
    
    def find_common_attempts(self, conflict: ConflictData) -> str:
        return "Both have tried informal solutions"
    
    def calculate_agreement_rate(self, conflict: ConflictData) -> int:
        """Calculate agreement rate between user and PP"""
        user_words = set(conflict.user_facts.lower().split())
        pp_words = set(conflict.pp_facts.lower().split())
        common = user_words.intersection(pp_words)
        
        if len(user_words) == 0:
            return 0
        
        agreement = len(common) / len(user_words) * 100
        return min(int(agreement), 100)
    
    def identify_key_gaps(self, conflict: ConflictData) -> str:
        return "Different expectations about fairness, communication styles, and responsibility distribution."
    
    def identify_leverage_points(self, conflict: ConflictData) -> str:
        return "PP willing to compromise, both recognize the problem, shared desire for better situation."
    
    def stage_strategies(self):
        """Step 5: Generate Resolution Strategies"""
        st.title("🧠 Step 5: Resolution Strategies")
        st.write("Based on the analysis, here are three tailored approaches.")
        
        conflict = st.session_state.conflict_data
        
        strategies = self.generate_strategies(conflict)
        
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
        
        st.write("### 💡 Strategy Guide")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write("**🤝 Collaborative**")
            st.write("Win-win solutions, requires PP cooperation")
        
        with col2:
            st.write("**💪 Assertive**")
            st.write("User-favored, subtle pressure tactics")
        
        with col3:
            st.write("**🚪 Exit**")
            st.write("Clean separation, minimal conflict")
    
    def generate_strategies(self, conflict: ConflictData) -> List[Dict[str, str]]:
        """Generate three resolution strategies"""
        
        # Strategy 1: Collaborative
        collaborative = {
            "name": "Shared Responsibility System",
            "archetype": "Collaborative (Win-Win)",
            "description": "Create a structured system that benefits both parties through mutual accountability.",
            "steps": [
                "Propose a trial period with a shared chore/schedule app that tracks contributions transparently",
                "Set up weekly 10-minute check-ins to review progress and adjust assignments based on current workload",
                "Implement a point system where completed tasks earn flexibility credits for future use",
                "Create clear escalation path for unresolved issues with predefined resolution steps",
                "Review and adjust system after 30 days based on feedback and participation rates"
            ],
            "timeline": "30-60 days to full implementation"
        }
        
        # Strategy 2: Assertive  
        assertive = {
            "name": "Framed Benefit Approach",
            "archetype": "Assertive (User-Favored)",
            "description": "Frame the solution as a benefit to PP while achieving user goals.",
            "steps": [
                "Present data showing how current situation affects PP's goals and well-being",
                "Offer solution that gives PP more free time/energy while meeting core needs",
                "Create 'win' messaging: 'This helps you get what you want while reducing stress'",
                "Set clear expectations with gentle but firm boundaries and consequences",
                "Follow up with positive reinforcement when cooperation occurs, address slip-ups promptly"
            ],
            "timeline": "2-3 weeks for initial agreement"
        }
        
        # Strategy 3: Exit
        exit_strategy = {
            "name": "Graceful Separation",
            "archetype": "Exit (Clean Break)",
            "description": "Minimize contact and create clear boundaries for peaceful coexistence.",
            "steps": [
                "Establish minimal necessary interaction protocols with clear communication boundaries",
                "Create written agreement on essential shared responsibilities only, nothing extra",
                "Set up systems to avoid direct coordination (separate schedules, automated payments)",
                "Identify exit options if situation doesn't improve (room transfer, boundary enforcement, separation)",
                "Implement gradual disengagement while maintaining professionalism and essential cooperation"
            ],
            "timeline": "Immediate boundaries, 60-90 days for full separation"
        }
        
        return [collaborative, assertive, exit_strategy]
    
    def stage_resolution(self):
        """Step 6: Generate Resolution Messages"""
        st.title("📨 Step 6: Send Resolution Messages")
        st.write("Choose how to communicate the strategy to PP.")
        
        strategy = st.session_state.strategy_selected
        conflict = st.session_state.conflict_data
        
        st.write(f"### 🎯 Selected Strategy: {strategy['name']} ({strategy['archetype']})")
        
        # Generate message templates
        messages = self.generate_message_templates(strategy, conflict)
        
        st.write("### 💬 Message Templates")
        
        for i, message in enumerate(messages, 1):
            with st.expander(f"**Template {i}: {message['tone']} Approach**", expanded=True):
                st.write(f"*Tone: {message['tone']}*")
                st.write(f"*Best for: {message['best_for']}*")
                st.write("---")
                st.text_area("Message Content", value=message['content'], height=150, key=f"msg_{i}")
                
                col1, col2 = st.columns([1, 4])
                with col1:
                    if st.button(f"📤 Send Template {i}", key=f"send_{i}"):
                        self.send_message(i, message['content'])
        
        # Resolution tracking
        st.write("### 📊 Resolution Progress")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Messages Sent", "1-3", delta="Based on user choice")
        
        with col2:
            st.metric("Expected Response Rate", "60-80%", delta="Anonymous, low-pressure")
        
        with col3:
            st.metric("Resolution Timeline", "1-4 weeks", delta="Typical response time")
        
        st.write("### 🎉 Success Tips")
        st.info("""
        **For Best Results:**
        - Send during PP's calm time of day (evenings often work well)
        - Use anonymous delivery when possible to reduce defensiveness
        - Follow up once if no response in 3-5 days
        - Stay focused on the proposed solution, not past conflicts
        - Be prepared with all 3 message templates for different response scenarios
        """)
        
        if st.button("🔄 Start New Mediation", type="secondary"):
            self.reset_session()
            st.rerun()
    
    def generate_message_templates(self, strategy: Dict, conflict: ConflictData) -> List[Dict[str, str]]:
        """Generate message templates for the selected strategy"""
        
        base_messages = []
        
        # Template 1: Soft approach
        if strategy['archetype'] == "Collaborative (Win-Win)":
            soft_content = f"""
Hi {conflict.problematic_party},

Mediator Bot insight: I've been thinking about our situation with {self.extract_trigger(conflict.problem_description)}. 
What if we tried a {strategy['name'].lower()} for 30 days? 

The idea: {strategy['steps'][0].lower()}

This could help both of us get what we want: you more {self.extract_benefit_for_pp(conflict, strategy)}, me {conflict.desired_outcome.lower()}.

No pressure - just wanted to explore if this approach might work for you too.

Best,
[Anonymous]
            """.strip()
            
            firm_content = f"""
Hi {conflict.problematic_party},

Data shows we both agree on the core issue: {self.find_common_facts(conflict).lower()}.

Given that, I'd like to propose the {strategy['name'].lower()}: {strategy['steps'][1]}

This addresses your concern about {conflict.pp_motive_theory.split('.')[0].lower()} while moving toward my goal of {conflict.desired_outcome.lower()}.

Thoughts? Let me know by [date 3 days from now].

Thanks,
[Anonymous]
            """.strip()
            
            exit_content = f"""
Hi {conflict.problematic_party},

Since we haven't found a workable solution for {self.extract_trigger(conflict.problem_description)}, I'm proposing a clean separation approach.

Going forward: {strategy['steps'][0]}

This minimizes conflict while ensuring essential needs are met. Let me know if you agree to these minimal interaction terms.

If no response by [date 1 week from now], I'll proceed with this plan.

Regards,
[Anonymous]
            """.strip()
        
        elif strategy['archetype'] == "Assertive (User-Favored)":
            soft_content = f"Mediator Bot insight: Try {strategy['steps'][0]} Wins for both?"
            firm_content = f"Data shows {self.find_common_facts(conflict)}. Propose {strategy['name']}. Reply?"
            exit_content = f"No fix? Clean break via {strategy['steps'][0]}. Confirm?"
        
        else:  # Exit strategy
            soft_content = f"""
Hi {conflict.problematic_party},

After trying to resolve {self.extract_trigger(conflict.problem_description)}, I believe we need clearer boundaries.

Proposed: {strategy['steps'][0]}

This ensures minimal conflict while protecting both our interests. Let me know if you agree.

[Anonymous]
            """.strip()
            firm_content = f"Boundary proposal: {strategy['steps'][1]}. No response = agreement by {strategy['steps'][4].split()[-1]}."
            exit_content = f"Final proposal: {strategy['steps'][2]}. Implementing in 7 days if no objection."
        
        base_messages.extend([
            {
                "tone": "Soft",
                "best_for": "Initial approach, maintaining relationship",
                "content": soft_content
            },
            {
                "tone": "Firm", 
                "best_for": "When soft approach doesn't work",
                "content": firm_content
            },
            {
                "tone": "Direct",
                "best_for": "Clear boundaries, exit strategies",
                "content": exit_content
            }
        ])
        
        return base_messages
    
    def extract_trigger(self, problem: str) -> str:
        """Extract the core trigger from problem description"""
        # Simple keyword extraction for demo
        triggers = {
            "chore": "shared chores",
            "money": "financial arrangements", 
            "space": "personal space",
            "communication": "communication style",
            "responsibility": "shared responsibilities",
            "clean": "cleaning responsibilities",
            "noise": "noise levels",
            "guest": "guest visits"
        }
        
        problem_lower = problem.lower()
        for key, trigger in triggers.items():
            if key in problem_lower:
                return trigger
        
        return "the situation"
    
    def extract_benefit_for_pp(self, conflict: ConflictData, strategy: Dict) -> str:
        """Extract what's in it for PP"""
        if "free time" in strategy['description'].lower():
            return "more free time and less stress"
        elif "flexibility" in strategy['description'].lower():
            return "more flexibility and reduced obligations"
        else:
            return "a better living/working environment"
    
    def send_message(self, template_num: int, content: str):
        """Simulate sending message"""
        st.success(f"📤 Template {template_num} sent successfully!")
        st.balloons()
        st.session_state.messages_generated = True
    
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
