import hashlib
import json
import time
from uuid import uuid4

from flask import Flask, jsonify, request


class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        self.new_block(prev_hash=None, prev_proof=100)

    def new_block(self, prev_hash=None, prev_proof=0):
        block = {
            'index':            len(self.chain),
            'timestamp':        time(),
            'transactions':     self.current_transactions,
            'previous_proof':   prev_proof,
            'previous_hash':    prev_hash,
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
        while not self.valid_proof(try_block=block, proof=proof):
            proof += 1
        return proof

    def valid_proof(self, try_block, proof):
        try_hash = self.hash(block=try_block, proof=proof)
        return try_hash[:4] == '0000'

app = Flask(__name__)

node_identifier = str(uuid4()).replace('-', '')

blockchain = Blockchain()

@app.route('/mine', methods=['GET'])
def mine():
