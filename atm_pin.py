import streamlit as st
import time

# Configuration
CORRECT_PIN = "0789"
MAX_ATTEMPTS = 3
LOCKOUT_TIME = 300  # 5 minutes in seconds

# Initialize session state
if 'security' not in st.session_state:
    st.session_state.security = {
        'attempts': 0,
        'blocked': False,
        'last_attempt_time': 0,
        'input': '',
        'show_reset': False
    }

# Streamlit UI
st.set_page_config(page_title="ATM Security", page_icon="🏦", layout="centered")
st.title("🏦 ATM PIN Verification")

# Security functions
def check_pin(pin):
    if pin == CORRECT_PIN:
        return True
    st.session_state.security['attempts'] += 1
    if st.session_state.security['attempts'] >= MAX_ATTEMPTS:
        st.session_state.security['blocked'] = True
        st.session_state.security['last_attempt_time'] = time.time()
    return False

def reset_system():
    st.session_state.security = {
        'attempts': 0,
        'blocked': False,
        'last_attempt_time': 0,
        'input': '',
        'show_reset': False
    }

# Handle blocked state
if st.session_state.security['blocked']:
    elapsed = time.time() - st.session_state.security['last_attempt_time']
    if elapsed < LOCKOUT_TIME:
        remaining = int(LOCKOUT_TIME - elapsed)
        st.error(f"🚨 Card blocked. Please try again in {remaining//60}m {remaining%60}s")
        st.progress(remaining/LOCKOUT_TIME)
    else:
        reset_system()
        st.rerun()
    st.stop()

# Main PIN interface
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Enter PIN")
    st.markdown(f"<h1 style='text-align: center; font-family: monospace;'>{'•' * len(st.session_state.security['input'])}</h1>", 
                unsafe_allow_html=True)
    
    if st.session_state.security['input'] == CORRECT_PIN:
        st.success("✅ Access Granted")
        st.balloons()
        if st.button("Lock System"):
            reset_system()
            st.rerun()
        st.stop()

with col2:
    # Create keypad
    keypad = st.container()
    with keypad:
        cols = st.columns(3)
        buttons = {
            '1': cols[0].button("1"),
            '2': cols[1].button("2"),
            '3': cols[2].button("3"),
            '4': cols[0].button("4"),
            '5': cols[1].button("5"),
            '6': cols[2].button("6"),
            '7': cols[0].button("7"),
            '8': cols[1].button("8"),
            '9': cols[2].button("9"),
            'C': cols[0].button("C"),
            '0': cols[1].button("0"),
            'E': cols[2].button("E", type="primary")
        }

    # Handle keypad input
    for num in "1234567890":
        if buttons[num]:
            if len(st.session_state.security['input']) < 4:
                st.session_state.security['input'] += num
                st.rerun()

    if buttons['C']:  # Clear
        st.session_state.security['input'] = ''
        st.rerun()

    if buttons['E']:  # Enter
        if len(st.session_state.security['input']) == 4:
            if check_pin(st.session_state.security['input']):
                st.rerun()
            else:
                st.session_state.security['input'] = ''
                st.error(f"❌ Invalid PIN (Attempt {st.session_state.security['attempts']}/{MAX_ATTEMPTS})")
                time.sleep(0.5)
                st.rerun()
        else:
            st.warning("Please enter 4 digits")
            time.sleep(0.5)
            st.rerun()

# Attempt counter
st.caption(f"Attempts: {st.session_state.security['attempts']}/{MAX_ATTEMPTS}")

# Security warning
if st.session_state.security['attempts'] == MAX_ATTEMPTS - 1:
    st.warning("⚠️ Last attempt before card lock")