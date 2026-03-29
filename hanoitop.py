import streamlit as st
import collections
import heapq
import time

# --- 1. 하노이 로직 및 상태 정의 (원반 4개 고정) ---
def is_valid_move(state, from_p, to_p):
    if not state[from_p]: return False
    if not state[to_p]: return True
    return state[from_p][-1] < state[to_p][-1]

def make_move(state, from_p, to_p):
    new_state = [list(p) for p in state]
    disk = new_state[from_p].pop()
    new_state[to_p].append(disk)
    return tuple(tuple(p) for p in new_state)

def get_h(state, goal):
    # 휴리스틱: 목표 기둥(C)에 있지 않은 원반의 개수
    return sum(len(p) for p in state) - len(state[2])

def state_to_label(state):
    # 요청하신 A: [], B: [], C: [] 형식으로 변환
    return f"A: {list(state[0])}<br>B: {list(state[1])}<br>C: {list(state[2])}"

# --- 2. 4대 알고리즘 탐색 엔진 ---
def run_full_search(start, goal, algo_type):
    all_nodes = [] 
    visited = {start}
    
    if algo_type == "너비 우선 탐색 (BFS)":
        container = collections.deque([(start, -1, 0)])
    elif algo_type == "깊이 우선 탐색 (DFS)":
        container = [(start, -1, 0)]
    elif algo_type == "최상 우선 탐색 (Best-First)":
        container = [(get_h(start, goal), 0, start, -1, 0)]
    elif algo_type == "A* 알고리즘":
        container = [(get_h(start, goal), 0, start, -1, 0)]

    count = 0
    # 무한 루프 방지 및 메모리 보호를 위한 안전 장치 (최대 500노드)
    while container and count < 500:
        if algo_type == "너비 우선 탐색 (BFS)":
            curr, parent, d = container.popleft()
        elif algo_type == "깊이 우선 탐색 (DFS)":
            curr, parent, d = container.pop()
        elif algo_type == "최상 우선 탐색 (Best-First)":
            _, _, curr, parent, d = heapq.heappop(container)
        elif algo_type == "A* 알고리즘":
            f, g, curr, parent, d = heapq.heappop(container)

        node_id = count
        all_nodes.append({"id": node_id, "label": state_to_label(curr), "parent": parent, "depth": d, "state": curr})
        
        if curr == goal: break
        
        count += 1
        for i in range(3):
            for j in range(3):
                if i != j and is_valid_move(curr, i, j):
                    nxt = make_move(curr, i, j)
                    if nxt not in visited:
                        visited.add(nxt)
                        if algo_type == "너비 우선 탐색 (BFS)":
                            container.append((nxt, node_id, d+1))
                        elif algo_type == "깊이 우선 탐색 (DFS)":
                            container.append((nxt, node_id, d+1))
                        elif algo_type == "최상 우선 탐색 (Best-First)":
                            heapq.heappush(container, (get_h(nxt, goal), count, nxt, node_id, d+1))
                        elif algo_type == "A* 알고리즘":
                            g_new = d + 1
                            heapq.heappush(container, (g_new + get_h(nxt, goal), count, nxt, node_id, d+1))
                            
    return all_nodes

# --- 3. UI 레이아웃 및 트리 렌더링 ---
st.set_page_config(page_title="KISH Hanoi Lab", layout="wide")

st.markdown("""
    <style>
    .tree-wrapper { display: flex; flex-direction: column; align-items: center; width: 100%; }
    .level-container { 
        display: flex; flex-wrap: wrap; justify-content: center; 
        gap: 20px; width: 100%; margin-bottom: 40px; position: relative;
    }
    .node-card {
        background: #ffffff; border: 2px solid #5C6BC0; border-radius: 8px;
        padding: 12px; text-align: left; min-width: 150px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1); position: relative; z-index: 2;
    }
    .node-header { font-size: 10px; color: #888; margin-bottom: 5px; border-bottom: 1px solid #eee; }
    .node-body { font-family: 'Courier New', monospace; font-size: 13px; font-weight: 600; color: #222; }
    .goal-node { border-color: #27ae60; background-color: #f0fff4; }
    .line-indicator {
        position: absolute; top: -20px; left: 50%; width: 2px; height: 20px;
        background-color: #cbd5e0; z-index: 1;
    }
    </style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.title("🛡️ 탐색 전략")
    algo = st.radio("알고리즘 선택", ["너비 우선 탐색 (BFS)", "깊이 우선 탐색 (DFS)", "최상 우선 탐색 (Best-First)", "A* 알고리즘"])
    st.write("---")
    st.write("**조건:** 원반 4개 (A->C)")

st.header(f"🌳 {algo} : 상태 공간 트리")

disks = 4
init = (tuple(range(disks, 0, -1)), (), ())
goal = ((), (), tuple(range(disks, 0, -1)))

if st.button("▶ 탐색 시작"):
    all_nodes = run_full_search(init, goal, algo)
    
    st.success(f"탐색 완료! 총 {len(all_nodes)}개의 노드 생성")
    
    # Depth별 그룹화
    depth_groups = collections.defaultdict(list)
    for n in all_nodes:
        depth_groups[n['depth']].append(n)

    # 렌더링 영역
    st.markdown("<div class='tree-wrapper'>", unsafe_allow_html=True)
    for d in sorted(depth_groups.keys()):
        st.write(f"**Depth {d}**")
        html_content = "<div class='level-container'>"
        for node in depth_groups[d]:
            goal_class = "goal-node" if node['state'] == goal else ""
            line_html = "<div class='line-indicator'></div>" if node['depth'] > 0 else ""
            
            html_content += f"""
                <div class="node-card {goal_class}">
                    {line_html}
                    <div class="node-header">Node {node['id']} (Parent: {node['parent']})</div>
                    <div class="node-body">{node['label']}</div>
                </div>
            """
        html_content += "</div>"
        st.markdown(html_content, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
