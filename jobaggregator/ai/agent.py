from typing import TypedDict, List
from langgraph.graph import StateGraph

from jobs.models import Job
from .services import parse_query, semantic_search, generate_questions


# -------------------------------
# 🔹 AGENT STATE
# -------------------------------

class AgentState(TypedDict):
    query: str
    skill: str
    location: str
    jobs: List
    semantic_jobs: List
    questions: str
    final_response: dict
    next_step: str   # 🔥 NEW


# -------------------------------
# 🔹 NODE 1: PARSE QUERY (LLM)
# -------------------------------
def parse_query(query):

    prompt = f"""
    Extract the following from the query:

    1. skill (technology or role like Python, Java, React, Backend)
    2. location (city name or remote)

    Query: {query}

    Return STRICT JSON only:
    {{
        "skill": "...",
        "location": "..."
    }}

    If not found, return empty string.
    """

    try:
        res = model.generate_content(prompt)
        content = res.text.strip()

        content = content.replace("```json", "").replace("```", "").strip()

        print("🔥 Parsed Response:", content)

        return json.loads(content)

    except Exception as e:
        print("Parse Error:", e)
        return {"skill": "", "location": ""}


# -------------------------------
# 🔹 NODE 2: DB FILTER
# -------------------------------

def job_filter_node(state: AgentState):

    print("🔥 STEP 2: Filtering Jobs")

    jobs = Job.objects.all()

    skill = state.get("skill", "").lower()
    location = state.get("location", "").lower()

    if skill:
        jobs = jobs.filter(title__icontains=skill)  # 🔥 better

    if location:
        jobs = jobs.filter(location__icontains=location)

    jobs = list(jobs[:5])

    return {"jobs": jobs}


# -------------------------------
# 🔹 NODE 3: DECISION NODE 🔥
# -------------------------------

def decision_node(state: AgentState):

    print("🔥 STEP 3: Decision Making")

    jobs = state.get("jobs", [])

    if len(jobs) == 0:
        print("⚠️ No exact jobs → using semantic")
        return {"next_step": "semantic"}

    return {"next_step": "interview"}

# -------------------------------
# 🔹 NODE 4: SEMANTIC SEARCH (RAG)
# -------------------------------

def semantic_node(state: AgentState):

    print("🔥 STEP 4: Semantic Search")

    results = semantic_search(state["query"])

    return {"semantic_jobs": results}


# -------------------------------
# 🔹 NODE 5: INTERVIEW QUESTIONS
# -------------------------------

def interview_node(state: AgentState):

    print("🔥 STEP 5: Generating Questions")

    skill = state.get("skill")

    if not skill:
        return {"questions": "No skill detected"}

    questions = generate_questions(skill)

    return {"questions": questions}


# -------------------------------
# 🔹 NODE 6: FINAL RESPONSE
# -------------------------------

def response_node(state: AgentState):

    print("🔥 STEP 6: Building Response")

    jobs = state.get("jobs", [])

    return {
        "final_response": {
            "jobs": [
                {
                    "title": job.title,
                    "company": job.company,
                    "location": job.location
                } for job in jobs
            ],
            "semantic_matches": state.get("semantic_jobs", []),
            "questions": state.get("questions", "")
        }
    }


# -------------------------------
# 🔹 BUILD AGENT GRAPH
# -------------------------------

def build_agent():

    graph = StateGraph(AgentState)

    # Nodes
    graph.add_node("parse", parse_query)
    graph.add_node("job_filter", job_filter_node)
    graph.add_node("decision", decision_node)   # 🔥 NEW
    graph.add_node("semantic", semantic_node)
    graph.add_node("interview", interview_node)
    graph.add_node("response", response_node)

    # Entry
    graph.set_entry_point("parse")

    # Flow
    graph.add_edge("parse", "job_filter")
    graph.add_edge("job_filter", "decision")

    # 🔥 CONDITIONAL FLOW
    graph.add_conditional_edges(
        "decision",
        lambda state: state["next_step"],
        {
            "semantic": "semantic",
            "interview": "interview"
        }
    )

    graph.add_edge("semantic", "interview")
    graph.add_edge("interview", "response")

    return graph.compile()


# -------------------------------
# 🔹 RUN AGENT
# -------------------------------

agent = build_agent()

def run_agent(query: str):
    result = agent.invoke({
        "query": query,
        "skill": "",
        "location": "",
        "jobs": [],
        "semantic_jobs": [],
        "questions": "",
        "next_step": ""
    })
    return result["final_response"]