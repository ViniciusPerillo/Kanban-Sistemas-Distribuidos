import paho.mqtt.client as mqtt
import time
import json

from .utils import *

class KanbanBase:

    PARTS = [f"part{part:0>3}" for part in range(1,101)]

    PRODUCT_PARTS = {
        'prod01': [f"part{part:0>3}" for part in range(1,44)] 
                + [f"part{part:0>3}" for part in range(44,53)]
                + [f"part{part:0>3}" for part in range(71,77)],

        'prod02': [f"part{part:0>3}" for part in range(1,44)] 
                + [f"part{part:0>3}" for part in range(44,53)]
                + [f"part{part:0>3}" for part in range(77,83)],

        'prod03': [f"part{part:0>3}" for part in range(1,44)] 
                + [f"part{part:0>3}" for part in range(53,62)]
                + [f"part{part:0>3}" for part in range(83,89)],

        'prod04': [f"part{part:0>3}" for part in range(1,44)] 
                + [f"part{part:0>3}" for part in range(53,62)]
                + [f"part{part:0>3}" for part in range(89,95)],

        'prod05': [f"part{part:0>3}" for part in range(1,44)] 
                + [f"part{part:0>3}" for part in range(62,71)]
                + [f"part{part:0>3}" for part in range(95,101)],
    }

    CLOCK = 'clock'

    @staticmethod
    def __on_connect(client, userdata, flags, reason_code, properties):
        if reason_code == 0:
            print_log("Conectado ao broker MQTT!")
            for topic in userdata:
                client.subscribe(topic)
                print_log(f"Assinando o tópico: {topic}")
        else:
            print_log(f"Falha na conexão, código de retorno: {reason_code}\n")

    @staticmethod
    def __on_message(client, userdata, msg):
        print_log(f"Mensagem recebida no tópico '{msg.topic}'")
        try:
            payload = json.loads(msg.payload.decode())
            userdata.handle_message(msg.topic, data = payload['data'])
        except json.JSONDecodeError:
            print_log(f" > Payload não é um JSON válido: {msg.payload.decode()}")

    @staticmethod
    def __on_publish(client, userdata, mid, rc, props):
        print_log(f"Mensagem {mid} confirmada pelo broker")
    

    def __init__(self, topics, client_id):
        self.__broker_address = "broker"
        self.__port = 1883
        self.topics = topics
        self.client_id = client_id
        self.messages = dict.fromkeys(self.topics, None)
        self.to_do = dict.fromkeys(self.topics, None)

        self.client = mqtt.Client(
                mqtt.CallbackAPIVersion.VERSION2,
                client_id=client_id
            )
        
        self.client.user_data_set(self)
        self.client.on_connect = KanbanBase.__on_connect
        self.client.on_message = KanbanBase.__on_message
        self.client.on_publish = KanbanBase.__on_publish

    def start(self, function, args = []):
        try:
            self.client.connect(self.__broker_address, self.__port, 60)
            self.client.loop_start()

            function(*args)

        except KeyboardInterrupt:
            print_log(f"Encerrado")
            self.client.loop_stop()
            self.client.disconnect()

    def loop_forever(self):
        self.client.connect(self.__broker_address, self.__port, 60)
        self.client.loop_forever()

    def handle_message(self, topic, data):
        if topic == KanbanBase.CLOCK:
            self.to_do = self.messages
            self.messages = dict.fromkeys(self.topics, None)
            self.do_day_cycle()
        else:
            self.messages[topic] = data

    def do_day_cycle(self):
        pass

    def publish(self, topic, payload):
        result = self.client.publish(topic, json.dumps(payload), qos=1)
                
        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            print_log(f"Publicado: {topic}")
        else:
            print_log(f"Erro na publicação: {result.rc}")

