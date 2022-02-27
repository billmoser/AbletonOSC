from functools import partial
from typing import Tuple, Any
from .handler import AbletonOSCHandler
from .osc_server import toOscMessage

class SongHandler(AbletonOSCHandler):

    def init_api(self):
        #--------------------------------------------------------------------------------
        # Init callbacks for Set: methods
        #--------------------------------------------------------------------------------
        for method in [
            "start_playing",
            "stop_playing",
            "continue_playing",
            "stop_all_clips",
            "create_audio_track",
            "create_midi_track",
            "create_return_track",
            "create_scene",
            "jump_by"
        ]:
            callback = partial(self._call_method, self.song, method)
            self.osc_server.add_handler("/live/song/%s" % method, callback)

        #--------------------------------------------------------------------------------
        # Init callbacks for Set: properties
        #--------------------------------------------------------------------------------
        properties_rw = [
            "arrangement_overdub",
            "back_to_arranger",
            "clip_trigger_quantization",
            "current_song_time",
            "groove_amount",
            "loop",
            "loop_length",
            "loop_start",
            "metronome",
            "midi_recording_quantization",
            "nudge_down",
            "nudge_up",
            "punch_in",
            "punch_out",
            "record_mode",
            "tempo"
        ]
        properties_r = [
            "is_playing"
        ]

        for prop in properties_r + properties_rw:
            self.osc_server.add_handler("/live/song/get/%s" % prop, partial(self._get, self.song, prop))
            self.osc_server.add_handler("/live/song/start_listen/%s" % prop, partial(self._start_listen, self.song, prop))
            self.osc_server.add_handler("/live/song/stop_listen/%s" % prop, partial(self._stop_listen, self.song, prop))
        for prop in properties_rw:
            self.osc_server.add_handler("/live/song/set/%s" % prop, partial(self._set, self.song, prop))

        def song_get_num_tracks(song, params: Tuple[Any] = ()):
            return len(song.tracks),

        # TODO num_tracks listener
        self.osc_server.add_handler("/live/song/get/num_tracks", partial(song_get_num_tracks, self.song))

        self.last_song_time = -1.0

        def song_time_changed():
            key = "beat"
            # If song has rewound or skipped to next beat, sent a /live/beat message
            if (self.song.current_song_time < self.last_song_time) or \
                    (int(self.song.current_song_time) > int(self.last_song_time)):
                value = int(self.song.current_song_time)
                msg = toOscMessage("/live/song/beat", (value,))
                self.publisher.publish(key, msg)
            self.last_song_time = self.song.current_song_time

        self.song.add_current_song_time_listener(song_time_changed)

        def _start_listen_beat(params) -> None: 
            key = "beat"
            self.publisher.add_listener(key) # adds current client as listener

        def _stop_listen_beat(params) -> None:
            key = "beat"
            self.publisher.remove_listener(key) # removes current client as listener

        self.osc_server.add_handler("/live/song/start_listen/beat", _start_listen_beat)
        self.osc_server.add_handler("/live/song/stop_listen/beat", _stop_listen_beat)
