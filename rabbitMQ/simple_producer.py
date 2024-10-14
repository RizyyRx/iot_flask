import pika #library used to comm with rabbitMQ
import random
import time

credentials = pika.PlainCredentials('rizyy','password@123') # Creates an object with the usernae and password 
parameters = pika.ConnectionParameters('rabbitmq.selfmade.ninja','5672','rizwankendo_rizyy',credentials)

connection = pika.BlockingConnection(parameters) #creates a blocking connection
channel = connection.channel() #Creates a channel for communication with RabbitMQ
channel.queue_declare(queue='my_queue') #Ensures that the queue named 'my_queue' exists. If it doesn't, it creates it.


while True:
    msg = str(random.random())
    channel.basic_publish(exchange='',routing_key='my_queue',body=msg)
    print("message {} sent",format(msg))
    time.sleep(0.1)
    
connection.close()
