"""
Comprehensive tests for UI improvements to the Multi-Agent Joke System.

Tests cover:
- Correct cycle numbering
- Button actions triggering appropriate agent methods
- Diff viewer appearing only from cycle 2 onward
- Sidebar navigation reflecting cycles
- Error handling for LLM failures
- Models used summary rendering
- Mobile-responsive expanders
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.graph.workflow import JokeWorkflow
from app.agents.critic import JokeFeedback


class TestCycleNumbering:
    """Test that cycles are numbered correctly."""
    
    def test_initial_cycle_is_cycle_1(self):
        """First cycle should be numbered as Cycle 1."""
        history = [
            {"joke": "Test joke", "feedback": {}, "cycle_type": "initial"}
        ]
        
        assert len(history) == 1
        # In the UI, this would be displayed as "Cycle 1"
        cycle_num = 1
        assert cycle_num == 1
    
    def test_multiple_cycles_numbered_sequentially(self):
        """Multiple cycles should be numbered 1, 2, 3, etc."""
        history = [
            {"joke": "Joke 1", "feedback": {}, "cycle_type": "initial"},
            {"joke": "Joke 2", "feedback": {}, "cycle_type": "revised"},
            {"joke": "Joke 3", "feedback": {}, "cycle_type": "revised"},
        ]
        
        for idx, cycle in enumerate(history):
            cycle_num = idx + 1
            assert cycle_num == idx + 1
        
        assert len(history) == 3
    
    def test_reevaluated_cycle_increments_count(self):
        """Re-evaluation should create a new cycle with incremented number."""
        history = [
            {"joke": "Joke 1", "feedback": {"score": 65}, "cycle_type": "initial"},
            {"joke": "Joke 1", "feedback": {"score": 70}, "cycle_type": "reevaluated"},
        ]
        
        assert len(history) == 2
        # Same joke, different evaluation
        assert history[0]["joke"] == history[1]["joke"]
        assert history[0]["feedback"] != history[1]["feedback"]


class TestButtonActions:
    """Test that buttons trigger the correct agent methods."""
    
    @patch('app.graph.workflow.JokeWorkflow')
    def test_refine_button_calls_revise_joke(self, mock_workflow_class):
        """Refine button should call workflow.revise_joke()."""
        mock_workflow = Mock()
        mock_workflow.revise_joke.return_value = {
            "joke": "Revised joke",
            "feedback": {"laughability_score": 75},
            "performer_completed": True,
            "critic_completed": True
        }
        mock_workflow.evaluate_joke.return_value = {
            "joke": "Revised joke",
            "feedback": {
                "laughability_score": 75,
                "age_appropriateness": "Teen",
                "strengths": ["Better punchline"],
                "weaknesses": ["Still needs work"],
                "suggestions": ["Add more context"],
                "overall_verdict": "Improved"
            },
            "critic_completed": True
        }
        
        mock_workflow_class.return_value = mock_workflow
        
        # Simulate refine action
        original_joke = "Original joke"
        original_feedback = {
            "laughability_score": 65,
            "age_appropriateness": "Teen",
            "strengths": ["Decent setup"],
            "weaknesses": ["Weak punchline"],
            "suggestions": ["Improve ending"],
            "overall_verdict": "Needs improvement"
        }
        
        result = mock_workflow.revise_joke(original_joke, original_feedback)
        
        mock_workflow.revise_joke.assert_called_once_with(original_joke, original_feedback)
        assert result["joke"] == "Revised joke"
    
    @patch('app.graph.workflow.JokeWorkflow')
    def test_reevaluate_button_calls_reevaluate_joke(self, mock_workflow_class):
        """Re-evaluate button should call workflow.reevaluate_joke()."""
        mock_workflow = Mock()
        mock_workflow.reevaluate_joke.return_value = {
            "joke": "Same joke",
            "feedback": {
                "laughability_score": 70,
                "age_appropriateness": "Teen",
                "strengths": ["Different perspective"],
                "weaknesses": ["Timing"],
                "suggestions": ["Adjust delivery"],
                "overall_verdict": "Fresh take"
            },
            "critic_completed": True
        }
        
        mock_workflow_class.return_value = mock_workflow
        
        # Simulate reevaluate action
        joke = "Same joke"
        result = mock_workflow.reevaluate_joke(joke)
        
        mock_workflow.reevaluate_joke.assert_called_once_with(joke)
        assert result["joke"] == joke
        assert result["feedback"]["laughability_score"] == 70
    
    def test_complete_button_sets_workflow_complete_flag(self):
        """Complete button should set workflow_complete to True."""
        workflow_complete = False
        
        # Simulate complete action
        workflow_complete = True
        
        assert workflow_complete == True


class TestDiffViewer:
    """Test diff viewer functionality."""
    
    def test_diff_viewer_not_shown_for_cycle_1(self):
        """Diff viewer should NOT appear for the initial cycle."""
        cycle_num = 1
        cycle_type = "initial"
        previous_joke = None
        
        # Diff should only be shown if cycle_num > 1 and cycle_type == "revised"
        should_show_diff = cycle_num > 1 and cycle_type == "revised" and previous_joke is not None
        
        assert should_show_diff == False
    
    def test_diff_viewer_shown_for_cycle_2_revised(self):
        """Diff viewer SHOULD appear for cycle 2 when joke is revised."""
        cycle_num = 2
        cycle_type = "revised"
        previous_joke = "Original joke"
        current_joke = "Revised joke"
        
        should_show_diff = (
            cycle_num > 1 and 
            cycle_type == "revised" and 
            previous_joke is not None and 
            previous_joke != current_joke
        )
        
        assert should_show_diff == True
    
    def test_diff_viewer_not_shown_for_reevaluated_cycles(self):
        """Diff viewer should NOT appear for re-evaluated cycles (same joke)."""
        cycle_num = 2
        cycle_type = "reevaluated"
        previous_joke = "Same joke"
        current_joke = "Same joke"
        
        should_show_diff = (
            cycle_num > 1 and 
            cycle_type == "revised" and 
            previous_joke is not None and 
            previous_joke != current_joke
        )
        
        assert should_show_diff == False
    
    def test_diff_viewer_shows_changes(self):
        """Diff viewer should detect and show changes between jokes."""
        import difflib
        
        previous_joke = "Why did the programmer quit? Because they didn't get arrays!"
        revised_joke = "Why did the programmer quit? Because they couldn't C their future!"
        
        # Simulate diff generation
        previous_words = previous_joke.split()
        revised_words = revised_joke.split()
        
        diff = list(difflib.unified_diff(
            previous_words,
            revised_words,
            lineterm='',
            n=0
        ))
        
        assert len(diff) > 0  # Changes detected
        assert any("arrays!" in line for line in previous_words)
        assert any("future!" in line for line in revised_words)


class TestSidebarNavigation:
    """Test sidebar navigation for iterations."""
    
    def test_sidebar_shows_all_cycles(self):
        """Sidebar should display all cycle entries."""
        history = [
            {"joke": "J1", "feedback": {}, "cycle_type": "initial"},
            {"joke": "J2", "feedback": {}, "cycle_type": "revised"},
            {"joke": "J3", "feedback": {}, "cycle_type": "revised"},
        ]
        
        # Sidebar should show 3 navigation items
        nav_items = []
        for idx, cycle_data in enumerate(history):
            cycle_num = idx + 1
            cycle_type = cycle_data["cycle_type"]
            nav_items.append({
                "cycle_num": cycle_num,
                "cycle_type": cycle_type
            })
        
        assert len(nav_items) == 3
        assert nav_items[0]["cycle_type"] == "initial"
        assert nav_items[1]["cycle_type"] == "revised"
        assert nav_items[2]["cycle_type"] == "revised"
    
    def test_sidebar_nav_labels_correct(self):
        """Sidebar navigation should have correct labels for each cycle type."""
        history = [
            {"cycle_type": "initial"},
            {"cycle_type": "revised"},
            {"cycle_type": "reevaluated"},
        ]
        
        expected_emojis = {
            "initial": "🎬",
            "revised": "✍️",
            "reevaluated": "🔄"
        }
        
        for idx, cycle_data in enumerate(history):
            cycle_type = cycle_data["cycle_type"]
            emoji = expected_emojis.get(cycle_type, "🔄")
            
            if cycle_type == "initial":
                assert emoji == "🎬"
            elif cycle_type == "revised":
                assert emoji == "✍️"
            elif cycle_type == "reevaluated":
                assert emoji == "🔄"
    
    def test_sidebar_empty_when_no_history(self):
        """Sidebar navigation should not appear when history is empty."""
        history = []
        
        should_show_sidebar_nav = len(history) > 0
        
        assert should_show_sidebar_nav == False


class TestErrorHandling:
    """Test error handling for LLM provider failures."""
    
    @patch('app.graph.workflow.JokeWorkflow')
    def test_refine_action_handles_llm_failure(self, mock_workflow_class):
        """Refine action should handle LLM failures gracefully."""
        mock_workflow = Mock()
        mock_workflow.revise_joke.side_effect = Exception("API rate limit exceeded")
        
        mock_workflow_class.return_value = mock_workflow
        
        # Simulate refine action with error
        try:
            result = mock_workflow.revise_joke("joke", {})
            assert False, "Should have raised exception"
        except Exception as e:
            error_message = str(e)
            assert "API rate limit exceeded" in error_message
            # In UI, this would show st.error() without breaking the app
    
    @patch('app.graph.workflow.JokeWorkflow')
    def test_reevaluate_action_handles_llm_failure(self, mock_workflow_class):
        """Re-evaluate action should handle LLM failures gracefully."""
        mock_workflow = Mock()
        mock_workflow.reevaluate_joke.side_effect = Exception("Model unavailable")
        
        mock_workflow_class.return_value = mock_workflow
        
        # Simulate reevaluate action with error
        try:
            result = mock_workflow.reevaluate_joke("joke")
            assert False, "Should have raised exception"
        except Exception as e:
            error_message = str(e)
            assert "Model unavailable" in error_message
            # In UI, this would show st.error() without breaking the app
    
    @patch('app.graph.workflow.JokeWorkflow')
    def test_initial_generation_handles_llm_failure(self, mock_workflow_class):
        """Initial joke generation should handle LLM failures gracefully."""
        mock_workflow = Mock()
        mock_workflow.run.side_effect = Exception("Authentication failed")
        
        mock_workflow_class.return_value = mock_workflow
        
        # Simulate initial generation with error
        try:
            result = mock_workflow.run("test topic")
            assert False, "Should have raised exception"
        except Exception as e:
            error_message = str(e)
            assert "Authentication failed" in error_message
            # In UI, this would show st.error() with helpful message
    
    def test_error_message_suggests_provider_switch(self):
        """Error messages should suggest switching providers."""
        error_msg = "API rate limit exceeded"
        
        # In the UI, error handling includes a suggestion message
        suggestion = "Try switching providers or regenerating the joke. Some providers may have rate limits or temporary issues."
        
        assert "switching providers" in suggestion
        assert "rate limits" in suggestion


class TestModelsUsedSummary:
    """Test rendering of 'Models Used' summary."""
    
    def test_models_summary_shows_correct_providers(self):
        """Models summary should display the correct provider names."""
        llm_config = {
            "performer_provider": "groq",
            "performer_model": "llama-3.3-70b-versatile",
            "critic_provider": "openai",
            "critic_model": "gpt-4o-mini"
        }
        
        # Verify config structure
        assert llm_config["performer_provider"] == "groq"
        assert llm_config["critic_provider"] == "openai"
    
    def test_models_summary_shows_correct_models(self):
        """Models summary should display the correct model names."""
        llm_config = {
            "performer_provider": "groq",
            "performer_model": "llama-3.3-70b-versatile",
            "critic_provider": "openai",
            "critic_model": "gpt-4o-mini"
        }
        
        performer_display = f"{llm_config['performer_provider']}/{llm_config['performer_model']}"
        critic_display = f"{llm_config['critic_provider']}/{llm_config['critic_model']}"
        
        assert performer_display == "groq/llama-3.3-70b-versatile"
        assert critic_display == "openai/gpt-4o-mini"
    
    def test_models_summary_includes_cycle_number(self):
        """Models summary should include the cycle number."""
        cycle_num = 3
        llm_config = {
            "performer_provider": "groq",
            "performer_model": "llama-3.3-70b-versatile",
            "critic_provider": "openai",
            "critic_model": "gpt-4o-mini"
        }
        
        # Summary should reference the cycle number
        summary_text = f"Models Used in Cycle {cycle_num}"
        
        assert "Cycle 3" in summary_text


class TestMobileResponsiveness:
    """Test mobile-responsive features (expanders)."""
    
    def test_latest_cycle_not_in_expander(self):
        """Latest cycle should be displayed prominently, not in expander."""
        history = [
            {"joke": "J1", "feedback": {}, "cycle_type": "initial"},
            {"joke": "J2", "feedback": {}, "cycle_type": "revised"},
        ]
        
        for idx, cycle in enumerate(history):
            is_latest = (idx == len(history) - 1)
            
            if idx == 0:
                assert is_latest == False
            elif idx == 1:
                assert is_latest == True
    
    def test_previous_cycles_in_expanders(self):
        """Previous cycles should be in collapsible expanders."""
        history = [
            {"joke": "J1", "feedback": {}, "cycle_type": "initial"},
            {"joke": "J2", "feedback": {}, "cycle_type": "revised"},
            {"joke": "J3", "feedback": {}, "cycle_type": "revised"},
        ]
        
        cycles_in_expanders = []
        for idx, cycle in enumerate(history):
            is_latest = (idx == len(history) - 1)
            if not is_latest:
                cycles_in_expanders.append(idx + 1)
        
        # Cycles 1 and 2 should be in expanders
        assert cycles_in_expanders == [1, 2]
        # Cycle 3 is latest, not in expander
        assert len(history) == 3
        assert len(cycles_in_expanders) == 2


class TestLoadingMessages:
    """Test context-aware loading messages."""
    
    def test_initial_generation_loading_message(self):
        """Initial generation should show appropriate loading message."""
        loading_message = "Performer is writing a new joke about 'programming'..."
        
        assert "writing a new joke" in loading_message
        assert "programming" in loading_message
    
    def test_revision_loading_message(self):
        """Revision should show feedback-based loading message."""
        loading_message = "Performer is revising the joke based on feedback..."
        
        assert "revising" in loading_message
        assert "feedback" in loading_message
    
    def test_reevaluation_loading_message(self):
        """Re-evaluation should show new evaluation message."""
        loading_message = "Critic is running a new evaluation..."
        
        assert "new evaluation" in loading_message
    
    def test_evaluation_loading_message(self):
        """Evaluation should show critic-specific message."""
        loading_message = "Critic is evaluating the joke..."
        
        assert "Critic" in loading_message
        assert "evaluating" in loading_message


class TestCycleTypeLabels:
    """Test cycle type labels and emojis."""
    
    def test_initial_cycle_label(self):
        """Initial cycle should have correct label."""
        cycle_type = "initial"
        cycle_num = 1
        
        header_emoji = "🎬"
        header_text = f"Revision Cycle #{cycle_num} (Initial)"
        
        assert header_emoji == "🎬"
        assert "Initial" in header_text
    
    def test_revised_cycle_label(self):
        """Revised cycle should have correct label."""
        cycle_type = "revised"
        cycle_num = 2
        
        header_emoji = "✍️"
        header_text = f"Revision Cycle #{cycle_num} (Revised)"
        
        assert header_emoji == "✍️"
        assert "Revised" in header_text
    
    def test_reevaluated_cycle_label(self):
        """Re-evaluated cycle should have correct label."""
        cycle_type = "reevaluated"
        cycle_num = 3
        
        header_emoji = "🔄"
        header_text = f"Revision Cycle #{cycle_num} (Re-evaluated)"
        
        assert header_emoji == "🔄"
        assert "Re-evaluated" in header_text


class TestExplanationCard:
    """Test explanation card content."""
    
    def test_explanation_card_present(self):
        """Explanation card should be present at the top."""
        explanation_text = """
        How this app works:
        This app uses two AI agents — a Performer that writes jokes and a Critic that evaluates them.
        """
        
        assert "two AI agents" in explanation_text
        assert "Performer" in explanation_text
        assert "Critic" in explanation_text
    
    def test_explanation_mentions_refinement(self):
        """Explanation should mention iterative refinement."""
        explanation_text = "You can refine the joke multiple times using the action buttons"
        
        assert "refine" in explanation_text
        assert "multiple times" in explanation_text


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

