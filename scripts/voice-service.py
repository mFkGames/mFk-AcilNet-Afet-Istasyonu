#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mFk AcilNet - Çevrimdışı Sesli & Yazılı Afet İletişim Mikro-Servisi
Raspberry Pi üzerinde arka planda çalışarak Wi-Fi hotspot'a bağlı
tüm cihazlar arasında canlı ses anonslarını ve yerel yazılı duyuruları dağıtır.
"""

import http.server
import json
import threading
import time

PORT = 8081
MAX_BODY = 2 * 1024 * 1024        # istek gövdesi üst sınırı (2 MB)
MAX_AUDIO_B64 = 1_500_000         # tek ses paketi üst sınırı (karakter)
VALID_CHANNELS = ('1', '2', '3')
VALID_CATS = ('duyuru', 'acil', 'ihtiyac', 'guvende')

LOCK = threading.Lock()
VOICE_DISPATCHES = []
VOICE_CHANNELS_BUSY = {}
# En yeni mesaj başta.
TEXT_MESSAGES = [
    {
        "cat": "duyuru",
        "text": "mFk AcilNet İstasyonu aktif. Çevrimdışı yerel Wi-Fi ağı üzerinden kesintisiz çalışmaktadır."
    }
]


class VoiceHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # Gereksiz konsol kirliliğini önle

    def _reply(self, code, payload=None):
        body = b'' if payload is None else json.dumps(payload).encode('utf-8')
        self.send_response(code)
        if payload is not None:
            self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        if body:
            self.wfile.write(body)

    def do_OPTIONS(self):
        self._reply(200)

    def do_GET(self):
        path = self.path.split('?')[0]
        now = time.time()

        if path in ('/api/voice/list', '/api/voice/status'):
            with LOCK:
                for ch in list(VOICE_CHANNELS_BUSY.keys()):
                    if VOICE_CHANNELS_BUSY[ch].get('expires', 0) <= now:
                        del VOICE_CHANNELS_BUSY[ch]
                resp = {
                    'busy': dict(VOICE_CHANNELS_BUSY),
                    'dispatches': list(VOICE_DISPATCHES[-30:])
                }
            return self._reply(200, resp)

        if path == '/api/messages':
            with LOCK:
                msgs = list(TEXT_MESSAGES[:30])  # en yeni 30 mesaj
            return self._reply(200, msgs)

        if path in ('/ping', '/health'):
            return self._reply(200, {'status': 'ok'})

        self._reply(404)

    def _read_json(self):
        try:
            length = int(self.headers.get('Content-Length', 0))
        except ValueError:
            return None
        if length < 0 or length > MAX_BODY:
            return None
        raw = self.rfile.read(length) if length > 0 else b'{}'
        try:
            data = json.loads(raw.decode('utf-8'))
        except Exception:
            return None
        return data if isinstance(data, dict) else None

    def do_POST(self):
        path = self.path.split('?')[0]
        now = time.time()

        if path not in ('/api/messages', '/api/voice/busy',
                        '/api/voice/release', '/api/voice/send'):
            return self._reply(404)

        data = self._read_json()
        if data is None:
            return self._reply(400)

        if path == '/api/messages':
            author = str(data.get('author', '')).strip()[:30]
            text = str(data.get('text', '')).strip()[:300]
            cat = str(data.get('cat', 'duyuru')).strip().lower()
            if cat not in VALID_CATS:
                cat = 'duyuru'
            if text:
                msg = {'cat': cat, 'text': text}
                if author and author not in ('SİSTEM', 'ANONİM', 'DUYURU'):
                    msg['author'] = author
                with LOCK:
                    TEXT_MESSAGES.insert(0, msg)
                    del TEXT_MESSAGES[50:]
            return self._reply(200, {'status': 'ok'})

        ch = str(data.get('channel', '1'))
        if ch not in VALID_CHANNELS:
            return self._reply(400)
        sender = str(data.get('sender', 'AFETZEDE')).strip()[:30] or 'AFETZEDE'

        if path == '/api/voice/busy':
            with LOCK:
                active = VOICE_CHANNELS_BUSY.get(ch)
                if active and active['expires'] > now and active['sender'] != sender:
                    return self._reply(200, {'allowed': False, 'busy_by': active['sender']})
                VOICE_CHANNELS_BUSY[ch] = {'sender': sender, 'expires': now + 30}
            return self._reply(200, {'allowed': True})

        if path == '/api/voice/release':
            with LOCK:
                if ch in VOICE_CHANNELS_BUSY and VOICE_CHANNELS_BUSY[ch].get('sender') == sender:
                    del VOICE_CHANNELS_BUSY[ch]
            return self._reply(200, {'status': 'released'})

        # /api/voice/send: yalnızca bilinen alanları, doğrulanmış biçimde sakla
        audio = data.get('audioBase64', '')
        if (not isinstance(audio, str) or len(audio) > MAX_AUDIO_B64
                or not audio.startswith('data:audio/') or ';base64,' not in audio):
            return self._reply(400)
        try:
            duration = max(1, min(int(data.get('duration', 1)), 60))
        except (TypeError, ValueError):
            duration = 1
        item = {
            'id': int(now * 1000),
            'sender': sender,
            'channel': ch,
            'duration': duration,
            'time': str(data.get('time', ''))[:10] or time.strftime('%H:%M:%S'),
            'audioBase64': audio,
        }
        with LOCK:
            VOICE_CHANNELS_BUSY.pop(ch, None)
            VOICE_DISPATCHES.append(item)
            del VOICE_DISPATCHES[:-50]
        return self._reply(200, {'status': 'ok'})


def run():
    http.server.ThreadingHTTPServer.allow_reuse_address = True
    http.server.ThreadingHTTPServer.daemon_threads = True
    with http.server.ThreadingHTTPServer(("0.0.0.0", PORT), VoiceHandler) as httpd:
        print(f"[OK] mFk AcilNet Sesli Telsiz & Mesaj Servisi Port {PORT} uzerinde devrede.")
        httpd.serve_forever()


if __name__ == "__main__":
    run()
