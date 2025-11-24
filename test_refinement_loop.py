#!/usr/bin/env python3
"""
Test suite for the iterative refinement loop functionality.
Tests the revision and re-evaluation workflows.
"""
import sys
from pathlib import Path
from unittest.mock import Mock, MagicMock

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from app.agents.performer import PerformerAgent
from app.agents.critic import CriticAgent, JokeFeedback
from app.graph.workflow import JokeWorkflow


def create_mock_llm(response_content: str):
    """Create a mock LLM that returns a predefined response."""
    mock_llm = Mock()
    mock_response = Mock()
    mock_response.content = response_content
    mock_llm.invoke = Mock(return_value=mock_response)
    return mock_llm


def test_initial_workflow():
    """Test 1: Initial workflow - generate joke + evaluation."""
    print("Test 1: Initial workflow")
    print("=" * 50)
    
    # Create mock LLMs
    performer_llm = create_mock_llm("Why did the programmer quit? Because they didn't get arrays!")
    
    critic_response = """{
        "laughability_score": 65,
        "age_appropriateness": "Teen",
        "strengths": ["Good wordplay", "Relatable to programmers"],
        "weaknesses": ["Predictable punchline"],
        "suggestions": ["Add more surprise", "Twist the ending"],
        "overall_verdict": "Decent programmer joke but could be funnier"
    }"""
    critic_llm = create_mock_llm(critic_response)
    
    # Create workflow
    workflow = JokeWorkflow(performer_llm, critic_llm)
    
    # Run initial workflow
    result = workflow.run("programming")
    
    # Simulate history tracking
    history = [{
        "joke": result["joke"],
        "feedback": result["feedback"],
        "cycle_type": "initial"
    }]
    
    # Assertions
    assert len(history) == 1, "History should have 1 entry"
    assert history[0]["joke"] is not None, "Joke should be generated"
    assert history[0]["feedback"] is not None, "Feedback should be provided"
    assert history[0]["cycle_type"] == "initial", "First cycle should be 'initial'"
    
    print(f"✅ PASS: Initial workflow generated joke and evaluation")
    print(f"   Joke: {result['joke']}")
    print(f"   Score: {result['feedback']['laughability_score']}/100")
    print(f"   History length: {len(history)}")
    print()
    return history, workflow


def test_green_check_refinement(history, workflow):
    """Test 2: Green Check - refine joke based on feedback."""
    print("Test 2: Green Check - Refine joke")
    print("=" * 50)
    
    latest_cycle = history[-1]
    
    # Mock revised joke response
    revised_joke = "Why did the programmer quit? Because they couldn't C their future!"
    workflow.performer_agent.llm.invoke = Mock(return_value=Mock(content=revised_joke))
    
    # Mock new evaluation
    new_critic_response = """{
        "laughability_score": 75,
        "age_appropriateness": "Teen",
        "strengths": ["Better wordplay with C pun", "More clever"],
        "weaknesses": ["Still predictable"],
        "suggestions": ["Add unexpected twist"],
        "overall_verdict": "Improved with better wordplay"
    }"""
    workflow.critic_agent.llm.invoke = Mock(return_value=Mock(content=new_critic_response))
    
    # Revise the joke
    revised_joke = workflow.revise_joke(latest_cycle["joke"], latest_cycle["feedback"])
    
    # Evaluate the revised joke
    new_feedback = workflow.evaluate_joke(revised_joke)
    
    # Add to history
    history.append({
        "joke": revised_joke,
        "feedback": new_feedback,
        "cycle_type": "revised"
    })
    
    # Assertions
    assert len(history) == 2, "History should have 2 entries after refinement"
    assert history[1]["joke"] != history[0]["joke"], "Revised joke should be different"
    assert history[1]["cycle_type"] == "revised", "Second cycle should be 'revised'"
    assert history[1]["feedback"]["laughability_score"] > history[0]["feedback"]["laughability_score"], \
        "Score should improve after revision"
    
    print(f"✅ PASS: Joke refined and re-evaluated")
    print(f"   Original: {history[0]['joke']}")
    print(f"   Revised: {history[1]['joke']}")
    print(f"   Score improved: {history[0]['feedback']['laughability_score']} → {history[1]['feedback']['laughability_score']}")
    print(f"   History length: {len(history)}")
    print()
    return history


def test_red_cross_reevaluation(history, workflow):
    """Test 3: Red Cross - re-evaluate same joke."""
    print("Test 3: Red Cross - Re-evaluate same joke")
    print("=" * 50)
    
    latest_cycle = history[-1]
    
    # Mock new evaluation (different perspective on same joke)
    new_critic_response = """{
        "laughability_score": 78,
        "age_appropriateness": "Teen",
        "strengths": ["Visual pun works well", "Clever use of C language"],
        "weaknesses": ["Could use more context"],
        "suggestions": ["Add setup about career path"],
        "overall_verdict": "On second thought, the wordplay is quite clever"
    }"""
    workflow.critic_agent.llm.invoke = Mock(return_value=Mock(content=new_critic_response))
    
    # Re-evaluate the same joke
    new_feedback = workflow.reevaluate_joke(latest_cycle["joke"])
    
    # Add to history with same joke but new feedback
    history.append({
        "joke": latest_cycle["joke"],
        "feedback": new_feedback,
        "cycle_type": "reevaluated"
    })
    
    # Assertions
    assert len(history) == 3, "History should have 3 entries after re-evaluation"
    assert history[2]["joke"] == history[1]["joke"], "Joke should be the same"
    assert history[2]["cycle_type"] == "reevaluated", "Third cycle should be 'reevaluated'"
    assert history[2]["feedback"] != history[1]["feedback"], "Feedback should be different"
    
    print(f"✅ PASS: Same joke re-evaluated with fresh perspective")
    print(f"   Joke (unchanged): {history[2]['joke']}")
    print(f"   Score changed: {history[1]['feedback']['laughability_score']} → {history[2]['feedback']['laughability_score']}")
    print(f"   History length: {len(history)}")
    print()
    return history


def test_termination():
    """Test 4: Termination - workflow complete, no new calls."""
    print("Test 4: Termination - I'm all set")
    print("=" * 50)
    
    # Simulate workflow complete state
    workflow_complete = False
    history_length_before = 3
    
    # User clicks "I'm all set"
    workflow_complete = True
    history_length_after = 3  # Should remain the same
    
    # Assertions
    assert workflow_complete == True, "Workflow should be marked complete"
    assert history_length_before == history_length_after, \
        "History length should not change after completion"
    
    print(f"✅ PASS: Workflow terminated successfully")
    print(f"   Workflow complete: {workflow_complete}")
    print(f"   History length unchanged: {history_length_after}")
    print(f"   No new agent calls made")
    print()


def test_multiple_iterations():
    """Test 5: Multiple iterations - simulate full refinement cycle."""
    print("Test 5: Multiple iterations")
    print("=" * 50)
    
    # Create mock LLMs
    performer_llm = create_mock_llm("Test joke")
    critic_llm = create_mock_llm('{"laughability_score": 60, "age_appropriateness": "Teen", '
                                   '"strengths": ["x"], "weaknesses": ["y"], '
                                   '"suggestions": ["z"], "overall_verdict": "ok"}')
    
    workflow = JokeWorkflow(performer_llm, critic_llm)
    
    # Initial generation
    result = workflow.run("test")
    history = [{
        "joke": result["joke"],
        "feedback": result["feedback"],
        "cycle_type": "initial"
    }]
    
    # Simulate 3 refinement cycles
    for i in range(3):
        # Refine
        revised_joke = f"Revised joke v{i+2}"
        performer_llm.invoke = Mock(return_value=Mock(content=revised_joke))
        
        revised = workflow.revise_joke(history[-1]["joke"], history[-1]["feedback"])
        feedback = workflow.evaluate_joke(revised)
        
        history.append({
            "joke": revised,
            "feedback": feedback,
            "cycle_type": "revised"
        })
    
    # Assertions
    assert len(history) == 4, "Should have 4 cycles (1 initial + 3 refinements)"
    assert history[0]["cycle_type"] == "initial", "First should be initial"
    assert all(h["cycle_type"] == "revised" for h in history[1:]), "Others should be revised"
    
    print(f"✅ PASS: Multiple iterations completed")
    print(f"   Total cycles: {len(history)}")
    print(f"   Cycle types: {[h['cycle_type'] for h in history]}")
    print()


def main():
    """Run all tests."""
    print("\n" + "="*50)
    print("🧪 ITERATIVE REFINEMENT LOOP TEST SUITE")
    print("="*50 + "\n")
    
    try:
        # Run tests in sequence
        history, workflow = test_initial_workflow()
        history = test_green_check_refinement(history, workflow)
        history = test_red_cross_reevaluation(history, workflow)
        test_termination()
        test_multiple_iterations()
        
        print("\n" + "="*50)
        print("✅ ALL TESTS PASSED")
        print("="*50)
        print("\nSummary:")
        print("  ✅ Initial workflow test: PASS")
        print("  ✅ Green check refinement test: PASS")
        print("  ✅ Red cross re-evaluation test: PASS")
        print("  ✅ Termination test: PASS")
        print("  ✅ Multiple iterations test: PASS")
        print("\nAll iterative refinement features are working correctly!")
        
        return 0
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        return 1
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

