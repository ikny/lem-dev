from random import randint
import numpy as np
from lib.constants import DTYPE
from lib.tracks import RecordedTrack


def test_append():
    r = RecordedTrack()
    a = np.array([[1, 1]], dtype=DTYPE)
    b = np.array([[2, 2] for i in range(2)], dtype=DTYPE)
    c = np.array([[3, 3] for i in range(3)], dtype=DTYPE)

    r.join(a)
    assert r.to_array().all() == a.all()

    r.join(b)
    assert r.to_array().all() == np.concatenate([a, b]).all()

    r.join(c)
    assert r.to_array().all() == np.concatenate([a, b, c]).all()

    print(r.to_array())
    print(np.concatenate([a, b, c]))


def test_init():
    a = RecordedTrack()
    print(a.data)
    assert a.data == []

    b = np.array([[2, 2] for _ in range(2)], dtype=DTYPE)
    c = np.array([[3, 3] for _ in range(3)], dtype=DTYPE)

    a.join(b)
    a.join(c)

    b = RecordedTrack()
    assert b.data == []

def test_append_vs_concat():
    l = []
    a = np.array([[randint(-32768, 32767), randint(-32768, 32767)] for i in range(100)], dtype=DTYPE)
    b = np.array([[randint(-32768, 32767), randint(-32768, 32767)] for i in range(100)], dtype=DTYPE)
    c = np.array([[randint(-32768, 32767), randint(-32768, 32767)] for i in range(100)], dtype=DTYPE)

    l.append(a)
    l.append(b)
    l.append(c)

    lc = np.concatenate(l)
    cc = np.concatenate([a, b, c])
    assert lc.all() == cc.all()


if __name__ == "__main__":
    test_append_vs_concat()
