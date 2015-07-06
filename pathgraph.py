#!/usr/bin/python2
'''
Simple tool that draws directory graph from selected root.
Requires only graph_tool
'''
import sys
import os
from os.path import join, getsize

from graph_tool.all import *

class memoize:
    def __init__(self, function):
        self.function = function
        self.memoized = {}

    def __call__(self, *args):
        try:
            return self.memoized[args]
        except KeyError:
            self.memoized[args] = self.function(*args)
            return self.memoized[args]

@memoize
def getFolderSize(path):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
        for d in dirnames:
            dp = os.path.join(dirpath, d)
            total_size += getFolderSize(dp)
    return total_size

if __name__ == "__main__":
    if len(sys.argv) != 5 or sys.argv[1] == '-h':
        print "Usage pathgraph.py DIR_PATH OUT_PATH SIZE_X SIZE_Y"
        print "Example: pathgraph.py /home /home/out.png 1920 1080"
        sys.exit()
    
    root_path = sys.argv[1]
    out_path = sys.argv[2]
    out_w = int(sys.argv[3])
    out_h = int(sys.argv[4])
    
    out_s = out_w * out_h
    g = Graph(directed = True)
    v_paths = g.new_vertex_property('string')
    g.vertex_properties["path"] = v_paths
    v_sizes = g.new_vertex_property('int')
    g.vertex_properties["size"] = v_sizes
    v_font_sizes = g.new_vertex_property('int')
    g.vertex_properties["font size"] = v_font_sizes
    v_root = g.add_vertex()
    v_paths[v_root] = "root" # root_path
    v_desc = {} # Contain pairs path -> vertex sedcriptor
    v_desc[root_path] = v_root
    root_size = getFolderSize(root_path)
    for root, dirs, files in os.walk(root_path):
        v_sizes[v_desc[root]] = max(int(out_s**0.5 * getFolderSize(root) 
            / (float(root_size) * 14)), out_s **0.5/ 200)
        v_font_sizes[v_desc[root]] = max(int(out_s**0.5 * getFolderSize(root) 
            / (float(root_size) * 8)) / len(root)**0.5, out_s **0.5/ 160)
        for i in dirs:
            parent = join(root,i) # path to folder
            v_parent = g.add_vertex()
            v_paths[v_parent] = i
            v_desc[parent] = v_parent
            g.add_edge(v_desc[root], v_desc[parent])

    graph_draw(g, pos=sfdp_layout(g, vweight=v_sizes), 
    output=out_path,output_size=(out_w, out_h), vertex_text=v_paths,
    vertex_size=v_sizes, vertex_font_size=v_font_sizes)
