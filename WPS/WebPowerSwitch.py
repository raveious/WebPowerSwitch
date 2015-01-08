"""
Web Power Switch
"""

from urllib.request import Request, urlopen
import time
import sys
import base64
import re


class WebPowerSwitch(object):
    """
    Digital Logger web power switch.
    """

    # out of the box defaults
    defaults = {
        'address': '192.168.0.100',
        'port': 80,
        'username': 'admin',
        'password': '1234'
    }

    def __init__(self, address=None, port=None, username=None, password=None):
        self.host     = address  or self.defaults['address']
        self.port     = port     or self.defaults['port']
        self.username = username or self.defaults['username']
        self.password = password or self.defaults['password']

        self.outlet = {}
        re_descriptions = re.compile(r'^<tr bgcolor="#[0-9A-F]{6}"><td align=center>(\d)</td>$.^<td>([\w+\s+]*)</td><td>$', re.M | re.S)

        for e in self._get_info(re_descriptions):
            self.outlet[int(e[0])] = self.Outlet(self, int(e[0]), e[1])

    def all_on(self):
        """Turns on all ports on the Web Power Switch."""
        for n, o in power.outlet.items():
            o.on()

    def all_off(self):
        """Turns off all ports on the Web Power Switch."""
        for n, o in power.outlet.items():
            o.off()
    def cycle_all(self):
        """Cycles all ports on the Web Power Switch with the system delay."""
        for n, o in power.outlet.items():
            o.cycle()

    def _build_url(self, url):
        """ Build the URL and authentication """
        request = Request(url)

        # Make the authentication stuff
        auth = ('%s:%s' % (self.username, self.password)).encode('utf-8')
        base64string = base64.encodestring(auth)[:-1]
        request.add_header("Authorization", "Basic %s" % base64string.decode("utf-8"))

        return request

    def _action(self, port, state):
        """Does all the setting actions to the Web Power Switch"""

        # Build the URL
        request = self._build_url("http://%s/outlet?%s=%s" % (self.host, port, state))

        # try to do the action
        response = urlopen(request)
        result = response.read()

    def _get_info(self, regex):
        """Gets from the Web Power Switch by opening the page and using a
        regular expression to find information. The regex used in passed as
        the argument. Returning an array of matches.
        """

        # Build the URL
        request = self._build_url("http://%s/index.htm" % self.host)

        # try to do the action
        response = urlopen(request)
        result = response.read()

        return regex.findall(result.decode())

    class Outlet(object):
        re_state = re.compile("^<!-- state=[0-9a-f]{2} lock=[0-9a-f]{2} -->$", re.M)

        def __init__(self, wps, number, name):
            self._wps = wps
            self.number = number
            self.name = name
            
        def on(self):
            """Turns on a port on the Web Power Switch."""
            self._wps._action(self.number, 'ON')
            if not self.status():
                raise InvalidPowerStateException("Failed to turn on power.")

        def off(self):
            """Turns off a port on the Web Power Switch."""
            self._wps._action(self.number, 'OFF')
            if self.status():
                raise InvalidPowerStateException("Failed to turn off power.")


        def cycle(self, delay=None):
            """Power cycles a port on the Web Power Switch.
            If no delay is specified, will use the controller's default value and
            will not block. Otherwise, will block.
            """
            if not delay:
                self._wps._action(self.number, 'CCL')
            else:
                self.off(self.number)
                time.sleep(int(delay))
                self.on(self.number)

        def status(self):
            """Gets the current status of a port on the Web Power Switch"""
            status = self._wps._get_info(self.re_state)[0]

            state = int(status.split()[1][-2:], 16)
            lock = int(status.split()[2][-2:], 16)

            # because the outlets start at 0 when represented here, not 1
            return state & (1 << (self.number - 1)) > 0

class InvalidPowerStateException(Exception):
    """ Raised if a power state change is requested but didn't happen """
    def _init_(self, msg=None):
        self.msg = msg

    def _str_(self):
        return msg
