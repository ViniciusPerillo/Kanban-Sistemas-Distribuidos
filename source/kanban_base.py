import paho.mqtt.client as mqtt
import time
import pickle as pkl
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
            for topic in userdata.topics:
                client.subscribe(topic)
                #print_log(f"Assinando o tópico: {topic}")
            print_log("Topicos inscritos")
        else:
            print_log(f"Falha na conexão, código de retorno: {reason_code}\n")

    @staticmethod
    def __on_message(client, userdata, msg):
        # print_log(f"Mensagem recebida no tópico '{msg.topic}'")
        try:
            payload = pkl.loads(msg.payload)  # Tentativa de desserialização
            userdata.handle_message(msg.topic, data=payload['data'])
            
        except pkl.UnpicklingError as e:
            # Mostra o payload ORIGINAL (bytes) sem tentar desserializar novamente
            print_log(f"\033[91mERRO: {msg.topic} - Payload não é um Pickle válido. Bytes: {msg.payload}")
            
        # except KeyError as e:
        #     # Payload foi desserializado, mas falta a chave 'data'
        #     print_log(f"\033[91mERRO: {msg.topic} - Estrutura inválida: {pkl.loads(msg.payload)}. Erro: {e}")

    @staticmethod
    def __on_publish(client, userdata, mid, rc, props):
        pass
        # print_log(f"Mensagem {mid} confirmada pelo broker")
    

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
            self.publish(f'{self.client_id}_finished', {'data': 1})
        else:
            self.messages[topic] = data

    def do_day_cycle(self):
        pass

    def publish(self, topic, payload):
        result = self.client.publish(topic, pkl.dumps(payload), qos=1)
                
        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            pass
            #print_log(f"Publicado: {topic} - {str(payload)[:100]}")
        else:
            print_log(f"Erro na publicação: {result.rc}")

