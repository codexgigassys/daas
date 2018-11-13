def generate_worker_result(sample, timeout=120, elapsed_time=5, failed=False, decompiler_name='mock decompiler'):
    timed_out = elapsed_time >= timeout
    exit_status = 124 if timed_out else (1 if failed else 0)
    info_for_statistics = {'sha1': sample.sha1,
                           'timeout': timeout,
                           'elapsed_time': elapsed_time + 1,
                           'exit_status': exit_status,
                           'timed_out': timed_out,
                           'output': 'decompiler output',
                           'decompiled': exit_status == 0,
                           'decompiler': decompiler_name,
                           'version': 1}
    return {'statistics': info_for_statistics, 'zip': 'fake zip'}
