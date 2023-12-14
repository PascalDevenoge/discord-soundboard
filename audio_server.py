import discord
from discord.ext import tasks

import numpy as np

import multiprocessing
import multiprocessing.connection
import threading
from dataclasses import dataclass

import data_access
from event import Event, EventType

from sqlalchemy import Engine
from sqlalchemy.orm import Session

from pydub import AudioSegment

import logging

from typing import Tuple, Generator

FRAME_LENGTH: int = int(48000 * 0.02)

log = logging.getLogger('audio-server')

active_clip_list: list[Generator] = []
active_clip_list_lock = threading.Lock()


def audio_server_main(shutdown_event: multiprocessing.Event, api_token: str, voice_channel_name: str):
    playback_active = threading.Event()

    command_receiver_thread = threading.Thread(
        target=command_processor_main, name='Command processor', args=[shutdown_event, playback_active])
    command_receiver_thread.start()

    bot_client = BotClient(shutdown_event, playback_active, voice_channel_name)
    bot_client.run(api_token, log_handler=None)


def command_processor_main(shutdown_event: multiprocessing.Event, playback_active: threading.Event):
    global active_clip_list
    global active_clip_list_lock

    log.info("Starting up")
    engine : Engine = data_access.init()
    event_connection = multiprocessing.connection.Client('discord-soundboard/event-broker')
    while not shutdown_event.is_set():
        while event_connection.poll():
            event : Event = event_connection.recv()
            match event.type:
                case EventType.PLAY_CLIP:
                    with Session(engine) as session:
                        track = data_access.get_track(session, event.id)
                        if track is None:
                            log.info(f"Cannot play track {event.id}. Track not in database")
                        else:
                            with active_clip_list_lock:
                                active_clip_list.append(track.samples[::20])
                case EventType.PLAY_ALL:
                    with Session(engine) as session:
                        tracks = data_access.get_all_tracks(session)
                        with active_clip_list_lock:
                            for track in tracks:
                                active_clip_list.append(track.samples[::20])
                case EventType.STOP_ALL:
                    with active_clip_list_lock:
                        active_clip_list = []

    log.info("Shutting down")


class ClipMixingAudioSource(discord.AudioSource):
    def __init__(self, playback_active) -> None:
        self.playback_active = playback_active
        self.playback_active.set()

    def cleanup(self) -> None:
        self.playback_active.clear()

    def read(self) -> bytes:
        global active_clip_list
        global active_clip_list_lock

        finished_frame = AudioSegment.silent(duration=20, frame_rate=48000).set_sample_width(2).set_channels(2)

        with active_clip_list_lock:
            unfinished_clips : list[Generator] = []
            for active_track in active_clip_list:
                try:
                    finished_frame = finished_frame.overlay(next(active_track))
                except StopIteration:
                    continue
                else:
                    unfinished_clips.append(active_track)
            active_clip_list = unfinished_clips

        return finished_frame.raw_data


class BotClient(discord.Client):
    def __init__(self, shutdown_event: multiprocessing.Event, playback_active: threading.Event, voice_channel_name: str) -> None:
        self.shutdown_event = shutdown_event
        self.voice_channel_name = voice_channel_name
        self.voice_channel = None
        self.audio_client = None
        self.playback_active = playback_active

        super().__init__(intents=discord.Intents.default())

    async def _join_leave(self):
        if self.audio_client == None or not self.audio_client.is_connected():
            # Not connected to channel
            target_channels = [ch for ch in self.get_all_channels(
            ) if ch.type == discord.ChannelType.voice and ch.name == self.voice_channel_name]
            if len(target_channels) == 0:
                # No target channel present
                return
            else:
                # Target channel found
                if len(target_channels) > 1:
                    log.warning(
                        f'Unexpected number of channels with name {self.voice_channel_name} found')
                self.voice_channel = target_channels[0]
                if len(self.voice_channel.members) == 0:
                    # No members in target voice channel
                    return
                else:
                    # Activate audio stream

                    # FIXME: Something, the client attempts to connect to the same channel again while already joined
                    try:
                        self.audio_client = await self.voice_channel.connect()
                    except discord.ClientException as e:
                        log.error(
                            f"Failed to connect to voice channel: {e.args[0]}")
                    else:
                        self.audio_client.play(
                            ClipMixingAudioSource(self.playback_active))
        else:
            # Connected to channel
            if len(self.voice_channel.members) == 1:
                # Alone in channel
                await self.audio_client.disconnect()
            else:
                # Clients connected to channel
                if self.audio_client.is_playing():
                    # Stream online
                    return
                else:
                    # Audio stream is not playing
                    self.audio_client.play(
                        ClipMixingAudioSource(self.playback_active))

    async def on_ready(self):
        log.info("Starting up")
        await self._join_leave()
        self.stream_replay_task.start()
        self.shutdown_task.start()

    async def on_voice_state_update(self, member, _, __):
        if member == self.user:
            return
        await self._join_leave()

    @tasks.loop(seconds=1)
    async def stream_replay_task(self):
        await self._join_leave()

    @tasks.loop(seconds=1)
    async def shutdown_task(self):
        if self.shutdown_event.is_set():
            log.info("Shutting down")
            raise KeyboardInterrupt