import pickle

from factorio_scrapper import Item, Row, ItemFromFactorioIcon, Recipe

# with open('factorio.pkl', 'rb') as f:
#     visited_link, items = pickle.load(f)
with open('factorio.pkl', 'rb') as f:
    visited_link, items = pickle.load(f)




#%%

all_recipes = set([item['Recipe'] for k, item in items.items() if 'Recipe' in item.values])
all_req_tech = [(item['Required technologies'], item) for k, item in items.items() if 'Required technologies' in item.values]
all_prod_by = [(item['Produced by'], item) for k, item in items.items() if 'Produced by' in item.values]


LI = ItemFromFactorioIcon.from_values

# manually add recipe

extra_recipes = [
    Recipe.from_values([LI('Heavy oil', 20), LI('Time', 20)],
                       [LI('Solid fuel', 1)]),
    Recipe.from_values([LI('Light oil', 10), LI('Time', 20)],
                       [LI('Solid fuel', 1)]),
    Recipe.from_values([LI('Petroleum gas', 20), LI('Time', 20)],
                       [LI('Solid fuel', 1)]),
    Recipe.from_values([LI('Crude oil', 100), LI('Water', 50), LI('Time', 5)],
                       [LI('Petroleum gas', 55), LI('Heavy oil',25), LI('Light oil', 45)]),
]

all_recipes.update(extra_recipes)


#%%

from graphviz import Digraph

dot = Digraph(comment='factorio')

_nodes = set()
_edges = set()

FILTER_OUT = {
    'Time',
    'barrel',
    'Empty barrel'
}

def add_edge(e1, e2, *args, **kwargs):
    if e1 in FILTER_OUT or e2 in FILTER_OUT:
        return False
    dot.edge(e1, e2, *args, **kwargs)
    _edges.add((e1, e2))
    return True

# dir(dot)
# dot.edge(set(c.name for c in r.conditions), tuple(e.name for c in r.effects))
#
#
# tuple(c.name for c in r.conditions)
# tuple(e.name for c in r.effects)


phantom_nodes = []
def get_phantom_nodes():
    p = f'_phantom_node{len(phantom_nodes)}'
    phantom_nodes.append(p)
    return p

#%%


for r in all_recipes:
    p1 = get_phantom_nodes()
    p2 = get_phantom_nodes()

    # if len(r.conditions) == len(r.effects) == 1:
    #     #  one to one mapping
    #     add_edge(c.conditions[0].name, r.effects[0], color='blue')
    # else:
    for c in r.conditions:
        add_edge(c.name, p1, str(c.count), dir='none', color='blue')
    if len(r.effects) == 1:
        add_edge(p1, r.effects[0].name, str(r.effects[0].count), color='red')
    else:
        for e in r.effects:
            add_edge(p2, e.name, str(e.count), color='red')
        add_edge(p1, p2, dir='none', color='red')

used_edges = set()
for e in _edges:
    used_edges.update(e)
for p in phantom_nodes:
    if p in used_edges:
        dot.node(p, shape='point', width='0.01', height='0.01')

#%%
"""ORIGINAL ADD RECIPE"""
# for r in all_recipes:
#     for c in r.conditions:
#         for e in r.effects:
            # add_edge(c.name, e.name, color='blue')

"""REQ TECH"""
if False:
    for req_tech, item in all_req_tech:
        for r in req_tech:
            add_edge(r.name, item.name, color='green')

# we need to do some filtering first
_edges_to_be_process = {}
for prod_by, item in all_prod_by:
    for p in prod_by:
        if item.name in FILTER_OUT or p.name in FILTER_OUT:
            continue
        _p_out_edge = _edges_to_be_process.get(item.name, [])
        _p_out_edge.append(p.name)
        _edges_to_be_process[item.name] = _p_out_edge
        # _edges_to_be_process.append((p.name, item.name))
        # add_edge(p.name, item.name, color='purple')
# try to add manual crafting first, if not exist then assembling machine 1..3
for dest, incomings in _edges_to_be_process.items():
    incomings = list(filter(lambda x : 'barrel' not in x, incomings))
    if 'Crafting#Manual crafting' in incomings:
        # we treat manual crafting as do-able always
        continue
    if len(incomings) == 1:
        true_incoming = incomings[0]
    elif 'Assembling machine 1' in incomings:
        true_incoming = 'Assembling machine 1'
    elif 'Assembling machine 2' in incomings:
        true_incoming = 'Assembling machine 2'
    elif 'Assembling machine 3' in incomings:
        true_incoming = 'Assembling machine 3'
    elif 'Oil refinery' in incomings:
        true_incoming = 'Oil refinery'
    elif 'Stone furnace' in incomings:
        true_incoming = 'Oil refinery'
    else:
        raise Exception((dest, incomings))

    add_edge(true_incoming, dest, color='purple')
    dot.node(true_incoming, style='filled', fillcolor='maroon1')

#%%
for e in _edges:
    _nodes.update(e)

def check_not_exists_in_all_edges(name, idx):
    """Given an index, this will check if there exists no given name
    among the idex of all edges."""
    for e in _edges:
        if n == e[idx]:
            return False
    return True

for n in _nodes:
    # color node without incomings (root)
    if check_not_exists_in_all_edges(name=n, idx=1):
        dot.node(n, style='filled', fillcolor='green3')
    # color node without outcomings (leaves)
    if check_not_exists_in_all_edges(name=n, idx=0):
        dot.node(n, style='filled', fillcolor='aquamarine')

#%%

# dot.save('factorio.dot')
dot.render('factorio', view=True)

#%%



def use_igraph():
    import igraph

    vertices = list(items.keys())
    sorted(vertices)

    G = igraph.Graph(directed=True)
    # G.add_vertices(vertices)

    vertices_used = []

    edges = []

    for item in items.values():
        # try:
        if 'Recipe' in item.values:
            edge_a = item.item_url_name
            for _i in item.values['Recipe']:
                edge_b = _i.item_url_name

                # print(edge_a, edge_b)


                # assert edge_a in vertices, edge_a
                # assert edge_b in vertices, edge_b
                if edge_a not in vertices_used:
                    vertices_used.append(edge_a)
                if edge_b not in vertices_used:
                    vertices_used.append(edge_b)


                edges.append((edge_b, edge_a))
                # edges.append((edge_a, edge_b))
                # edges.append((vertices_used.index(edge_a), vertices_used.index(edge_b)))
        # except KeyError:
        #     continue
        #     pass
        # a
        # a
        # G.add_edges()
    G.add_vertices(vertices_used)
    G.add_edges(edges)

    G.vs[0]


    G.vs['label'] = vertices
    G.vs['shape'] = ['rectangle'] * len(vertices)
    G.vs['label_size'] = [10] * len(vertices)
    G.vs['size'] = [30] * len(vertices)
    G.vs['size2'] = [2] * len(vertices)

    igraph.plot(
                G,
                margin=150,
                bbox=(1500, 1500),  #layout=G.layout("kk"),
                # bbox=(300, 300),  #layout=G.layout("kk"),
                # mark_groups=
                # group,
                # collections.OrderedDict(reversed(list(group.items()))),
                # shapes=[2] * 100,  # square
                # **plot_ig_kwargs,
                autocurve=True)



def previous_trial():

    def add_node(color=None):
        if edge_a not in _nodes:
            _nodes.add(edge_a)
            dot.node(edge_a, color=color)
        if edge_b not in _nodes:
            _nodes.add(edge_b)
            dot.node(edge_b, color=color)


    BLACK_LIST = [
        'Advanced_oil_processing',
        'Barrel',
        'Coal_liquefaction',
        'Crafting#Manual_crafting',
        'Empty_barrel',
        'Empty_water_barrel',
        'Fill_crude_oil_barrel',
        'Fill_heavy_oil_barrel',
        'Fill_light_oil_barrel',
        'Fill_lubricant_barrel',
        'Fill_petroleum_gas_barrel',
        'Fill_sulfuric_acid_barrel',
        'Fill_water_barrel',
        'Heavy_oil_cracking',
        'Light_oil_cracking',
        'Oil_processing',
        'Oil_processing#Recipes',
        'Solid_fuel_from_heavy_oil',
        'Solid_fuel_from_light_oil',
        'Time',
        'Solid_fuel_from_petroleum_gas',
     ]


    i = 0

    {i['Prototype type'] for i in items.values() if 'Prototype type' in i.values}

    for k, item in items.items():
        i += 1
        # if i > 80:
        #     break
        # try:


        try:
            if k in BLACK_LIST:
                continue

            # if item['Prototype type'] not in (
            #     'resource',
            #     'recipe',
            #     'item',
            #     'tool',
            # ):
            #     continue

            edge_a = item['Internal name']
            # edge_a = item.item_url_name

            if 'Recipe' in item.values:
                item['Recipe'].condition

            for row_type in [
                # 'Recipe',
                             # 'Required technologies',
                'Produced by',
                             # 'Consumed by',
                             ]:



                if row_type in item.values:
                    for _i in item[row_type]:
                        # print(_i.item_url_name)

                        if _i.item_url_name == 'Crafting#Manual_crafting':
                            print(item)

                        if _i.item_url_name in BLACK_LIST:
                            continue


                        edge_b = items[_i.item_url_name]['Internal name']
                        # edge_b = _i.item_url_name


                        if row_type == 'Recipe':
                            color='blue'
                        elif row_type == 'Required technologies':
                            color='red'
                        elif row_type == 'Produced by':
                            color='green'
                        elif row_type == 'Consumed by':
                            color='brown'
                        else:
                            raise Exception()

                        edge_added = False



                        if row_type in (
                            'Recipe',
                            'Required technologies',
                            'Produced by'
                            ):
                            e = edge_b, edge_a
                            dot.edge(edge_b, edge_a, color=color)
                            edge_added=True
                        elif row_type in (
                            '___',
                            'Consumed by',
                            # ,
                            ):
                            e = edge_a, edge_b
                            dot.edge(edge_a, edge_b, color=color)
                            edge_added=True

                        _edges.add(e)


                        if edge_added:
                            _nodes.add(edge_a)
                            _nodes.add(edge_b)

                        if row_type == 'Produced by':
                            break

        except KeyError as e:
            raise e
            print(str(e))
        except AssertionError as ee:
            # raise e
            # print(e)
            print(row_type)

    i

    len(_nodes)

    for n in _nodes:
        # check if it has incoming edge
        color = 'red'
        for e in _edges:
            if e[1] == n:
                color = 'white'

        if n in [
            'copper-ore',
            'iron-ore',
            'stone',
            'coal',
        ]:
            color = 'red'

        dot.node(n, style='filled', fillcolor=color)
