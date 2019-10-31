import hashlib
import json
from time import time
from uuid import uuid4

from flask import Flask, jsonify, request


class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        self.new_block(prev_hash=None, prev_proof=100)

    def new_block(self, prev_hash=None, prev_proof=0, creator='System'):
        block = {
            'index':            len(self.chain),
            'timestamp':        time(),
            'transactions':     self.current_transactions,
            'previous_proof':   prev_proof,
            'previous_hash':    prev_hash,
            'created_by':       creator,
        }

        self.current_transactions = []
        self.chain.append(block)
        return block

    def hash(self, block, proof):
        to_hash = {
            'block': json.dumps(block, sort_keys=True),
            'proof': proof
        }

        block_proof_string = json.dumps(to_hash).encode()
        hex_hash = hashlib.sha256(block_proof_string).hexdigest()
        return hex_hash

    @property
    def last_block(self):
        return self.chain[-1]

    def proof_of_work(self, block):
        proof = 0
        while not self.valid_proof(try_block=block, proof=proof)[0]:
            proof += 1
        return proof

    def valid_proof(self, try_block, proof):
        try_hash = self.hash(block=try_block, proof=proof)
        return [try_hash[:4] == '0000', try_hash]

app = Flask(__name__)

node_identifier = str(uuid4()).replace('-', '')

blockchain = Blockchain()

@app.route('/mine', methods=['GET'])
def mine():
    mine_info = request.get_json()
    req_keys = ['proof', 'id']

    if not all(k in mine_info for k in req_keys):
        if (req_keys[0] not in mine_info) & (req_keys[1] in mine_info):
            response = {'message': "Missing proof, try again"}
            return jsonify(response), 400
        elif (req_keys[0] in mine_info) & (req_keys[1] not in mine_info):
            response = {'message': "Missing ID, try again"}
            return jsonify(response), 400
        else:
            response = {'message': "Missing information, please resend"}
            return jsonify(response), 400

    try_proof = mine_info.get('proof')

    last_block = blockchain.last_block

    check = blockchain.valid_proof(try_block=last_block, proof=try_proof)
    is_valid, res_hash = check[0], check[1]
    if is_valid:
        block = blockchain.new_block(prev_hash=res_hash,
                                     prev_proof=try_proof,
                                     creator=mine_info.get['id'])
        response = {
            'message':          "New Block Forged",
            'index':            block['index'],
            'transactions':     block['transactions'],
            'previous_proof':   block['previous_proof'],
            'previous_hash':    block['previous_hash'],
            'created_by':       block['created_by'],
        }
        return jsonify(response), 200
    else:
        response = {'message': 'Invalid Proof'}
        return jsonify(response), 400


@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'length':   len(blockchain.chain),
        'chain':    blockchain.chain,
    }
    return jsonify(response), 200

@app.route('/last_block', methods=['GET'])
def last_block():
    return jsonify(blockchain.last_block)

# Run on port 8000
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)