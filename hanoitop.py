import streamlit as st
import collections
import time
import heapq

# --- 1. 하노이 로직 및 유틸리티 ---
def is_valid_move(state, from_peg, to_peg):
    if not state[from_peg]: return False
    if not state[to_peg]: return True
    return state[from_peg][-1] < state[to_peg][-1]

def make_move(state, from_peg, to_peg):
    new_state = [list(peg) for peg in state]
    disk = new_state[from_peg].pop()
    new_state[to_peg].append(disk)
    return tuple(tuple(peg) for peg in new_state)

def get_h(state, goal):
    # 목표 기둥에 있지 않은 원반 수 (휴리스틱)
    return sum(len(p) for p in state) - len(state[2])

def render_hanoi(state):
    # 시각적으로 더 깔끔하게 상태 표시
    pegs = ["A", "B", "C"]
    res = ""
    for i, p in enumerate(state):
        res += f"**Peg {pegs[i]}**: {list(p) if p else '[]'}\n\n"
    return res

# --- 2. 4대 알고리즘 (트리 데이터 포함) ---
def run_algo(start, goal, type):
    explored = []
    queue = []
    visited = {start: 0}
    
    if type == "BFS":
        queue = collections.deque([(start, [start])])
        while queue:
            curr, path = queue.popleft()
            explored.append(curr)
            if curr == goal: return path, explored
            for i in range(3):
                for j in range(3):
                    if i != j and is_valid_move(curr, i, j):
                        nxt = make_move(curr, i, j)
                        if nxt not in visited:
                            visited[nxt] = len(path)
                            queue.append((nxt, path + [nxt]))

    elif type == "DFS":
        stack = [(start, [start])]
        while stack:
            curr, path = stack.pop()
            explored.append(curr)
            if curr == goal: return path, explored
            if len(path) > 10: continue # 깊이 제한
            for i in range(3):
                for j in range(3):
                    if i != j and is_valid_move(curr, i, j):
                        nxt = make_move(curr, i, j)
                        if nxt not in visited or visited[nxt] > len(path):
                            visited[nxt] = len(path)
                            stack.append((nxt, path + [nxt]))

    elif type == "Best-First":
        pq = [(get_h(start, goal), start, [start])]
        while pq:
            _, curr, path = heapq.heappop(pq)
            explored.append(curr)
            if curr == goal: return path, explored
            for i in range(3):
                for j in range(3):
                    if i != j and is_valid_move(curr, i, j):
                        nxt = make_move(curr, i, j)
                        if nxt not in visited:
                            visited[nxt] = True
                            heapq.heappush(pq, (get_h(nxt, goal), nxt, path + [nxt]))

    elif type == "A*":
        pq = [(get_h(start, goal), 0, start, [start])]
        while pq:
            f, g, curr, path = heapq.heappop(pq)
            explored.append(curr)
            if curr == goal: return path, explored
            for i in range(3):
                for j in range(3):
                    if i != j and is_valid_move(curr, i, j):
                        nxt = make_move(curr, i, j)
                        new_g = g + 1
                        if nxt not in visited or visited[nxt] > new_g:
                            visited[nxt] = new_g
                            heapq.heappush(pq, (new_g + get_h(nxt, goal), new_g, nxt, path + [nxt]))
    return [], explored

# --- 3. Streamlit UI 디자인 ---
st.set_page_config(page_title="KISH Algorithm Lab", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stCode { background-color: #ffffff !important; border-radius: 10px; border: 1px solid #e0e0e0; }
    .algo-card { 
        padding: 20px; border-radius: 15px; background: white; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.05); border: 1px solid #eee;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🗼 Hanoi Search Visualizer")
st.write("각 알고리즘이 상태 공간 트리 내에서 어떻게 목표를 찾아가는지 시각적으로 비교합니다.")

with st.sidebar:
    st.header("Control Panel")
    disks = st.select_slider("원반 개수", options=[2, 3, 4], value=2)
    show_steps = st.checkbox("탐색 과정 상세 보기", value=True)
    speed = st.slider("시뮬레이션 속도", 0.01, 0.5, 0.1)

init = (tuple(range(disks, 0, -1)), (), ())
goal = ((), (), tuple(range(disks, 0, -1)))

if st.button("▶️ Run Comparison"):
    cols = st.columns(4)
    types = ["BFS", "DFS", "Best-First", "A*"]
    
    for i, t in enumerate(types):
        with cols[i]:
            st.markdown(f"<div class='algo-card'><h3>{t}</h3></div>", unsafe_allow_html=True)
            path, explored = run_algo(init, goal, t)
            
            st.metric("Explored Nodes", f"{len(explored)}")
            st.metric("Final Path", f"{len(path)-1} steps")
            
            if show_steps:
                step_container = st.empty()
                progress_bar = st.progress(0)
                
                # 탐색 경로 애니메이션 (제시한 사이트 느낌)
                for idx, step in enumerate(path):
                    with step_container.container():
                        st.markdown(f"**Step {idx}**")
                        st.info(render_hanoi(step))
                    progress_bar.progress((idx + 1) / len(path))
                    time.sleep(speed)
            st.success(f"{t} Analysis Complete")

st.divider()
st.markdown("### 🔍 알고리즘별 특징 요약")
st.table({
    "알고리즘": ["BFS", "DFS", "Best-First", "A*"],
    "전략": ["가까운 곳부터 전부", "한 놈만 끝까지", "목표만 보고 돌진", "과거+미래 비용 합산"],
    "최단 경로 보장": ["✅ 예", "❌ 아니오", "❌ 아니오", "✅ 예"],
    "효율성 (노드 수)": ["낮음", "매우 낮음", "매우 높음", "높음"]
})
