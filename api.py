#-----------------------------------
# Author: Nathaniel Colburn
# Date: 10/1/2023
# Fetch Backend Internship Challenge
#-----------------------------------

import json
from flask import Flask, Response, jsonify, request
from collections import OrderedDict
app = Flask(__name__)

payers = dict() # payerName : totalPoints
transaction = dict() # timestamp : [payerName, points]
totalPoints = 0 # total points in user's account

# Add points to user's account
@app.route('/add', methods=['POST'])
def addPoints():
    data = json.loads(request.data)
    payerName = data['payer']
    points = data['points']
    timestamp = data['timestamp']

    # Add to total points for each payer
    if payerName in payers:
        payers[payerName] += points
    else:
        payers[payerName] = points
    transaction[timestamp] = [payerName, points]
    global totalPoints
    totalPoints += int(points)
    return Response(status=200)

# Spend points from user's account
@app.route('/spend', methods=['POST'])
def spendPoints():
    data = json.loads(request.data)
    points = data['points']
    subtracted = dict()
    global totalPoints

    if points > totalPoints:
        return jsonify({ 'error': 'User does not have enough points.' }), 400

    # Sort the payers by timestamp
    global transaction
    sortedDict = sorted(transaction.items())
    transaction = dict(sortedDict)

    for timestamp in transaction.keys():
        payer = transaction[timestamp][0]
        transAmount = transaction[timestamp][1]
        payers[payer] = int(payers[payer])

        if transAmount >= points:
            payers[payer] -= points
            totalPoints -= points
            
            # Add to subtracted
            if payer in subtracted:
                subtracted[payer] -= points
            else:
                subtracted[payer] = -(points)
            points = 0
        else:
            points -= transAmount
            if payer in subtracted:
                subtracted[payer] -= transAmount
            else:
                subtracted[payer] = -(transAmount)
            payers[payer] -= transAmount
            totalPoints -= transAmount

    returnList = []
    for payer in subtracted.keys():
        returnList.append({"payer" : payer, "points" : subtracted[payer]})
    return jsonify(returnList), 200

# Get the points balance for each payer
@app.route('/balance', methods=['GET'])
def getPoints():
    returnDict = dict()
    for payer in payers:
        returnDict[payer] = payers[payer]
    return jsonify(returnDict), 200

if __name__ == '__main__':
    app.run(port=8000)