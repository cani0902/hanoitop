import streamlit as st
import collections
import heapq

# --- 1. 하노이 로직 (원반 4개 고정) ---
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
    return sum(len(p) for p in state) - len(state[2])

def state_to_label(state):
    # 각 기둥 상태를 깔끔하게 한 줄씩 표시
    return f"A: {list(state[0])}<br>B: {list(state[1])}<br>C: {list(state[2])}"

# --- 2. 탐색 엔진 ---
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
    while container and count < 400: # 안전을 위한 노드 제한
        if algo_type == "너비 우선 탐색 (BFS)":
            curr, parent, d = container.popleft()
        elif algo_type == "깊이 우선 탐색 (DFS)":
            curr, parent, d = container.pop()
        else: # Priority Queues
            _, _, curr, parent, d = heapq.heappop(container)

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
                        if algo_type == "너비 우선 탐색 (BFS)": container.append((nxt, node_id, d+1))
                        elif algo_type == "깊이 우선 탐색 (DFS)": container.append((nxt, node_id, d+1))
                        elif algo_type == "최상 우선 탐색 (Best-First)": 
                            heapq.heappush(container, (get_h(nxt, goal), count, nxt, node_id, d+1))
                        elif algo_type == "A* 알고리즘": 
                            heapq.heappush(container, (d + 1 + get_h(nxt, goal), count, nxt, node_id, d+1))
    return all_nodes

# --- 3. UI 및 CSS (코드 노출 방지) ---
st.set_page_config(page_title="KISH Hanoi Lab", layout="wide")

st.markdown("""
    <style>
    .tree-container { display: flex; flex-direction: column; align-items: center; width: 100%; background-color: #f8f9fa; padding: 20px; border-radius: 15px; }
    .level-row { display: flex; flex-wrap: nowrap; justify-content: center; gap: 15px; margin-bottom: 30px; width: 100%; overflow-x: auto; padding: 10px; }
    .node-card {
        background: white; border: 1px solid #d1d5db; border-radius: 8px;
        padding: 10px; min-width: 140px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        text-align: left; position: relative;
    }
    .node-card.goal { border: 2px solid #10b981; background-color: #ecfdf5; }
    .header { font-size: 9px; color: #6b7280; margin-bottom: 4px; border-bottom: 1px solid #f3f4f6; }
    .body { font-family: 'monospace'; font-size: 12px; font-weight: bold; color: #111827; line-height: 1.2; }
    .depth-tag { background: #3b82f6; color: white; padding: 2px 8px; border-radius: 4px; font-size: 12px; margin-bottom: 5px; }
    </style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.title("🛡️ 탐색 전략")
    algo = st.radio("알고리즘 선택", ["너비 우선 탐색 (BFS)", "깊이 우선 탐색 (DFS)", "최상 우선 탐색 (Best-First)", "A* 알고리즘"])
    st.divider()
    st.write("**원반 4개 (A -> C)**")

st.header(f"🌳 {algo} 시뮬레이션")

# 실행 로직
init, goal = (tuple(range(4, 0, -1)), (), ()), ((), (), tuple(range(4, 0, -1)))

if st.button("▶ 탐색 시작"):
    nodes = run_full_search(init, goal, algo)
    st.success(f"탐색 완료: {len(nodes)}개 노드 생성")
    
    depth_groups = collections.defaultdict(list)
    for n in nodes: depth_groups[n['depth']].append(n)

    # 트리 출력 (HTML 문자열 결합 후 단 한 번의 st.markdown 호출)
    tree_html = "<div class='tree-container'>"
    for d in sorted(depth_groups.keys()):
        tree_html += f"<div class='depth-tag'>Depth {d}</div>"
        tree_html += "<div class='level-row'>"
        for node in depth_groups[d]:
            is_goal = "goal" if node['state'] == goal else ""
            tree_html += f"""
                <div class="node-card {is_goal}">
                    <div class="header">Node {node['id']} (P:{node['parent']})</div>
                    <div class="body">{node['label']}</div>
                </div>
            """
        tree_html += "</div>"
    tree_html += "</div>"
    
    # 이 부분이 핵심: 작성된 HTML을 렌더링함
    st.markdown(tree_html, unsafe_allow_html=True)
