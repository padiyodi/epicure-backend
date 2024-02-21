# epicure-backend
Backend Code for Epicure Robotics

The Gunicorn "Green Unicorn" is a Python Web Server Gateway Interface HTTP server
Run the api.py using command 

gunicorn -b 127.0.0.1:2020 -w2 --timeout 10 juice_api_test:app 

or 

If u want to run the API in background then use this command gunicorn -b 127.0.0.1:2020 -w2 --timeout 10 juice_api_test:app --daemon

# Static folder
In static folder there are 2 sub-folder 1.imges 2.assets 
save images in this foldder for required epicure-project,serve this file in API 

# DataBase
In this used sql Databse the sql means the relation database,created multiple folder for API 

# MQTT 
Basically MQTT means a lightweight, publish-subscribe, machine to machine network protocol for message queue/message queuing service. It is designed for connections with remote locations that have devices with resource constraints 

we used MQTT for get smoothie status from vending machine

