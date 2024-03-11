from argparse import ArgumentParser
import os
from time import perf_counter

from utils import *

# v should have small weight
# its uncovered neighbors u large weight
# small edge weight between u and v
# large edge weight between u and other u's neighbors
def greedy_newer_active(g):
    start_time = perf_counter()
    
    s = set()
    g_copy = g.copy()

    # for every node v - sum of edge weights beteen v and v's neighbors
    edge_weights = [0 for _ in g.nodes]
    for u in g_copy.nodes: # changing - we want to calculate only the uncovered nodes
        for v in g_copy[u]:
            edge_weights[u] += g[u][v]['weight']

    while len(g_copy.nodes) != 0:
        v_star = None
        max_val = -1
        for v in g_copy.nodes:
            uv_edge_weights = 0
            other_edge_weights = 0
            node_weights = 0
            for u in g_copy[v]:
                node_weights += g_copy.nodes(data=True)[u]['weight']
                uv_edge_weights += g_copy[u][v]['weight']
                other_edge_weights += edge_weights[u] - g_copy[u][v]['weight']
            should_be_large = node_weights + other_edge_weights
            should_be_small = g_copy.nodes(data=True)[v]['weight'] + uv_edge_weights
            val = should_be_large / should_be_small
            if val > max_val:
                max_val = val
                v_star = v
        s.add(v_star)
        neighbors = set(g_copy[v_star])
        for v in neighbors:
            for u in g_copy[v]:
                edge_weights[u] -= g_copy[v][u]['weight']
            g_copy.remove_node(v)
        for u in g_copy[v_star]:
            edge_weights[u] -= g_copy[v_star][u]['weight']
        g_copy.remove_node(v_star)

    num_incorrect, cost, _, _ = calc_initial_solution_cost(s, g)
    
    time_elapsed = perf_counter() - start_time
    
    return s, num_incorrect, cost, time_elapsed

def solve_all_greedy(in_dir_path, instances_subset, out_dir_path):
    out_file_name = f'{instances_subset}_greedy_results.csv'
    out_file_path = os.path.join(out_dir_path, out_file_name)
    with open(out_file_path, 'w') as f:
        for i, file_name in enumerate(sorted(os.listdir(in_dir_path))):
            if file_name.startswith(instances_subset):
                file_path = os.path.join(in_dir_path, file_name)
                g = read_instance(file_path)
                _, num_incorrect_nodes, cost, time_elapsed = greedy_newer_active(g)
                f.write(f'{file_name}, {num_incorrect_nodes}, {cost}, {time_elapsed}\n')

def main():
    parser = ArgumentParser()
    parser.add_argument('-i', '--in_dir_path', type=str, help='Path to the folder containing the instances')
    parser.add_argument('-s', '--instances_subset', type=str, help='Filename substring defining subset of instances, e.g. 100_r014')
    parser.add_argument('-o', '--out_dir_path', type=str, help='Path to the folder to write results to')
    args = parser.parse_args()

    solve_all_greedy(
        in_dir_path=args.in_dir_path,
        instances_subset=args.instances_subset,
        out_dir_path=args.out_dir_path,
    )

if __name__ == '__main__':
    main()