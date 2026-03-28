import streamlit as st
from collections import deque
import heapq
import networkx as nx
import matplotlib.pyplot as plt

# -----------------------------
# 상태 정의
# -----------------------------
def initial_state(n):
    return (tuple(range(n, 0, -1)), (), ())

def goal_state(n):
    return ((), (), tuple(range(n, 0, -1)))

# -----------------------------
# 상태 문자열 (노드 라벨용)
# -----------------------------
def state_to_str(state):
    return f"A{state[0]}\nB{state[1]}\nC{state[2]}"

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
# BFS (트리 생성 포함)
# -----------------------------
def bfs_tree(start, goal):
    queue = deque([start])
    visited = set()
    parent = {}
    G = nx.DiGraph()

    while queue:
        state = queue.popleft()

        if state in visited:
            continue
        visited.add(state)

        for next_state in get_neighbors(state):
            G.add_edge(state_to_str(state), state_to_str(next_state))

            if next_state not in visited:
                parent[next_state] = state
                queue.append(next_state)

    return G

# -----------------------------
# DFS
# -----------------------------
def dfs_tree(start, goal):
    stack = [start]
    visited = set()
    G = nx.DiGraph()

    while stack:
        state = stack.pop()

        if state in visited:
            continue
        visited.add(state)

        for next_state in get_neighbors(state):
            G.add_edge(state_to_str(state), state_to_str(next_state))

            if next_state not in visited:
                stack.append(next_state)

    return G

# -----------------------------
# Greedy
# -----------------------------
def greedy_tree(start, goal):
    heap = [(heuristic(start, goal), start)]
    visited = set()
    G = nx.DiGraph()

    while heap:
        _, state = heapq.heappop(heap)

        if state in visited:
            continue
        visited.add(state)

        for next_state in get_neighbors(state):
            G.add_edge(state_to_str(state), state_to_str(next_state))
            heapq.heappush(heap, (heuristic(next_state, goal), next_state))

    return G

# -----------------------------
# A*
# -----------------------------
def astar_tree(start, goal):
    heap = [(0 + heuristic(start, goal), 0, start)]
    visited = set()
    G = nx.DiGraph()

    while heap:
        f, g, state = heapq.heappop(heap)

        if state in visited:
            continue
        visited.add(state)

        for next_state in get_neighbors(state):
            G.add_edge(state_to_str(state), state_to_str(next_state))
            heapq.heappush(heap, (g+1 + heuristic(next_state, goal), g+1, next_state))

    return G

# -----------------------------
# 그래프 그리기
# -----------------------------
def draw_graph(G):
    plt.figure(figsize=(10, 7))

    pos = nx.spring_layout(G, seed=42)  # 자동 배치

    nx.draw(
        G, pos,
        with_labels=True,
        node_size=2000,
        node_color="lightblue",
        font_size=8,
        arrows=True
    )

    st.pyplot(plt)

# -----------------------------
# UI
# -----------------------------
st.title("🧩 하노이의 탑 상태 공간 트리")

n = st.slider("원판 개수", 2, 4, 3)

algo = st.selectbox(
    "알고리즘 선택",
    ["BFS", "DFS", "Greedy", "A*"]
)

start = initial_state(n)
goal = goal_state(n)

if st.button("트리 생성"):
    if algo == "BFS":
        G = bfs_tree(start, goal)
    elif algo == "DFS":
        G = dfs_tree(start, goal)
    elif algo == "Greedy":
        G = greedy_tree(start, goal)
    elif algo == "A*":
        G = astar_tree(start, goal)

    st.write(f"노드 수: {len(G.nodes)} / 간선 수: {len(G.edges)}")

    draw_graph(G)[2])
