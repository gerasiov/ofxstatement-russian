import os.path

SAMPLES_DIR = os.path.join(os.path.dirname(__file__), 'samples')


def file_sample(name):
    result = os.path.join(SAMPLES_DIR, name)
    if not os.path.exists(result):
        raise RuntimeError("Failed to find " + result)
    return result
