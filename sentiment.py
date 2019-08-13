from flask import Flask, request, jsonify
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from flask_cors import CORS, cross_origin
from collections import Counter
import sys
import mysql.connector
from mysql.connector import Error
connection = mysql.connector.connect(host='localhost',
                             database='sentiment',
                             user='root',
                             password='')
    #note: depending on how you installed (e.g., using source code download versus pip install), you may need to import like this:
    #from vaderSentiment import SentimentIntensityAnalyzer

app = Flask(__name__)
CORS(app)




@app.route("/getText", methods=['POST','GET'])
def getText():

    if request.method == 'POST':
        userRequired = {
            'type': '',
            'sentiment': '',
            'positiveNegetiveCount': '',
            'status': ''
        }
        jsonData = request.get_json(force=True)
        textDescription = jsonData['textDescription']
        positiveNegetiveCount=positive_negetive_count(textDescription)

        analyzer = SentimentIntensityAnalyzer()
        vs = analyzer.polarity_scores(textDescription)
        #print("{:-<65} {}".format(textDescription, str(vs)))

        analyisResult = {
            'type': 'sentiment',
            'sentiment':str(vs),
			'positiveNegetiveCount':positiveNegetiveCount,
            'status': 1
        }


        try:

            query = "INSERT INTO sentiment_keyword(keyword,	possitive,negetive,sentiment_result)  VALUES(%s,%s,%s,%s)"
            args = (textDescription,vs['pos'],vs['neg'] ,'')
            cursor = connection.cursor()
            cursor.execute(query, args)
            connection.commit()
        except Error as e:
            print("Error while connecting to MySQL", e)
        return jsonify(analyisResult)
        sys.exit()


def positive_negetive_count(paragraph):
    f = open('positive.txt')
    positive = [line.rstrip() for line in f.readlines()]
    f2 = open('negetive.txt')
    negative = [line.rstrip() for line in f2.readlines()]
    polarity = ''
    textSet = ''
    count = Counter(paragraph.split())
    pos = 0
    neg = 0
    positive_negetive_arr=[]
    for key, val in count.items():
        key = key.rstrip('.,?!\n')  # removing possible punctuation signs

        if key in positive:
            pos += val

        if key in negative:
            neg += val


    positive_negetive_arr={'pos':pos,'neg':neg}
    return positive_negetive_arr

@app.route("/getHistory", methods=['POST','GET'])
def getHistory():
    sql_select_Query = "select * from sentiment_keyword  order by id desc limit 6"
    cursor = connection.cursor()
    cursor.execute(sql_select_Query)
    records = cursor.fetchall()

    return jsonify(records)
    sys.exit()

if __name__=='__main__':
    app.debug = True
    app.run(host="192.168.43.173",port=5000)