import json
from hashlib import sha256
import time
from flask import Flask, request
import requests
import datetime
from flask import render_template, redirect, request
from app import app

#Estaremos almacenando transacciones en bloques

class Block:
    def __init__(self, index, transactions, timestamp):
        """
        Constructor de la clase `Block`.
        :param index: ID único del bloque.
        :param transactions: Lista de transacciones.
        :param timestamp: Momento en que el bloque fue generado.
        """
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp

#Si queremos detectar si han manipulado la información almacenadada dentro de un bloque,
#podemos usar funciones 'hash' criptográficas.

#Hay varias funciones hash populares. Este es un ejemplo en Python usando la función hash SHA-256.

data = b"Un poco de informacion de longitud variada"
sha256(data).hexdigest()
'976cb22d161e5bd6225b543c04743015daa8ee4fcbb01a5c489e33d01b2f951f'
# No importa cuántas veces lo ejecutes, siempre retorna la misma cadena de 256 caracteres.
sha256(data).hexdigest()
'976cb22d161e5bd6225b543c04743015daa8ee4fcbb01a5c489e33d01b2f951f'
# Agregamos un caracter al final.
data = b"Un poco de informacion de longitud variada2"
sha256(data).hexdigest()
'd3b1df2ef471d726dc5521200338f5626ddbcccf8463c33709ab9ea04f18c7b9'
# Notemos cómo el hash resultante ha cambiado completamente.

#Guardaremos el hash de cada uno de los bloques en un campo dentro de nuestro objeto 'Block'
#para que actúe como una huella dactilar (o firma digital)


def compute_hash(block):
    """
    Convierte el bloque en una cadena JSON y luego retorna el hash
    del mismo.
    """
    block_string = json.dumps(block.__dict__, sort_keys=True)
    return sha256(block_string.encode()).hexdigest()

#Necesitamos una solución para asegurarnos de que cualquier cambio en los bloques anteriores
#invalide la cadena entera. Para ello, necesitamos crear una dependencia mutua entre bloques
#consecutivos al encadenarlos por el hash del bloque inmediatamente anterior a ellos.
#Con 'encadenar' nos referimos a incluir el hash del bloque anterior en el actual.

class Block:
    def __init__(self, index, transactions, timestamp, previous_hash):
        """
        Constructor de la clase `Block`.
        :param index: ID único del bloque.
        :param transactions: Lista de transacciones.
        :param timestamp: Momento en que el bloque fue generado.
        """
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        # Agregamos un campo para el hash del bloque anterior.
        self.previous_hash = previous_hash

    def compute_hash(self):
        """
        Convierte el bloque en una cadena JSON y luego retorna el hash
        del mismo.
        """
        # La cadena equivalente también considera el nuevo campo previous_hash,
        # pues self.__dict__ devuelve todos los campos de la clase.
        block_string = json.dumps(self.__dict__, sort_keys=True)
        return sha256(block_string.encode()).hexdigest()


class Blockchain:

    def __init__(self):
        """
        Constructor para la clase `Blockchain`.
        """
        self.chain = []
        self.create_genesis_block()

    def create_genesis_block(self):
        """
        Una función para generar el bloque génesis y añadirlo a la
        cadena. El bloque tiene index 0, previous_hash 0 y un hash
        válido.
        """
        genesis_block = Block(0, [], time.time(), "0")
        genesis_block.hash = genesis_block.compute_hash()
        self.chain.append(genesis_block)

    @property
    def last_block(self):
        """
        Una forma rápida y pythonica de retornar el bloque más reciente de la cadena.
        Nótese que la cadena siempre contendrá al menos un último bloque (o sea,
        el bloque génesis).
        """
        return self.chain[-1]

#En lugar de aceptar cualquier hash para el bloque, le agregamos alguna restricción.
#Introduzcamos un nuevo campo en nuestro bloque llamado 'nonce'.
#Un 'nonce' es un número que cambiará constantemente hasta que obtengamos un hash que satisfaga
#nuestra restricción.
class Blockchain:
    # Dificultad del algoritmo de prueba de trabajo.
    difficulty = 2

    """
    Código anterior...
    """

    def proof_of_work(self, block):
        """
        Función que intenta distintos valores de nonce hasta obtener
        un hash que satisfaga nuestro criterio de dificultad.
        """
        block.nonce = 0

        computed_hash = block.compute_hash()
        while not computed_hash.startswith('0' * Blockchain.difficulty):
            block.nonce += 1
            computed_hash = block.compute_hash()

        return computed_hash


#Veamos el código para insertar bloques en la cadena:
class Blockchain:
    """
    Código anterior...
    """

    def add_block(self, block, proof):
        """
        Una función que agrega el bloque a la cadena luego de la verificación.
        La verificación incluye:
        * Chequear que la prueba es válida.
        * El valor del previous_hash del bloque coincide con el hash del último
        bloque de la cadena.
        """
        previous_hash = self.last_block.hash

        if previous_hash != block.previous_hash:
            return False

        if not self.is_valid_proof(block, proof):
            return False

        block.hash = proof
        self.chain.append(block)
        return True

    def is_valid_proof(self, block, block_hash):
        """
        Chquear si block_hash es un hash válido y satisface nuestro
        criterio de dificultad.
        """
        return (block_hash.startswith('0' * Blockchain.difficulty) and
                block_hash == block.compute_hash())


#El proceso de poner transacciones no confirmadas en un bloque y calcular la prueba de trabajo
#es conocido como el 'minado' de bloques.
# Una vez que el 'nonce' que satisface nuestra condición es averiguado, podemos decir que el bloque
#ha sido 'minado' y puede ser colocado en el blockchain.
#Así es como se ve nuestra función de minado.
class Blockchain:

    def __init__(self):
        # Información que todavía no ha ingresado al blockchain.
        self.unconfirmed_transactions = []
        self.chain = []
        self.create_genesis_block()

    """
    Código anterior continuado...
    """

    def add_new_transaction(self, transaction):
        self.unconfirmed_transactions.append(transaction)

    def mine(self):
        """
        Esta función sirve como una interfaz para añadir las transacciones
        pendientes al blockchain añadiéndolas al bloque y calculando la
        prueba de trabajo.
        """
        if not self.unconfirmed_transactions:
            return False

        last_block = self.last_block

        new_block = Block(index=last_block.index + 1,
                        transactions=self.unconfirmed_transactions,
                        timestamp=time.time(),
                        previous_hash=last_block.hash)

        proof = self.proof_of_work(new_block)
        self.add_block(new_block, proof)
        self.unconfirmed_transactions = []
        return new_block.index


#Ahora es momento de crear interfaces para que nuestro nodo blockchain interactúe con la
#aplicación que vamos a crear.

# Inicializar la aplicación Flask
app =  Flask(__name__)

# Inicializar el objeto blockchain.
blockchain = Blockchain()


#Necesitamos un punto de acceso para que nuestra aplicación envíe una nueva transacción.
# El método de Flask para declarar puntos de acceso.
@app.route('/new_transaction', methods=['POST'])
def new_transaction():
    tx_data = request.get_json()
    required_fields = ["author", "content"]

    for field in required_fields:
        if not tx_data.get(field):
            return "Invlaid transaction data", 404

    tx_data["timestamp"] = time.time()

    blockchain.add_new_transaction(tx_data)

    return "Success", 201


#Para solicitar todas las publicaciones y luego las mostrarlas.
@app.route('/chain', methods=['GET'])
def get_chain():
    chain_data = []
    for block in blockchain.chain:
        chain_data.append(block.__dict__)
    return json.dumps({"length": len(chain_data), "chain": chain_data})

#Para solicitar al nodo que mine las transacciones sin confirmar.
@app.route('/mine', methods=['GET'])
def mine_unconfirmed_transactions():
    result = blockchain.mine()
    if not result:
        return "No transactions to mine"
    return "Block #{} is mined.".format(result)


@app.route('/pending_tx')
def get_pending_tx():
    return json.dumps(blockchain.unconfirmed_transactions)


#Entonces, para pasar de un solo nodo a una red de pares crearemos un punto de acceso para permitirle
#a un nodo tener conciencia de otros compañeros en la red:
# Contiene las direcciones de otros compañeros que participan en la red.
peers = set()

# Punto de acceso para añadir nuevos compañeros a la red.
@app.route('/register_node', methods=['POST'])
def register_new_peers():
    # La dirección del nodo compañero.
    node_address = request.get_json()["node_address"]
    if not node_address:
        return "Invalid data", 400

    # Añadir el nodo a la lista de compañeros.
    peers.add(node_address)

    # Retornar el blockhain al nuevo nodo registrado para que pueda sincronizar.
    return get_chain()


@app.route('/register_with', methods=['POST'])
def register_with_existing_node():
    """
    Internamente llama al punto de acceso `/register_node`
    para registrar el nodo actual con el nodo remoto especificado
    en la petición, y sincronizar el blockchain asimismo con el
    nodo remoto.
    """
    node_address = request.get_json()["node_address"]
    if not node_address:
        return "Invalid data", 400

    data = {"node_address": request.host_url}
    headers = {'Content-Type': "application/json"}

    # Hacer una petición para registrarse en el nodo remoto y obtener
    # información.
    response = requests.post(node_address + "/register_node",
                            data=json.dumps(data), headers=headers)

    if response.status_code == 200:
        global blockchain
        global peers
        # Actualizar la cadena y los compañeros.
        chain_dump = response.json()['chain']
        blockchain = create_chain_from_dump(chain_dump)
        peers.update(response.json()['peers'])
        return "Registration successful", 200
    else:
        # si algo sale mal, pasárselo a la respuesta de la API
        return response.content, response.status_code


def create_chain_from_dump(chain_dump):
    blockchain = Blockchain()
    for idx, block_data in enumerate(chain_dump):
        block = Block(block_data["index"],
                    block_data["transactions"],
                    block_data["timestamp"],
                    block_data["previous_hash"])
        proof = block_data['hash']
        if idx > 0:
            added = blockchain.add_block(block, proof)
            if not added:
                raise Exception("The chain dump is tampered!!")
        else:  # el bloque es un bloque génesis, no necesita verificación
            blockchain.chain.append(block)
    return blockchain


#La copia de cadenas de algunos nodos puede diferir. En ese caso, necesitamos ponernos de acuerdo
#respecto de alguna versión de la cadena para mantener la integridad de todo el sistema.
def consensus():
    """
    Nuestro simple algoritmo de consenso. Si una cadena válida más larga es
    encontrada, la nuestra es reemplazada por ella.
    """
    global blockchain

    longest_chain = None
    current_len = len(blockchain)

    for node in peers:
        response = requests.get('http://{}/chain'.format(node))
        length = response.json()['length']
        chain = response.json()['chain']
        if length > current_len and blockchain.check_chain_validity(chain):
            current_len = length
            longest_chain = chain

    if longest_chain:
        blockchain = longest_chain
        return True

    return False


#Ahora finalmente, necesitamos desarrollar una forma para que cada nodo pueda anunciar a la red
#que ha minado un bloque para que todos puedan actualizar su blockchain y seguir minando otras
#transacciones.
# punto de acceso para añadir un bloque minado por alguien más a la cadena del nodo.
@app.route('/add_block', methods=['POST'])
def validate_and_add_block():
    block_data = request.get_json()
    block = Block(block_data["index"], block_data["transactions"],
                block_data["timestamp", block_data["previous_hash"]])

    proof = block_data['hash']
    added = blockchain.add_block(block, proof)

    if not added:
        return "The block was discarded by the node", 400

    return "Block added to the chain", 201

def announce_new_block(block):
    for peer in peers:
        url = "http://{}/add_block".format(peer)
        requests.post(url, data=json.dumps(block.__dict__, sort_keys=True))


#Crear la aplicación:
# Nodo de la red blockchain con el que nuestra aplicación
# se comunicará para obtener y enviar información
CONNECTED_NODE_ADDRESS = "http://127.0.0.1:8000"

posts = []

def fetch_posts():
    """
    Función para obtener la cadena desde un nodo blockchain,
    procesar la información y almacenarla localmente.
    """
    get_chain_address = "{}/chain".format(CONNECTED_NODE_ADDRESS)
    response = requests.get(get_chain_address)
    if response.status_code == 200:
        content = []
        chain = json.loads(response.content)
        for block in chain["chain"]:
            for tx in block["transactions"]:
                tx["index"] = block["index"]
                tx["hash"] = block["previous_hash"]
                content.append(tx)

        global posts
        posts = sorted(content, key=lambda k: k['timestamp'],
                    reverse=True)

@app.route('/submit', methods=['POST'])
def submit_textarea():
    """
    Punto de acceso para crear una nueva transacción vía nuestra
    aplicación.
    """
    post_content = request.form["content"]
    author = request.form["author"]

    post_object = {
        'author': author,
        'content': post_content,
    }

    # Submit a transaction
    new_tx_address = "{}/new_transaction".format(CONNECTED_NODE_ADDRESS)

    requests.post(new_tx_address,
                json=post_object,
                headers={'Content-type': 'application/json'})

    return redirect('/')