import streamlit as st
import heapq
import networkx as nx
from pyvis.network import Network
import streamlit.components.v1 as components

# --- Page Configuration ---
st.set_page_config(page_title="Blantyre Smart Route Optimizer", layout="wide", initial_sidebar_state="expanded")

# --- Custom CSS for Styling ---
st.markdown("""
    <style>
    .main-header { font-size: 40px; color: #2E8B57; font-weight: bold; text-align: center; margin-bottom: 0px;}
    .sub-header { font-size: 18px; color: #555; text-align: center; margin-bottom: 30px;}
    .result-box { padding: 20px; background-color: #f0f8ff; border-radius: 10px; border-left: 5px solid #2E8B57; margin-top: 20px;}
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header"> Blantyre Smart Route Optimizer</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Dijkstra\'s Algorithm Implementation</div>', unsafe_allow_html=True)

# --- Graph Data ---

graph = {
    "Lunzu": {"Chileka": 7, "Kameza": 9, "Blantyre town": 12},
    "Chileka": {"Lunzu": 7, "Baluti": 2},
    "Baluti": {"Chileka": 2, "Nancholi": 12},
    "Kameza": {"Lunzu": 9, "Blantyre town": 6, "Ndirande": 9},
    "Blantyre town": {"Lunzu": 12, "Kameza": 6, "Nancholi": 6, "Mandala": 10, "Nyambadwe": 8},
    "Nancholi": {"Baluti": 12, "Blantyre town": 6, "Naperi": 12, "Mpemba": 9},
    "Mpemba": {"Nancholi": 9, "Chilobwe": 9},
    "Naperi": {"Nancholi": 12, "Mandala": 6, "Chitawira": 2, "Chilobwe": 7, "Zingwangwa": 0.6},
    "Mandala": {"Blantyre town": 10, "Naperi": 6, "Nyambadwe": 6},
    "Nyambadwe": {"Blantyre town": 8, "Mandala": 6, "Ndirande": 6},
    "Ndirande": {"Kameza": 9, "Nyambadwe": 6, "Chichiri": 7, "Machinjiri": 16},
    "Chilobwe": {"Mpemba": 9, "Naperi": 7, "Soche": 0.5},
    "Zingwangwa": {"Naperi": 0.6, "Chitawira": 2, "Soche": 0.5},
    "Chitawira": {"Naperi": 2, "Zingwangwa": 2, "Chichiri": 2, "Nkolokosa": 0.5, "Chinyonga": 2},
    "Chichiri": {"Ndirande": 7, "Chitawira": 2, "Machinjiri": 2, "Chinyonga": 2},
    "Machinjiri": {"Ndirande": 16, "Chichiri": 2, "Bangwe": 16},
    "Chinyonga": {"Chitawira": 2, "Chichiri": 2, "Nkolokosa": 3, "Bangwe": 4, "Limbe": 3},
    "Nkolokosa": {"Chitawira": 0.5, "Chinyonga": 3, "Soche": 0.5, "Limbe": 2},
    "Soche": {"Chilobwe": 0.5, "Zingwangwa": 0.5, "Nkolokosa": 0.5, "Limbe": 2},
    "Bangwe": {"Machinjiri": 16, "Chinyonga": 4, "Limbe": 3},
    "Limbe": {"Soche": 2, "Nkolokosa": 2, "Chinyonga": 3, "Bangwe": 3}
}


# --- Dijkstra Algorithm ---
def run_dijkstra(graph, start, end):
    distances = {node: float('infinity') for node in graph}
    distances[start] = 0
    previous_nodes = {node: None for node in graph}
    pq = [(0, start)]
    
    while pq:
        current_distance, current_node = heapq.heappop(pq)
        if current_node == end: break
        if current_distance > distances[current_node]: continue
        
        for neighbor, weight in graph[current_node].items():
            distance = current_distance + weight
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                previous_nodes[neighbor] = current_node
                heapq.heappush(pq, (distance, neighbor))
                
    path = []
    current = end
    while current is not None:
        path.append(current)
        current = previous_nodes[current]
    path.reverse()
    
    return path, distances[end]

# --- Sidebar UI ---
with st.sidebar:
    
    try:
        st.image("malawi_map.png", width=200)
    except:
        st.info("Add 'malawi_map.png' to your folder to see the map here.")
        
    st.header("Route Input")
    
    nodes = list(graph.keys())
    start_node = st.selectbox(" Select Starting Location", nodes, index=nodes.index("Lunzu"))
    end_node = st.selectbox(" Select Destination", nodes, index=nodes.index("Limbe"))
    
    st.markdown("<br>", unsafe_allow_html=True)
    find_route_btn = st.button(" Find Best Route", use_container_width=True, type="primary")
    
    st.markdown("---")
    st.write("**Note:** The interactive map on the right shows the road network. Drag nodes to rearrange them!")

# --- Main App Logic ---
if find_route_btn:
    if start_node == end_node:
        st.warning(" Start and End locations cannot be the same!")
    else:
        # Run algorithm
        path, total_distance = run_dijkstra(graph, start_node, end_node)
        
        # Display Results Box
        st.markdown(f"""
            <div class="result-box">
                <h3> Prediction Result</h3>
                <p><b>Shortest Route:</b> {' ➔ '.join(path)}</p>
                <p><b>Total Distance:</b> {total_distance} km</p>
            </div>
        """, unsafe_allow_html=True)
        
        # --- Generate PyVis Interactive Graph ---
        G = nx.Graph()
        for u, adj in graph.items():
            for v, w in adj.items():
                G.add_edge(u, v, weight=w)

        net = Network(height="600px", width="100%", bgcolor="#ffffff", font_color="black", directed=False)
        
        # Prepare the path for easy checking (making sure we check both directions)
        path_edges = list(zip(path, path[1:]))
        normalized_path_edges = set()
        for u, v in path_edges:
            normalized_path_edges.add(tuple(sorted((u, v))))
            
        # Add nodes (Teal by default, Orange-Red if on the path)
        for node in G.nodes():
            if node in path:
                net.add_node(node, label=node, color="#FF4500", size=30) # Highlighted node
            else:
                net.add_node(node, label=node, color="#20B2AA", size=20, font={'size': 200, 'face': 'arial'})
                
        # Add edges (Grey by default, Red if on the path)
        for u, v, data in G.edges(data=True):
            edge_tuple = tuple(sorted((u, v)))
            if edge_tuple in normalized_path_edges:
                # This is a path edge! Make it red and thick
                net.add_edge(u, v, title=str(data['weight']), color="#FF0000", width=5)
            else:
                # Normal edge
                net.add_edge(u, v, title=str(data['weight']), color="#a0a0a0", width=1)

        net.repulsion(node_distance=150, central_gravity=0.2, spring_length=200)
        
        st.subheader("Interactive Network Map")
        st.write("The highlighted red path shows the shortest route.")
        components.html(net.generate_html(), height=600)

else:
    st.info(" Select your start and end locations in the sidebar and click **Find Best Route**.")
