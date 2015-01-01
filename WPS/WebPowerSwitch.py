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
    re_descriptions = re.compile(r'^<tr bgcolor="#[0-9A-F]{6}"><td align=center>(\d)</td>$.^<td>([\w+\s+]*)</td><td>$', re.M | re.S)
    re_state = re.compile("^<!-- state=[0-9a-f]{2} lock=[0-9a-f]{2} -->$", re.M)

    def __init__(self, address=None, port=None, username=None, password=None):
        self.host     = address  or self.defaults['address']
        self.port     = port     or self.defaults['port']
        self.username = username or self.defaults['username']
        self.password = password or self.defaults['password']

        self.names = {}
        t = self._get_info(self.re_descriptions)
        for e in t:
            self.names[int(e[0])]=e[1]

    def get_name(self, outlet):
        """Gets the name of a outlet"""
        return self.names.get(outlet)

    def get_names(self):
        """Gets the names of all the outlets"""
        return self.names;

    def on(self, outlet):
        """Turns on a port on the Web Power Switch."""
        self._action(outlet, 'ON')
        if not self.get_status(outlet):
            raise InvalidPowerStateException("Failed to turn on power.")

    def all_on(self):
        """Turns on all ports on the Web Power Switch."""
        self._action('a', 'ON')

    def off(self, outlet):
        """Turns off a port on the Web Power Switch."""
        self._action(outlet, 'OFF')
        if self.get_status(outlet):
            raise InvalidPowerStateException("Failed to turn off power.")

    def all_off(self):
        """Turns off all ports on the Web Power Switch."""
        self._action('a', 'OFF')

    def cycle(self, outlet, delay=None):
        """Power cycles a port on the Web Power Switch.
        If no delay is specified, will use the controller's default value and
        will not block. Otherwise, will block.
        """
        if not delay:
            self._action(outlet, 'CCL')
        else:
            self.off(outlet)
            time.sleep(int(delay))
            self.on(outlet)

    def cycle_all(self):
        self._action('a', 'CCL')

    def get_status(self, outlet):
        """Gets the current status of a port on the Web Power Switch"""
        # because the outlets start at 0 when represented here, not 1
        outlet -= 1

        status = self._get_info(self.re_state)[0]

        state = int(status.split()[1][-2:], 16)
        lock = int(status.split()[2][-2:], 16)

        #print("{0:b} & (1 << {1}) > 0 = {2}".format(state, port, state & (1 << port) > 0))
        return state & (1 << outlet) > 0

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


class InvalidPowerStateException(Exception):
    """ Raised if a power state change is requested but doesn't happen """
    def _init_(self, msg=None):
        self.msg = msg

    def _str_(self):
        return msg
