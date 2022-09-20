# pa_sink_mon

Listens for changes to the default PulseAudio sink and makes sure that music doesn't suddenly play out of the built-in speakers.

When the default sink changes away from the built-in speakers, the built-in speakers are muted.

When the default sink changes to the built-in speakers, the command `playerctl pause` is executed to pause any running media.
