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
    return f"{list(state[0])} | {list(state[1])} | {list(state[2])}"

# --- 2. 알고리즘별 탐색 및 계층 데이터 생성 ---
def get_tree_hierarchy(start, goal, algo, max_nodes=12):
    nodes = []
    visited = {start}
    queue = []
    
    # [상태, 부모ID, 깊이, 가중치]
    if algo == "BFS": queue = collections.deque([(start, -1, 0)])
    elif algo == "DFS": queue = [(start, -1, 0)]
    elif algo == "Best-First": queue = [(get_h(start, goal), start, -1, 0)]
    elif algo == "A*": queue = [(get_h(start, goal), 0, start, -1, 0)]

    count = 0
    while queue and count < max_nodes:
        if algo == "BFS": curr, parent, d = queue.popleft()
        elif algo == "DFS": curr, parent, d = queue.pop()
        elif algo == "Best-First": _, curr, parent, d = heapq.heappop(queue)
        elif algo == "A*": _, g, curr, parent, d = heapq.heappop(queue)

        node_id = count
        nodes.append({"id": node_id, "label": state_to_label(curr), "parent": parent, "depth": d, "state": curr})
        
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

# --- 3. UI 및 트리 렌더링 CSS ---
st.set_page_config(page_title="Hanoi Tree Lab", layout="wide")

st.markdown("""
    <style>
    .tree-wrapper { display: flex; flex-direction: column; align-items: center; padding: 20px; font-family: sans-serif; }
    .node-row { display: flex; justify-content: center; width: 100%; margin-bottom: 40px; position: relative; }
    .node-card {
        background: white; border: 2px solid #4A90E2; border-radius: 8px;
        padding: 10px; min-width: 140px; text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1); position: relative; z-index: 2;
    }
    .node-id { font-size: 10px; color: #888; margin-bottom: 5px; }
    .node-content { font-size: 13px; font-weight: bold; color: #333; }
    .line-to-parent {
        position: absolute; top: -40px; left: 50%; width: 2px; height: 40px;
        background-color: #A0A0A0; z-index: 1;
    }
    .goal-node { border-color: #4CAF50; background-color: #E8F5E9; }
    </style>
""", unsafe_allow_html=True)

# 사이드바
with st.sidebar:
    st.header("📌 Search Options")
    algo = st.selectbox("알고리즘 선택", ["BFS", "DFS", "Best-First", "A*"])
    disks = st.slider("원반 개수", 2, 3, 2)
    max_n = st.number_input("최대 노드 표시", 5, 20, 10)

# 메인 화면
st.title("🌲 하노이의 탑 상태 공간 트리 시각화")
st.write(f"현재 알고리즘: **{algo}** | 원반: **{disks}개**")

if st.button("▶ 트리 생성 시뮬레이션 시작"):
    nodes = get_tree_hierarchy(init_state := (tuple(range(disks, 0, -1)), (), ()), 
                               goal_state := ((), (), tuple(range(disks, 0, -1))), algo, max_n)
    
    # 깊이(Depth)별로 노드 그룹화
    depth_map = collections.defaultdict(list)
    for n in nodes:
        depth_map[n['depth']].append(n)

    # 트리 렌더링
    st.markdown("<div class='tree-wrapper'>", unsafe_allow_html=True)
    for d in sorted(depth_map.keys()):
        st.markdown(f"<div class='node-row'>", unsafe_allow_html=True)
        cols = st.columns(len(depth_map[d]) + 2) # 중앙 정렬을 위한 트릭
        
        for idx, node in enumerate(depth_map[d]):
            with cols[idx+1]:
                is_goal = "goal-node" if node['state'] == goal_state else ""
                parent_line = "<div class='line-to-parent'></div>" if node['depth'] > 0 else ""
                
                st.markdown(f"""
                    <div class="node-card {is_goal}">
                        {parent_line}
                        <div class="node-id">Node {node['id']} (Parent: {node['parent']})</div>
                        <div class="node-content">{node['label']}</div>
                    </div>
                """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.divider()
st.markdown("### 📝 관찰 가이드")
st.write(f"1. **{algo}** 알고리즘이 노드를 어떤 순서(Node ID)로 생성하는지 확인하세요.")
st.write(f"2. 상단 노드에서 하단 노드로 이어지는 **계층 구조**가 알고리즘마다 어떻게 다른지 비교해 보세요.")
