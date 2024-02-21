import paho.mqtt.client as paho
from paho import mqtt
import sys
import time
import ssl


def on_connect(client, userdata, flags, rc):
  print("Connected with result code "+str(rc))
  client.subscribe("/tsb_input")

def on_message(client, userdata, msg):
	global input_flg, input_str

	print(msg.payload.decode())
	input_flg = 1
	data = msg.payload.decode()
	input_str = data
		
def generate_sequence(smoothie_input):
	global ingredients_dict, toppings_dict

	ingredients_str, toppings_str = smoothie_input.split("|")

	ingredients_details = ingredients_str.split('-')
	ingredients_dict = {int(i.split(':')[0]):int(i.split(':')[1]) for i in ingredients_details}
	
	try:
		toppings_details = toppings_str.split('-')
		toppings_dict = {int(i.split(':')[0]):int(i.split(':')[1]) for i in toppings_details}
		top_seq = 1
	except Exception as e:
			print("No toppings!")
			top_seq = 0
	
	if top_seq:
		total_seq = ['w-5', "000_feedback", "w-5", "001_feedback", "w-10", "010_feedback", "w-5", "011_feedback", "w-2", "100_feedback", 'w-10', "101_feedback"]

	else:
		total_seq = ['w-5', "000_feedback", "w-5", "001_feedback", "w-10", "010_feedback", "w-2", "100_feedback", 'w-10', "101_feedback"]

	return total_seq

def start(smoothie_input):
	global main_sequence, ingredients_dict, toppings_dict, dispensed_quans, clean_flag

	try:
		main_sequence = generate_sequence(smoothie_input)
	except:
		client.publish("/tsb_feedback", "incorrect_input")

		return

	st = time.time()
	main()
	print("Total time taken: ", time.time() - st)
	

def main(args=None):
	global main_sequence
	
	for command in main_sequence:

		if "feedback" in command:
			fb, _ = command.split("_")
			client.publish("/tsb_feedback", fb)

		elif 'w' in command:
			_,t = command.split('-')
			
			print("waiting for {} seconds".format(t))
			time.sleep(float(t))
		
		
	client.publish("/tsb_feedback", "110") #process done feedback
	
if __name__ == '__main__':

	main_sequence = []
	ingredients_dict = {}
	toppings_dict = {}
	type_ = 0
	
	broker_address = "bc7ad181ea014fedb722198e18386a65.s2.eu.hivemq.cloud"
	port = 8883  # MQTT port (secure)
	username = "TSB_APP"
	password = "TheSmoothieBar1"

	client = paho.Client()
	input_flg = 0

	# enable TLS for secure connection
	client.tls_set(cert_reqs=ssl.CERT_NONE, tls_version=ssl.PROTOCOL_TLS)


	# set username and password
	client.username_pw_set(username, password)
	# connect to HiveMQ Cloud on port 8883 (default for MQTT)
	client.connect(broker_address, port, keepalive=60)

	client.on_connect = on_connect
	client.on_message = on_message
	client.loop_start()
	
	try:		
		while True:
			if(input_flg):	
				print("Input received:", input_str)
				if input_str == 'q':
					break

				start(input_str)
				input_flg=0
				
	except KeyboardInterrupt:
		print("\nCtrl+C pressed. Exiting...")
		sys.exit(0)
			