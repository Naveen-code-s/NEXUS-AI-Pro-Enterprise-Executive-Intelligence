import streamlit as st


def inject_styles():
    st.markdown("""<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');
    :root{--r:#ff3b30;--bg:#070708;--panel:#101012;--line:#27272b;--muted:#96969f;--text:#f4f4f5}
    .stApp{background:radial-gradient(circle at 82% 0%,rgba(255,59,48,.13),transparent 34%),linear-gradient(180deg,#09090b,#070708);color:var(--text)}
    .block-container{max-width:1480px;padding-top:1.8rem;padding-bottom:4rem}
    h1,h2,h3,h4{font-family:'Space Grotesk',sans-serif!important;letter-spacing:-.04em}p,div,button,input,textarea{font-family:'DM Sans',sans-serif}
    .brand{font:700 28px 'Space Grotesk'}.brand span,.kicker,.command-label{color:var(--r)}.muted{color:var(--muted)}
    .hero{border:1px solid var(--line);border-radius:24px;background:linear-gradient(135deg,rgba(255,255,255,.045),rgba(255,255,255,.015));padding:38px;box-shadow:0 20px 70px rgba(0,0,0,.24);margin-bottom:24px}
    .hero h1{font-size:clamp(2.2rem,5vw,4.6rem);max-width:1000px;margin:.2rem 0 1rem}
    .command-label{font-weight:700;font-size:12px;letter-spacing:.16em;margin:28px 0 8px}
    .source{border:1px solid var(--line);border-left:3px solid var(--r);background:#101012;padding:15px;margin:10px 0;border-radius:0 14px 14px 0;line-height:1.55}
    .empty-state{margin-top:26px;border:1px dashed #38383e;border-radius:22px;padding:32px;background:rgba(255,255,255,.018)}
    .chips span,.op-pill{display:inline-block;border:1px solid var(--line);border-radius:999px;padding:7px 12px;margin:5px 5px 5px 0;color:#c7c7cd;font-size:13px}.op-pill{background:rgba(255,59,48,.06);border-color:rgba(255,59,48,.28)}
    .stButton>button{border-radius:11px;background:#151518;border:1px solid #333339;min-height:42px}.stButton>button:hover{border-color:var(--r)}
    [data-testid="stSidebar"]{background:#0b0b0d;border-right:1px solid var(--line)}
    [data-testid="stFileUploader"]{border:1px dashed #39393f;border-radius:14px;padding:8px}
    </style>""", unsafe_allow_html=True)
