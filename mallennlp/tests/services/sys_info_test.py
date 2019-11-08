import pytest
import torch

from mallennlp.services.sys_info import SysInfoService

MOCKED_GPU_QUERY_OUTPUT = """
0, GeForce GTX 1070, 418.87.01, 410, 8116, 8, 43, 29
1, GeForce GTX 1070, 418.87.01, 201, 8116, 2, 41, 21
"""

MOCKED_CUDA_VERSION_QUERY_OUTPUT = """
Fri Nov  8 11:00:45 2019
+-----------------------------------------------------------------------------+
| NVIDIA-SMI 418.87.01    Driver Version: 418.87.01    CUDA Version: 10.1     |
|-------------------------------+----------------------+----------------------+
| GPU  Name        Persistence-M| Bus-Id        Disp.A | Volatile Uncorr. ECC |
| Fan  Temp  Perf  Pwr:Usage/Cap|         Memory-Usage | GPU-Util  Compute M. |
|===============================+======================+======================|
|   0  GeForce GTX 1070    On   | 00000000:01:00.0  On |                  N/A |
| 29%   42C    P8     7W / 151W |    480MiB /  8116MiB |      6%      Default |
+-------------------------------+----------------------+----------------------+

+-----------------------------------------------------------------------------+
| Processes:                                                       GPU Memory |
|  GPU       PID   Type   Process name                             Usage      |
|=============================================================================|
|    0      2278      G   /usr/lib/xorg/Xorg                            36MiB |
|    0      2361      G   /usr/bin/gnome-shell                          81MiB |
|    0      3301      G   /usr/lib/xorg/Xorg                           135MiB |
|    0      3462      G   /usr/bin/gnome-shell                         206MiB |
|    0      6171      G   /usr/lib/firefox/firefox                       3MiB |
|    0      6300      G   /usr/lib/firefox/firefox                       3MiB |
|    0      6334      G   /usr/lib/firefox/firefox                       3MiB |
|    0      6830      G   /usr/lib/firefox/firefox                       3MiB |
|    0     13166      G   /usr/lib/firefox/firefox                       3MiB |
+-----------------------------------------------------------------------------+
"""


def test_parse_output(monkeypatch):
    def mock_gpu_query_output():
        return MOCKED_GPU_QUERY_OUTPUT

    def mock_cuda_version_query_output():
        return MOCKED_CUDA_VERSION_QUERY_OUTPUT

    monkeypatch.setattr(SysInfoService, "get_gpu_query_output", mock_gpu_query_output)
    monkeypatch.setattr(
        SysInfoService, "get_cuda_version_query_output", mock_cuda_version_query_output
    )

    info = SysInfoService.get()
    assert info.driver_version == "418.87.01"
    assert info.cuda_version == "10.1"
    assert len(info.gpus) == 2
    assert info.gpus[0].id == 0
    assert info.gpus[0].name == "GeForce GTX 1070"
    assert info.gpus[0].mem_usage == 410
    assert info.gpus[0].mem_capacity == 8116
    assert info.gpus[0].utilization == 8
    assert info.gpus[0].temp == 43
    assert info.gpus[0].fan == 29


@pytest.mark.skipif(not torch.cuda.is_available(), reason="No GPU available")
def test_get_with_nvidia_gpu():
    info = SysInfoService().get()
    assert len(info.gpus) > 0
    assert info.driver_version is not None


@pytest.mark.skipif(torch.cuda.is_available(), reason="GPU available")
def test_get_without_gpu():
    info = SysInfoService().get()
    assert info.gpus is None
    assert info.driver_version is None
