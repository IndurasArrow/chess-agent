# ♟️ AI Chess Agent Arena (Powered by Gemini 2.5 Flash Lite)

A multi-agent AI system where two **Google Gemini 2.5 Flash Lite** agents play chess against each other, managed by a proxy Game Master for rule validation. Built with **AutoGen** and **Streamlit**.

## 🚀 Features
- **Dual AI Agents:**
    - **Agent White (Gemini):** Strategic decision-maker.
    - **Agent Black (Gemini):** Tactical opponent.
- **Game Master (Arbiter):** A proxy agent that validates moves using the `python-chess` library and ensures rule compliance.
- **Live Visualization:** Real-time chess board rendering with move highlighting.
- **Move History & Replay:** Scrub through the game timeline with an interactive slider.
- **Modern UI:** Clean, dark-themed dashboard built with Streamlit.

## 🛠️ Tech Stack
- **Framework:** [AutoGen](https://microsoft.github.io/autogen/)
- **LLM:** Google Gemini 2.5 Flash Lite
- **Frontend:** Streamlit
- **Chess Logic:** python-chess

## 💻 How to Run Locally

1. Clone the repo
2. `pip install -r requirements.txt`
3. `streamlit run app.py`
