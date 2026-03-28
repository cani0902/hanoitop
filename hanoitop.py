import streamlit as st
import collections
import time
import heapq
import graphviz

# --- 기본 로직 (이전과 동일) ---
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
    return sum(len(p) for p in state) - len(state[2])

def state_to_str(state):
    return f"A{list(state[0])}\nB{list(state[1])}\nC{list(state[2])}"

# --- 알고리즘별 트리 생성 로직 ---
def solve_with_tree(start, goal, algo_type):
    dot = graphviz.Digraph()
    dot.attr(rankdir='TB')
    
    visited = set()
    count = 0
    path = []
    
    # 알고리즘 선택 및 실행
    if algo_type == "BFS":
        queue = collections.deque([(start, [start])])
        visited.add(start)
        while queue:
            curr, p = queue.popleft()
            count += 1
            dot.node(str(curr), state_to_str(curr), color='lightblue', style='filled')
            if curr == goal: return p, count, dot
            for i in range(3):
                for j in range(3):
                    if i != j and is_valid_move(curr, i, j):
                        nxt = make_move(curr, i, j)
                        if nxt not in visited:
                            visited.add(nxt)
                            dot.edge(str(curr), str(nxt))
                            queue.append((nxt, p + [nxt]))

    elif algo_type == "A*":
        pq = [(0 + get_heuristic(start, goal), 0, start, [start])]
        visited_costs = {start: 0}
        while pq:
            f, g, curr, p = heapq.heappop(pq)
            count += 1
            dot.node(str(curr), f"{state_to_str(curr)}\nf={f}", color='lightgreen', style='filled')
            if curr == goal: return p, count, dot
            for i in range(3):
                for j in range(3):
                    if i != j and is_valid_move(curr, i, j):
                        nxt = make_move(curr, i, j)
                        new_g = g + 1
                        if nxt not in visited_costs or visited_costs[nxt] > new_g:
                            visited_costs[nxt] = new_g
                            dot.edge(str(curr), str(nxt))
                            heapq.heappush(pq, (new_g + get_heuristic(nxt, goal), new_g, nxt, p + [nxt]))

    return path, count, dot

# --- Streamlit UI ---
st.set_page_config(layout="wide")
st.title("🗼 하노이의 탑: 상태 공간 트리(State Space Tree) 시각화")

with st.sidebar:
    disks = st.slider("원반 개수", 2, 3, 2) # 트리가 너무 커지면 보기 힘드므로 2~3개 권장
    algo_choice = st.selectbox("알고리즘 선택", ["BFS", "A*"])

init = (tuple(range(disks, 0, -1)), (), ())
target = ((), (), tuple(range(disks, 0, -1)))

if st.button("탐색 시작 및 트리 생성"):
    path, explored, tree_dot = solve_with_tree(init, target, algo_choice)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("🏃 탐색 결과")
        st.write(f"탐색한 총 노드 수: **{explored}개**")
        for step in path:
            st.code(state_to_str(step))
            
    with col2:
        st.subheader("🌳 상태 공간 트리 (교과서 스타일)")
        st.graphviz_chart(tree_dot)

st.info("💡 팁: 원반 개수를 2개로 설정하면 트리의 구조를 한눈에 파악하기 가장 좋습니다.")
