import pytest
from pydantic import BaseModel

from . import Potato
from .utils import compare_dict

basic_potato = Potato(id=0, thickness=.24, mass=1.2, color='Brown', type='Russet')


def test_get(client, url: str = '/potato'):
    res = client.get(url)
    data = res.json()

    assert res.status_code == 200
    assert type(data) == list and len(data) == 0


def test_post(client, url: str = '/potato', model: BaseModel = basic_potato):
    res = client.post(url, json=model.dict())
    assert res.status_code == 200

    data = client.get(url).json()
    assert len(data) == 1


def test_get_one(client, url: str = '/potato', model: BaseModel = basic_potato):
    res = client.post(url, json=model.dict())
    assert res.status_code == 200

    data = client.get(url).json()
    assert len(data) == 1

    res = client.get(f'{url}/{data[0]["id"]}')
    assert res.status_code == 200

    assert compare_dict(res.json(), model.dict())


def test_update(client, url: str = '/potato', model: BaseModel = basic_potato):
    res = client.post(url, json=model.dict())
    data = res.json()
    assert res.status_code == 200

    tuber = model.copy()
    tuber.color = 'yellow'

    res = client.put(f'{url}/{data["id"]}', json=tuber.dict())
    assert res.status_code == 200
    assert compare_dict(res.json(), tuber.dict())
    assert not compare_dict(res.json(), model.dict())

    res = client.get(f'{url}/{data["id"]}')
    assert res.status_code == 200
    assert compare_dict(res.json(), tuber.dict())
    assert not compare_dict(res.json(), model.dict())


def test_delete_one(client, url: str = '/potato', model: BaseModel = basic_potato):
    res = client.post(url, json=model.dict())
    data = res.json()
    assert res.status_code == 200

    res = client.get(f'{url}/{data["id"]}')
    assert res.status_code == 200
    assert compare_dict(res.json(), model.dict())

    res = client.delete(f'{url}/{data["id"]}')
    assert res.status_code == 200
    assert compare_dict(res.json(), model.dict())

    res = client.get(url)
    assert res.status_code == 200
    assert len(res.json()) == 0


def test_delete_all(client, url: str = '/potato', model: BaseModel = basic_potato):
    res = client.post(url, json=model.dict())
    assert res.status_code == 200

    res = client.post(url, json=model.dict())
    assert res.status_code == 200

    assert len(client.get(url).json()) == 2

    res = client.delete(url)
    assert res.status_code == 200
    assert len(res.json()) == 0

    assert len(client.get(url).json()) == 0


@pytest.mark.parametrize('id_', [-1, 0, 4, '14'])
def test_not_found(client, id_, url='/potato', model=basic_potato):
    url = f'{url}/{id_}'

    assert client.get(url).status_code == 404
    assert client.put(url, json=model.dict()).status_code == 404
    assert client.delete(url).status_code == 404


def test_dne(client):
    res = client.get('/')
    assert res.status_code == 404

    res = client.get(f'/tomatoes')
    assert res.status_code == 404



