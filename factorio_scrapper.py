from selenium import webdriver
from binary_downloader.phantomjs import PhantomjsDownloader

phantomjs_downloader = PhantomjsDownloader()
import os
if not os.path.isfile(phantomjs_downloader.get_bin()):
    # None exists, download binary file
    print("Downloading phantomjs binary file")
    phantomjs_downloader.download()
    print("Done!")

kwargs = {
    'executable_path': phantomjs_downloader.get_bin(),
    # 'service_log_path': log_path
}

# webdriver.Chrome(**kwargs)

driver = webdriver.PhantomJS(**kwargs)

#%%


# dir(driver)

rows_to_retrieve = [
    'Recipe',
    'Total raw',
    'Stack size',
    'Prototype type',
    'Internal name',
    'Required technologies',
    'Produced by',
    'Required technologies',
    'Fuel value',
    'Used as fuel by',
    # 'Mining time',
    # 'Vehicle acceleration',
    'Consumed by',
    ]

multi_item_types = ['Recipe',
                    'Total raw',
                    'Required technologies',
                    'Produced by',
                    'Consumed by',]

for i in multi_item_types:
    assert i in rows_to_retrieve

# %%%

class Row():
    def __init__(self, web_element):
        # self.web_element = web_element
        self.items = [ItemFromFactorioIcon(e) for e in
                      web_element.find_elements_by_class_name('factorio-icon')]

    def __repr__(self):
        return f'<Row: {self.items}>'

    def __iter__(self):
        return self.items.__iter__()

    def __getitem__(self, idx):
        return self.items[idx]

    @staticmethod
    def from_values(items):
        new_item = Row.__new__(Row)
        new_item.items = items
        return new_item

class ItemFromFactorioIcon():
    def __init__(self, web_element):
        # self.web_element = web_element
        self.name = web_element.find_element_by_tag_name('a').get_attribute('title')
        self.link = web_element.find_element_by_tag_name('a').get_attribute('href')
        self.count = web_element.find_element_by_class_name('factorio-icon-text').text

    @property
    def item_url_name(self):
        return self.link.split('/')[-1]

    def __repr__(self):
        count = self.count
        if count == '':
            return f"<LinkedItem:{self.name}>"
        else:
            return f"<LinkedItem:{self.name}={self.count}>"

    def __eq__(self, other):
        return self.name == other.name and self.count == other.count

    @staticmethod
    def from_values(name, count, link=None):
        new_item = ItemFromFactorioIcon.__new__(ItemFromFactorioIcon)
        new_item.name = name
        new_item.link = link
        new_item.count = count
        return new_item

    def __hash__(self):
        return hash((self.name, self.link, self.count))


class Item():
    """Represent an item, and store all of the important information."""
    def __init__(self, web_element):
        # self.web_element = web_element
        self.name = web_element.title.split(' - ')[0]
        self.item_url_name = web_element.current_url.split('/')[-1]
        self.values = {}
        for row in rows_to_retrieve:
            try:
                self.values[row] = get_value(row)
            except AssertionError:
                pass

    def __getitem__(self, idx):
        return self.values[idx]

    def __repr__(self):
        text = '\n'.join([f'      {k}: {v}' for k,v in self.values.items()])
        return f'<item:{self.name}\n{text}\n\item>'

    def __hash__(self):
        return hash(self.item_url_name)

    @staticmethod
    def from_values(item_url_name, values):
        new_item = Item.__new__(Item)
        new_item.item_url_name = item_url_name
        new_item.values = values
        return new_item

def get_row_from_title(title, idx_to_return=None, return_next_row=False):
    """This helper function helps to locate a row title,
    and then return the following row (if the optional argument is given,
    because they are separated as two different row)
    if idx_to_return is set, return if have multiple items
    ."""

    xpath = f"//tr[contains(@class, 'border-top') and starts-with(normalize-space(.), '{title}')]"
    element = driver.find_elements_by_xpath(xpath)
    if idx_to_return is None:
        assert len(element) == 1, f"{len(element)}, Not haing exactly one matching row"
        idx_to_return = 0
    else:
        assert len(element) > 0
    if return_next_row:
        # return immediate next row
        return driver.find_elements_by_xpath(f'{xpath}/following-sibling::tr')[idx_to_return]
    else:
        return element[idx_to_return]

def get_value(row_type):
    """Return the correct value depend on row type."""
    if row_type == 'Recipe':
        return Recipe(get_row_from_title(row_type, return_next_row=True, idx_to_return=0))
    elif row_type in multi_item_types:
        return Row(get_row_from_title(row_type, return_next_row=True, idx_to_return=0))
    else:
        values = get_row_from_title(row_type).text.split('\n')[1:]
        assert len(values) == 1, values
        return values[0]


class Recipe(Row):

    def __init__(self, web_element):
        super().__init__(web_element)
        self.items = [ItemFromFactorioIcon(e) for e in
                      web_element.find_elements_by_class_name('factorio-icon')]
        # extract conditions and effects
        self.operators = self.get_equation_effects(web_element.text)
        assert len(self.items) == len(self.operators)
        self.conditions = [self.items[i] for i in range(len(self.items))
                           if self.operators[i] == 'condition']
        self.effects = [self.items[i] for i in range(len(self.items))
                           if self.operators[i] == 'effect']

    @staticmethod
    def get_equation_effects(equation):
        current_operator = 'condition'
        operators = []
        eq_split = equation.split('\n')
        # make sure we can make each odd element as float (as they must be qualtity)
        for i in range(len(eq_split)):
            if i % 2 == 0: # we are testing even instead of odd because of 0-base indexing
                operators.append(current_operator)
            else:
                if eq_split[i] not in ('+', '→'):
                    raise Exception(f'{repr(eq_split)} at {i} as {repr(eq_split[i])}')
                if eq_split[i] == '→':
                    current_operator = 'effect'
        return operators

    def __hash__(self):
        return hash((frozenset(self.conditions), frozenset(self.effects)))

    def __eq__(self, other):
        if len(self.conditions) != len(other.conditions):
            return False
        if len(self.effects) != len(other.effects):
            return False
        for i in range(len(self.conditions)):
            if self.conditions[i] != other.conditions[i]:
                return False
        for i in range(len(self.effects)):
            if self.effects[i] != other.effects[i]:
                return False
        return True

    def __repr__(self):
        linked_item_tostr = lambda x : f'<{x.name}={x.count}>'
        return (f"<Recipe: {' + '.join(map(linked_item_tostr, self.conditions))}"
               f" → {' + '.join(map(linked_item_tostr, self.effects))}>")

    def __iter__(self):
        return self.items.__iter__()

    def __getitem__(self, idx):
        return self.items[idx]

    @staticmethod
    def from_values(conditions, effects):
        new_item = Recipe.__new__(Recipe)
        new_item.items = []
        new_item.items.extend(conditions)
        new_item.items.extend(effects)
        new_item.conditions = conditions
        new_item.effects = effects
        return new_item

# %%
# get_row_from_title('Recipe', return_next_row=True, idx_to_return=0).text
def scrap():
    items = {}
    links_to_visit = ['https://wiki.factorio.com/Wood']
    # links_to_visit = ['https://wiki.factorio.com/Uranium-238']
    # links_to_visit = ['https://wiki.factorio.com/Combat_shotgun']
    visited_link = set()

    while len(links_to_visit):

        link = links_to_visit.pop(0)
        if link in visited_link:
            continue
        visited_link.add(link)

        print(f'[{len(visited_link)}] visiting {link}...')
        driver.get(link)

        item = Item(driver)
        items[item.item_url_name] = item
        for field in multi_item_types:
            if field in item.values:
                links_to_visit.extend((linked_item.link for linked_item in item.values[field]))

# import pickle
#
#
# with open('fact.pkl', 'wb') as f:
#     # pickle.dump((visited_link, from_json(data)), f)
#     pickle.dump((visited_link, items), f)


# %%
#

def to_json(x):
    """Convert the nested scrapped items dict to json text"""
    y = {}
    if isinstance(x, Recipe)  or str(type(x)) == "<class '__main__.Recipe'>":
        y['type'] =  'Recipe'
        y['items'] = list(map(to_json, x.items))
        y['operators'] = x.operators
        y['conditions'] = list(map(to_json, x.conditions))
        y['effects'] = list(map(to_json, x.effects))

    elif isinstance(x, Row) or str(type(x)) == "<class '__main__.Row'>":
        y['type'] =  'Row'
        y['items'] = list(map(to_json, x.items))

    elif isinstance(x, Item) or str(type(x)) == "<class '__main__.Item'>":
        y['type'] =  'Item'
        y['item_url_name'] =  x.item_url_name
        y['values'] = to_json(x.values)

    elif isinstance(x, ItemFromFactorioIcon) or str(type(x)) == "<class '__main__.ItemFromFactorioIcon'>":
        y['type'] =  'ItemFromFactorioIcon'
        y['name'] =  x.name
        y['link'] =  x.link
        y['count'] =  x.count

    elif isinstance(x, dict):
        y =  {k : to_json(v) for k,v in  x.items()}

    elif isinstance(x, (str, float, int)):
        y = x
    else:
        raise Exception(type(x))

    return y

def from_json(x):
    """Convert the nested scrapped items dict to """
    if isinstance(x, dict):
        if 'type' not in x:
            return {k : from_json(v) for k, v in x.items()}

        elif x['type'] == 'Recipe':
            return Recipe.from_values(
                conditions=[from_json(_x) for _x in x['conditions']],
                effects=[from_json(_x) for _x in x['effects']])

        elif x['type'] == 'Row':
            return Row.from_values([from_json(_x) for _x in x['items']])

        elif x['type'] == 'Item':
            return Item.from_values(
                item_url_name=x['item_url_name'],
                values=from_json(x['values']))

        elif x['type'] == 'ItemFromFactorioIcon':
            return ItemFromFactorioIcon.from_values(
                name=x['name'],
                count=x['count'],
                link=x['link'])

    elif isinstance(x, (str,)):
        return x

    else:
        print(x)
        raise Exception(type(x))

# import json
#
# with open("factorioaaa.json", "w") as write_file:
#     json.dump(to_json(items), write_file)
#
# with open("factorio.json", "r") as write_file:
#     data = json.load(write_file)


if __name__ == '__main__':
    scrap()
