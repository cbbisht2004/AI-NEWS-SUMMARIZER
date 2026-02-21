import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
import json


class DisplayResultStreamlit:
    def __init__(self, usecase, graph, user_message, thread_id=None):
        self.usecase = usecase
        self.graph = graph
        self.user_message = user_message
        self.thread_id = thread_id

    def display_result_on_ui(self):
        usecase = self.usecase
        graph = self.graph
        user_message = self.user_message
        config = {"configurable": {"thread_id": self.thread_id}} if self.thread_id else {}
        print(user_message)

        if usecase == "Basic Chatbot":
            # Replay prior turns so they remain visible on every Streamlit rerun
            for human_msg, ai_msg in st.session_state.get("chat_history", []):
                with st.chat_message("user"):
                    st.write(human_msg)
                with st.chat_message("assistant"):
                    st.write(ai_msg)

            # Stream current turn; InMemorySaver appends to checkpoint automatically
            ai_response = ""
            for event in graph.stream({"messages": ("user", user_message)}, config=config):
                print(event.values())
                for value in event.values():
                    print(value["messages"])
                    ai_response = value["messages"].content
                    with st.chat_message("user"):
                        st.write(user_message)
                    with st.chat_message("assistant"):
                        st.write(ai_response)

            # Persist turn in display history
            if ai_response:
                st.session_state.chat_history.append((user_message, ai_response))

        elif usecase == "Chatbot With Web":
            # Replay prior turns from display history (clean user/AI pairs only)
            for human_msg, ai_msg in st.session_state.get("chat_history", []):
                with st.chat_message("user"):
                    st.write(human_msg)
                with st.chat_message("assistant"):
                    st.write(ai_msg)

            # Invoke graph — InMemorySaver passes full history to the LLM internally
            initial_state = {"messages": [user_message]}
            res = graph.invoke(initial_state, config=config)

            # Extract only the final AI response — skip ToolMessages and intermediate steps
            ai_response = ""
            for message in reversed(res["messages"]):
                if isinstance(message, AIMessage) and message.content:
                    ai_response = message.content
                    break

            with st.chat_message("user"):
                st.write(user_message)
            if ai_response:
                with st.chat_message("assistant"):
                    st.write(ai_response)
                st.session_state.chat_history.append((user_message, ai_response))

        elif usecase == "AI News":
            # Pipeline usecase — no checkpointer, no thread_id, no chat memory
            frequency = self.user_message
            with st.spinner("Fetching and summarizing news... ⏳"):
                result = graph.invoke({"messages": frequency})
                try:
                    # Read the markdown file
                    AI_NEWS_PATH = f"./AINews/{frequency.lower()}_summary.md"
                    with open(AI_NEWS_PATH, "r") as file:
                        markdown_content = file.read()

                    # Display the markdown content in Streamlit
                    st.markdown(markdown_content, unsafe_allow_html=True)
                except FileNotFoundError:
                    st.error(f"News Not Generated or File not found: {AI_NEWS_PATH}")
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")