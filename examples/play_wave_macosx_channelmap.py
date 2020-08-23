# Copyright 2020 Andrzej Cichocki

# This file is part of outport.
#
# outport is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# outport is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with outport.  If not, see <http://www.gnu.org/licenses/>.

# This file incorporates work covered by the following copyright and
# permission notice:

# Copyright (c) 2006 Hubert Pham
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

"""
PyAudio Example: Mac OS X-only: Play a wave file with channel maps.
"""

import pyaudio
import wave
import sys

chunk = 1024

PyAudio = pyaudio.PyAudio

if len(sys.argv) < 2:
    print("Plays a wave file.\n\nUsage: %s filename.wav" % sys.argv[0])
    sys.exit(-1)

wf = wave.open(sys.argv[1], 'rb')

p = PyAudio()

# standard L-R stereo
# channel_map = (0, 1)

# reverse: R-L stereo
# channel_map = (1, 0)

# no audio
# channel_map = (-1, -1)

# left channel audio --> left speaker; no right channel
# channel_map = (0, -1)

# right channel audio --> right speaker; no left channel
# channel_map = (-1, 1)

# left channel audio --> right speaker
# channel_map = (-1, 0)

# right channel audio --> left speaker
channel_map = (1, -1)
# etc...

try:
    stream_info = pyaudio.PaMacCoreStreamInfo(
        flags=pyaudio.PaMacCoreStreamInfo.paMacCorePlayNice, # default
        channel_map=channel_map)
except AttributeError:
    print("Sorry, couldn't find PaMacCoreStreamInfo. Make sure that "
          "you're running on Mac OS X.")
    sys.exit(-1)

print("Stream Info Flags:", stream_info.get_flags())
print("Stream Info Channel Map:", stream_info.get_channel_map())

# open stream
stream = p.open(
    format=p.get_format_from_width(wf.getsampwidth()),
    channels=wf.getnchannels(),
    rate=wf.getframerate(),
    output=True,
    output_host_api_specific_stream_info=stream_info)

# read data
data = wf.readframes(chunk)

# play stream
while len(data) > 0:
    stream.write(data)
    data = wf.readframes(chunk)

stream.stop_stream()
stream.close()

p.terminate()
