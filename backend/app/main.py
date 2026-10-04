from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.models.expertise import Expertise
from app.services.compiler import compile_skill, slugify
from app.services.extractor import extract_expertise
from app.services.evaluator import evaluate_skill


app = FastAPI(
    title="Apprentice API",
    description="Human expertise -> validated Agent Skills",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class GenerateRequest(BaseModel):
    demonstration: str


@app.get("/")
def root():
    return {
        "message": "Welcome to Apprentice",
        "tagline": "Show it once. It writes the skill.",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "apprentice-backend",
        "version": "0.1.0",
    }


@app.post("/api/skills/compile")
def compile_expertise(expertise: Expertise):
    skill_markdown = compile_skill(expertise)

    return {
        "skill_id": slugify(expertise.title),
        "status": "compiled",
        "skill_markdown": skill_markdown,
    }


@app.post("/api/skills/generate")
def generate_skill(request: GenerateRequest):
    expertise = extract_expertise(request.demonstration)

    skill_markdown = compile_skill(expertise)

    confidences = [
        step.confidence
        for step in expertise.steps
    ]

    if confidences:
        overall_confidence = sum(confidences) / len(confidences)
    else:
        overall_confidence = 0.0

    needs_review = overall_confidence < 0.8

    # Teach-back validation
    evaluation = evaluate_skill(
        expertise,
        request.demonstration
    )

    return {
        "status": "generated",
        "skill_id": slugify(expertise.title),
        "expertise": expertise.model_dump(),
        "skill_markdown": skill_markdown,
        "confidence": round(overall_confidence, 2),
        "needs_review": needs_review,
        "evaluation": evaluation,
    }

@app.get("/demo", response_class=HTMLResponse)
def demo():
    return """
<!DOCTYPE html>
<html>
<head>
<title>Apprentice</title>
<style>
body {
    font-family: Arial, sans-serif;
    background: #0b1020;
    color: white;
    margin: 0;
    padding: 40px;
}
.container {
    max-width: 1100px;
    margin: auto;
}
.grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 24px;
}
.card {
    background: #151c31;
    padding: 24px;
    border-radius: 16px;
}
textarea {
    width: 100%;
    height: 260px;
    box-sizing: border-box;
    background: #090d18;
    color: white;
    border: 1px solid #394563;
    border-radius: 10px;
    padding: 14px;
}
button {
    width: 100%;
    margin-top: 15px;
    padding: 15px;
    background: #7657ff;
    color: white;
    border: 0;
    border-radius: 10px;
    font-size: 16px;
    font-weight: bold;
    cursor: pointer;
}
.score {
    font-size: 48px;
    font-weight: bold;
}
.pass {
    color: #40d99a;
}
pre {
    white-space: pre-wrap;
    background: #090d18;
    padding: 15px;
    border-radius: 10px;
    max-height: 450px;
    overflow: auto;
}
.check {
    padding: 8px;
    border-bottom: 1px solid #303a55;
}
</style>
</head>

<body>
<div class="container">

<h1>🧠 Apprentice</h1>
<p>Show it once. It writes the skill.</p>

<div class="grid">

<div class="card">
<h2>Teach Apprentice</h2>

<textarea id="demo">When my motorcycle does not start, I first turn off the ignition. I inspect the battery terminals for corrosion. Then I set my multimeter to DC voltage and measure the battery. If the voltage is very low, I charge or replace the battery. I never short the battery terminals.</textarea>

<button onclick="generate()" id="button">
✨ Compile My Expertise
</button>
</div>

<div class="card">
<h2>Generated Skill</h2>
<div id="result">
<p>Waiting for demonstration...</p>
</div>
</div>

</div>
</div>

<script>
async function generate() {

    const button = document.getElementById("button");
    const result = document.getElementById("result");

    button.disabled = true;
    button.innerText = "Gemma is compiling...";

    result.innerHTML = "<p>🧠 Gemma is extracting expertise...</p>";

    try {

        const response = await fetch("/api/skills/generate", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                demonstration: document.getElementById("demo").value
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(JSON.stringify(data));
        }

        const evaluation = data.evaluation;

        let checks = evaluation.checks.map(c => `
            <div class="check">
                ${c.passed ? "✅" : "⚠️"}
                <b>${c.name}</b>
                <br>
                <small>${c.detail}</small>
            </div>
        `).join("");

        result.innerHTML = `
            <div class="score pass">
                ${evaluation.fidelity_percent}%
            </div>

            <h3>
                ${evaluation.status === "PASS"
                    ? "✓ CERTIFIED"
                    : "⚠ EXPERT REVIEW"}
            </h3>

            <h2>${data.expertise.title}</h2>

            <p>${data.expertise.purpose}</p>

            <h3>Validation</h3>
            ${checks}

            <h3>Generated SKILL.md</h3>

            <pre>${escapeHtml(data.skill_markdown)}</pre>
        `;

    } catch(error) {

        result.innerHTML =
            "<p style='color:#ff7777'>Error: " +
            error.message +
            "</p>";
    }

    button.disabled = false;
    button.innerText = "✨ Compile My Expertise";
}

function escapeHtml(text) {
    return text
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;");
}
</script>

</body>
</html>
"""