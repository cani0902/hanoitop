import streamlit as st
import collections
import heapq
import time

# --- 1. 하노이 로직 ---
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
    return sum(len(p) for p in state) - len(state[2])

def state_to_label(state):
    return f"{list(state[0])}|{list(state[1])}|{list(state[2])}"

# --- 2. 알고리즘별 탐색 및 트리 구조 생성 ---
def get_tree_data(start, goal, algo):
    nodes = [] # (id, label, parent_id, color)
    visited = {start}
    queue = []
    
    if algo == "BFS":
        queue = collections.deque([(start, None, 0)]) # state, parent_idx, depth
    elif algo == "DFS":
        queue = [(start, None, 0)]
    elif algo == "Best-First":
        queue = [(get_h(start, goal), start, None, 0)]
    elif algo == "A*":
        queue = [(get_h(start, goal), 0, start, None, 0)]

    count = 0
    limit = 15 # 화면 표시상 노드 제한

    while queue and count < limit:
        # 알고리즘별 추출
        if algo == "BFS": curr, parent, d = queue.popleft()
        elif algo == "DFS": curr, parent, d = queue.pop()
        elif algo == "Best-First": _, curr, parent, d = heapq.heappop(queue)
        elif algo == "A*": _, g, curr, parent, d = heapq.heappop(queue)

        node_id = count
        color = "#e1f5fe" if curr != goal else "#c8e6c9"
        nodes.append({"id": node_id, "label": state_to_label(curr), "parent": parent, "color": color})
        
        if curr == goal: break
        
        count += 1
        for i in range(3):
            for j in range(3):
                if i != j and is_valid_move(curr, i, j):
                    nxt = make_move(curr, i, j)
                    if nxt not in visited:
                        visited.add(nxt)
                        if algo == "BFS": queue.append((nxt, node_id, d+1))
                        elif algo == "DFS": queue.append((nxt, node_id, d+1))
                        elif algo == "Best-First": heapq.heappush(queue, (get_h(nxt, goal), nxt, node_id, d+1))
                        elif algo == "A*": heapq.heappush(queue, (g+1+get_h(nxt, goal), g+1, nxt, node_id, d+1))
    
    return nodes

# --- 3. UI 구성 (N-Puzzle 스타일) ---
st.set_page_config(page_title="Hanoi Tree Visualizer", layout="wide")

st.markdown("""
    <style>
    .node-box {
        border: 2px solid #333; border-radius: 8px; padding: 10px;
        background-color: white; text-align: center; font-family: monospace;
        font-size: 12px; min-width: 120px; display: inline-block; margin: 5px;
    }
    .tree-container { display: flex; flex-direction: column; align-items: center; }
    .level { display: flex; justify-content: center; margin-bottom: 20px; width: 100%; }
    .arrow { font-size: 20px; color: #888; }
    </style>
""", unsafe_allow_html=True)

# 사이드바 설정
with st.sidebar:
    st.title("⚙️ Settings")
    algo = st.radio("알고리즘 선택", ["BFS", "DFS", "Best-First", "A*"])
    disks = st.slider("원반 개수", 2, 3, 2)
    st.info("A*는 f = g + h 비용을 계산하여 효율적으로 트리를 확장합니다.")

# 메인 화면
st.header(f"🌳 {algo} 상태 공간 트리 생성")
st.write("실행 버튼을 누르면 탐색 순서에 따라 트리가 시각적으로 구성됩니다.")

init_state = (tuple(range(disks, 0, -1)), (), ())
goal_state = ((), (), tuple(range(disks, 0, -1)))

if st.button("트리 생성 실행"):
    nodes = get_tree_data(init_state, goal_state, algo)
    
    # 트리를 층(Depth)별로 정리하여 시각화
    # 간단한 시각화를 위해 순차적 리스트로 표시하되, 부모 정보를 노출
    st.subheader("탐색된 상태 노드 (Step-by-Step)")
    
    for node in nodes:
        with st.container():
            col1, col2 = st.columns([1, 5])
            with col1:
                if node['parent'] is not None:
                    st.markdown(f"<div style='text-align:right' class='arrow'>└─ Parent Node {node['parent']}</div>", unsafe_allow_html=True)
                else:
                    st.markdown("**START**")
            with col2:
                st.markdown(f"""
                    <div class="node-box" style="background-color: {node['color']};">
                        <strong>Node ID: {node['id']}</strong><br>
                        {node['label']}
                    </div>
                """, unsafe_allow_html=True)
            time.sleep(0.1)

    st.success(f"탐색 완료: 총 {len(nodes)}개의 상태 노드가 생성되었습니다.")

st.divider()
st.markdown("### 💡 알고리즘 비교 가이드")
st.write("- **BFS**: 모든 형제 노드를 다 만든 후 다음 층으로 내려갑니다 (넓은 트리).")
def generate_summary():
    return {
        "BFS": "모든 노드를 순차적으로 탐색하여 최단 경로를 보장합니다.",
        "DFS": "한 경로를 깊게 파고들며 탐색합니다 (가장 왼쪽 아래부터 생성).",
        "A*": "목표까지의 거리를 계산하여 꼭 필요한 노드 위주로 트리를 만듭니다."
    }
st.write(f"- **{algo}**: {generate_summary().get(algo, '목표 방향으로 우선 탐색합니다.')}")
