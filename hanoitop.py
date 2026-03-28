import streamlit as st
from collections import deque
import heapq

# -----------------------------
# 상태 정의
# -----------------------------
def initial_state(n):
    return (tuple(range(n, 0, -1)), (), ())

def goal_state(n):
    return ((), (), tuple(range(n, 0, -1)))

# -----------------------------
# 퍼즐 스타일 출력
# -----------------------------
def state_to_pretty(state, n):
    pegs = [list(p) for p in state]
    
    # 높이 맞추기
    for p in pegs:
        while len(p) < n:
            p.insert(0, " ")

    lines = []
    for i in range(n):
        lines.append(f"{pegs[0][i]} | {pegs[1][i]} | {pegs[2][i]}")

    lines.append("A   B   C")
    return "\\n".join(lines)

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
# 휴리스틱
# -----------------------------
def heuristic(state, goal):
    return len(goal[2]) - len(state[2])

# -----------------------------
# 트리 생성 (목표까지)
# -----------------------------
def build_tree(start, goal, algo):
    visited = set()
    edges = []

    if algo == "BFS":
        structure = deque([start])
        pop = structure.popleft
        push = structure.append

    elif algo == "DFS":
        structure = [start]
        pop = structure.pop
        push = structure.append

    elif algo == "Greedy":
        structure = [(heuristic(start, goal), start)]
        pop = lambda: heapq.heappop(structure)
        push = lambda x: heapq.heappush(structure, x)

    elif algo == "A*":
        structure = [(heuristic(start, goal), 0, start)]
        pop = lambda: heapq.heappop(structure)
        push = lambda x: heapq.heappush(structure, x)

    while structure:
        if algo in ["BFS", "DFS"]:
            state = pop()
        elif algo == "Greedy":
            _, state = pop()
        else:
            _, g, state = pop()

        if state in visited:
            continue
        visited.add(state)

        # 🎯 목표 도달 시 종료
        if state == goal:
            break

        for next_state in get_neighbors(state):
            edges.append((state, next_state))

            if algo in ["BFS", "DFS"]:
                push(next_state)
            elif algo == "Greedy":
                push((heuristic(next_state, goal), next_state))
            else:
                push((g + 1 + heuristic(next_state, goal), g + 1, next_state))

    return edges

# -----------------------------
# Graphviz 생성 (가독성 개선)
# -----------------------------
def build_graphviz(edges, n):
    dot = "digraph G {\n"
    dot += "rankdir=TB;\n"
    dot += "node [shape=box, style=filled, fillcolor=lightyellow, fontsize=10];\n"
    dot += "edge [color=gray];\n"

    for parent, child in edges:
        p = state_to_pretty(parent, n)
        c = state_to_pretty(child, n)

        dot += f"\"{p}\" -> \"{c}\";\n"

    dot += "}"
    return dot

# -----------------------------
# UI
# -----------------------------
st.title("🧩 하노이의 탑 트리 (가독성 개선 버전)")

n = st.slider("원판 개수", 2, 4, 3)

algo = st.radio(
    "알고리즘 선택",
    ["BFS", "DFS", "Greedy", "A*"]
)

start = initial_state(n)
goal = goal_state(n)

if st.button("트리 생성"):
    edges = build_tree(start, goal, algo)

    st.write(f"간선 수: {len(edges)}")

    dot = build_graphviz(edges, n)

    st.graphviz_chart(dot)
