from typing import Any, Iterable, List, Union


def flatten(list_of_lists: Iterable[Iterable[Any]]) -> List[Any]:
    result = []
    for sublist in list_of_lists:
        result.extend(sublist)
    return result


def recursive_flatten(something: Union[Any, Iterable[Any]]) -> List[Any]:
    if type(something) is list:
        result = []
        for element in something.copy():
            result.extend(recursive_flatten(element))
    else:
        result = [something]
    return result
