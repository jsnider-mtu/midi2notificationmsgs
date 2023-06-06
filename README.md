# Midi2NotificationMsgs

This script will create NotificationSequence objects for each channel in the midi file, meant to be used in Flipper Applications (FAP)

The objects each have the `include` statements so that you can easily delete the preceding and succeeding lines more easily

### Usage

`python midi2notificationmsgs.py file.mid > <song_name>.h`

Then locate the channel you want and rename it to \<song\_name\>. The rest of the contents of the file can be removed

Be sure to `#include` the file in your program
