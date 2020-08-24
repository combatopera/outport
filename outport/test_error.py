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

import sys
import time
import unittest

import outport

class PyAudioErrorTests(unittest.TestCase):
    def setUp(self):
        self.p = outport.PyAudio()

    def tearDown(self):
        self.p.terminate()

    def test_invalid_sample_size(self):
        with self.assertRaises(ValueError):
            self.p.get_sample_size(10)

    def test_invalid_width(self):
        with self.assertRaises(ValueError):
            self.p.get_format_from_width(8)

    def test_invalid_device(self):
        with self.assertRaises(IOError):
            self.p.get_host_api_info_by_type(-1)

    def test_invalid_hostapi(self):
        with self.assertRaises(IOError):
            self.p.get_host_api_info_by_index(-1)

    def test_invalid_host_api_devinfo(self):
        with self.assertRaises(IOError):
            self.p.get_device_info_by_host_api_device_index(0, -1)

        with self.assertRaises(IOError):
            self.p.get_device_info_by_host_api_device_index(-1, 0)

    def test_invalid_device_devinfo(self):
        with self.assertRaises(IOError):
            self.p.get_device_info_by_index(-1)

    def test_error_without_stream_start(self):
        with self.assertRaises(IOError):
            stream = self.p.open(channels=1,
                                 rate=44100,
                                 format=outport.paInt16,
                                 input=True,
                                 start=False)  # not starting stream
            stream.read(2)

    def test_error_writing_to_readonly_stream(self):
        with self.assertRaises(IOError):
            stream = self.p.open(channels=1,
                                 rate=44100,
                                 format=outport.paInt16,
                                 input=True)
            stream.write('foo')

    def test_error_negative_frames(self):
        with self.assertRaises(ValueError):
            stream = self.p.open(channels=1,
                                 rate=44100,
                                 format=outport.paInt16,
                                 input=True)
            stream.read(-1)

    def test_invalid_attr_on_closed_stream(self):
        stream = self.p.open(channels=1,
                             rate=44100,
                             format=outport.paInt16,
                             input=True)
        stream.close()
        with self.assertRaises(IOError):
            stream.get_input_latency()
        with self.assertRaises(IOError):
            stream.read(1)

    def test_invalid_format_supported(self):
        with self.assertRaises(ValueError):
            self.p.is_format_supported(8000, -1, 1, outport.paInt16)

        with self.assertRaises(ValueError):
            self.p.is_format_supported(8000, 0, -1, outport.paInt16)

    def test_write_underflow_exception(self):
        stream = self.p.open(channels=1,
                             rate=44100,
                             format=outport.paInt16,
                             output=True)
        time.sleep(0.5)
        stream.write('\x00\x00\x00\x00', exception_on_underflow=False)

        # It's difficult to invoke an underflow on ALSA, so skip.
        if sys.platform in ('linux', 'linux2'):
            return

        with self.assertRaises(IOError) as err:
            time.sleep(0.5)
            stream.write('\x00\x00\x00\x00', exception_on_underflow=True)

        self.assertEqual(err.exception.errno, outport.paOutputUnderflowed)
        self.assertEqual(err.exception.strerror, 'Output underflowed')

    def test_read_overflow_exception(self):
        stream = self.p.open(channels=1,
                             rate=44100,
                             format=outport.paInt16,
                             input=True)
        time.sleep(0.5)
        stream.read(2, exception_on_overflow=False)

        # It's difficult to invoke an underflow on ALSA, so skip.
        if sys.platform in ('linux', 'linux2'):
            return

        with self.assertRaises(IOError) as err:
            time.sleep(0.5)
            stream.read(2, exception_on_overflow=True)

        self.assertEqual(err.exception.errno, outport.paInputOverflowed)
        self.assertEqual(err.exception.strerror, 'Input overflowed')
