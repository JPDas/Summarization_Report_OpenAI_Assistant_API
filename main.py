import streamlit as st
from download_reports import Retriever
from loguru import logger

# Set up our front end page
st.set_page_config(page_title="Knowledgebase OpenAI Assistant", page_icon=":books:")


st.session_state.assistant_id = "asst_ScRFYlNSuOdq25lLxgp9zyX1"
st.session_state.thread_id = "thread_oqnFZOR5z5mhIxBUEytfP1jH"
st.session_state.retriever_message = """ANZ’s Dispute Resolution Principles and Model Litigant Guidelines":

---

**ANZ’s Dispute Resolution Principles and Model Litigant Guidelines**

These guidelines are intended for ANZ, its employees, and representatives to effectively manage customer complaints, disputes, and litigation in New Zealand, specifically for retail and small business customers.

### General Principles

1. **Listen Intently**: Customers should be given the opportunity to express their concerns fully.
2. **Don’t Defend the Indefensible**: Acknowledge mistakes without making excuses.
3. **Apologise**: Recognize and apologize for errors made.
4. **Follow Through**: Address underlying issues that may affect other customers.

### Managing Complaints and Disputes

5. **Work Toward a Solution**: Understand what the customer seeks and aim for a satisfactory resolution.
6. **Take Quick Action**: Resolve issues promptly and communicate necessary steps and timelines to the customer.
7. **Communicate Directly**: Use clear language and maintain a single point of contact for the customer.
8. **Be Responsive**: Provide requested documents in a timely manner.
9. **Take Extra Care**: For sensitive cases, consider personal meetings and provide support for vulnerable customers.
10. **Be Even Handed**: Treat all complaints consistently and fairly, ensuring equitable compensation.
11. **Rectify Our Errors**: Correct mistakes that lead to financial loss for customers.
12. **Cooperate with External Dispute Resolution Bodies**: Inform customers of their rights to escalate disputes and cooperate with relevant bodies.

### Managing Legal Proceedings

13. **Assess ANZ’s Position Early**: Evaluate the likelihood of success in legal proceedings and address liabilities promptly.
14. **Only Litigate Where There Is No Reasonable Alternative**: Legal action should be a last resort.
15. **Keep Costs Down**: Minimize litigation costs by clarifying disputes, avoiding unnecessary delays, and ensuring proper authority in negotiations.
16. **Act Fairly**: Treat all claimants fairly, especially those who may lack resources."""

# === Sidebar - where users can upload files
file_uploaded = st.sidebar.file_uploader(
    "Upload a pdf file along with meta to be transformed into embeddings", key="file_upload", type=["pdf"]
)

# Upload file button - store the file ID
if st.sidebar.button("Retrieve Report"):

    retriever = Retriever(assistant_id = st.session_state.assistant_id, thread_id=st.session_state.thread_id)
            

    st.session_state.thread_id = retriever.thread_id

    logger.info(f"Thread_id created::{st.session_state.thread_id}")

    # Show a spinner while the assistant is thinking...
    with st.spinner("Wait... Generating response..."):

        prompt = "Generate the report from the file name user_guide"
        response = retriever.run_thread(prompt)

        logger.info(f"Response from tool {response}")

        prompt = f"Summarize below content. Use 2000 words or less. content: {response}"
        final_response = retriever.run_thread(prompt)

        logger.info(f"final Response from tool {final_response}")

        # st.write(response, unsafe_allow_html=True)

        message_content = final_response[0].content[0].text
        st.session_state.retriever_message = message_content.value

        logger.info(f"Final response:: {st.session_state.retriever_message}")
    
    st.write("Ingested succesfull")


# the main interface ...
st.title("Knowledgebase OpenAI Assistant")
st.write("Learn fast by chatting with your documents")

# # Check sessions
# if st.session_state.start_chat:
    
if "messages" not in st.session_state:
    st.session_state.messages = []

# Show existing messages if any...
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

logger.info(f"Thread_id ::{st.session_state.thread_id}")
retriever = Retriever(assistant_id = st.session_state.assistant_id, thread_id=st.session_state.thread_id)
# chat input for the user
if prompt := st.chat_input("What's new?"):
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

        response = retriever.run_thread(final_prompt)

        st.session_state.messages.append(
            {"role": "assistant", "content": response}
            )
        with st.chat_message("assistant"):
            st.markdown(response, unsafe_allow_html=True)



