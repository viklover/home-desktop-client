import json
import random
import time

import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

from connectors import BaseConnector


class VkConnector(BaseConnector):

    FREQUENCY_SEND = 6

    class ReceivingChannel(BaseConnector.ReceivingChannel):

        def __init__(self, connector):
            super(VkConnector.ReceivingChannel, self).__init__(connector)

        def run(self):
            while self.status:
                try:
                    for event in self.connector.long_poll.listen():

                        if event.type == VkBotEventType.MESSAGE_NEW:

                            json_data = json.loads(event.object.text)

                            self.connector.last_response_time = time.time()

                            if 'event' in json_data and self.connector.connected:
                                print('Receive: ', json_data)
                                self.connector.events.append(json_data)
                                continue

                            if 'response' in json_data and json_data['id'] in self.connector.request_ids:
                                print('Receive: ', json_data)
                                self.connector.request_ids.remove(json_data['id'])
                                self.connector.responses.append(json_data)

                except json.decoder.JSONDecodeError:
                    print('error json')
                except:
                    self.connector.connected = False

    def __init__(self, controller):
        super(VkConnector, self).__init__(controller)
        self.name = 'VK-API'

        self.vk = None
        self.long_poll = None
        self.session = None

        self.timer = None

    def init_connection(self):

        try:
            self.vk = vk_api.VkApi(token=BaseConnector.VK_CONFIG['token'])
            self.long_poll = VkBotLongPoll(self.vk, BaseConnector.VK_CONFIG['group_id'])
            self.session = self.vk.get_api()

            super().init_connection()

            self.start_io_threads()

            if self.get_response(self.send_request({'request': 'is_alive'})):
                self.connected = True
                self.start_alive_thread()
        except:
            self.connected = False

        return self.connected

    def process_task(self, task, args, kwargs):

        if not self.session:
            return False

        if self.timer is None:
            self.timer = time.time()
        else:
            difference = time.time() - self.timer
            if VkConnector.FREQUENCY_SEND - difference > 0:
                time.sleep(VkConnector.FREQUENCY_SEND - difference)
            self.timer = time.time()

        try:
            self.session.messages.send(
                peer_id=VkConnector.VK_CONFIG['chat_id'],
                message=json.dumps(task),
                random_id=random.randint(1, 121212)
            )
        except:
            self.connected = False

        return True
