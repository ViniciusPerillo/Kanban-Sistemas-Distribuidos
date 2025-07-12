import paho.mqtt.client as mqtt
import time
import json


from utils import *

class ConnectionMQTT:
    @staticmethod
    def on_connect(client, userdata, flags, reason_code, properties):
        if reason_code == 0:
            print_log("Conectado ao broker MQTT!")
            for topic in userdata:
                client.subscribe(topic)
                print_log(f"Assinando o tópico: {topic}")
        else:
            print_log(f"Falha na conexão, código de retorno: {reason_code}\n")

    @staticmethod
    def on_message(client, userdata, msg):
        print_log(f"Mensagem recebida no tópico '{msg.topic}'")
        try:
            payload = json.loads(msg.payload.decode())
            userdata.handle_message(payload)
        except json.JSONDecodeError:
            print_log(f"  > Payload não é um JSON válido: {msg.payload.decode()}")

    @staticmethod
    def on_publish(client, userdata, mid, rc, props):
        print_log(f"Mensagem {mid} confirmada pelo broker")
    

    def __init__(self, topics):
        self.broker_address = "broker"
        self.port = 1883
        self.topics = topics

        self.client = mqtt.Client(
                mqtt.CallbackAPIVersion.VERSION2,
                client_id="linha_producao_1"
            )
        
        self.client.user_data_set(self)
        self.client.on_connect = ConnectionMQTT.on_connect
        self.client.on_message = ConnectionMQTT.on_message
        self.client.on_publish = ConnectionMQTT.on_publish
        time.sleep(5)

    def start(self):

        try:
            self.client.connect(self.broker_address, self.port, 60)
            self.client.loop_start()

        except KeyboardInterrupt:
            print(f"\n[{datetime.datetime.now()}] Publicação encerrada.")
            self.client.loop_stop()
            self.client.disconnect()

    def handle_message(self, payload):
        pass

