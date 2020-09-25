from flask import Flask, render_template, request
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
import sqlite3
import random

app = Flask(__name__)

mybot = ChatBot("PizzaBot",storage_adapter="chatterbot.storage.SQLStorageAdapter")

training_data_quesans = open('training_data/ques_ans.txt').read().splitlines()

training_data = training_data_quesans

trainer = ListTrainer(mybot)
trainer.train(training_data)

p_name=''
name=''
phone=''

db=sqlite3.connect('db1.sqlite3')
cursor = db.cursor()
cursor.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='orders' ''')
if cursor.fetchone()[0]==0 :
    cursor.execute('''CREATE TABLE orders(id INTEGER PRIMARY KEY,name TEXT, phone TEXT, address TEXT,pizza_name TEXT, status TEXT)''')
db.commit()

flag = 0
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/get")
def get_bot_response():
    with sqlite3.connect("db1.sqlite3") as db:
        global flag
        global p_name
        global name
        global phone
        cursor = db.cursor()
        userText = request.args.get('msg')
        if(userText=='Double Paneer Supreme' or userText=='Veg Exotica' or userText=='Triple Chicken Feast' or userText=='Malai Chicken Tikka'):
            if(p_name==''):
                p_name=userText
            else:
                p_name=p_name+', '+userText
        if(flag == 1):
            status = ["Your order is already out for delivery", "Your order is being prepared"]
            cursor.execute('''INSERT INTO orders(name, phone, address, pizza_name, status) VALUES(?,?,?,?,?)''',(name, phone, userText, p_name, random.choice(status)))
            cursor.execute('''SELECT id FROM orders WHERE phone=(?)''',(phone,))
            rows=cursor.fetchall()
            db.commit()
            flag = 0
            p_name=''
            return 'Your order has been placed successfully. Your order id: '+str(rows[0][0])
        elif(flag==2):
            result=''
            myid=int(userText)
            cursor.execute(''' SELECT count(id) FROM orders WHERE id=(?) ''',(myid,))
            if cursor.fetchone()[0] == 0:
                flag=0
                db.commit()
                return 'Kindly make an order with us'
            cursor.execute('''SELECT * FROM orders WHERE id=(?)''',(myid,))
            rows=cursor.fetchall()
            for i in rows[0]:
                if(result==''):
                    result=str(i)
                else:
                    result=result+', '+i
            flag=0
            db.commit()
            return result[3:]
        elif(flag==4):
            name=userText
            flag=5
            return 'Provide your contact number'
        elif(flag==5):
            phone=userText
            flag=1
            return 'Provide your delivery address'
        else:
            res = str(mybot.get_response(userText))
            if(res=='Kindly provide your name'):
                flag=4
            elif(res=='Please provide your order id'):
                flag=2
            return res

if __name__ == "__main__":
    app.run()

