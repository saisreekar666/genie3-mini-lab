import streamlit as st
import json

from parser import parse_prompt_to_config
from world import World
from agent import bfs_plan, path_to_actions
from eval import evaluate
import genie_client

st.set_page_config(page_title="Genie3 Mini Lab", layout="wide")

# --- session state ---
if "world" not in st.session_state:
    st.session_state.world = None
    st.session_state.actions = []
    st.session_state.action_idx = 0

st.title("Genie-style Promptable World (Mini Lab)")

# ======================
# Sidebar: Prompt, Events, Agent, Evaluate
# ======================
with st.sidebar:
    st.header("Prompt → World")
    prompt = st.text_area(
        "Describe your world",
        value="grassy plains with a river and some rocks; start west, goal east; rainy; width 24 height 16",
        height=120,
    )
    colA, colB = st.columns(2)
    with colA:
        gen_btn = st.button("Generate World")
    with colB:
        reset_btn = st.button("Reset")

    st.markdown("---")
    st.subheader("Events")
    event_fired = False
    ev_col1, ev_col2, ev_col3 = st.columns(3)
    with ev_col1:
        if st.button("Toggle Rain"):
            if st.session_state.world:
                st.session_state.world.apply_event("toggle_rain")
                event_fired = True
    with ev_col2:
        if st.button("Spawn Obstacles"):
            if st.session_state.world:
                st.session_state.world.apply_event("spawn_obstacles")
                event_fired = True
    with ev_col3:
        if st.button("Spawn Enemy"):
            if st.session_state.world:
                st.session_state.world.apply_event("spawn_enemy")
                event_fired = True

    # Auto-replan if any event happened
    if event_fired and st.session_state.world:
        path = bfs_plan(st.session_state.world)
        st.session_state.actions = (
            path_to_actions(st.session_state.world, path) if path else []
        )
        st.session_state.action_idx = 0

    st.markdown("---")
    st.subheader("Agent")
    do_plan = st.button("Plan Path (BFS)")
    run_agent = st.button("Run Agent")

    st.markdown("---")
    st.subheader("Evaluate")
    trials = st.slider("Trials", 5, 100, 20, step=5)
    run_eval = st.button("Run Evaluation")

# ======================
# Generate / Reset world
# ======================
if gen_btn or reset_btn:
    cfg = parse_prompt_to_config(prompt)
    # Try a real world-model client first (stub returns None by default)
    gen = genie_client.generate_world(prompt)
    if gen is not None:
        world = World.from_generated(
            {
                "width": gen.width,
                "height": gen.height,
                "tiles": gen.tiles,
                "start": gen.start,
                "goal": gen.goal,
                "enemies": gen.enemies or [],
            }
        )
    else:
        world = World.random(cfg["width"], cfg["height"], cfg)

    st.session_state.world = world
    st.session_state.actions = []
    st.session_state.action_idx = 0

# ======================
# Main layout
# ======================
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("World")
    if st.session_state.world is None:
        st.info("Enter a prompt on the left and click **Generate World**.")
    else:
        img = st.session_state.world.render(scale=24)
        st.image(
            img,
            caption=f"start={st.session_state.world.start}  "
                    f"goal={st.session_state.world.goal}  "
                    f"rain={st.session_state.world.raining}",
        )

with col2:
    st.subheader("Controls")
    if st.session_state.world:
        # Plan path
        if do_plan:
            path = bfs_plan(st.session_state.world)
            if not path:
                st.warning("No path found.")
            else:
                st.session_state.actions = path_to_actions(
                    st.session_state.world, path
                )
                st.session_state.action_idx = 0
                st.success(f"Plan length: {len(st.session_state.actions)} steps")

        # Run agent through planned actions
        if run_agent and st.session_state.actions:
            steps = 0
            while (
                st.session_state.action_idx < len(st.session_state.actions)
                and steps < 200
            ):
                act = st.session_state.actions[st.session_state.action_idx]
                info = st.session_state.world.step(act)
                st.session_state.action_idx += 1
                steps += 1
                if info.get("done"):
                    break
            st.rerun()  # refresh frame to show movement

        # Manual controls
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("⬅️ Left"):
                st.session_state.world.step("left")
        with c2:
            up = st.button("⬆️ Up")
            down = st.button("⬇️ Down")
            if up:
                st.session_state.world.step("up")
            if down:
                st.session_state.world.step("down")
        with c3:
            if st.button("➡️ Right"):
                st.session_state.world.step("right")

# ======================
# Evaluation
# ======================
if run_eval:
    cfg = parse_prompt_to_config(prompt)
    metrics = evaluate(cfg, trials=trials)
    st.json(metrics)
    st.download_button(
        "Download metrics.json",
        data=json.dumps(metrics, indent=2),
        file_name="metrics.json",
        mime="application/json",
    )
