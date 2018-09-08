from utils import RelationRepository


# This function will be launched by redis queue worker
def process_task_from_queue(task_dictionary):
    sample = task_dictionary['sample']
    RelationRepository().submit_sample(sample)
