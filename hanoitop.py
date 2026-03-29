import streamlit as st
import collections
import heapq
import time

# --- 1. 하노이 로직 및 상태 정의 ---
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
    return f"{list(state[0])}\n{list(state[1])}\n{list(state[2])}"

# --- 2. 4대 알고리즘 탐색 엔진 ---
def run_full_search(start, goal, algo_type):
    nodes = []
    visited = {start}
    path_found = False
    
    # [상태, 부모ID, 깊이, 추가지표]
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
        # 알고리즘별 자료구조 추출 (Queue, Stack, Priority Queue)
        if algo_type == "너비 우선 탐색 (BFS)":
            curr, parent, d = container.popleft()
        elif algo_type == "깊이 우선 탐색 (DFS)":
            curr, parent, d = container.pop()
        elif algo_type == "최상 우선 탐색 (Best-First)":
            _, _, curr, parent, d = heapq.heappop(container)
        elif algo_type == "A* 알고리즘":
            f, g, curr, parent, d = heapq.heappop(container)

        node_id = count
        nodes.append({"id": node_id, "label": state_to_label(curr), "parent": parent, "depth": d, "state": curr})
        
        if curr == goal:
            path_found = True
            break
        
        count += 1
        # 원반 4개는 상태 공간이 매우 넓으므로 안전을 위해 탐색 순서 최적화
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
                            
    return nodes, path_found

# --- 3. UI 레이아웃 및 시각화 ---
st.set_page_config(page_title="KISH Hanoi State Space", layout="wide")

st.markdown("""
    <style>
    .tree-node {
        border: 1px solid #333; border-radius: 5px; padding: 8px;
        background: #ffffff; margin: 5px; min-width: 120px; text-align: center;
        font-family: 'Courier New', Courier, monospace; font-size: 11px;
    }
    .goal-node { border: 3px solid #2ecc71; background-color: #e8f8f5; }
    .depth-row { display: flex; justify-content: center; border-bottom: 1px dashed #ccc; padding: 10px 0; }
    </style>
""", unsafe_allow_html=True)

# 사이드바 설정 (원반 4개 고정)
with st.sidebar:
    st.title("🛡️ 탐색 전략 선택")
    algo = st.radio("실행할 알고리즘을 고르세요", 
                    ["너비 우선 탐색 (BFS)", "깊이 우선 탐색 (DFS)", "최상 우선 탐색 (Best-First)", "A* 알고리즘"])
    st.write("---")
    st.write("**조건:** 원반 4개, 기둥 3개")

st.header(f"🌳 {algo} : 전체 상태 공간 트리")
st.write("초기 상태(모든 원반 A)에서 목표 상태(모든 원반 C)까지의 모든 탐색 과정을 시각화합니다.")

# 고정 설정
disks = 4
initial = (tuple(range(disks, 0, -1)), (), ())
target = ((), (), tuple(range(disks, 0, -1)))

if st.button("▶ 탐색 프로세스 시작"):
    with st.spinner("목표 상태를 찾을 때까지 모든 노드를 생성 중입니다..."):
        start_time = time.time()
        tree_data, found = run_full_search(initial, target, algo)
        end_time = time.time()
        
        # 깊이별 정렬
        depth_groups = collections.defaultdict(list)
        for n in tree_data:
            depth_groups[n['depth']].append(n)
            
        st.success(f"탐색 성공! (소요 시간: {end_time - start_time:.2f}초)")
        st.metric("생성된 총 노드 수", f"{len(tree_data)}개")

        # 트리 렌더링
        for d in sorted(depth_groups.keys()):
            st.markdown(f"<div class='depth-row'>", unsafe_allow_html=True)
            cols = st.columns(len(depth_groups[d]) + 2)
            for idx, node in enumerate(depth_groups[d]):
                with cols[idx+1]:
                    is_goal = "goal-node" if node['state'] == target else ""
                    st.markdown(f"""
                        <div class="tree-node {is_goal}">
                            <small>ID:{node['id']} (P:{node['parent']})</small><br>
                            <strong>{node['label'].replace('|', '<br>')}</strong>
                        </div>
                    """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
