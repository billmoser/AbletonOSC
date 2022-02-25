from . import send_message, server, await_reply, wait_one_tick

def test_clip_add_notes(server):
    send_message(server, "/live/clip_slot/delete_clip", [0, 0])
    send_message(server, "/live/clip_slot/create_clip", [0, 0, 4.0])
    wait_one_tick()
    send_message(server, "/live/clip/add_new_note", [0, 0, 60, 0.0, 0.25, 64, False])
    send_message(server, "/live/clip/add_new_note", [0, 0, 67, 0.25, 0.5, 32, False])
    def check_notes(_, *params):
        assert params[:5] == (60, 0.0, 0.25, 64, False)
        assert params[5:10] == (67, 0.25, 0.5, 32, False)
        return True

    send_message(server, "/live/clip/get/notes", [0, 0])
    assert await_reply(server, "/live/clip/get/notes", check_notes)
