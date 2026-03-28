import streamlit as st
import collections
import time
import heapq

# --- 1. 기본 하노이 로직 ---
def is_valid_move(state, from_peg, to_peg):
    if not state[from_peg]: return False
    if not state[to_peg]: return True
    return state[from_peg][-1] < state[to_peg][-1]

def make_move(state, from_peg, to_peg):
    new_state = [list(peg) for peg in state]
    disk = new_state[from_peg].pop()
    new_state[to_peg].append(disk)
    return tuple(tuple(peg) for peg in new_state)

def get_heuristic(state, goal):
    # 목표 기둥(C)에 있지 않은 원반의 개수 (남은 거리 예측)
    return sum(len(p) for p in state) - len(state[2])

def state_to_str(state):
    return f"A{list(state[0])}, B{list(state[1])}, C{list(state[2])}"

# --- 2. 알고리즘 통합 탐색 함수 ---
def solve_hanoi(start, goal, algo_type):
    tree_lines = []
    tree_dict = collections.defaultdict(list)
    visited_for_tree = set()
    explored_count = 0
    final_path = []

    # 알고리즘별 탐색 수행
    if algo_type == "BFS (너비 우선)":
        queue = collections.deque([(start, [start])])
        visited = {start}
        while queue:
            curr, path = queue.popleft()
            explored_count += 1
            if curr == goal: 
                final_path = path
                break
            for i in range(3):
                for j in range(3):
                    if i != j and is_valid_move(curr, i, j):
                        nxt = make_move(curr, i, j)
                        if nxt not in visited:
                            visited.add(nxt)
                            tree_dict[curr].append(nxt)
                            queue.append((nxt, path + [nxt]))

    elif algo_type == "DFS (깊이 우선)":
        # DFS는 트리가 너무 깊어질 수 있어 깊이 제한(15)을 둡니다.
        stack = [(start, [start])]
        visited = {start: 0}
        while stack:
            curr, path = stack.pop()
            explored_count += 1
            if curr == goal: 
                final_path = path
                break
            if len(path) > 15: continue
            for i in range(3):
                for j in range(3):
                    if i != j and is_valid_move(curr, i, j):
                        nxt = make_move(curr, i, j)
                        if nxt not in visited or visited[nxt] > len(path):
                            visited[nxt] = len(path)
                            tree_dict[curr].append(nxt)
                            stack.append((nxt, path + [nxt]))

    elif algo_type == "최상 우선 (Best-First)":
        pq = [(get_heuristic(start, goal), start, [start])]
        visited = {start}
        while pq:
            h, curr, path = heapq.heappop(pq)
            explored_count += 1
            if curr == goal: 
                final_path = path
                break
            for i in range(3):
                for j in range(3):
                    if i != j and is_valid_move(curr, i, j):
                        nxt = make_move(curr, i, j)
                        if nxt not in visited:
                            visited.add(nxt)
                            tree_dict[curr].append(nxt)
                            heapq.heappush(pq, (get_heuristic(nxt, goal), nxt, path + [nxt]))

    elif algo_type == "A* (에이 스타)":
        pq = [(0 + get_heuristic(start, goal), 0, start, [start])]
        visited = {start: 0}
        while pq:
            f, g, curr, path = heapq.heappop(pq)
            explored_count += 1
            if curr == goal: 
                final_path = path
                break
            for i in range(3):
                for j in range(3):
                    if i != j and is_valid_move(curr, i, j):
                        nxt = make_move(curr, i, j)
                        new_g = g + 1
                        if nxt not in visited or visited[nxt] > new_g:
                            visited[nxt] = new_g
                            tree_dict[curr].append(nxt)
                            h = get_heuristic(nxt, goal)
                            heapq.heappush(pq, (new_g + h, new_g, nxt, path + [nxt]))

    # 트리 텍스트 생성 (재귀)
    def build_tree_text(node, level, seen):
        if node in seen: return
        seen.add(node)
        indent = "    " * level
        children = tree_dict[node]
        for i, child in enumerate(children):
            prefix = "└── " if i == len(children) - 1 else "├── "
            tree_lines.append(f"{indent}{prefix}{state_to_str(child)}")
            build_tree_text(child, level + 1, seen)

    tree_lines.append(state_to_str(start))
    build_tree_text(start, 0, set())
    
    return "\n".join(tree_lines), explored_count, final_path

# --- 3. Streamlit UI ---
st.set_page_config(layout="wide", page_title="KISH 하노이 알고리즘 비교")
st.title("🗼 하노이의 탑: 4대 알고리즘 상태 공간 트리 비교")

with st.sidebar:
    st.header("설정")
    disks = st.slider("원반 개수", 2, 3, 2)
    algo_choice = st.selectbox("알고리즘 선택", 
                               ["BFS (너비 우선)", "DFS (깊이 우선)", "최상 우선 (Best-First)", "A* (에이 스타)"])

init = (tuple(range(disks, 0, -1)), (), ())
goal = ((), (), tuple(range(disks, 0, -1)))

if st.button("탐색 및 트리 생성 시작"):
    tree_text, count, path = solve_hanoi(init, goal, algo_choice)
    
    c1, c2 = st.columns([1, 2])
    with c1:
        st.subheader("📊 탐색 통계")
        st.metric("탐색한 노드 수", f"{count}개")
        st.metric("최종 경로 길이", f"{len(path)-1}회")
        
        st.write("**최종 이동 경로:**")
        for i, s in enumerate(path):
            st.write(f"{i}. {state_to_str(s)}")

    with c2:
        st.subheader("🌳 상태 공간 트리 (시각화)")
        st.code(tree_text, language="text")

st.divider()
st.info("💡 **수행평가 팁:** 원반 2개로 설정하면 트리의 전체 구조가 한눈에 들어옵니다. 각 알고리즘이 트리를 얼마나 '가지치기' 하며 효율적으로 뻗어나가는지 비교해 보세요.")
