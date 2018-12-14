#!/bin/python3

from pynats import NATSClient
import json
import requests
from random import randint

def data_treatment(message):
    print(message)
    parse_args(message)

def parse_args(message):
    p = json.loads(message.payload)
    if ("!" in p['message']):
        print(p['message'])
        cmd = p['message'].split("!")[1]
        params = cmd.split()
        
        if(len(params) > 0):
            cmd = params[0]
            if (len(params) < 2):
                params = None
                print("aucun param !")
            else:
                params.remove(cmd)
                for param in params:
                    print("param: " + param)

            if cmd == "pokemon":
                if (params is None):
                    client.publish("irc.message.send", payload=b'{"channel": "##cesi", "message": "Donne moi un nom de pokemon en parametre !!!" }')
                else:
                    getPokemonAbilities(params)
            elif (cmd == "rjoke"):
                    getRandomBlague()
            # else:
            #     response = '{"channel": "##cesi", "message": "Commande ' + cmd + ' inconnue chez trodix !" }'
            #     client.publish("irc.message.send", payload=response.encode())


        
def getPokemonAbilities(params):
    pokemon_name = params[0]
    response = requests.get("https://pokeapi.co/api/v2/pokemon/" + pokemon_name)
    try:
        data = response.json()
        # print(json.dumps(data, indent=4))
        abilities = data["abilities"]
        to_send = "Abilities: "
        ability_names = []
        for ability in abilities:
            ability_names.append(ability["ability"]["name"])
        to_send += ",".join(ability_names)
        print(to_send)
        tmp = '{"channel": "##cesi", "message": "Reponse pour la commande !pokemon ' + pokemon_name + ' => ' + to_send + '"}'
        client.publish("irc.message.send", payload=tmp.encode())
    except Exception as ex:
        print(ex)
        client.publish("irc.message.send", payload=b'{"channel": "##cesi", "message": "unknown pokemon name !" }')

def getRandomBlague():
    blague_id = str(randint(0, 50))
    response = requests.get("https://bridge.buddyweb.fr/api/blagues/blagues/" + blague_id)
    try:
        data = response.json()
        to_send = data["blagues"]
        tmp = '{"channel": "##cesi", "message": "Reponse pour la commande !rjoke => ' + to_send + '"}'
        client.publish("irc.message.send", payload=tmp.encode())

    except Exception as ex:
        print(ex)
        client.publish("irc.message.send", payload=b'{"channel": "##cesi", "message": "unknown joke id !" }')

with NATSClient("nats://dev.lookingfora.name:4222") as client:

    client.publish("irc.message.send", payload=b'{"channel": "##cesi", "message": "Type !pokemon <pokemon_name> to get pokemon abilities or Type !rjoke to get a random joke" }')
    client.subscribe(subject="irc.message.##cesi", callback=data_treatment)
    client.wait()
