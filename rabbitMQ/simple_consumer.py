import pika

def callback(ch, method, properties, body):
    print(" [x] Received %r" % body)


credentials = pika.PlainCredentials('rizyy','password@123') # Creates an object with the usernae and password 
parameters = pika.ConnectionParameters('rabbitmq.selfmade.ninja','5672','rizwankendo_rizyy',credentials)

connection = pika.BlockingConnection(parameters) #creates a blocking connection
channel = connection.channel() #Creates a channel for communication with RabbitMQ
channel.queue_declare(queue='my_queue') #Ensures that the queue named 'my_queue' exists. If it doesn't, it creates it.

channel.basic_consume(queue='my_queue',auto_ack=True,on_message_callback=callback)

print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()
