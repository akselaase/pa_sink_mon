#!/usr/bin/env python3

import re
import sys
import subprocess
from typing import IO, Iterable


builtin_speakers = 'alsa_output.pci-0000_00_1f.3.analog-stereo'


def iter_pactl(stream: IO[str]) -> Iterable[tuple[str, str, str]]:
    pattern = re.compile(r'Event \'([-a-z]+)\' on ([-a-z]+) #(\d+)')
    for line in stream:
        if m := pattern.match(line):
            yield m.group(1, 2, 3)
        else:
            print(f'Unexpected line: "{line.rstrip()}"', file=sys.stderr)


def get_default_sink() -> str:
    p_get = subprocess.Popen(
        ['pactl', 'get-default-sink'],
        encoding='utf-8',
        stdout=subprocess.PIPE,
    )
    stdout, _ = p_get.communicate()
    return stdout.strip()


def handle_new_sink(prev_sink, new_sink: str):
    print(f'Changed from {prev_sink} to {new_sink}')
    if prev_sink == builtin_speakers:
        print(f'Connected to external sink, muting.')
        subprocess.run(['pactl', 'set-sink-mute', builtin_speakers, '1'])
    if new_sink == builtin_speakers:
        print(f'Connected to builtin speakers, pausing.')
        subprocess.run(['playerctl', 'pause'])


def main():
    p_mon = subprocess.Popen(
        ['pactl', 'subscribe'],
        bufsize=1,
        encoding='utf-8',
        stdout=subprocess.PIPE,
    )
    
    prev_sink = get_default_sink()

    for event, target, id in iter_pactl(p_mon.stdout):
        if event in ('new', 'change', 'remove') and target in ('sink', 'card'):
            new_sink = get_default_sink()
            if new_sink != prev_sink:
                handle_new_sink(prev_sink, new_sink)
                prev_sink = new_sink


if __name__ == '__main__':
    main()
