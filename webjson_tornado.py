import json
from datetime import datetime

import tornado.httpserver as httpserver
import tornado.ioloop as ioloop
import tornado.web as web

PORT = 8181
SERIAL_NUMBER = 50623
TYPE = 'MATRIX II WIFI'
ONLINE_FLAG = 0


class WebJsonHandler(web.RequestHandler):
    def get(self):
        raise web.HTTPError(501)

    def post(self):
        jsn = self.get_json()
        self.send(self.parse(jsn))

    def get_length(self):
        return int(self.request.headers['content-length'])

    def get_json(self):
        try:
            return json.loads(self.request.body)
        except:
            raise web.HTTPError(400)

    def check_sn(self, jsn):
        if jsn.get('sn') is not None:
            return True if jsn['sn'] == SERIAL_NUMBER else False
        else:
            return False

    def check_type(self, jsn):
        if jsn.get('type') is not None:
            return True if jsn['type'] == TYPE else False
        else:
            return False

    def parse(self, jsn):
        answer = []

        for msg in jsn['messages']:
            cmd = msg.get('operation')

            if cmd is None:
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
        response['messages'] = [{
            'id': 0,
            'operation': 'set_mode',
            'mode': mode
            }]
        return response

    def cl_events_success(self, msg):
        response = self._response()
        response['messages'] = [{
            'id': 0,
            'operation': 'events',
            'events_success': len(msg['events'])
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
        self.set_header("Content-Type", "application/json")
        self.write(json.dumps(msg))
        print(f'Send to reader {json.dumps(msg)}')


def run():
    application = web.Application([
        (r"/", WebJsonHandler),
        ])
    http_server = httpserver.HTTPServer(application)
    http_server.listen(PORT)
    ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    run()
