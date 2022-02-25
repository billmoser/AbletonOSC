
from . import send_message, server, query_and_await, await_reply, wait_one_tick

def test_song_tempo_get(server):
    send_message(server, "/live/song/set/tempo", [120.0])
    assert query_and_await(server, "/live/song/get/tempo",
                           lambda _, *params: params[0] == 120.0)
    send_message(server, "/live/song/set/tempo", [125.0])
    assert query_and_await(server, "/live/song/get/tempo",
                           lambda _, *params: params[0] == 125.0)


def test_song_start_playing(server):
    send_message(server, "/live/song/start_playing", [])
    wait_one_tick()
    assert query_and_await(server, "/live/song/get/is_playing",
                           lambda _, *params: params[0] is True)

    send_message(server, "/live/song/stop_playing", [])
    wait_one_tick()
    assert query_and_await(server, "/live/song/get/is_playing",
                           lambda _, *params: params[0] is False)

def test_song_beat(server):
    send_message(server, "/live/song/stop_playing", [])
    send_message(server, "/live/song/start_playing", [])
    send_message(server, "/live/song/start_listen/beat", [])
    assert await_reply(server, "/live/song/beat", lambda _, *params: params[0] == 0, timeout=1.0)
    assert await_reply(server, "/live/song/beat", lambda _, *params: params[0] == 1, timeout=1.0)
    assert await_reply(server, "/live/song/beat", lambda _, *params: params[0] == 2, timeout=1.0)
    send_message(server, "/live/song/stop_playing", [])
    send_message(server, "/live/song/stop_listen/beat", [])

