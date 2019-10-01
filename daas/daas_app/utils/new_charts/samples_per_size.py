from ..configuration_manager import ConfigurationManager

option = {
    'tooltip': {
        'trigger': 'axis',
        'axisPointer': {
            'type': 'shadow'
        }
    },
    'legend': {
        'data': ConfigurationManager().get_identifiers()
    },
    'grid': {
        'left': '3%',
        'right': '4%',
        'bottom': '3%',
        'containLabel': True
    },
    'yAxis':  {
        'type': 'value'
    },
    'xAxis': {
        'type': 'category',
        'data': [str(item) for item in range(1, biggest_size)]  # kb
    },
    'series': [
        {
            'name': 'exe',
            'type': 'bar',
            'stack': 'samples_per_type',
            'label': {
                'normal': {
                    'show': True,
                    'position': 'insideRight'
                }
            },
            'data': [320, 302, 301, 334, 390, 330, 320]
        },
        {
            'name': 'java',
            'type': 'bar',
            'stack': 'samples_per_type',
            'label': {
                'normal': {
                    'show': True,
                    'position': 'insideRight'
                }
            },
            'data': [120, 132, 101, 134, 90, 230, 210]
        },
        {
            'name': 'flash',
            'type': 'bar',
            'stack': 'samples_per_type',
            'label': {
                'normal': {
                    'show': True,
                    'position': 'insideRight'
                }
            },
            'data': [220, 182, 191, 234, 290, 330, 310]
        },
    ]
}