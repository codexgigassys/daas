from decompiler_factory import DecompilerFactory
from utils import DaaSAPIConnector


# This function should by called by redis queue (rq command).
def worker(task):
    decompiler = DecompilerFactory().create(task['config'])
    sample_id = task['sample_id']
    connector = DaaSAPIConnector(task['api_base_url'])
    sample = connector.get_sample(sample_id)
    result = decompiler.process(sample)
    connector.send_result(result)
