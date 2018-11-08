def generate_item(classification, count):
    return {'name': classification, 'value': count}


def generate_multiple_items(data):
    return [generate_item(classification, counts) for classification, counts in data.items()]


def generate_pie_chart(data):
    """
    :param data: {class: value, class2: value2, ...}. For example, if you have two apples and five oranges:
                 {'apples':2, 'oranges': 5}
    :return:
    """
    option = {'title': {'text': '', 'subtext': '', 'x': 'center'},
              'tooltip': {'trigger': 'item', 'formatter': "{a} <br/>{b} : {c} ({d}%)"},
              'legend': {'orient': 'horizontal', 'x': 'center', 'data': [classification for classification in data.keys()]},
              'toolbox': {'show': True,
                          'feature': {'saveAsImage': {'show': True}}},
              'calculable': True,
              'series': [{'name': 'Samples',
                          'type': 'pie',
                          'radius': '70%',
                          'center': ['50%', '50%'],
                          'data': generate_multiple_items(data)}]}
    return option
