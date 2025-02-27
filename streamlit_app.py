import streamlit as st
from openai import OpenAI
import requests
from datetime import datetime, timedelta

# Show title and description.
st.title("📈 Stock Advisor Chatbot")
st.write(
    "This chatbot helps you buy stock based on current global news and provides a score on how likely the event will affect the stock price. "
    "To use this app, you need to provide an OpenAI API key, which you can get [here](https://platform.openai.com/account/api-keys). "
    "You can also learn how to build this app step by step by [following our tutorial](https://docs.streamlit.io/develop/tutorials/llms/build-conversational-apps)."
)

# Ask user for their OpenAI API key via `st.text_input`.
openai_api_key = st.text_input("OpenAI API Key", type="password")
if not openai_api_key:
    st.info("Please add your OpenAI API key to continue.", icon="🗝️")
else:
    # Create an OpenAI client.
    client = OpenAI(api_key=openai_api_key)

    # Create a session state variable to store the chat messages. This ensures that the
    # messages persist across reruns.
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display the existing chat messages via `st.chat_message`.
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Create a chat input field to allow the user to enter a message. This will display
    # automatically at the bottom of the page.
    if prompt := st.chat_input("Ask about stock advice based on current news"):

        # Store and display the current prompt.
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Fetch current global news using NewsAPI.
        news_api_key = "9e5c6c91e83c406a90f7c3eb84c9d981"
        today = datetime.now().strftime('%Y-%m-%d')
        last_week = (datetime.now() - timedelta(days=20)).strftime('%Y-%m-%d')
        news_url = f"https://newsapi.org/v2/everything?q=stock&from={last_week}&to={today}&language=en&apiKey={news_api_key}"
        news_response = requests.get(news_url)
        news_data = news_response.json()

        # Generate a response using the OpenAI API.
        news_summary = "\n".join([article["title"] for article in news_data["articles"][:5]])
        stream = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "You are a stock advisor based on current global news."},
                {"role": "user", "content": f"Analyze the following news and provide stock advice:\n{news_summary}"}
            ],
            stream=True,
        )

        # Stream the response to the chat using `st.write_stream`, then store it in session state.
        with st.chat_message("assistant"):
            response = st.write_stream(stream)
        st.session_state.messages.append({"role": "assistant", "content": response})

        # Score the impact of the news on stock prices.
        score_response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "You are a stock advisor based on current global news."},
                {"role": "user", "content": f"Score the impact of the following news on stock prices and advice the user on investment or release of stocks if he holds any:\n{news_summary}"}
            ],
        )
        score = score_response.choices[0].message.content
        st.session_state.messages.append({"role": "assistant", "content": f"Impact Score: {score}"})
        with st.chat_message("assistant"):
            st.markdown(f"Impact Score: {score}")