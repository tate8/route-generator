import numpy as np
import networkx as nx
import osmnx as ox
from typing import NamedTuple
import random
import torch_geometric
import torch
import requests
import copy


class NetworkDatasetFactory:  
    class BoundingBox(NamedTuple):
        north: float # lat
        east: float # lng
        south: float # lat
        west: float # lng
            
    @property
    def bbox_areas(self):
        wasatch = self.BoundingBox(40.871006, -111.441968, 40.445959, -111.977901) # big
        pcmr = self.BoundingBox(40.710475, -111.440984,40.571173,-111.616881) # medium
        bentonville = self.BoundingBox(36.5041, -94.0979, 36.2675, -94.3609) # medium
        fayettville = self.BoundingBox(36.0698, -94.1638, 36.0177, -94.2285) # small-medium
        sedona = self.BoundingBox(34.882, -111.7516, 34.8051, -111.8889) # medium
        upper_sedona = self.BoundingBox(34.9067, -111.8121, 34.8597, -111.8643) # small
        lower_sedona = self.BoundingBox(34.8547,-111.7862, 34.8288,-111.8328) # small
        hog_sedona = self.BoundingBox(34.848, -111.7441, 34.8244, -111.7738) # small
        round_valley = self.BoundingBox(40.7187, -111.4548, 40.6715, -111.514) # small
        pine_canyon = self.BoundingBox(40.5702, -111.4239, 40.5235, -111.5198) # small-medium
        corner_canyon = self.BoundingBox(40.5148, -111.7358, 40.4229, -111.917) # medium
        milcreek_and_right = self.BoundingBox(40.7618, -111.5208, 40.6397, -111.7862) # medium
        moab_upper = self.BoundingBox(38.7637,-109.5921, 38.5315,-109.8544) # medium
        slickrock_area = self.BoundingBox(38.6170,-109.4762, 38.5757,-109.5593) # medium
        st_george = self.BoundingBox(37.1631,-113.5372, 37.0587,-113.7003) # large
        sun_valley = self.BoundingBox(43.7577,-114.2647, 43.6072, -114.4872) # large
        bbox_areas = [wasatch, pcmr, bentonville, fayettville, sedona, 
                      upper_sedona, lower_sedona, hog_sedona, round_valley, 
                      pine_canyon, corner_canyon, milcreek_and_right, moab_upper, 
                      slickrock_area, st_george, sun_valley]
        return bbox_areas
    
    def random_bbox_within_bounding(self, bounding):
        bounding_width = bounding.east - bounding.west
        bounding_height = bounding.north - bounding.south

        one_mile_latlng = 1/60
        min_width = one_mile_latlng
        width = random.uniform(min_width, bounding_width)

        min_height = one_mile_latlng
        height = random.uniform(min_height, bounding_height)


        # choose where the width and heights starts (we have a rectangle, 
        # we need to choose where it fits within the bigger rectangle)
        random_south = random.uniform(bounding.south, bounding.north-height)
        random_north = random_south + height
        random_west = random.uniform(bounding.west, bounding.east-width)
        random_east = random_west + width

        return self.BoundingBox(random_north, random_east, random_south, random_west)
    
    
    def cleanup_graph(self, G):
        for edge in G.edges:
            edge_data = G.edges[edge]
            if 'name' not in edge_data.keys():
                G.edges[edge]['name'] = 'Unknown'
            if 'highway' not in edge_data.keys():
                G.edges[edge]['highway'] = 'Unknown'
            if 'surface' not in edge_data.keys():
                G.edges[edge]['surface'] = 'Unknown'

    def cleanup_merged_edges(self, G):
        for edge in G.edges:
            edge_data = G.edges[edge]
            if isinstance(edge_data['name'], list):
                name = ' & '.join(edge_data['name'])
                G.edges[edge]['name'] = name
            if isinstance(edge_data['highway'], list):
                highway = edge_data['highway'][0]
                G.edges[edge]['highway'] = highway
            if isinstance(edge_data['surface'], list):
                surface = edge_data['surface'][0]
                G.edges[edge]['surface'] = surface
    
    def add_node_elevations(self, G):
        latlongs = []
        for node in G.nodes(data=True):
            latlongs.append(f'{node[1]["y"]},{node[1]["x"]}')
        body = {
            'locations': '|'.join(latlongs),
        }

        url = 'http://localhost:5001/v1/srtm30m_geotiff'
        response = requests.post(url, json=body).json()

        if 'error' in response:
            raise Exception(f'API Error: {response.error}')

        elevations = []
        for result in response['results']:
            elevation = result['elevation']
            elevations.append(elevation)

        for node, elevation in zip(G.nodes, elevations):
            G.nodes[node]['elevation'] = elevation

    def add_edge_surface_types(self, G):
        for edge in G.edges:
            edge_data = G.edges[edge]

            surface_type = None
            s = edge_data['surface'].lower()
            h = edge_data['highway'].lower()
            if  h=='path' or s=='rock' or s=='ground' or s=='dirt' or s=='earth' or s=='grass' or s=='mud' or s=='sand':
                surface_type = 2
            elif h=='track' or s=='gravel' or s=='unhewn_cobblestone' or s=='cobblestone' or s=='wood' or s=='unpaved' or s=='compacted' or s=='fine_gravel' or s=='gravel':
                surface_type = 1
            elif (h!='path' and h!='track') or s=='paved' or s=='asphalt' or s=='chipseal' or s=='concrete' or s=='paving_stones' or s=='sett':
                surface_type = 0
            else:
                print(f'Unknown Surface Type: {s=}, {h=}')

            G.edges[edge]['surface_type'] = surface_type
            G.edges[edge]['is_not_motor_road'] = int(h == 'path' or h == 'track')
            
    def convert_all_grades_to_percent_grades(self, G):
        for edge in G.edges:
            edge_data = G.edges[edge]
            grade = edge_data['grade']
            grade_abs = edge_data['grade_abs']

            G.edges[edge]['grade'] = grade * 100
            G.edges[edge]['grade_abs'] = grade_abs * 100

    
    def add_node_attributes(self, G):
        new_attrs = {
            'is_start_node': 0,
            'is_end_node': 0,
            'is_in_route': 0,
            'is_current_node': 0
        }
        G.add_nodes_from(G.nodes, **new_attrs)
        
    def cleanup_node_attributes(self, G):
        attrs_to_keep = ['is_start_node', 'is_end_node', 'is_in_route', 'is_current_node']
        
        for node in G.nodes:
            node_data = G.nodes[node]

            to_delete = []
            for attr, value in node_data.items():
                if attr not in attrs_to_keep:
                    to_delete.append(attr)
            for attr in to_delete:
                del G.nodes[node][attr]

    def cleanup_edge_attributes(self, G):
        attrs_to_keep = ['length', 'surface_type', 'grade_abs']
        for edge in G.edges:
            edge_data = G.edges[edge]

            to_delete = []
            for attr, value in edge_data.items():
                if attr not in attrs_to_keep:
                    to_delete.append(attr)
            for attr in to_delete:
                del G.edges[edge][attr]

    def choose_random_start_and_end_nodes(self, G):
        num_nodes = len(G.nodes)
        start = np.random.randint(0, num_nodes)
        end = np.random.randint(0, num_nodes)
        while end == start:
            end = np.random.randint(0, num_nodes)

        G.nodes[list(G.nodes)[start]]['is_start_node'] = 1
        G.nodes[list(G.nodes)[start]]['is_current_node'] = 1
        G.nodes[list(G.nodes)[start]]['is_in_route'] = 1
        G.nodes[list(G.nodes)[end]]['is_end_node'] = 1
    
    def get_random_pyg_graph(self):
        bounding = random.choice(self.bbox_areas)
        bbox = self.random_bbox_within_bounding(bounding)
        ox.settings.useful_tags_way = ['highway', 'surface', 'name']
        custom_filter = '["highway"]["area"!~"yes"]\
                        ["highway"!~"service|abandoned|bus_guideway\
                         |construction|corridor|elevator|escalator|\
                         footway|motor|no|planned|platform|proposed|raceway|razed|steps"]\
                        ["bicycle"!~"no"]["service"!~"private"]["informal"!~"yes"]["access"!="private"]'
        G = ox.graph_from_bbox(bbox.north, bbox.south, bbox.east, bbox.west, custom_filter=custom_filter)
        
        # processing
        self.cleanup_graph(G)
        self.cleanup_merged_edges(G)
        self.add_node_elevations(G)
        ox.add_edge_grades(G)
        self.convert_all_grades_to_percent_grades(G)
        self.add_edge_surface_types(G)
        self.add_node_attributes(G)
        self.choose_random_start_and_end_nodes(G)
        r_g = copy.deepcopy(G)
        
        self.cleanup_node_attributes(G)
        self.cleanup_edge_attributes(G)
        pyg_graph = torch_geometric.utils.convert.from_networkx(G, 
                                group_node_attrs=['is_start_node', 'is_end_node', 'is_in_route', 'is_current_node'],
                                group_edge_attrs=['length', 'surface_type', 'grade_abs'])
        length_index = 0
        graph_length = sum(pyg_graph.edge_attr[:, length_index])
        
        user_preferences = {
            'overall_distance': np.random.uniform(0, graph_length),
            'steepnesss': np.random.randint(0, 100),
            'surface_roughness': np.random.randint(0, 100),
        }
        pyg_graph.y = torch.tensor(list(user_preferences.values()))
        return r_g, pyg_graph