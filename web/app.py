from flask import Flask, render_template, jsonify
import osmnx as ox
import networkx as nx
from shapely.wkt import loads

app = Flask(__name__)

def wkt_to_list(wkt_string):
    linestring = loads(wkt_string)
    coords = list(linestring.coords)
    return [[x, y] for x, y in coords]

@app.route('/')
def index():
  return render_template('index.html')

@app.route('/get_network_latlons')
def get_network_latlons():
  G = ox.graph_from_point((40.631475,-111.518367), 2000, network_type='bike')
  gdf_nodes, gdf_edges = ox.graph_to_gdfs(G)

  node_latlngs = gdf_nodes.reset_index()[['y', 'x']].values.tolist()

  edge_latlngs = list()
  for wkt_str in gdf_edges.reset_index()['geometry'].values.tolist():
    # edge_latlngs.append([pair[::-1] for pair in wkt_to_list(str(wkt_str))])
    edge_latlngs.append([pair for pair in wkt_to_list(str(wkt_str))])

      
  network_latlons_json = jsonify({'nodes': node_latlngs, 'edges': edge_latlngs})
  return network_latlons_json

if __name__ == '__main__':
    app.run(host="localhost", port=3000, debug=True)