import streamlit as st
from download_reports import Retriever
from loguru import logger

# Set up our front end page
st.set_page_config(page_title="Knowledgebase OpenAI Assistant", page_icon=":books:")

# the main interface ...
st.title("Knowledgebase OpenAI Assistant")
st.write("Learn fast by chatting with your documents")

st.session_state.assistant_id = "asst_ScRFYlNSuOdq25lLxgp9zyX1"
st.session_state.thread_id = None

if "thread_id" not in st.session_state:
    st.session_state.thread_id = None

if "retriever_message" not in st.session_state:
    st.session_state.retriever_message = ""

if "retriever" not in st.session_state:
    st.session_state.retriever = None

# === Sidebar - where users can upload files
file_uploaded = st.sidebar.text_input(
    "Enter filename or url"
)

# Upload file button - store the file ID
if st.sidebar.button("Retrieve Report"):

    st.session_state.retriever = Retriever(assistant_id = st.session_state.assistant_id, thread_id=st.session_state.thread_id)
            

    st.session_state.thread_id = st.session_state.retriever.thread_id

    logger.info(f"Thread_id created::{st.session_state.thread_id}")

    # Show a spinner while the assistant is thinking...
    with st.spinner("Wait... Generating response..."):

        prompt = "Generate the report from the file name user_guide"
        response = st.session_state.retriever.run_thread(prompt)

        logger.info(f"Response from tool {response}")

        prompt = f"Summarize below content. Use 2000 words or less. content: {response}"
        final_response = st.session_state.retriever.run_thread(prompt)

        logger.info(f"final Response from tool {final_response}")

        # st.write(response, unsafe_allow_html=True)

        message_content = final_response[0].content[0].text
        st.session_state.retriever_message = message_content.value

        if st.session_state.retriever_message:
            st.sidebar.subheader("Report Content:")
            st.sidebar.text_area("", value=st.session_state.retriever_message, height=300) # Display the document in sidebar
        else:
            st.sidebar.error("Failed to read document.")

        logger.info(f"Final response:: {st.session_state.retriever_message}")
    
    st.write("Downloaded report succesfully")


# # Check sessions
# if st.session_state.start_chat:
    
if "messages" not in st.session_state:
    st.session_state.messages = []

# Show existing messages if any...
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])



# retriever = Retriever(assistant_id = st.session_state.assistant_id, thread_id=st.session_state.thread_id)
# chat input for the user
if prompt := st.chat_input("What's new?"):

    logger.info(f"Thread_id ::{st.session_state.thread_id}")
    logger.info(f"Retriever :: {st.session_state.retriever}")

    logger.info(f"Retriever message :: {st.session_state.retriever_message}")
    # Add user message to the state and display on the screen
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    
    # Show a spinner while the assistant is thinking...
    with st.spinner("Wait... Generating response..."):

        final_prompt = f"""From the below content, please answer the question.
        Question: {prompt}

        Content: {st.session_state.retriever_message}
        """

        logger.info(f"Final prompt:: {final_prompt}")

        response = st.session_state.retriever.run_thread(final_prompt)

        st.session_state.messages.append(
            {"role": "assistant", "content": response}
            )
        with st.chat_message("assistant"):
            st.markdown(response, unsafe_allow_html=True)



