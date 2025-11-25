    %% ================================
    %%  USER INTERACTION LAYER
    %% ================================

    subgraph UI["💡 Streamlit UI Layer"]
        SB["Sidebar (LLM Provider/Model Select)"]
        JS["Generated Joke Section"]
        CS["Critic Feedback Section"]
        HS["Iteration History Panel"]
        VS["Voice Playback Button"]
        BTN["Action Buttons (✔ Approve / ❌ Re-eval / 🚫 Done)"]
        TM["Theming (Dark AI + CSS)"]
    end

    %% ================================
    %%  APPLICATION / APP LAYER
    %% ================================

    subgraph APP["🧩 Application Layer (app/)"]
        subgraph STATE["State Management (state/session.py)"]
            ST1["Track cycles"]
            ST2["Store jokes & feedback"]
            ST3["Session cache"]
        end

        subgraph WF["LangGraph Workflow (graph/workflow.py)"]
            W1["Performer → Critic Flow"]
            W2["Revision Loop Handler"]
        end

        subgraph AGENTS["Agents (agents/)"]
            PA["🤖 PerformerAgent"]
            CA["🧠 CriticAgent"]
            AF["AgentFactory"]
        end

        subgraph TTS["Text-to-Speech Layer (tts/)"]
            GTTS["Google TTS"]
            FTTS["Fallback Browser TTS"]
            TF["TTS Factory"]
        end
    end

    %% ================================
    %%  FOUNDATION LAYER
    %% ================================

    subgraph LLM["🔌 LLM Provider Layer (llm/)"]
        PROV["Provider Factory"]
        GROQ["Groq Provider"]
        HF["HuggingFace Provider"]
        DI["DeepInfra Provider"]
        OAI["OpenAI Provider (optional)"]
        MODELS["Model Catalog"]
    end

    subgraph UTIL["🛠 Utils / Config (utils/)"]
        CFG["Settings (env variables)"]
        CACHE["Cache Helpers"]
        FMT["Format Helpers"]
        ERR["Exception Handling"]
    end

    subgraph OBS["📊 Observability"]
        LS["LangSmith Tracing"]
    end

    %% ================================
    %%  CONNECTIONS
    %% ================================

    SB --> PROV
    SB --> MODELS

    BTN --> WF
    JS --> VS
    VS --> TF

    TF --> GTTS
    TF --> FTTS

    WF --> PA
    WF --> CA
    WF --> ST1
    WF --> ST2

    PA --> PROV
    CA --> PROV

    PROV --> GROQ
    PROV --> HF
    PROV --> DI
    PROV --> OAI

    WF --> LS