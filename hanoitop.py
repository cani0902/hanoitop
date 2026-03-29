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
    return sum(len(p) for p in state) - len(state[2])

def state_to_label(state):
    return f"{list(state[0])}\n{list(state[1])}\n{list(state[2])}"

# --- 2. 4대 알고리즘 탐색 엔진 (계층 데이터 포함) ---
def run_full_search(start, goal, algo_type):
    # 트리 렌더링을 위해 노드를 저장할 순서가 중요함
    all_nodes = [] 
    visited = {start}
    
    # [상태, 부모ID, 깊이, 가중치]
    if algo_type == "너비 우선 탐색 (BFS)":
        container = collections.deque([(start, -1, 0)])
    elif algo_type == "깊이 우선 탐색 (DFS)":
        container = [(start, -1, 0)]
    elif algo_type == "최상 우선 탐색 (Best-First)":
        container = [(get_h(start, goal), 0, start, -1, 0)]
    elif algo_type == "A* 알고리즘":
        container = [(get_h(start, goal), 0, start, -1, 0)]

    count = 0
    while container:
        # 알고리즘별 추출 방식 (FIFO vs LIFO vs Priority)
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

# --- 3. UI 레이아웃 및 심화 트리 렌더링 (N-Puzzle 스타일) ---
st.set_page_config(page_title="Hanoi Lab: True Tree", layout="wide")

st.markdown("""
    <style>
    /* 트리를 감싸는 전체 영역 */
    .tree-container {
        display: flex; flex-direction: column; align-items: center;
        padding: 20px; font-family: sans-serif;
    }
    
    /* 각 층(Depth)의 노드들을 정렬하는 스타일 */
    .level {
        display: flex; justify-content: center; width: 100%;
        margin-bottom: 50px; position: relative;
    }
    
    /* 개별 노드 카드 디자인 */
    .node-card {
        background: white; border: 2px solid #5C6BC0; border-radius: 10px;
        padding: 10px; text-align: center; min-width: 130px;
        box-shadow: 0 6px 10px rgba(0,0,0,0.1); position: relative; z-index: 2;
    }
    .node-id { font-size: 11px; color: #777; border-bottom: 1px solid #eee; padding-bottom: 3px; margin-bottom: 5px; }
    .node-content { font-size: 14px; font-weight: bold; color: #333; line-height: 1.4; }
    
    /* 부모 노드와 연결되는 수직선 */
    .line-to-parent {
        position: absolute; top: -50px; left: 50%;
        width: 2px; height: 50px; background-color: #A0A0A0; z-index: 1;
    }
    
    /* 목표 노드 강조 */
    .goal-node { border-color: #4CAF50; background-color: #E8F5E9; }
    </style>
""", unsafe_allow_html=True)

# 사이드바 (원반 4개 고정)
with st.sidebar:
    st.title("🛡️ 탐색 전략")
    algo = st.radio("알고리즘을 고르세요", 
                    ["너비 우선 탐색 (BFS)", "깊이 우선 탐색 (DFS)", "최상 우선 탐색 (Best-First)", "A* 알고리즘"])
    st.write("---")
    st.write("**조건:** 원반 4개, 기둥 3개")

# 메인 화면
st.header(f"🌳 {algo} : 계층형 상태 공간 트리")
st.write("초기 상태에서 목표 상태를 찾을 때까지 생성된 **모든 노드**를 계층적 트리 구조로 시각화합니다.")

# 고정 설정
disks = 4
init = (tuple(range(disks, 0, -1)), (), ())
goal = ((), (), tuple(range(disks, 0, -1)))

if st.button("▶ 탐색 및 트리 생성 시작"):
    with st.spinner("목표 상태를 찾을 때까지 트리를 확장 중입니다..."):
        all_nodes, path_found = run_full_search(init, goal, algo)
        
        st.success(f"탐색 완료! 생성된 총 노드 수: **{len(all_nodes)}개**")
        
        # 깊이(Depth)별 노드 그룹화
        depth_map = collections.defaultdict(list)
        for n in all_nodes:
            depth_map[n['depth']].append(n)
            
        # 트리 렌더링
        st.markdown("<div class='tree-container'>", unsafe_allow_html=True)
        for d in sorted(depth_map.keys()):
            st.markdown(f"<div class='level'>", unsafe_allow_html=True)
            cols = st.columns(len(depth_map[d]) + 2) # 중앙 정렬 Trick
            
            for idx, node in enumerate(depth_map[d]):
                with cols[idx+1]:
                    is_goal = "goal-node" if node['state'] == goal else ""
                    parent_line = "<div class='line-to-parent'></div>" if node['depth'] > 0 else ""
                    
                    st.markdown(f"""
                        <div class="node-card {is_goal}">
                            {parent_line}
                            <div class="node-id">Node {node['id']} (P:{node['parent']})</div>
                            <div class="node-content">{node['label'].replace('\n', '<br>')}</div>
                        </div>
                    """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)True)
