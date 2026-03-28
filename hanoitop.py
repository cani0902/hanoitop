import streamlit as st
import collections
import time
import heapq

# --- 공통 유틸리티 ---
def is_valid_move(state, from_peg, to_peg):
    if not state[from_peg]: return False
    if not state[to_peg]: return True
    return state[from_peg][-1] < state[to_peg][-1]

def make_move(state, from_peg, to_peg):
    new_state = [list(peg) for peg in state]
    disk = new_state[from_peg].pop()
    new_state[to_peg].append(disk)
    return tuple(tuple(peg) for peg in new_state)

def get_heuristic(state, goal_state):
    # 목표 기둥(C)에 있지 않은 원반의 개수를 휴리스틱으로 사용
    # (A*와 최상 우선 탐색에서 사용)
    num_disks = sum(len(p) for p in state)
    return num_disks - len(state[2])

# --- 1. 너비 우선 탐색 (BFS) ---
def solve_bfs(start, goal):
    queue = collections.deque([(start, [start])])
    visited = {start}
    count = 0
    while queue:
        curr, path = queue.popleft()
        count += 1
        if curr == goal: return path, count
        for i in range(3):
            for j in range(3):
                if i != j and is_valid_move(curr, i, j):
                    nxt = make_move(curr, i, j)
                    if nxt not in visited:
                        visited.add(nxt)
                        queue.append((nxt, path + [nxt]))
    return None, count

# --- 2. 깊이 우선 탐색 (DFS) ---
def solve_dfs(start, goal, max_depth=50):
    stack = [(start, [start])]
    visited = {start: 0} # 상태: 도달했을 때의 깊이
    count = 0
    while stack:
        curr, path = stack.pop()
        count += 1
        if curr == goal: return path, count
        if len(path) > max_depth: continue
        
        for i in range(3):
            for j in range(3):
                if i != j and is_valid_move(curr, i, j):
                    nxt = make_move(curr, i, j)
                    if nxt not in visited or visited[nxt] > len(path):
                        visited[nxt] = len(path)
                        stack.append((nxt, path + [nxt]))
    return None, count

# --- 3. 최상 우선 탐색 (Best-First) ---
def solve_best_first(start, goal):
    pq = [(get_heuristic(start, goal), start, [start])]
    visited = {start}
    count = 0
    while pq:
        _, curr, path = heapq.heappop(pq)
        count += 1
        if curr == goal: return path, count
        for i in range(3):
            for j in range(3):
                if i != j and is_valid_move(curr, i, j):
                    nxt = make_move(curr, i, j)
                    if nxt not in visited:
                        visited.add(nxt)
                        heapq.heappush(pq, (get_heuristic(nxt, goal), nxt, path + [nxt]))
    return None, count

# --- 4. A* 알고리즘 ---
def solve_astar(start, goal):
    # f(n) = g(n) + h(n)
    # g(n): 현재까지의 이동 횟수, h(n): 남은 거리 예측
    pq = [(0 + get_heuristic(start, goal), 0, start, [start])]
    visited = {start: 0}
    count = 0
    while pq:
        f, g, curr, path = heapq.heappop(pq)
        count += 1
        if curr == goal: return path, count
        for i in range(3):
            for j in range(3):
                if i != j and is_valid_move(curr, i, j):
                    nxt = make_move(curr, i, j)
                    new_g = g + 1
                    if nxt not in visited or visited[nxt] > new_g:
                        visited[nxt] = new_g
                        h = get_heuristic(nxt, goal)
                        heapq.heappush(pq, (new_g + h, new_g, nxt, path + [nxt]))
    return None, count

# --- Streamlit UI ---
st.set_page_config(layout="wide")
st.title("🛡️ 하노이의 탑 4대 알고리즘 탐색 비교")

with st.sidebar:
    disks = st.slider("원반 개수", 2, 4, 3)
    speed = st.slider("지연 시간(초)", 0.0, 1.0, 0.2)

init = (tuple(range(disks, 0, -1)), (), ())
goal = ((), (), tuple(range(disks, 0, -1)))

if st.button("모든 알고리즘 동시 실행"):
    cols = st.columns(4)
    algos = [
        ("BFS (너비 우선)", solve_bfs),
        ("DFS (깊이 우선)", solve_dfs),
        ("최상 우선 (Best-First)", solve_best_first),
        ("A* (에이 스타)", solve_astar)
    ]

    for i, (name, func) in enumerate(algos):
        with cols[i]:
            st.subheader(name)
            start_time = time.time()
            path, explored = func(init, goal)
            end_time = time.time()
            
            st.write(f"⏱️ 시간: {end_time - start_time:.4f}s")
            st.write(f"🔍 탐색한 노드: **{explored}개**")
            st.write(f"🛣️ 최종 경로: **{len(path)-1}회**")
            
            display = st.empty()
            for step in path:
                display.code(f"A: {list(step[0])}\nB: {list(step[1])}\nC: {list(step[2])}")
                time.sleep(speed)
            st.success("완료!")
