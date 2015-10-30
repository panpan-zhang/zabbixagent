# -*- coding: utf-8 -*-
__author__ = 'zhangpanpan'

from zabbixagent.logger import get_logger
from time import sleep, time
import Queue

class ItemProcessingController(object):

    def __init__(self, config, shutdown_event, items, database, sender, queue):
        self._shutdown_event = shutdown_event
        self._items = items
        self._next_send_date = time()
        self._config = config
        self._database = database
        self._sender = sender
        self._logger = get_logger()
        self._update_interval = None
        self._queue = queue
        self._send_date = None

    def _setup_update_interval(self):
        minimun_update_interval = self._config.get('main', 'update_interval')
        for item in self._items:
            interval = item.get_update_interval()
            minimun_update_interval = min(interval, minimun_update_interval)
        self._update_interval = float(minimun_update_interval) / 2

    def start(self):
        self._setup_update_interval()
        self._start_items()
        self._process_until_shutdown()


    def _process_until_shutdown(self):
        while not self._shutdown_event.isSet():
            try:
                item_values = self._queue.get()
            except Queue.Empty,e:
                pass
            else:
                self._logger.debug('get item_values %s' % item_values)
                self._write_item_values_to_datase(item_values)
                self._sender.send()

    def _start_items(self):
        for item in self._items:
            item.start()

    def _update_next_sender_date(self):
        self._next_send_date = time() + self._update_interval

    def _store_send_date(self):
        self._send_date = time()

    def _write_item_values_to_datase(self, item_values):
        self._database.insert_values(item_values)