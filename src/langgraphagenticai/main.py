import streamlit as st
import uuid
from langgraph.checkpoint.memory import InMemorySaver
from src.langgraphagenticai.ui.streamlitui.loadui import LoadStreamlitUI
from src.langgraphagenticai.LLMS.groqllm import GroqLLM
from src.langgraphagenticai.graph.graph_builder import GraphBuilder
from src.langgraphagenticai.ui.streamlitui.display_result import DisplayResultStreamlit

def load_langgraph_agenticai_app():
    """
    Loads and runs the LangGraph AgenticAI application with Streamlit UI.
    This function initializes the UI, handles user input, configures the LLM model,
    sets up the graph based on the selected use case, and displays the output while 
    implementing exception handling for robustness.
    """

    # ── In-session memory: initialise once per browser session ──────────────
    if "thread_id" not in st.session_state:
        st.session_state.thread_id = str(uuid.uuid4())
    if "checkpointer" not in st.session_state:
        st.session_state.checkpointer = InMemorySaver()
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    # ────────────────────────────────────────────────────────────────────────

    ##Load UI
    ui = LoadStreamlitUI()
    user_input = ui.load_streamlit_ui()

    if not user_input:
        st.error("Error: Failed to load user input from the UI.")
        return

    # Text input for user message
    if st.session_state.IsFetchButtonClicked:
        user_message = st.session_state.timeframe
    else:
        user_message = st.chat_input("Enter your message:")

    if user_message:
        try:
            ## Configure The LLM's
            obj_llm_config = GroqLLM(user_contols_input=user_input)
            model = obj_llm_config.get_llm_model()

            if not model:
                st.error("Error: LLM model could not be initialized")
                return

            # Initialize and set up the graph based on use case
            usecase = user_input.get("selected_usecase")

            if not usecase:
                st.error("Error: No use case selected.")
                return

            ## Graph Builder — cache compiled graph in session_state so the
            ## InMemorySaver checkpointer is preserved across Streamlit reruns.
            ## Rebuild only when the usecase or model changes.
            graph_key = (usecase, user_input.get("selected_groq_model", ""))
            if st.session_state.get("graph_key") != graph_key:
                # New usecase/model: fresh thread so history doesn't bleed across
                st.session_state.thread_id = str(uuid.uuid4())
                st.session_state.chat_history = []
                graph_builder = GraphBuilder(model)
                checkpointer = (
                    st.session_state.checkpointer
                    if usecase in ("Basic Chatbot", "Chatbot With Web")
                    else None
                )
                try:
                    graph = graph_builder.setup_graph(usecase, checkpointer=checkpointer)
                    st.session_state.graph = graph
                    st.session_state.graph_key = graph_key
                except Exception as e:
                    st.error(f"Error: Graph set up failed- {e}")
                    return
            else:
                graph = st.session_state.graph

            print(user_message)
            DisplayResultStreamlit(
                usecase, graph, user_message, st.session_state.thread_id
            ).display_result_on_ui()

        except Exception as e:
            st.error(f"Error: Graph set up failed- {e}")
            return
