import streamlit as st
from collections import deque
from graphviz import Digraph

# -----------------------------
# 상태 정의
# -----------------------------
def initial_state(n):
    return (tuple(range(n, 0, -1)), (), ())

def goal_state(n):
    return ((), (), tuple(range(n, 0, -1)))

# -----------------------------
# 상태 표시 (3줄 형태)
# -----------------------------
def state_to_str(state):
    def pad(t):
        return list(t) + [" "] * (3 - len(t))

    A, B, C = map(pad, state)

    return f"{A[::-1]}\n{B[::-1]}\n{C[::-1]}"

# -----------------------------
# 이동 생성
# -----------------------------
def get_neighbors(state):
    neighbors = []
    pegs = list(state)

    for i in range(3):
        if not pegs[i]:
            continue

        for j in range(3):
            if i == j:
                continue

            if not pegs[j] or pegs[i][-1] < pegs[j][-1]:
                new_pegs = [list(p) for p in pegs]
                disk = new_pegs[i].pop()
                new_pegs[j].append(disk)
                neighbors.append(tuple(tuple(p) for p in new_pegs))

    return neighbors

# -----------------------------
# BFS 트리 생성 (레벨 포함)
# -----------------------------
def build_tree(start, max_depth=5):
    queue = deque([(start, 0)])
    visited = set()
    edges = []
    levels = {}

    while queue:
        state, depth = queue.popleft()

        if state in visited or depth > max_depth:
            continue
        visited.add(state)

        levels[state] = depth

        for next_state in get_neighbors(state):
            edges.append((state, next_state))
            queue.append((next_state, depth + 1))

    return edges, levels

# -----------------------------
# Graphviz 트리 생성
# -----------------------------
def draw_tree(edges, levels):
    dot = Digraph()
    dot.attr(rankdir="TB")  # Top -> Bottom

    # 노드 추가
    for state, depth in levels.items():
        dot.node(
            str(state),
            label=state_to_str(state),
            shape="box"
        )

    # 간선 추가
    for parent, child in edges:
        if parent in levels and child in levels:
            dot.edge(str(parent), str(child))

    return dot

# -----------------------------
# UI
# -----------------------------
st.title("🧩 하노이의 탑 트리 (계층형)")

n = st.slider("원판 개수", 2, 4, 3)
depth = st.slider("트리 깊이 제한", 1, 6, 4)

start = initial_state(n)

if st.button("트리 생성"):
    edges, levels = build_tree(start, depth)

    st.write(f"노드 수: {len(levels)} / 간선 수: {len(edges)}")

    dot = draw_tree(edges, levels)
    st.graphviz_chart(dot)
