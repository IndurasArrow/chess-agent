import os
import time
import chess
import chess.svg
import streamlit as st
from autogen import ConversableAgent, register_function, GroupChat, GroupChatManager
from dotenv import load_dotenv

# --- Load Environment Variables ---
load_dotenv()

# --- Page Configuration ---
st.set_page_config(
    page_title="Chess AI Arena",
    page_icon="♟️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- Custom CSS for Dark Showcase Look ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Main Background - Dark Slate */
    .stApp {
        background-color: #0F172A;
    }
    
    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1200px;
    }

    /* Cards - Unified container style */
    .stCard {
        background-color: #1E293B;
        padding: 24px;
        border-radius: 16px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        border: 1px solid #334155;
        margin-bottom: 24px;
    }

    /* Typography */
    h1 {
        font-weight: 800;
        letter-spacing: -0.03em;
        color: #F8FAFC !important;
    }
    
    h2, h3 {
        font-weight: 700;
        color: #E2E8F0 !important;
        letter-spacing: -0.01em;
    }
    
    /* General Text Color - Less Aggressive */
    .stApp, .stMarkdown, p {
        color: #CBD5E1;
    }
    
    label {
        color: #94A3B8 !important;
    }
    
    /* Specific overrides for Streamlit elements that might be stubborn */
    .stMarkdown p {
        color: #CBD5E1 !important;
    }

    /* Agent Header */
    .agent-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding-bottom: 15px;
        margin-bottom: 15px;
        border-bottom: 1px solid #334155;
    }
    
    .agent-name {
        font-weight: 600;
        font-size: 1.1rem;
        color: #F8FAFC;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    .agent-vs {
        font-weight: 700;
        color: #64748B;
        font-size: 0.9rem;
    }

    /* Buttons - Modern & Clean */
    .stButton > button {
        border-radius: 10px;
        font-weight: 600;
        border: none;
        padding: 0.5rem 1.2rem;
        transition: all 0.2s ease;
        color: white !important;
    }
    
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%);
        box-shadow: 0 4px 10px rgba(37, 99, 235, 0.3);
    }
    
    .stButton > button[kind="secondary"] {
        background-color: #334155;
        color: #F1F5F9 !important;
        border: 1px solid #475569;
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 15px rgba(0,0,0,0.3);
        filter: brightness(1.1);
    }

    /* Game Log - Terminal Style */
    .game-log {
        height: 350px;
        overflow-y: auto;
        padding: 15px;
        background: #0B1120;
        border-radius: 12px;
        border: 1px solid #334155;
        font-family: 'JetBrains Mono', monospace; /* Monospace for logs looks cooler */
        font-size: 0.9rem;
    }
    
    .log-entry {
        padding: 8px 0;
        border-bottom: 1px solid #1E293B;
        animation: fadeIn 0.3s ease-in;
    }
    
    .log-entry strong {
        color: #F8FAFC;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(5px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Expander & Status */
    .streamlit-expanderHeader {
        background-color: #1E293B !important;
        color: #F1F5F9 !important;
        border-radius: 8px;
    }
    
    div[data-testid="stStatusWidget"] {
        background-color: #1E293B;
        border-radius: 12px;
        border: 1px solid #334155;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
    }
    
    /* Remove default top margin for titles */
    .block-container > div:first-child {
        margin-top: 0;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    ::-webkit-scrollbar-track {
        background: #0F172A; 
    }
    ::-webkit-scrollbar-thumb {
        background: #334155; 
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #475569; 
    }
    </style>
    """, unsafe_allow_html=True)


# --- API Key Management ---
def get_api_key():
    # Try getting from environment variable (local .env)
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        return api_key
    
    # Try getting from Streamlit secrets (deployment)
    if "GEMINI_API_KEY" in st.secrets:
        return st.secrets["GEMINI_API_KEY"]
    
    return None

gemini_api_key = get_api_key()

# --- Session State Initialization ---
if "board" not in st.session_state:
    st.session_state.board = chess.Board()
if "made_move" not in st.session_state:
    st.session_state.made_move = False
if "move_history" not in st.session_state:
    st.session_state.move_history = []
if "move_descriptions" not in st.session_state:
    st.session_state.move_descriptions = [] 
if "game_active" not in st.session_state:
    st.session_state.game_active = False

# --- Helper Functions (Same as before but cleaned up) ---
def render_svg(svg):
    st.markdown(f'<div style="display: flex; justify-content: center; margin: 20px 0;">{svg}</div>', unsafe_allow_html=True)

def available_moves() -> str:
    available_moves = [str(move) for move in st.session_state.board.legal_moves]
    return "Available moves are: " + ",".join(available_moves)

def execute_move(move: str) -> str:
    time.sleep(0.5)  # Slightly longer for better visibility
    try:
        chess_move = chess.Move.from_uci(move)
        if chess_move not in st.session_state.board.legal_moves:
            return f"Invalid move: {move}. Please call available_moves() to see valid moves."
        
        # Track mover BEFORE pushing the move
        mover_color = "⚪ White" if st.session_state.board.turn == chess.WHITE else "⚫ Black"
        
        st.session_state.board.push(chess_move)
        st.session_state.made_move = True

        # Last move highlight color - Electric Blue
        fill_colors = {chess_move.from_square: "#3B82F6AA", chess_move.to_square: "#3B82F6AA"}
        
        board_svg = chess.svg.board(
            st.session_state.board,
            arrows=[(chess_move.from_square, chess_move.to_square)],
            fill=fill_colors,
            size=450,
            colors={
                "square light": "#E2E8F0",  # Slate 200
                "square dark": "#64748B",   # Slate 500
                "margin": "#1E293B",        # Slate 800 (Card Bg)
                "coord": "#94A3B8"          # Slate 400
            }
        )
        
        st.session_state.move_history.append(board_svg)

        # Description Logic
        moved_piece = st.session_state.board.piece_at(chess_move.to_square)
        piece_unicode = moved_piece.unicode_symbol() if moved_piece else ""
        piece_name = chess.piece_name(moved_piece.piece_type).capitalize() if moved_piece else "Piece"
        
        from_sq = chess.SQUARE_NAMES[chess_move.from_square]
        to_sq = chess.SQUARE_NAMES[chess_move.to_square]
        
        move_desc = f"**{mover_color}** moves **{piece_name}** ({piece_unicode}) from `{from_sq}` to `{to_sq}`"
        
        if st.session_state.board.is_checkmate():
            move_desc += " | 🏆 **Checkmate!**"
        elif st.session_state.board.is_stalemate():
            move_desc += " | 🤝 **Stalemate!**"
        elif st.session_state.board.is_check():
            move_desc += " | ⚠️ **Check!**"

        st.session_state.move_descriptions.append(move_desc)

        # --- Live Update for Board & Log ---
        # We use st.session_state.board_spot.container() to ensure multiple elements are handled correctly
        if "board_spot" in st.session_state:
            with st.session_state.board_spot.container():
                st.markdown(f'<div style="display: flex; justify-content: center; margin: 20px 0;">{board_svg}</div>', unsafe_allow_html=True)
                st.markdown(f"<div style='text-align: center; color: #94A3B8;'>{move_desc}</div>", unsafe_allow_html=True)
        
        if "log_spot" in st.session_state:
            with st.session_state.log_spot.container():
                log_html = '<div class="game-log">'
                for desc in reversed(st.session_state.move_descriptions):
                    log_html += f'<div class="log-entry">{desc}</div>'
                log_html += '</div>'
                st.markdown(log_html, unsafe_allow_html=True)

        return move_desc

    except Exception as e:
        return f"Error executing move {move}: {str(e)}"

# --- Sidebar (Configuration only) ---
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    
    st.markdown("---")
    st.markdown("""
    **Chess AI Arena**  
    Two **Gemini 2.5 Flash Lite** agents battle it out.  
    Moderated by **AutoGen**.
    """)
    if gemini_api_key:
        st.success("API Key Loaded ✅")
    else:
        st.error("API Key Not Found ❌")
        st.caption("Please set `GEMINI_API_KEY` in `.env` or Streamlit Secrets.")

# --- Main Layout ---
col_header_1, col_header_2 = st.columns([3, 1])
with col_header_1:
    st.title("Chess AI Arena")
    st.markdown("##### 🤖 Watch two AI Grandmasters compete for glory.")

if not gemini_api_key:
    st.warning("⚠️ No API Key found. Please configure your `.env` file or deployment secrets.")
    st.stop()

# Layout: Board (Left) | Controls & Logs (Right)
main_col1, main_col2 = st.columns([1.3, 1], gap="medium")

# --- Board Visualization (Left Column) - Setup first for Live Updates ---
with main_col1:
    st.markdown('<div class="stCard">', unsafe_allow_html=True)
    
    # Agent Names Header
    st.markdown("""
    <div class="agent-header">
        <div class="agent-name">
            <span>⚪</span> White (Gemini 2.5 Flash Lite)
        </div>
        <div class="agent-vs">VS</div>
        <div class="agent-name">
            <span>⚫</span> Black (Gemini 2.5 Flash Lite)
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Placeholder for the board (Live & Replay)
    board_spot = st.empty()
    st.session_state.board_spot = board_spot
    
    st.markdown("</div>", unsafe_allow_html=True)

# --- Controls & Logs (Right Column) ---
with main_col2:
    st.markdown('<div class="stCard">', unsafe_allow_html=True)
    st.subheader("🎮 Control Center")
    
    c1, c2 = st.columns(2)
    with c1:
        start_btn = st.button("▶️ Start Game", type="primary", use_container_width=True)
    with c2:
        reset_btn = st.button("🔄 Reset", type="secondary", use_container_width=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Game Status / Log
    st.markdown('<div class="stCard">', unsafe_allow_html=True)
    st.subheader("📜 Match Log")
    
    log_spot = st.empty()
    st.session_state.log_spot = log_spot

    if st.session_state.move_descriptions:
        with log_spot:
            # Show last 5 moves or scrollable area
            log_html = '<div class="game-log">'
            for desc in reversed(st.session_state.move_descriptions):
                log_html += f'<div class="log-entry">{desc}</div>'
            log_html += '</div>'
            st.markdown(log_html, unsafe_allow_html=True)
    else:
        st.info("Waiting for game to start...")
    
    st.markdown("</div>", unsafe_allow_html=True)

    if reset_btn:
        st.session_state.board.reset()
        st.session_state.made_move = False
        st.session_state.move_history = []
        st.session_state.move_descriptions = []
        st.session_state.game_active = False
        st.rerun()

# --- Game Logic ---
if start_btn:
    st.session_state.board.reset()
    st.session_state.made_move = False
    st.session_state.move_history = []
    st.session_state.move_descriptions = []
    
    # Initial Board Update
    initial_svg = chess.svg.board(
        st.session_state.board, 
        size=450, 
        colors={
            "square light": "#E2E8F0", 
            "square dark": "#64748B", 
            "margin": "#1E293B",
            "coord": "#94A3B8"
        }
    )
    st.session_state.move_history.append(initial_svg)
    st.session_state.move_descriptions.append("🏁 **Game Start**")
    
    # Render Initial Board
    with board_spot:
        render_svg(initial_svg)
        st.markdown("<div style='text-align: center; color: #94A3B8;'>Game Starting...</div>", unsafe_allow_html=True)

    # Agents
    try:
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ]
        
        config_list = [
            {
                "model": "gemini-2.5-flash-lite", 
                "api_key": gemini_api_key, 
                "api_type": "google",
                "safety_settings": safety_settings
            }
        ]
        
        def check_game_over(msg):
            return st.session_state.board.is_game_over()

        system_message_white = """You are a Chess Grandmaster playing as White.
Your goal is to win the game.
Always follow this sequence:
1. Call available_moves() to see all legal moves in UCI format.
2. Analyze the board and choose the best move.
3. Call execute_move(move='<your_move>') with the chosen UCI move.
Do not provide any other commentary or moves outside of this sequence. Be aggressive and precise."""

        system_message_black = """You are a Chess Grandmaster playing as Black.
Your goal is to win the game.
Always follow this sequence:
1. Call available_moves() to see all legal moves in UCI format.
2. Analyze the board and choose the best move.
3. Call execute_move(move='<your_move>') with the chosen UCI move.
Do not provide any other commentary or moves outside of this sequence. Be aggressive and precise."""

        agent_white = ConversableAgent(
            name="White_Player",
            system_message=system_message_white,
            llm_config={"config_list": config_list},
            human_input_mode="NEVER",
            is_termination_msg=check_game_over,
        )
        
        agent_black = ConversableAgent(
            name="Black_Player",
            system_message=system_message_black,
            llm_config={"config_list": config_list},
            human_input_mode="NEVER",
            is_termination_msg=check_game_over,
        )
        
        game_master = ConversableAgent(
            name="Arbiter",
            system_message="You are the Arbiter. Your job is to execute moves and manage the game state. When a player makes a move, confirm it and state whose turn it is.",
            llm_config=False,
            is_termination_msg=check_game_over,
            default_auto_reply="Move accepted. Next player.",
            human_input_mode="NEVER",
        )
        
        for p in [agent_white, agent_black]:
            register_function(execute_move, caller=p, executor=game_master, name="execute_move", description="Execute a chess move in UCI format.")
            register_function(available_moves, caller=p, executor=game_master, name="available_moves", description="Get list of legal moves.")

        def custom_speaker_selection(last_speaker, groupchat):
            messages = groupchat.messages
            if not messages:
                return agent_white
                
            last_msg = messages[-1]
            
            # If there's a tool call, Arbiter must execute it
            if "tool_calls" in last_msg:
                return game_master
                
            # If the last message was from Arbiter (tool result or acknowledgement)
            if last_speaker == game_master:
                if st.session_state.board.turn == chess.WHITE:
                    return agent_white
                else:
                    return agent_black
            
            # If a player just spoke but didn't call a tool, Arbiter should acknowledge
            return game_master

        groupchat = GroupChat(
            agents=[agent_white, agent_black, game_master],
            messages=[],
            max_round=500,
            speaker_selection_method=custom_speaker_selection,
        )
        
        manager = GroupChatManager(groupchat=groupchat, llm_config=None)

        with main_col2:
            with st.status("🧠 Agents are strategizing...", expanded=True) as status:
                # White starts the game
                game_master.initiate_chat(
                    recipient=manager,
                    message="The game has started. White, please make your first move.",
                    max_turns=None,
                    summary_method="last_msg"
                )
                status.update(label="✅ Game Over", state="complete", expanded=False)

    except Exception as e:
        st.error(f"An error occurred: {e}")

# --- Final Board Visualization (Replay/Static) ---
# This runs after the game logic or on normal re-runs
if st.session_state.move_history:
    with board_spot:
        # Replay Slider
        max_idx = len(st.session_state.move_history) - 1
        curr_idx = st.slider("Timeline", 0, max_idx, max_idx, key="board_slider", label_visibility="collapsed")
        
        render_svg(st.session_state.move_history[curr_idx])
        
        # Caption below board
        desc = st.session_state.move_descriptions[curr_idx] if curr_idx < len(st.session_state.move_descriptions) else ""
        if desc:
            st.caption(desc)
            
else:
    # Empty Board (Only show if not just cleared by Start Game which handles its own initial render, 
    # but Start Game logic runs before this, so this `else` is for fresh load or Reset)
    # Wait, if Start Game runs, move_history is populated, so the `if` block above runs.
    # If Start Game is NOT running, and move_history is empty, this runs.
    
    with board_spot:
        empty_svg = chess.svg.board(
            chess.Board(), 
            size=450, 
            colors={
                "square light": "#E2E8F0", 
                "square dark": "#64748B", 
                "margin": "#1E293B",
                "coord": "#94A3B8"
            }
        )
        render_svg(empty_svg)
        st.markdown("<div style='text-align: center; color: #94A3B8;'>Press <b>Start Game</b> to begin</div>", unsafe_allow_html=True)
