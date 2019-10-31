import hashlib
import requests

import sys
import json


def proof_of_work(block):
    """
    Simple Proof of Work Algorithm
    Look for a proof.
    Loop through possibilities, checking each one against `valid_proof`
    in an effort to find a number that is a valid proof
    :return: A valid proof for the provided block
    """

    proof = 0
    while not valid_proof(try_block=block, proof=proof):
        proof += 1
    return proof


def valid_proof(try_block, proof):
    """
    Validates the Proof:  Does hash(block_string, proof) contain 6
    leading zeroes?  Return true if the proof is valid
    :param try_block: <dict> The block to use to
    check in combination with `proof`
    :param proof: <int?> The value that when combined with the
    stringified previous block results in a hash that has the
    correct number of leading zeroes.
    :return: True if the resulting hash is a valid proof, False otherwise
    """

    try_hash = hash_256(try_block, proof)
    return try_hash[:4] == "0000"


def hash_256(block, proof):
    to_hash = {
        'block':    json.dumps(block, sort_keys=True),
        'proof':    proof,
    }

    block_proof_string = json.dumps(to_hash).encode()
    hex_hash = hashlib.sha256(block_proof_string).hexdigest()
    return hex_hash


if __name__ == '__main__':
    # What is the server address? IE `python3 miner.py https://server.com/api/`
    if len(sys.argv) > 1:
        node = sys.argv[1]
    else:
        node = "http://localhost:8000"

    # Load ID
    f = open("my_id.txt", "r")
    my_id = f.read()
    print("ID is", id)
    f.close()

    mined_coins = 0

    # Run forever until interrupted
    while True:
        r = requests.get(url=node + "/last_block")
        # Handle non-json response
        try:
            data = r.json()
        except ValueError:
            print("Error:  Non-json response")
            print("Response returned:")
            print(r)
            break

        new_proof = proof_of_work(data)


        # When found, POST it to the server {"proof": new_proof, "id": id}
        post_data = {"proof": new_proof, "id": my_id}

        r = requests.post(url=node + "/mine", json=post_data)
        data = r.json()

        if data.get('message') == "New Block Forged":
            mined_coins += 1
            print("Mined a new coin!")
            print(f"Total coins: {mined_coins}")
        else:
            print(data.get('message'))
