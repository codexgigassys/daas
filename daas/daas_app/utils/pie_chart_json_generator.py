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
    option = {'title': {'text': 'Samples per type', 'x': 'center'},
              'tooltip': {'trigger': 'item', 'formatter': "{a} <br/>{b} : {c} ({d}%)"},
              'legend': {'orient': 'vertical', 'x': 'left', 'data': [classification for classification in data.keys()]},
              'toolbox': {'show': True,
                          'feature': {'mark': {'show': True},
                                      'dataView': {'show': True, 'readOnly': False},
                                      'magicType': {'show': True,
                                                    'type': ['pie', 'funnel'],
                                                    'option': {'funnel': {'x': '25%',
                                                                          'width': '50%',
                                                                          'funnelAlign': 'left',
                                                                          'max': 1548}}},
                                      'restore': {'show': True},
                                      'saveAsImage': {'show': True}}},
              'calculable': True,
              'series': [{'name': 'Samples',
                          'type': 'pie',
                          'radius': '55%',
                          'center': ['50%', '60%'],
                          'data': generate_multiple_items(data)}]}
    return option
