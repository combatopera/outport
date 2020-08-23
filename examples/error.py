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
PyAudio Example: Test for a variety of error conditions. This example
demonstrates exception handling with PyAudio.
"""

import pyaudio

p = pyaudio.PyAudio()

# get invalid sample size
try:
    p.get_sample_size(10)
except ValueError as e:
    assert e.args[1] == pyaudio.paSampleFormatNotSupported
    print("OK: %s" % e.args[0])
else:
    assert False, "sample size"

# get format from invalid width
try:
    p.get_format_from_width(8)
except ValueError:
    print("OK: invalid format from width")
else:
    assert False, "invalid format"

# try to get an invalid device
try:
    p.get_host_api_info_by_type(-1)
except IOError as e:
    assert e.args[1] == pyaudio.paHostApiNotFound
    print("OK: %s" % e.args[0])
else:
    assert False, "invalid host type"

# try to get host api info by index
try:
    p.get_host_api_info_by_index(-1)
except IOError as e:
    assert e.args[1] == pyaudio.paInvalidHostApi
    print("OK: %s" % e.args[0])
else:
    assert False, "invalid host api index"

# try good host api device index
try:
    p.get_device_info_by_host_api_device_index(0, -1)
except IOError as e:
    assert ((e.args[1] == pyaudio.paInvalidDevice) or \
            (e.args[1] == pyaudio.paInvalidHostApi))
    print("OK: %s" % e.args[0])
else:
    assert False, "device info by host api device idnex"


# try bad host api and good device index
try:
    p.get_device_info_by_host_api_device_index(-1, 0)
except IOError as e:
    assert ((e.args[1] == pyaudio.paInvalidDevice) or \
            (e.args[1] == pyaudio.paInvalidHostApi))
    print("OK: %s" % e.args[0])
else:
    assert False, "device info by host api device idnex"


# bad device index
try:
    p.get_device_info_by_index(-1)
except IOError as e:
    assert e.args[1] == pyaudio.paInvalidDevice
    print("OK: %s" % e.args[0])
else:
    assert False, "bad device index"

### now for some real work ###

stream = p.open(channels = 1,
                rate = 44100,
                format = pyaudio.paInt16,
                input = True,
                start = False)

# (note that we didn't start the stream!)

try:
    data = stream.read(2)
except IOError as e:
    print("OK: %s" % e.args[0])
    assert e.args[1] == pyaudio.paStreamIsStopped, e.args[1]
else:
    assert False, "Should have caused exception"

stream.start_stream()

# try to write to the input stream
try:
    stream.write('foobar')
except IOError as e:
    assert e.args[1] == pyaudio.paCanNotWriteToAnInputOnlyStream
    print("OK: %s" % e.args[0])
else:
    assert False, "write to input stream"

# read some negative data
try:
    data = stream.read(-1)
except ValueError:
    print("OK: Invalid frames")
else:
    assert False, "invalid frames"

# read some real data
try:
    data = stream.read(2)
except IOError as e:
    # some slower machines might overflow
    assert e.args[1] == pyaudio.paInputOverflowed, e
    print("OK: %s" % e.args[0])
else:
    print("OK: got %d bytes of data" % len(data))

# close the stream; nothing should work with
# this stream afterwards

stream.close()

# query for properties
try:
    stream.get_input_latency()
except IOError as e:
    assert e.args[1] == pyaudio.paBadStreamPtr
    print("OK: %s" % e.args[0])
else:
    assert False, "closed stream"

# read some data again
try:
    stream.read(10)
except IOError as e:
    assert e.args[1] == pyaudio.paBadStreamPtr
    print("OK: %s" % e.args[0])
else:
    assert False, "closed stream"

# get invalid stream capabilities
try:
    p.is_format_supported(8000, -1, 1, pyaudio.paInt16)
except ValueError as e:
    assert e.args[1] == pyaudio.paInvalidDevice
    print("OK: %s" % e.args[0])
else:
    assert False, "invalid device"

# get invalid stream capabilities
try:
    p.is_format_supported(8000, 0, -1, pyaudio.paInt16)
except ValueError as e:
    assert e.args[1] == pyaudio.paInvalidChannelCount
    print("OK: %s" % e.args[0])
else:
    assert False, "invalid number of channels"

p.terminate()
