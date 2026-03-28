import streamlit as st
from collections import deque
import heapq

# -----------------------------
# 상태 표현
# -----------------------------
def initial_state(n):
    return (tuple(range(n, 0, -1)), (), ())

def goal_state(n):
    return ((), (), tuple(range(n, 0, -1)))

# -----------------------------
# 가능한 이동 생성
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
# 휴리스틱 (남은 원판 수)
# -----------------------------
def heuristic(state, goal):
    return len(goal[2]) - len(state[2])

# -----------------------------
# BFS
# -----------------------------
def bfs(start, goal):
    queue = deque([(start, [])])
    visited = set()

    while queue:
        state, path = queue.popleft()

        if state in visited:
            continue
        visited.add(state)

        if state == goal:
            return path + [state]

        for next_state in get_neighbors(state):
            queue.append((next_state, path + [state]))

    return None

# -----------------------------
# DFS
# -----------------------------
def dfs(start, goal):
    stack = [(start, [])]
    visited = set()

    while stack:
        state, path = stack.pop()

        if state in visited:
            continue
        visited.add(state)

        if state == goal:
            return path + [state]

        for next_state in get_neighbors(state):
            stack.append((next_state, path + [state]))

    return None

# -----------------------------
# Greedy Best First Search
# -----------------------------
def greedy(start, goal):
    heap = [(heuristic(start, goal), start, [])]
    visited = set()

    while heap:
        _, state, path = heapq.heappop(heap)

        if state in visited:
            continue
        visited.add(state)

        if state == goal:
            return path + [state]

        for next_state in get_neighbors(state):
            h = heuristic(next_state, goal)
            heapq.heappush(heap, (h, next_state, path + [state]))

    return None

# -----------------------------
# A* Search
# -----------------------------
def astar(start, goal):
    heap = [(0 + heuristic(start, goal), 0, start, [])]
    visited = set()

    while heap:
        f, g, state, path = heapq.heappop(heap)

        if state in visited:
            continue
        visited.add(state)

        if state == goal:
            return path + [state]

        for next_state in get_neighbors(state):
            new_g = g + 1
            h = heuristic(next_state, goal)
            heapq.heappush(heap, (new_g + h, new_g, next_state, path + [state]))

    return None

# -----------------------------
# UI
# -----------------------------
st.title("🧩 하노이의 탑 탐색 알고리즘 시각화")

n = st.slider("원판 개수", 2, 5, 3)

algo = st.selectbox(
    "알고리즘 선택",
    ["BFS", "DFS", "Greedy", "A*"]
)

start = initial_state(n)
goal = goal_state(n)

if st.button("실행"):
    if algo == "BFS":
        result = bfs(start, goal)
    elif algo == "DFS":
        result = dfs(start, goal)
    elif algo == "Greedy":
        result = greedy(start, goal)
    elif algo == "A*":
        result = astar(start, goal)

    if result:
        st.success(f"해결 완료! 단계 수: {len(result)-1}")

        for i, step in enumerate(result):
            st.write(f"Step {i}: {step}")
    else:
        st.error("해결 실패")

# -----------------------------
# 상태 시각화 함수
# -----------------------------
def draw_state(state):
    st.write("A:", state[0])
    st.write("B:", state[1])
    st.write("C:", state[2])
