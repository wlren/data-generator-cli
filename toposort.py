from collections import defaultdict, deque

def topological_sort(schema):
    dependency_graph = defaultdict(list)  # Adjacency list for the graph
    in_degree = defaultdict(int)  # Keeps track of the number of incoming edges

    # Initialize in_degree for all tables to 0
    for table in schema['tables']:
        in_degree[table['tableName']] = 0

    # Fill the graph and update in_degrees based on foreign key dependencies
    for table in schema['tables']:
        if 'foreign_key' in table:
            for fk in table['foreign_key']:
                dependent_table = table['tableName']
                base_table = fk['tableName']
                dependency_graph[base_table].append(dependent_table)
                in_degree[dependent_table] += 1

    # Topological sort using Kahn's algorithm
    order = []  # List to store the order of tables
    q = deque()  # Queue to manage the tables with no incoming edge

    # Enqueue tables with no incoming edge
    for table, degree in in_degree.items():
        if degree == 0:
            q.append(table)

    while q:
        table = q.popleft()
        order.append(table)
        for dependent in dependency_graph[table]:
            in_degree[dependent] -= 1  # Remove edge
            if in_degree[dependent] == 0:
                q.append(dependent)

    print("Topological Order: " , order)
    
    return order
