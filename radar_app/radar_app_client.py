#!/usr/bin/env python3
import logging
import socket
import traceback
import sys
import selectors
import json
import io
import struct

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(levelname)s %(threadName)s %(name)s %(message)s")
logger = logging.getLogger('RADAR APP CLIENT')
logger.setLevel(logging.DEBUG)


def _create_request_message(methode, parameter):
    return dict(
        type="text/json",
        encoding="utf-8",
        content=dict(methode=methode, parameter=parameter),
    )


class RadarAppClient:

    settings = None
    host = None
    port = None

    def send_server_request(self, methode, parameter):
        sel = selectors.DefaultSelector()
        address = (self.host, self.port)
        logger.info("Starting connection to %s", address)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setblocking(False)
        sock.connect_ex(address)
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        request = _create_request_message(methode, parameter)
        message = Message(sel, sock, address, request, self.radar_app_controller)
        sel.register(sock, events, data=message)

        try:
            while True:
                events = sel.select(timeout=1)
                for key, mask in events:
                    message = key.data
                    try:
                        message.process_events(mask)
                    except Exception:
                        logger.error("main: error: exception for %s: \n%s", message.addr, traceback.format_exc())
                        message.close()
                # Check for a socket being monitored to continue.
                if not sel.get_map():
                    break
        except KeyboardInterrupt:
            logger.error("Caught keyboard interrupt, exiting")
        finally:
            sel.close()

    def __init__(self, radar_app_controller):
        self.radar_app_controller = radar_app_controller

        with open("settings.json") as file:
            self.settings = json.load(file)

        self.host, self.port = self.settings["host-ip"], int(self.settings["host-port"])


class Message:
    def __init__(self, selector, sock, addr, request, radar_app_controller):
        self.selector = selector
        self.sock = sock
        self.addr = addr
        self.request = request
        self._recv_buffer = b""
        self._send_buffer = b""
        self._request_queued = False
        self._jsonheader_len = None
        self.jsonheader = None
        self.response = None
        self.radar_app_controller = radar_app_controller


    def _set_selector_events_mask(self, mode):
        """Set selector to listen for events: mode is 'r', 'w', or 'rw'."""
        if mode == "r":
            events = selectors.EVENT_READ
        elif mode == "w":
            events = selectors.EVENT_WRITE
        elif mode == "rw":
            events = selectors.EVENT_READ | selectors.EVENT_WRITE
        else:
            raise ValueError(f"Invalid events mask mode {repr(mode)}.")
        self.selector.modify(self.sock, events, data=self)

    def _read(self):
        try:
            # Should be ready to read
            data = self.sock.recv(4096)
            logger.debug("Data received")
        except BlockingIOError:
            # Resource temporarily unavailable (errno EWOULDBLOCK)
            logger.error("Blocking errror")
            pass
        else:
            if data:
                self._recv_buffer += data
            else:
                raise RuntimeError("Peer closed.")

    def _write(self):
        if self._send_buffer:
            logger.info("Sending %s to %s", repr(self._send_buffer), self.addr)
            try:
                # Should be ready to write
                sent = self.sock.send(self._send_buffer)
            except BlockingIOError:
                # Resource temporarily unavailable (errno EWOULDBLOCK)
                logger.error("BlockingIORead")
                pass
            else:
                self._send_buffer = self._send_buffer[sent:]

    def _json_encode(self, obj, encoding):
        return json.dumps(obj, ensure_ascii=False).encode(encoding)

    def _json_decode(self, json_bytes, encoding):
        tiow = io.TextIOWrapper(
            io.BytesIO(json_bytes), encoding=encoding, newline=""
        )
        obj = json.load(tiow)
        tiow.close()
        return obj

    def _create_message(
            self, *, content_bytes, content_type, content_encoding
    ):
        jsonheader = {
            "byteorder": sys.byteorder,
            "content-type": content_type,
            "content-encoding": content_encoding,
            "content-length": len(content_bytes),
        }
        jsonheader_bytes = self._json_encode(jsonheader, "utf-8")
        message_hdr = struct.pack(">H", len(jsonheader_bytes))
        message = message_hdr + jsonheader_bytes + content_bytes
        return message

    def _process_response_json_content(self):
        if self.response.get("methode") == "RESPONSE":
            logger.info("Received Response: Methode: %s; Description: %s; Value: %s", self.response.get("methode"),
                        self.response.get("description"), self.response.get("value"))
            self.radar_app_controller.process_response(self.response)


    def process_events(self, mask):
        if mask & selectors.EVENT_READ:
            self.read()
        if mask & selectors.EVENT_WRITE:
            self.write()

    def read(self):
        self._read()

        if self._jsonheader_len is None:
            self.process_protoheader()

        if self._jsonheader_len is not None:
            if self.jsonheader is None:
                self.process_jsonheader()

        if self.jsonheader:
            if self.response is None:
                self.process_response()

    def write(self):
        # INFO Wenn init request nicht geqeued ist, wird sie hier gequeued
        if not self._request_queued:
            self.queue_request()

        self._write()

        if self._request_queued:
            if not self._send_buffer:
                # Set selector to listen for read events, we're done writing.
                self._set_selector_events_mask("r")

    def close(self):
        logger.info("Closing connection to %s", self.addr)
        try:
            self.selector.unregister(self.sock)
        except Exception as e:
            logger.error("error: selector.unregister() exception for %s: %s", self.addr, repr(e))

        try:
            self.sock.close()
        except OSError as e:
            logger.error("error: socket.close() exception for %s: %s", self.addr, repr(e))
        finally:
            # Delete reference to socket object for garbage collection
            self.sock = None

    def queue_request(self):
        content_type = self.request["type"]
        content_encoding = self.request["encoding"]
        content = self.request["content"]
        if content_type == "text/json":
            req = {
                "content_bytes": self._json_encode(content, content_encoding),
                "content_type": content_type,
                "content_encoding": content_encoding,
            }
        else:
            req = {
                "content_bytes": content,
                "content_type": content_type,
                "content_encoding": content_encoding,
            }
        message = self._create_message(**req)
        self._send_buffer += message
        self._request_queued = True

    def process_protoheader(self):
        hdrlen = 2
        if len(self._recv_buffer) >= hdrlen:
            self._jsonheader_len = struct.unpack(
                ">H", self._recv_buffer[:hdrlen]
            )[0]
            self._recv_buffer = self._recv_buffer[hdrlen:]

    def process_jsonheader(self):
        hdrlen = self._jsonheader_len
        if len(self._recv_buffer) >= hdrlen:
            self.jsonheader = self._json_decode(
                self._recv_buffer[:hdrlen], "utf-8"
            )
            self._recv_buffer = self._recv_buffer[hdrlen:]
            for reqhdr in (
                    "byteorder",
                    "content-length",
                    "content-type",
                    "content-encoding",
            ):
                if reqhdr not in self.jsonheader:
                    raise ValueError(f'Missing required header "{reqhdr}".')

    def process_response(self):
        content_len = self.jsonheader["content-length"]
        if not len(self._recv_buffer) >= content_len:
            return
        data = self._recv_buffer[:content_len]
        self._recv_buffer = self._recv_buffer[content_len:]
        if self.jsonheader["content-type"] == "text/json":
            encoding = self.jsonheader["content-encoding"]
            self.response = self._json_decode(data, encoding)
            logger.info("Received response %s from %s", repr(self.response), self.addr)
            self._process_response_json_content()
        # Close when response has been processed
        self.close()
        print()