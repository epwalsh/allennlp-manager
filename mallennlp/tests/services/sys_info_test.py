import pytest
import torch

from mallennlp.services.sys_info import SysInfoService

MOCKED_QUERY_OUTPUT = """
0, GeForce GTX 1070, 418.87.01, 410, 8116, 8, 43, 29
1, GeForce GTX 1070, 418.87.01, 201, 8116, 2, 41, 21
"""


def test_parse_output(monkeypatch):
    def mock_gpu_query_output():
        return MOCKED_QUERY_OUTPUT

    monkeypatch.setattr(SysInfoService, "get_gpu_query_output", mock_gpu_query_output)
    info = SysInfoService.get()
    assert info.driver_version == "418.87.01"
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
