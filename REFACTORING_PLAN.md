# Multi-Agent Joke System - Refactoring Plan

## Status: IN PROGRESS

This document tracks the ongoing refactoring to convert the monolithic `app/main.py` (1665 lines) into a modular, production-quality architecture.

## Completed Steps ✅

### 1. New Directory Structure
```
app/llm/        ✅ Created
app/tts/        ✅ Created  
app/state/      ✅ Created
app/ui/         ✅ Created
```

### 2. Utility Modules Created
- ✅ `app/utils/exceptions.py` - Custom exceptions
- ✅ `app/utils/caching.py` - Caching decorators and session state manager
- ✅ `app/utils/formatting.py` - Text formatting, diffing, HTML generation
- ✅ `app/utils/llm_config.py` - API key management

### 3. LLM Modules Started
- ✅ `app/llm/model_catalog.py` - Model lists and defaults

## Remaining Work 🚧

### Phase 1: Core Modules (Priority: HIGH)
1. ⏳ **app/llm/providers.py** - Provider classes (GroqProvider, OpenAIProvider, etc.)
2. ⏳ **app/llm/factory.py** - LLM factory: `get_llm_client(provider, model)`
3. ⏳ **app/tts/google_tts.py** - Move from app/utils/tts.py
4. ⏳ **app/tts/fallback_tts.py** - JS speech synthesis fallback
5. ⏳ **app/tts/factory.py** - TTS factory
6. ⏳ **app/state/session.py** - Session state management
7. ⏳ **app/agents/factory.py** - Agent factory

### Phase 2: Graph & Workflow
8. ⏳ **app/graph/evaluator.py** - Critic evaluation formatting

### Phase 3: UI Components (Extract from app/main.py)
9. ⏳ **app/ui/theming.py** - CSS theme (lines 76-780 from main.py)
10. ⏳ **app/ui/sidebar.py** - Sidebar UI (LLM selection, settings)
11. ⏳ **app/ui/joke_section.py** - Joke display + voice button
12. ⏳ **app/ui/critic_section.py** - Critic feedback display
13. ⏳ **app/ui/buttons.py** - Action buttons (Accept/Reject/Done)
14. ⏳ **app/ui/iteration_history.py** - Cycle history display

### Phase 4: Integration
15. ⏳ **app/app.py** - New Streamlit entrypoint (replaces main.py logic)
16. ⏳ **main.py** - Update to `from app.app import run; run()`

### Phase 5: Documentation & Testing
17. ⏳ Update README.md with new structure
18. ⏳ Update all import paths
19. ⏳ Run syntax validation
20. ⏳ Test Streamlit app locally
21. ⏳ Update deployment docs

## Key Design Decisions

### Provider Pattern
Each LLM provider will be a class implementing a common interface:
```python
class BaseLLMProvider(ABC):
    @abstractmethod
    def get_client(self, model: str, **kwargs):
        pass
```

### Factory Pattern
Factories will handle object creation:
- `LLMFactory.create(provider, model)` → Returns LangChain LLM instance
- `TTSFactory.create(engine)` → Returns TTS engine
- `AgentFactory.create(agent_type, llm)` → Returns agent instance

### Session State
Centralized session state management in `app/state/session.py`:
- `SessionState.get(key, default)`
- `SessionState.set(key, value)`
- `SessionState.history` - Iteration history
- `SessionState.workflow` - Current workflow instance

### UI Components
Each UI component is a function that renders a specific section:
- `render_sidebar()` - Returns LLM config
- `render_joke_section(joke, cycle_num)` - Displays joke + voice button
- `render_critic_section(feedback)` - Displays evaluation
- `render_action_buttons(cycle_num)` - Displays action buttons
- `render_iteration_history(history)` - Displays cycle timeline

## Migration Notes

### Preserved Functionality
ALL existing functionality MUST be preserved:
- ✅ Multi-agent workflow (Performer → Critic)
- ✅ Multi-LLM provider/model switching
- ✅ Iterative refinement loop
- ✅ Voice playback with Google Cloud TTS
- ✅ Dark Windsurf theme
- ✅ LangSmith tracing
- ✅ Session history
- ✅ Diff viewer
- ✅ Mobile responsive design

### Import Path Changes
After refactoring, imports will change:
- `from app.utils.llm import get_llm` → `from app.llm.factory import LLMFactory`
- `from app.utils.tts import generate_standup_voice` → `from app.tts.factory import TTSFactory`
- `from app.utils.settings import MODEL_CATALOG` → `from app.llm.model_catalog import MODEL_CATALOG`

## Testing Strategy
1. Syntax validation: `python3 -m py_compile app/**/*.py`
2. Import test: `python3 -c "from app.app import run"`
3. Streamlit test: `streamlit run main.py --server.headless=true`
4. Full test suite: `pytest test_*.py`

## Rollback Plan
If refactoring breaks functionality:
1. Git revert to commit before refactoring
2. Identify specific broken module
3. Fix module in isolation
4. Re-test integration

## Timeline Estimate
- Phase 1: 2-3 hours (core modules)
- Phase 2: 30 minutes (graph)
- Phase 3: 2-3 hours (UI extraction from 1665-line file)
- Phase 4: 1 hour (integration)
- Phase 5: 1 hour (testing & docs)

**Total: 6-8 hours of focused work**

## Next Steps
1. Complete `app/llm/providers.py` with provider classes
2. Create `app/llm/factory.py` with unified factory
3. Move TTS code to new structure
4. Extract UI components from app/main.py
5. Create new app.py entrypoint
6. Test and validate

---
**Last Updated**: 2025-01-XX
**Status**: Phase 1 in progress

