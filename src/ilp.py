import os
import itertools
from argparse import ArgumentParser
from docplex.mp.model import Model

from utils import read_instance

def create_model_new1(graph, print_info):
    model = Model(name='new1')
    num_nodes = len(graph.nodes)
    x = model.binary_var_list(num_nodes, name='x')
    num_edges = len(graph.edges)
    z = model.binary_var_list(2 * num_edges, name='z')

    ij_to_arc_id = {(i,j): arc_id for arc_id, (i,j) in enumerate(graph.edges)}
    k = 0
    for (i,j), _ in list(ij_to_arc_id.items()):
        ij_to_arc_id[j,i] = num_edges + k
        k += 1

    for (i,j) in graph.edges:
        model.add_constraint(x[i] + x[j] <= 1) # 1

    for i in graph.nodes:
        model.add_constraint(x[i] + sum(x[j] for j in graph[i]) >= 1) # 2 TODO da li je ovo potrebno?

        model.add_constraint(x[i] + sum(z[ij_to_arc_id[j,i]] for j in graph[i]) == 1) # 3
        
    for (i,j), arc_id in ij_to_arc_id.items():
        model.add_constraint(z[arc_id] <= x[i]) # 4


    nodes_cost = sum(x[i] * w['weight'] for i, w in graph.nodes(data=True))
    external_edges_cost = sum(z[arc_id] * graph[i][j]['weight'] for (i, j), arc_id in ij_to_arc_id.items())

    model.minimize(nodes_cost + external_edges_cost)

    if print_info:
        model.print_information()

    return model

def create_model_new2(graph, print_info):
    model = Model(name='new2')
    num_nodes = len(graph.nodes)
    x = model.binary_var_list(num_nodes, name='x')
    q = model.continuous_var_list(num_nodes, name='q', lb=0)

    for (i,j) in graph.edges:
        model.add_constraint(x[i] + x[j] <= 1) # 1

    for i in graph.nodes:
        model.add_constraint(x[i] + sum(x[j] for j in graph[i]) >= 1) # 2

        sorted_adjacent_nodes = [x[0] for x in sorted(graph[i].items(), key=lambda x: x[1]['weight'])]
        for idx, k in enumerate(sorted_adjacent_nodes):
            xl_sum = sum((graph[k][i]['weight'] - graph[l][i]['weight']) * x[l] for l in itertools.islice(sorted_adjacent_nodes, idx))
            model.add_constraint(q[i] >= graph[k][i]['weight'] - xl_sum - graph[k][i]['weight']*x[i]) # 3

    total_cost = sum(x[i] * w['weight'] + q[i] for i, w in graph.nodes(data=True))

    model.minimize(total_cost)

    if print_info:
        model.print_information()

    return model

def create_model(model_name, g, print_info):
    if model_name == 'new1':
        return create_model_new1(g, print_info)
    elif model_name == 'new2':
        return create_model_new2(g, print_info)
    else:
        return None

def solve(model_name, g, print_info, memory_limit=4096, time_limit=None, return_solution=False):
    if time_limit is None:
        time_limit = 3 * len(g.nodes)

    model = create_model(model_name, g, print_info)
    model.set_time_limit(time_limit)
    model.context.cplex_parameters.workmem = memory_limit
    model.context.cplex_parameters.threads = 1
    model.context.cplex_parameters.mip.limits.treememory = memory_limit

    solution = model.solve()
    if return_solution:
        values = solution.get_values([model.get_var_by_name(f'x_{i}') for i in range(len(g.nodes))])
        model.end()
        return [i for i, x in enumerate(values) if x == 1]
    time = model.solve_details.time
    
    status = model.solve_details.status
    gap = model.solve_details.gap
    num_nodes_processed = model.solve_details.nb_nodes_processed
    model.end()
    return status, time, solution.get_objective_value(), gap, num_nodes_processed

def solve_all(in_dir_path, model_name, instances_subset, out_dir_path, print_info):
    in_dir_path = os.path.abspath(in_dir_path)

    out_file_name = f'{model_name}_{instances_subset}.csv'
    out_file_path = os.path.join(out_dir_path, out_file_name)
    with open(out_file_path, 'w') as f:
        f.write('status, time, cost, gap, num_nodes_processed\n')
        for i, file_name in enumerate(sorted(os.listdir(in_dir_path))):
            if file_name.startswith(instances_subset):
                print(i, file_name)
                file_path = os.path.join(in_dir_path, file_name)
                g = read_instance(file_path)
                status, time, cost, gap, num_nodes = solve(model_name, g, print_info)
                status = status.replace(',', '-')
                f.write(f'{status}, {time}, {cost}, {gap}, {num_nodes}\n')

def main():
    parser = ArgumentParser()
    parser.add_argument('-m', '--model_name', type=str, choices=['new1', 'new2'], help='Name of the ILP model to use')
    parser.add_argument('-i', '--in_dir_path', type=str, help='Path to the folder containing the instances')
    parser.add_argument('-s', '--instances_subset', type=str, default='', help='Optional filename substring defining subset of instances, e.g. 100_r014')
    parser.add_argument('-o', '--out_dir_path', type=str, help='Path to the folder to write results to')
    parser.add_argument('-v', '--verbose', action='store_true', default=True, help='Verbose output')
    args = parser.parse_args()

    solve_all(
        model_name=args.model_name,
        in_dir_path=args.in_dir_path,
        instances_subset=args.instances_subset,
        out_dir_path=args.out_dir_path,
        print_info=args.verbose,
    )

if __name__ == '__main__':
    main()