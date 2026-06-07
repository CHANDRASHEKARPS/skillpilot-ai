
import re
import json
import streamlit as st
from groq import Groq
from dotenv import load_dotenv
from openpyxl import Workbook
from PIL import Image, ImageDraw
from io import BytesIO
import os
import random
import urllib.parse

load_dotenv()

MEMORY_FILE = "memory.json"

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

st.set_page_config(
    page_title="SkillPilot AI",
    page_icon="🧠",
    layout="wide"
)

# ---------------- SESSION ----------------

if "roadmap" not in st.session_state:
    st.session_state.roadmap = []

if "quiz" not in st.session_state:
    st.session_state.quiz = ""

if "ai_content" not in st.session_state:
    st.session_state.ai_content = {}

if "coach_response" not in st.session_state:
    st.session_state.coach_response = ""

if "adaptive_plan" not in st.session_state:
    st.session_state.adaptive_plan = ""

if "completed_days" not in st.session_state:
    st.session_state.completed_days = []

# ---------------- MEMORY ----------------

def load_memory():

    if os.path.exists(MEMORY_FILE):

        with open(MEMORY_FILE, "r") as f:
            return json.load(f)

    return {
        "weak_topics": [],
        "burnout_logs": [],
        "missed_days": []
    }


def save_memory(memory):

    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=4)


memory = load_memory()

# ---------------- CSS ----------------

st.markdown("""

<style>

.stApp{
background:#0e1117;
color:white;
}

.title{
font-size:70px;
font-weight:bold;
text-align:center;
}

.sub{
text-align:center;
color:gray;
margin-bottom:30px;
}

.card{
padding:30px;
background:#1E1E1E;
border-radius:25px;
margin-bottom:30px;
border:1px solid #27374D;
box-shadow:0 0 20px rgba(0,100,255,.2);
}

.completed-card{
padding:30px;
background:#13291A;
border-radius:25px;
margin-bottom:30px;
border:2px solid #10B981;
box-shadow:0 0 20px rgba(16,185,129,.4);
}

.quiz-box{
background:#1E1E1E;
padding:20px;
border-radius:20px;
margin-bottom:20px;
border:1px solid #27374D;
}

</style>

""", unsafe_allow_html=True)

# ---------------- TITLE ----------------

st.markdown(
"<div class='title'>🧠 SkillPilot AI</div>",
unsafe_allow_html=True
)

st.markdown(
"<div class='sub'>Adaptive AI Learning Agent</div>",
unsafe_allow_html=True
)

# ---------------- INPUTS ----------------

c1, c2 = st.columns(2)

with c1:

    skill = st.text_input(
    "📘 Enter Skill",
    placeholder="DSA, React, Essay Writing..."
    )

with c2:

    level = st.selectbox(
    "🎯 Select Level",
    [
    "Beginner",
    "Intermediate",
    "Pro"
    ]
    )

days = st.slider(
"📅 Days",
1,
365,
60
)

# ---------------- GENERATE ----------------

if st.button("🚀 Generate Roadmap"):

    prompt = f"""

Create a realistic {days}-day learning roadmap.

Skill: {skill}

Level:{level}

STRICT FORMAT ONLY.

Return exactly like this:

Day 1|Java Basics|2
Day 2|Variables|2
Day 3|Loops|3

Rules:
- DO NOT use markdown
- DO NOT use numbering
- DO NOT add explanation
- EVERY line must contain |
- Format must be:
Day X|Topic|Hours

"""

    with st.spinner("Building roadmap..."):

        try:

            response = client.chat.completions.create(

            model="llama-3.3-70b-versatile",

            messages=[
            {
            "role":"user",
            "content":prompt
            }
            ]

            )

            text = response.choices[0].message.content

            data = []

            for line in text.split("\n"):

                if "|" not in line:
                    continue

                p = line.split("|")

                if len(p) >= 3:

                    day = p[0].replace(
                    "Day",""
                    ).strip()

                    topic = p[1].strip()

                    data.append({

                    "day":day,

                    "topic":topic,

                    "hours":p[2]

                    })

            st.session_state.roadmap = data
            st.session_state.completed_days = []

            st.success(
            "Roadmap Generated 🎉"
            )

        except Exception as e:

            st.error(e)

# ---------------- PROGRESS ----------------

if len(st.session_state.roadmap) > 0:

    completed = len(st.session_state.completed_days)
    total = len(st.session_state.roadmap)

    progress = completed / total

    st.markdown("## 📈 Learning Progress")

    st.progress(progress)

    st.info(
    f"Completed {completed} out of {total} roadmap days"
    )

# ---------------- POSTER ----------------

def createposter(data):

    img = Image.new(
    "RGB",
    (2200,3200),
    "#0f172a"
    )

    draw = ImageDraw.Draw(img)

    draw.text(
    (850,50),
    "SkillPilot Roadmap",
    fill="white"
    )

    x = 80
    y = 150
    count = 0

    colors = [
    "#2563EB",
    "#9333EA",
    "#10B981",
    "#F59E0B"
    ]

    for item in data:

        color = random.choice(colors)

        draw.rounded_rectangle(
        (
        x,
        y,
        x+550,
        y+180
        ),
        radius=30,
        fill=color
        )

        txt = f"""

Day {item['day']}

{item['topic'][:30]}

{item['hours']} hrs

"""

        draw.text(
        (x+30,y+30),
        txt,
        fill="white"
        )

        x += 650

        count += 1

        if count % 3 == 0:

            x = 80
            y += 250

    buf = BytesIO()

    img.save(
    buf,
    format="PNG"
    )

    buf.seek(0)

    return buf

# ---------------- EXCEL ----------------

def createexcel(data):

    wb = Workbook()

    ws = wb.active

    ws.append([
    "Day",
    "Topic",
    "Hours"
    ])

    for x in data:

        ws.append([
        x["day"],
        x["topic"],
        x["hours"]
        ])

    out = BytesIO()

    wb.save(out)

    out.seek(0)

    return out

# ---------------- SIDEBAR ----------------

if len(st.session_state.roadmap) > 0:

    with st.sidebar:

        st.header("⚡ Practice Zone")

        poster = createposter(
        st.session_state.roadmap
        )

        st.download_button(
        "🖼 Download Poster",
        poster,
        "roadmap.png"
        )

        excel = createexcel(
        st.session_state.roadmap
        )

        st.download_button(
        "📊 Download Excel",
        excel,
        "roadmap.xlsx"
        )

        st.markdown("---")

        day = st.text_input(
        "Day or Range",
        placeholder="1 or 1-3"
        )

        # ---------------- QUIZ ----------------

        if st.button(
        "🧠 Generate Quiz"
        ):

            selected_topics=[]

            if "-" not in day:

                for x in st.session_state.roadmap:

                    if x["day"]==day.strip():

                        selected_topics.append(
                        x["topic"]
                        )

            else:

                try:

                    start,end=day.split("-")

                    start=int(start.strip())
                    end=int(end.strip())

                    for x in st.session_state.roadmap:

                        current_day=int(
                        x["day"]
                        )

                        if start<=current_day<=end:

                            selected_topics.append(
                            x["topic"]
                            )

                except:

                    st.error(
                    "Invalid range format. Use like 1-3"
                    )

            if len(selected_topics)==0:

                st.error(
                "No matching roadmap days found."
                )

            else:

                topics="\n".join(
                selected_topics
                )

                prompt=f"""

Generate EXACTLY 5 MCQ questions.

Topics:
{topics}

STRICT RULES:
- ONLY MCQs
- NO coding challenges
- NO projects
- Questions ONLY from selected topics
- 4 options only

FORMAT:

Q1:
Question here

A. option
B. option
C. option
D. option

Answer: A

"""

                with st.spinner(
                "Generating quiz..."
                ):

                    try:

                        response=client.chat.completions.create(

                        model="llama-3.3-70b-versatile",

                        messages=[
                        {
                        "role":"user",
                        "content":prompt
                        }
                        ]
                        )

                        st.session_state.quiz=(

                        response.choices[0].message.content

                        )

                    except Exception as e:

                        st.error(e)

        # ---------------- INTERACTIVE QUIZ ----------------

        if st.session_state.quiz:

            st.markdown("## 🧠 Interactive Quiz")

            quiz_text = st.session_state.quiz

            question_blocks = re.findall(
                r"(Q\d+:.*?Answer:\s*[A-D])",
                quiz_text,
                re.DOTALL
            )

            for idx, block in enumerate(question_blocks):

                lines = block.strip().split("\n")

                clean_lines=[]

                for line in lines:

                    line=line.strip()

                    if line:
                        clean_lines.append(line)

                question=""
                options=[]
                correct=""

                for i,line in enumerate(clean_lines):

                    if line.startswith("Q"):

                        if i+1 < len(clean_lines):

                            question=clean_lines[i+1]

                    elif line.startswith(("A.","B.","C.","D.")):

                        options.append(line)

                    elif line.startswith("Answer:"):

                        correct=line.replace(
                        "Answer:",
                        ""
                        ).strip()

                st.markdown(f"""

<div class='quiz-box'>

<h3 style='color:white;'>
Q{idx+1}
</h3>

<p style='font-size:20px;color:white;'>
{question}
</p>

</div>

""", unsafe_allow_html=True)

                user_answer = st.radio(

                    f"Choose answer for Q{idx+1}",
                    options,
                    key=f"quiz_{idx}"

                )

                if st.button(
                    f"Submit Q{idx+1}",
                    key=f"submit_{idx}"
                ):

                    selected = user_answer[0]

                    if selected == correct:

                        st.success(
                        "✅ Correct Answer"
                        )

                    else:

                        st.error(
                        f"❌ Wrong Answer. Correct answer is {correct}"
                        )

                st.divider()

# ---------------- AI COACH ----------------

if len(st.session_state.roadmap) > 0:

    st.markdown("## 🤖 AI Study Coach")

    coach_input = st.text_area(
    "Describe your learning issue",
    placeholder="I am struggling with arrays..."
    )

    if st.button("🧠 Ask AI Coach"):

        roadmap_context = ""

        for x in st.session_state.roadmap[:15]:

            roadmap_context += (
            f"Day {x['day']} : "
            f"{x['topic']} - "
            f"{x['hours']} hrs\n"
            )

        coach_prompt = f"""

You are an intelligent AI learning coach.

Skill:
{skill}

Level:
{level}

Roadmap:
{roadmap_context}

Student Problem:
{coach_input}

Previous Memory:
{memory}

Your task:
- analyze issue
- reduce burnout
- motivate student
- adapt study plan
- suggest improvements

Keep response practical and human.

"""

        with st.spinner("AI Coach Thinking..."):

            try:

                response = client.chat.completions.create(

                    model="llama-3.3-70b-versatile",

                    messages=[
                        {
                            "role":"user",
                            "content":coach_prompt
                        }
                    ]

                )

                st.session_state.coach_response = (
                    response.choices[0].message.content
                )

                lower_input = coach_input.lower()

                if "struggle" in lower_input:
                    memory["weak_topics"].append(coach_input)

                if "burnout" in lower_input:
                    memory["burnout_logs"].append(coach_input)

                if "missed" in lower_input or "skipped" in lower_input:
                    memory["missed_days"].append(coach_input)

                save_memory(memory)

            except Exception as e:

                st.error(e)

    if st.session_state.coach_response:

        st.markdown(st.session_state.coach_response)

# ---------------- ROADMAP ----------------

for i,item in enumerate(
st.session_state.roadmap
):

    completed = item["day"] in st.session_state.completed_days

    card_type = "completed-card" if completed else "card"

    st.markdown(
f"""

<div class='{card_type}'>

<h1>Day {item['day']}</h1>

<h2>{item['topic']}</h2>

{item['hours']} hrs

</div>

""",
unsafe_allow_html=True
    )

    c1,c2,c3,c4 = st.columns(4)

    query = urllib.parse.quote(
    item["topic"]+" "+skill
    )

    with c1:

        st.link_button(
        "🎥 Video",
        f"https://www.youtube.com/results?search_query={query}"
        )

    with c2:

        st.link_button(
        "📘 Resource",
        f"https://www.google.com/search?q={query}+tutorial"
        )

    with c3:

        key = f"learn{i}"

        if st.button(
        "🧠 Learn with AI",
        key=key
        ):

            prompt = f"""

Teach {item['topic']}

For beginner.

Include:
- simple explanation
- real examples
- small code if needed

"""

            response = client.chat.completions.create(

            model="llama-3.3-70b-versatile",

            messages=[
            {
            "role":"user",
            "content":prompt
            }
            ]
            )

            st.session_state.ai_content[i] = (
            response.choices[0].message.content
            )

    with c4:

        if completed:

            st.success("Completed")

        else:

            if st.button(
            "✅ Complete",
            key=f"complete{i}"
            ):

                st.session_state.completed_days.append(
                item["day"]
                )

                st.rerun()

    if i in st.session_state.ai_content:

        st.info(
        st.session_state.ai_content[i]
        )

    st.divider()

