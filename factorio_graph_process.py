import pickle

from factorio_scrapper import ItemFromFactorioIcon, Recipe, Item, Row

# with open('factorio.pkl', 'rb') as f:
#     visited_link, items = pickle.load(f)
with open("factorio.pkl", "rb") as f:
    visited_link, items = pickle.load(f)

# %%

# filter out unwanted nodes
BLACK_LIST = [
    'Uranium processing',
    'Uranium processing (research)',
  'Kovarex enrichment process',
  'Kovarex enrichment process (research)'
              ]

def clean_item(packed):
    key, item = packed
    value_dict = item.values
    new_value_dict = {}
    for k, v in list(value_dict.items()):
        # print(v)
        if isinstance(v, Row):
            dirty = False
            for _v in v:
                if _v.name in BLACK_LIST:
                    dirty = True
                    break
            if dirty:
                # create a new row
                new_values = [_v for _v in v[:] if _v.name not in BLACK_LIST]
                print(v)
                v = Row.from_values(new_values)
                print(v)
                item.values[k] = v
                # new_value_dict[k] = v
        else:

            for b in BLACK_LIST:
                if b in v:
                    print(v)
                    asdas
            print(v)
            from pprint import pprint

            pprint(new_value_dict)

        new_value_dict[k] = v

    for b in BLACK_LIST:
        assert b not in str(new_value_dict), str(new_value_dict)
        assert b not in key
        if b in item.name:
            return None
        assert b not in item.name
    new_item = Item.from_values(None, new_value_dict)
    new_item.name = item.name
    for b in BLACK_LIST:
        assert b not in str(new_item), (new_item, new_item.values)
    return key, new_item
        # new_value_dict[k] = v
    # item.values = new_value_dict
    # old_item = item
    # item = Item.from_values(None, new_value_dict)
    # item.name = old_item.name
    # return
    # for b in BLACK_LIST:
    #     if b in str(new_value_dict):
    #     # if b in str(item):
    #         from pprint import pprint
    #         print(item)
    #         pprint(value_dict)
    #         pprint(new_value_dict)
    #         asdsd
    # return key, item
    # return item

_TMP = list(items.items())
_ = [clean_item(x) for x in _TMP]

items = {}
for packed in _:
    if packed is None:
        continue
    items[packed[0]] = packed[1]


# items = dict([clean_item(item) for item in items.items()])

#CLEANING IS DONE IN PLACE!

items['Atomic_bomb_(research)'].values

all_recipes = set(
    [item["Recipe"] for k, item in items.items() if "Recipe" in item.values]
)
all_req_tech = [
    (item["Required technologies"], item)
    for k, item in items.items()
    if "Required technologies" in item.values
]
all_prod_by = [
    (item["Produced by"], item)
    for k, item in items.items()
    if "Produced by" in item.values
]
'Uranium processing' in  str([a[1] for a in all_req_tech])

'Uranium processing' in str(all_req_tech)
'Kovarex enrichment process' in str(all_prod_by)
'Kovarex enrichment process' in str(all_prod_by)




LI = ItemFromFactorioIcon.from_values

# manually add recipe

extra_recipes = [
    Recipe.from_values([LI("Heavy oil", 20), LI("Time", 20)], [LI("Solid fuel", 1)]),
    Recipe.from_values([LI("Light oil", 10), LI("Time", 20)], [LI("Solid fuel", 1)]),
    Recipe.from_values(
        [LI("Petroleum gas", 20), LI("Time", 20)], [LI("Solid fuel", 1)]
    ),
    Recipe.from_values(
        [LI("Crude oil", 100), LI("Water", 50), LI("Time", 5)],
        [LI("Petroleum gas", 55), LI("Heavy oil", 25), LI("Light oil", 45)],
    ),
]

all_recipes.update(extra_recipes)


# %%
class CoolEdge:
    """Represent an edge that can be one-to-one, many-to-many, ... etc."""

    def __init__(
        self, fm=None, to=None, *args, tos=None, fms=None, type=None, **kwargs
    ):
        if (to is None and tos is None) or (fm is None and fms is None):
            raise ValueError("'To' or 'From' is not given!")
        if type is None:
            raise ValueError("type of edge is not given!")

        if tos is None:
            tos = [to]
        if fms is None:
            fms = [fm]

        # filter out unwanted edges.
        no_unwanted_edge = lambda x: x.name not in FILTER_OUT
        tos = list(filter(no_unwanted_edge, tos))
        fms = list(filter(no_unwanted_edge, fms))

        self.tos = tos
        self.fms = fms
        self.args = args
        self.kwargs = kwargs
        self.type = type

    def __hash__(self):
        return hash((frozenset(self.fms), frozenset(self.tos)))

    def __eq__(self, other):
        return frozenset(self.fms) == frozenset(other.fms) and frozenset(
            self.tos
        ) == frozenset(other.tos)

    def __iter__(self):
        for t in self.tos:
            yield t
        for f in self.fms:
            yield f

    def __repr__(self):
        edge_str = f"{' + '.join((f.name for f in self.fms))} -> {' + '.join((t.name for t in self.tos))}"
        return f"<CEdge|{self.type}:{edge_str}>"

    def _add(self, *args, **kwargs):
        kwargs.update(self.kwargs)
        self.dot.edge(*args, *self.args, **kwargs)

    def add(self, dot):
        self.dot = dot
        if self.type == "recipe":
            p1 = get_phantom_nodes()
            for f in self.fms:
                self._add(f.name, p1, str(f.count), dir="none", color="blue")
                # dot.edge(f.name, p1, str(f.count), *self.args, dir='none', color='blue', *self.kwargs)
            if len(self.tos) == 1:
                self._add(p1, self.tos[0].name, str(self.tos[0].count), color="red")
            else:
                p2 = get_phantom_nodes()
                for t in self.tos:
                    self._add(p2, t.name, str(t.count), color="red")
                self._add(p1, p2, dir="none", color="red")
                dot.node(p2, shape="point", width="0.01", height="0.01")

            dot.node(p1, shape="point", width="0.01", height="0.01")
        elif self.type == "req_tech":
            assert len(self.tos) == len(self.fms) == 1
            self._add(self.fms[0].name, self.tos[0].name)
        elif self.type == "prod_by":
            assert len(self.tos) == len(self.fms) == 1
            self._add(self.fms[0].name, self.tos[0].name)
        else:
            raise ValueError(f"Unknown type {self.type}!")


# %%

from graphviz import Digraph

dot = Digraph(comment="factorio")

_nodes = set()
_edges = set()

FILTER_OUT = {"Time", "barrel", "Empty barrel"}

phantom_nodes = []


def get_phantom_nodes():
    p = f"_phantom_node{len(phantom_nodes)}"
    phantom_nodes.append(p)
    return p


# %%
"""ADD RECIPE"""
for r in all_recipes:
    _edges.add(
        CoolEdge(
            fms=[c for c in r.conditions], tos=[e for e in r.effects], type="recipe"
        )
    )

"""REQ TECH"""
if False:
    for req_tech, item in all_req_tech:
        for r in req_tech:
            _edges.add(CoolEdge(r, item, color="green", type="req_tech"))
            dot.node(r.name, style="filled", fillcolor="green")

"""PRODUCE BY"""
# we need to do some filtering first
_edges_to_be_process = {}
for prod_by, item in all_prod_by:
    for p in prod_by:
        if item in FILTER_OUT or p in FILTER_OUT:
            continue
        _p_out_edge = _edges_to_be_process.get(item, [])
        _p_out_edge.append(p)
        _edges_to_be_process[item] = _p_out_edge
# try to add manual crafting first, if not exist then assembling machine 1..3
for dest, incomings in _edges_to_be_process.items():
    incomings = list(filter(lambda x: "barrel" not in x.name, incomings))
    incoming_by_str_name = {x.name: x for x in incomings}
    if "Crafting#Manual crafting" in incoming_by_str_name:
        # we treat manual crafting as do-able always
        continue
    elif len(incomings) == 1:
        true_incoming = incomings[0]
    elif "Assembling machine 1" in incoming_by_str_name:
        true_incoming = incoming_by_str_name["Assembling machine 1"]
    elif "Assembling machine 2" in incoming_by_str_name:
        true_incoming = incoming_by_str_name["Assembling machine 2"]
    elif "Assembling machine 3" in incoming_by_str_name:
        true_incoming = incoming_by_str_name["Assembling machine 3"]
    elif "Oil refinery" in incoming_by_str_name:
        true_incoming = incoming_by_str_name["Oil refinery"]
    elif "Stone furnace" in incoming_by_str_name:
        true_incoming = incoming_by_str_name["Stone furnace"]
    else:
        raise Exception((dest, incoming_by_str_name))

    _edges.add(CoolEdge(true_incoming, dest, color="magenta", type="prod_by"))
    dot.node(true_incoming.name, style="filled", fillcolor="maroon1")

# %%
# actually add edges to graphviz
for e in _edges:
    e.add(dot)
    _nodes.update((_e.name for _e in e))

# for easier of checking edges
_edges_as_str = []
for e in _edges:
    _edges_as_str.append(([_e.name for _e in e.fms], [_e.name for _e in e.tos]))


def check_not_exists_in_all_edges(name, type):
    """Given an index, this will check if there exists no given name
    among the idex of all edges."""
    if type == "outgoing":
        for e in _edges_as_str:
            if name in e[0]:
                return False
    elif type == "incoming":
        for e in _edges_as_str:
            if name in e[1]:
                return False
    return True


for n in _nodes:
    # color node without incomings (root)
    if check_not_exists_in_all_edges(name=n, type="incoming"):
        dot.node(n, style="filled", fillcolor="green3")
        print(n)
    # color node without outgoing (leaves)
    if check_not_exists_in_all_edges(name=n, type="outgoing"):
        dot.node(n, style="filled", fillcolor="aquamarine")

# %%
_edges_list = list(_edges)

print("These are the items that cannot be made:")
for _n in _nodes:
    for _e in _edges_list:
        # type(_n)
        if any(_n == __e.name for __e in _e.tos):
            break
    else:
        print(" -", _n)

# %%

# dot.save('factorio.dot')
dot.render("factorio", view=True)

# %%
# post-process all nodes/edges

actions = []

len([e for e in _edges if e.type == "recipe"])
len(_nodes)

len(actions)

prod_by_dictionary = {}
for e in _edges:
    if e.type == "prod_by":
        _by = prod_by_dictionary.get(e.tos[0].name, [])
        _by.extend(e.fms)

        prod_by_dictionary[e.tos[0].name] = _by

__a = [str(e) for e in _edges]

[x for x in __a if 'ude oil' in x.lower()]
[x for x in __a if 'prod_by' in x.lower()]

for e in _edges:
    if e.type == "recipe":
        actions.append({"conditions": [], "effects": []})
        # special case for oil refinary
        tos = [_e.name for _e in e.tos]
        if "Light oil" in tos and "Heavy oil" in tos and "Petroleum gas" in tos:
            pass
        else:
            actions[-1]["conditions"].extend((_e.name, 0) for _e in e.tos)
        actions[-1]["conditions"].extend((_e.name, 1) for _e in e.fms)
        actions[-1]["effects"].extend((_e.name, 1) for _e in e.tos)
        actions[-1]["effects"].extend((_e.name, 0) for _e in e.fms)
        req = set()
        # search for the req_tech for each child node.
        for _e in e.tos:
            if _e.name in prod_by_dictionary:
                req.update(prod_by_dictionary[_e.name])
        for r in req:
            actions[-1]["conditions"].append((r.name, 1))
        # # for f in e.fms:
        # #     for
        # #     states[f.name]['children'].append()
        # for t in e.tos:
        #     states[t.name]['conditions'].append((e.fms[0].name, 1)) # should be e.count for extension
        # for t in e.tos:
        #     states[t.name]['effects'].append((e.fms[0].name, 0)) # should be count

    elif e.type == "req_tech":
        pass

    elif e.type == "prod_by":
        assert len(e.fms) == 1
        assert len(e.tos) == 1
        # print(e.tos[0].name)

        # search to see if this is part of any recipe's produce
        _all_recipes_list = list(all_recipes)

        for r in _all_recipes_list:
            for eff in r.effects:
                if e.tos[0].name == eff.name:
                    break
            else:
                continue
            break
        else:
            print(e)

        # # special case for Crude oil as it requires no recipe
        # if 'Pumpjack' == e.fms[0].name and 'Crude oil' == e.tos[0].name:
            actions.append({"conditions": [], "effects": []})
            actions[-1]["conditions"].append((e.tos[0].name, 0))
            actions[-1]["conditions"].append((e.fms[0].name, 1))
            actions[-1]["effects"].append((e.tos[0].name, 1))
            print(actions[-1])
    else:
        raise Exception()

states_name = sorted(_nodes)
map_state_name_to_int = {s: i for i, s in enumerate(states_name)}




#%%



actions = sorted(actions, key=lambda x: map_state_name_to_int[x["effects"][0][0]])

# %%
# manually add actions that does not require any materials
actions[0:0] = [
    {"conditions": [("Wood", 0)], "effects": [("Wood", 1)]},
    {"conditions": [("Stone", 0)], "effects": [("Stone", 1)]},
    {"conditions": [("Coal", 0)], "effects": [("Coal", 1)]},
    {"conditions": [("Copper ore", 0)], "effects": [("Copper ore", 1)]},
    {"conditions": [("Iron ore", 0)], "effects": [("Iron ore", 1)]},
]


# %%

def to_state_str(item_name):
    # USE underscore int
    if False:
    # if True:
        return int_to_padded_str(map_state_name_to_int[item_name])
    else:
        return f"s[{map_state_name_to_int[item_name]}]"



def int_to_padded_str(i, length=4):
    return "_" * (length - len(str(i))) + str(i)


def print_with_width_limits(strings, offset_prev=9, offset_after=14, width_limit=80):
    final_str = f"{i:>3} : "
    _i = 0
    while _i < len(strings):
        if offset_prev + len(final_str) + offset_after >= width_limit:
            print(final_str)
            final_str = "   "
        if _i != 0:
            final_str += " & "
        final_str += strings[_i]
        _i += 1
    print(final_str + ",")


# %%
print_comment = True
# %%
# Print conditions
for i, action in enumerate(actions):
    strings = []
    for c in action["conditions"]:
        strings.append(f"({to_state_str(c[0])} == {c[1]})")
    if print_comment:
        print(f"# cond on: " + ", ".join(str(c[0]) for c in action["conditions"]))
    print_with_width_limits(strings)

# %%
# Print effect
AA = set()
for i, action in enumerate(actions):
    strings = []
    for e in action["effects"]:
        strings.append(
            f"({to_state_str(e[0])} @ {1 - e[1]} >> {e[1]})"
        )
        AA.add(map_state_name_to_int[e[0]])
        # AA.add(e[0])
    if print_comment:
        print(f"# eff on: " + ", ".join(str(e[0]) for e in action["effects"]))
    print_with_width_limits(strings)




# %%
# Print actions description

for i, action in enumerate(actions):
    print(
        f"{i:>3}. Get {' + '.join(e[0].lower() for e in action['effects'] if e[1] == 1)}"
    )

# %%
# Print state name
for i, n in enumerate(states_name):
    print(f"{i:>3}. Has {n.lower()}")

# %%
# find missing item

map_state_name_to_int

B = {v:k for k,v in map_state_name_to_int.items()}

B[193]
B[88]
B[187]

for i in range(198):
    if i not in AA:
        print(i)
AA



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
        if "Recipe" in item.values:
            edge_a = item.item_url_name
            for _i in item.values["Recipe"]:
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

    G.vs["label"] = vertices
    G.vs["shape"] = ["rectangle"] * len(vertices)
    G.vs["label_size"] = [10] * len(vertices)
    G.vs["size"] = [30] * len(vertices)
    G.vs["size2"] = [2] * len(vertices)

    igraph.plot(
        G,
        margin=150,
        bbox=(1500, 1500),  # layout=G.layout("kk"),
        # bbox=(300, 300),  #layout=G.layout("kk"),
        # mark_groups=
        # group,
        # collections.OrderedDict(reversed(list(group.items()))),
        # shapes=[2] * 100,  # square
        # **plot_ig_kwargs,
        autocurve=True,
    )


def previous_trial():
    def add_node(color=None):
        if edge_a not in _nodes:
            _nodes.add(edge_a)
            dot.node(edge_a, color=color)
        if edge_b not in _nodes:
            _nodes.add(edge_b)
            dot.node(edge_b, color=color)

    BLACK_LIST = [
        "Advanced_oil_processing",
        "Barrel",
        "Coal_liquefaction",
        "Crafting#Manual_crafting",
        "Empty_barrel",
        "Empty_water_barrel",
        "Fill_crude_oil_barrel",
        "Fill_heavy_oil_barrel",
        "Fill_light_oil_barrel",
        "Fill_lubricant_barrel",
        "Fill_petroleum_gas_barrel",
        "Fill_sulfuric_acid_barrel",
        "Fill_water_barrel",
        "Heavy_oil_cracking",
        "Light_oil_cracking",
        "Oil_processing",
        "Oil_processing#Recipes",
        "Solid_fuel_from_heavy_oil",
        "Solid_fuel_from_light_oil",
        "Time",
        "Solid_fuel_from_petroleum_gas",
    ]

    i = 0

    {i["Prototype type"] for i in items.values() if "Prototype type" in i.values}

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

            edge_a = item["Internal name"]
            # edge_a = item.item_url_name

            if "Recipe" in item.values:
                item["Recipe"].condition

            for row_type in [
                # 'Recipe',
                # 'Required technologies',
                "Produced by",
                # 'Consumed by',
            ]:

                if row_type in item.values:
                    for _i in item[row_type]:
                        # print(_i.item_url_name)

                        if _i.item_url_name == "Crafting#Manual_crafting":
                            print(item)

                        if _i.item_url_name in BLACK_LIST:
                            continue

                        edge_b = items[_i.item_url_name]["Internal name"]
                        # edge_b = _i.item_url_name

                        if row_type == "Recipe":
                            color = "blue"
                        elif row_type == "Required technologies":
                            color = "red"
                        elif row_type == "Produced by":
                            color = "green"
                        elif row_type == "Consumed by":
                            color = "brown"
                        else:
                            raise Exception()

                        edge_added = False

                        if row_type in (
                            "Recipe",
                            "Required technologies",
                            "Produced by",
                        ):
                            e = edge_b, edge_a
                            dot.edge(edge_b, edge_a, color=color)
                            edge_added = True
                        elif row_type in (
                            "___",
                            "Consumed by",
                            # ,
                        ):
                            e = edge_a, edge_b
                            dot.edge(edge_a, edge_b, color=color)
                            edge_added = True

                        _edges.add(e)

                        if edge_added:
                            _nodes.add(edge_a)
                            _nodes.add(edge_b)

                        if row_type == "Produced by":
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
        color = "red"
        for e in _edges:
            if e[1] == n:
                color = "white"

        if n in ["copper-ore", "iron-ore", "stone", "coal"]:
            color = "red"

        dot.node(n, style="filled", fillcolor=color)
