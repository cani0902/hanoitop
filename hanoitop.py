import streamlit as st
import collections
import heapq
import time

# --- 1. 문제의 상태 정의 및 작업 (Action) ---
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

def state_to_str(state):
    return f"A{list(state[0])} | B{list(state[1])} | C{list(state[2])}"

# --- 2. 탐색 전략 알고리즘 (자료구조 적용) ---
def run_search(start, goal, algo_type, max_nodes=15):
    nodes = [] # 트리 시각화용 데이터
    visited = {start}
    
    # [상태, 부모ID, 깊이, 가중치]
    if algo_type == "BFS (Queue)":
        container = collections.deque([(start, -1, 0)])
    elif algo_type == "DFS (Stack)":
        container = [(start, -1, 0)]
    else: # Best-First, A* (Priority Queue)
        container = []
        heapq.heappush(container, (get_h(start, goal), 0, start, -1, 0))

    count = 0
    while container and count < max_nodes:
        # 자료구조별 추출 방식 (LIFO vs FIFO vs Priority)
        if algo_type == "BFS (Queue)": 
            curr, parent, d = container.popleft()
        elif algo_type == "DFS (Stack)": 
            curr, parent, d = container.pop()
        elif algo_type == "Best-First": 
            _, _, curr, parent, d = heapq.heappop(container)
        elif algo_type == "A*": 
            f, g, curr, parent, d = heapq.heappop(container)

        node_id = count
        nodes.append({"id": node_id, "label": state_to_str(curr), "parent": parent, "depth": d, "state": curr})
        if curr == goal: break
        
        count += 1
        for i in range(3):
            for j in range(3):
                if i != j and is_valid_move(curr, i, j):
                    nxt = make_move(curr, i, j)
                    if nxt not in visited:
                        visited.add(nxt)
                        if algo_type == "BFS (Queue)": container.append((nxt, node_id, d+1))
                        elif algo_type == "DFS (Stack)": container.append((nxt, node_id, d+1))
                        elif algo_type == "Best-First": heapq.heappush(container, (get_h(nxt, goal), count, nxt, node_id, d+1))
                        elif algo_type == "A*": 
                            g_new = d + 1
                            heapq.heappush(container, (g_new + get_h(nxt, goal), count, nxt, node_id, d+1))
    return nodes

# --- 3. 웹 UI 레이아웃 (교과서 스타일 반영) ---
st.set_page_config(page_title="KISH Hanoi Lab", layout="wide")

# CSS로 트리 카드 디자인
st.markdown("""
    <style>
    .tree-node {
        border: 2px solid #4A90E2; border-radius: 10px; padding: 10px;
        background: white; margin: 10px; min-width: 180px; text-align: center;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }
    .goal-node { border-color: #4CAF50; background-color: #E8F5E9; }
    .node-info { font-size: 11px; color: #666; border-bottom: 1px solid #eee; margin-bottom: 5px; }
    </style>
""", unsafe_allow_html=True)

st.title("🌲 하노이의 탑 상태 공간 트리 시각화")
st.info("교과서의 '문제 해결을 위한 탐색 과정'을 시뮬레이션합니다.")

with st.sidebar:
    st.header("📋 탐색 전략 설정")
    algo = st.selectbox("알고리즘(자료구조) 선택", 
                        ["BFS (Queue)", "DFS (Stack)", "Best-First", "A*"])
    disks = st.slider("원반 개수", 2, 4, 3)
    max_view = st.number_input("표시할 최대 노드 수", 5, 30, 12)

# 초기/목표 상태 설정
initial = (tuple(range(disks, 0, -1)), (), ())
target = ((), (), tuple(range(disks, 0, -1)))

if st.button("▶ 탐색 및 트리 생성 실행"):
    with st.spinner("상태 공간 트리 구축 중..."):
        tree_data = run_search(initial, target, algo, max_view)
        
        # 깊이(Depth)별 렌더링
        depths = collections.defaultdict(list)
        for n in tree_data: depths[n['depth']].append(n)
        
        for d in sorted(depths.keys()):
            cols = st.columns(len(depths[d]) + 2)
            for idx, node in enumerate(depths[d]):
                with cols[idx+1]:
                    is_goal = "goal-node" if node['state'] == target else ""
                    st.markdown(f"""
                        <div class="tree-node {is_goal}">
                            <div class="node-info">ID: {node['id']} | Parent: {node['parent']}</div>
                            <div style="font-weight: bold;">{node['label']}</div>
                        </div>
                    """, unsafe_allow_html=True)
            st.write("---")
    st.success(f"{algo} 전략으로 탐색 완료!")

st.markdown("### 📝 학습지 작성 가이드")
st.write(f"- **현재 전략:** {algo}")
st.write(f"- **데이터 구조:** {'LIFO (Stack)' if 'DFS' in algo else 'FIFO (Queue)' if 'BFS' in algo else 'Priority Queue'}")
st.write("- **관찰 포인트:** 노드 ID의 생성 순서를 보며 알고리즘이 트리를 '어느 방향'으로 확장하는지 비교하세요.")
