import streamlit as st
from collections import deque
import heapq

# -----------------------------
# 상태 정의
# -----------------------------
def initial_state(n):
    return (tuple(range(n, 0, -1)), (), ())

# -----------------------------
# 상태 표시
# -----------------------------
def state_to_str(state):
    return f"{state[0]}\n{state[1]}\n{state[2]}"

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
# 공통 트리 생성 함수
# -----------------------------
def build_tree(start, algo, max_depth=4):
    visited = set()
    edges = []

    if algo == "BFS":
        structure = deque([(start, 0)])
        pop = structure.popleft
        push = structure.append

    elif algo == "DFS":
        structure = [(start, 0)]
        pop = structure.pop
        push = structure.append

    elif algo == "Greedy":
        structure = [(heuristic(start, goal), start, 0)]
        pop = lambda: heapq.heappop(structure)
        push = lambda x: heapq.heappush(structure, x)

    elif algo == "A*":
        structure = [(heuristic(start, goal), 0, start, 0)]
        pop = lambda: heapq.heappop(structure)
        push = lambda x: heapq.heappush(structure, x)

    while structure:
        if algo in ["BFS", "DFS"]:
            state, depth = pop()
        elif algo == "Greedy":
            _, state, depth = pop()
        else:  # A*
            _, g, state, depth = pop()

        if state in visited or depth > max_depth:
            continue
        visited.add(state)

        for next_state in get_neighbors(state):
            edges.append((state, next_state))

            if algo == "BFS" or algo == "DFS":
                push((next_state, depth + 1))
            elif algo == "Greedy":
                push((heuristic(next_state, goal), next_state, depth + 1))
            else:
                push((depth + 1 + heuristic(next_state, goal), depth + 1, next_state, depth + 1))

    return edges

# -----------------------------
# Graphviz 문자열 생성
# -----------------------------
def build_graphviz(edges):
    dot = "digraph G {\n"
    dot += "rankdir=TB;\n"
    dot += "node [shape=box];\n"

    for parent, child in edges:
        dot += f"\"{state_to_str(parent)}\" -> \"{state_to_str(child)}\";\n"

    dot += "}"
    return dot

# -----------------------------
# UI
# -----------------------------
st.title("🧩 하노이의 탑 탐색 트리")

n = st.slider("원판 개수", 2, 4, 3)
depth = st.slider("트리 깊이", 1, 6, 4)

algo = st.radio(
    "알고리즘 선택",
    ["BFS", "DFS", "Greedy", "A*"]
)

start = initial_state(n)
goal = ((), (), tuple(range(n, 0, -1)))

if st.button("트리 생성"):
    edges = build_tree(start, algo, depth)

    st.write(f"간선 수: {len(edges)}")

    dot = build_graphviz(edges)

    st.graphviz_chart(dot)
