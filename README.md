
# Genie3 Mini Lab — Promptable World Demo (Agent-in-the-loop)

A lightweight, **Genie‑style** demo you can run locally to showcase:
- Turning a **text prompt** into a **navigable 2D world** (procedurally generated),
- **Promptable world events** (rain, new obstacles/enemies) to test counterfactuals,
- A simple **agent** (BFS planner) to execute multi‑step goals,
- **Evaluation** metrics for goal success under event perturbations.

> ⚠️ This project does **not** include Google DeepMind's Genie 3. It provides a clean
> interface (`genie_client.py`) so you can **swap in Genie 3** or any other world model
> later. For now, it uses a procedural world generator so you can record a credible demo.

## Quickstart

```bash
python -m venv .venv && source .venv/bin/activate  # (Windows: .venv\Scripts\activate)
pip install -r requirements.txt
streamlit run app.py
```

Then open the local URL Streamlit prints (usually http://localhost:8501).

## What you can demo in 60 seconds

1. Type a prompt like:  
   _"grassy plains with a river and scattered rocks; start west, goal east; rainy"_  
   Click **Generate World**.
2. Click **Run Agent** → watch the planned route to the goal.
3. Toggle **Rain** or **Spawn obstacles** mid‑episode and see the route update.
4. Open the **Evaluate** tab → run 20 trials with scheduled events and screenshot the metrics.

## Repo structure

```
genie3-mini-lab/
├─ app.py                 # Streamlit UI (prompt → world + events + agent + eval)
├─ world.py               # Grid world, physics/costs, rendering
├─ parser.py              # Simple keyword parser (prompt → config dict)
├─ events.py              # Event scheduler and controls
├─ agent.py               # BFS planner and stepper
├─ eval.py                # Batch evaluation utilities
├─ genie_client.py        # Interface stub you can replace with the real Genie 3 client
├─ requirements.txt
└─ README.md
```

## Swapping in Genie 3 (when access is available)

- Implement `genie_client.generate_world(prompt: str) -> GeneratedWorld` to return a structure
  compatible with `World.from_generated(...)` in `world.py` (tiles, start, goal, entities).
- Keep the **event hooks** (`apply_event(...)`) so you can test **promptable world events** like
  changing weather or adding objects live.

## Notes

- Built to be **portable** (no GPU needed).
- Uses **Streamlit** for a quick, clean UI.
- If you want a browser‑native (canvas) version, you can port `render_world` to Pygame or a JS grid.
- License: MIT (add your name).
