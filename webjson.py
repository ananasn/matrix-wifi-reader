# -*- coding: future_fstrings -*-

import json

from datetime import datetime
#from http.server import BaseHTTPRequestHandler, HTTPServer
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

IP = '0.0.0.0'
PORT = 8181

SERIAL_NUMBER = 50623
TYPE = 'MATRIX II WIFI'
ONLINE_FLAG = 0


class WebJsonHandler(BaseHTTPRequestHandler):


    def do_GET(self):
        self.send_error(501, 'Not Implemented')

    def do_POST(self):
        length = self.check_length()
        jsn = self.get_json(length)
        print(jsn)
        self.send(self.parse(jsn))

    def check_length(self):
        length = int(self.headers['content-length'])
        if length > 2000:
            self.send_error(400, 'Bad Request')
            return
        return length

    def get_json(self, length):
        try:
            return json.loads(self.rfile.read(length))
        except:
            self.send_error(400, 'Bad Request')
            return

    def check_sn(self, jsn):
        if jsn.get('sn') is not None:
            return True if jsn['sn'] == SERIAL_NUMBER else False
        else:
            return  False

    def check_type(self, jsn):
        if jsn.get('type') is not None:
            return True if jsn['type'] == TYPE else False
        else:
            return False

    def parse(self, jsn):
        answer = []

        for msg in jsn['messages']:
            cmd = msg.get('operation')

            if cmd is None :
                if msg.get('success') == 1:
                    print('SUCCESS')
                    answer = self._response()

            elif cmd == 'power_on':
                print('POWER ON')
                answer = self.cl_set_active()

            elif cmd == 'ping':
                print('PING')
                answer = self._response()

            elif cmd == 'events':
                print('EVENTS')
                answer = self.cl_events_success(msg)
            else:
                answer = self._response()
                print(f'Received unknown command from {TYPE}')
        return answer


    def cl_set_mode(self, mode=0):
        response = self._response()
        response['messages'] = {
                                'id': 0,
                                'operation': 'set_mode',
                                'mode': mode
                                }
        return response

    def cl_events_success(self, cmd):
        response = self._response()
        response['messages'] = [{
                                'id': 0,
                                'operation': 'events',
                                'events_success': len(cmd['events'])
                                }]
        return response

    def cl_set_active(self, active=1):
        response = self._response()
        response['messages'] = [{
                                'id': 0,
                                'operation': 'set_active',
                                'active': active,
                                'online': ONLINE_FLAG
                                }]
        return response

    def _response(self):
        return {
                'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'interval': 10,
                'messages': []
                }

    def send(self, msg):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        #answer = bytes(json.dumps(msg), 'utf-8')
        answer = json.dumps(msg)
        print(type(answer))
        self.wfile.write(answer)
        print(f'Send to reader {json.dumps(msg)}')

def run():
  server_address = (IP, PORT)
  httpd = HTTPServer(server_address, WebJsonHandler)
  print(f'Running {TYPE} web-json server with {IP} on {PORT}...')
  httpd.serve_forever()


if __name__ == '__main__':
    run()
