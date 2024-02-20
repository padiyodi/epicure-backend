# epicure-backend
Backend Code for Epicure Robotics

The Gunicorn "Green Unicorn" is a Python Web Server Gateway Interface HTTP server
Run the api.py using command gunicorn -b 127.0.0.1:2020 -w2 --timeout 10 juice_test_api:app 

or 

If u want to run the API in background then use this command gunicorn -b 127.0.0.1:2020 -w2 --timeout 10 juice_test_api:app --daemon

