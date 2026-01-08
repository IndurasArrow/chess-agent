# ♟️ AI Chess Agent Arena (Powered by Gemini 2.5)

A multi-agent AI system where two **Google Gemini 2.5** agents play chess against each other, managed by a proxy Game Master for rule validation. Built with **AutoGen** and **Streamlit**.

## 🏗️ Architecture

This project demonstrates an **Autonomous Multi-Agent System**:

- **Agent White (Gemini):** Strategic decision-maker.
- **Agent Black (Gemini):** Tactical opponent.
- **Game Master (Proxy):** A deterministic agent that validates moves using the `python-chess` library and prevents hallucinations.

## 🚀 Features

- **Interactive Game Replay:** Navigate through the entire game history with a slider to analyze every move.
- **Modern UI:** A polished, dark-themed dashboard with card-based layout and responsive design.
- **Visual Gameplay:** High-quality SVG board rendering for crisp visuals at any size.
- **Robust Validation:** Prevents AI "hallucinations" (illegal moves) via a strict rule engine.
- **Secure:** API keys are handled via environment secrets, not hardcoded.
- **Move History:** Full tracking of the game state and moves.

## 🛠️ Tech Stack

- **Framework:** Streamlit
- **Orchestration:** Microsoft AutoGen
- **LLM:** Google Gemini 2.5 Flash
- **Game Engine:** Python-Chess

## 💻 How to Run Locally

1. Clone the repo
2. `pip install -r requirements.txt`
3. `streamlit run app.py`
