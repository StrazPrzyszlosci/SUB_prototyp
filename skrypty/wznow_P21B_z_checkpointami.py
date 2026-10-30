"""Resume unchanged P21B campaign with atomic per-frequency solver checkpoints.

Original scientific inputs and campaign hash remain unchanged. Cache identity
includes exact assembled matrices, forcing, solver source and library versions.
NPZ stores arrays without pickle; only complete, validated files are reused.
"""
from pathlib import Path
import hashlib
import json
import os
import tempfile
import numpy as np
import scipy
from model_gazu_3D_P21B import AcousticCavity
import analiza_gazu_przestrzennego_P21B as campaign

ORIGINAL_SOLVE = AcousticCavity.solve
CACHE = campaign.OUT / 'p21b_checkpointy_czestotliwosci'


def identity(gas, frequency):
    if not hasattr(gas, '_checkpoint_identity'):
        h = hashlib.sha256()
        for matrix in (gas.solid.K, gas.solid.M, gas.solid.C, gas.A, gas.C, gas.B):
            matrix = matrix.tocsr()
            for array in (np.asarray(matrix.shape), matrix.indptr, matrix.indices, matrix.data):
                h.update(array.tobytes())
        h.update(gas.Hext.tobytes())
        h.update(str(gas.solid.beta).encode())
        h.update((campaign.ROOT/'skrypty/model_gazu_3D_P21B.py').read_bytes())
        h.update((np.__version__ + scipy.__version__).encode())
        gas._checkpoint_identity = h.hexdigest()
    return hashlib.sha256((gas._checkpoint_identity + repr(float(frequency))).encode()).hexdigest()


def cached_solve(self, frequency, spatial_scale=1., ports=None, split_mean=True):
    if spatial_scale != 1. or ports is not None or not split_mean:
        return ORIGINAL_SOLVE(self, frequency, spatial_scale, ports, split_mean)
    key = identity(self, frequency)
    CACHE.mkdir(parents=True, exist_ok=True)
    target = CACHE / (key + '.npz')
    if target.exists():
        with np.load(target, allow_pickle=False) as data:
            assert str(data['_identity']) == key
            result = {k: (data[k].item() if data[k].ndim == 0 else data[k])
                      for k in data.files if k != '_identity'}
        print('P21B frequency checkpoint:', frequency, key[:12], flush=True)
        return result
    result = ORIGINAL_SOLVE(self, frequency)
    assert all(np.all(np.isfinite(v)) for v in result.values())
    fd, name = tempfile.mkstemp(prefix=key+'.', suffix='.tmp', dir=CACHE)
    try:
        with os.fdopen(fd, 'wb') as stream:
            np.savez_compressed(stream, _identity=key, **result)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, target)
    finally:
        if os.path.exists(name):
            os.unlink(name)
    print('P21B frequency saved:', frequency, key[:12], flush=True)
    return result


def main():
    AcousticCavity.solve = cached_solve
    campaign.main()


if __name__ == '__main__':
    main()
