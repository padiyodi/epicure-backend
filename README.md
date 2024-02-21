# Smoothie Bar Web API

This repository contains the source code for a web API designed to manage a smoothie bar system. It provides endpoints for various functionalities such as recipe management, home carousel data, payment initiation, smoothie status updates, feedback handling, and more.

# Features

Recipe Management: Allows users to submit recipes for smoothies, which are then processed and prepared.
Home Carousel: Manages the items displayed in the home carousel, including their names, recipes, prices, discounts, and toppings.
Payment Initiation: Initiates payment processing for completed orders.
Smoothie Status: Provides real-time updates on the status of smoothie preparation.
Feedback Handling: Handles feedback from customers.
Fun Facts: Provides interesting facts related to smoothies.
Sweetness Level: Allows users to customize the sweetness level of their smoothies.
Inventory Management: Manages the inventory of ingredients and items.
Order Completion: Handles order completion and provides relevant information.
Payment Information: Retrieves payment-related information.
Recipe Listing: Lists available recipes.
Promo Code Management: Manages promo codes for discounts.
Static File Serving: Serves static image files for the user interface.

# Usage

Clone the repository: 

git clone https://github.com/padiyodi/epicure-backend.git

Install dependencies:

pip install -r requirements.txt

# Configuration

Configure MQTT Broker Settings:
Open the juice_api_test.py file and locate the following section:
# MQTT broker settings
broker_address = "bc7ad181ea014fedb722198e18386a65.s2.eu.hivemq.cloud"

port = 8883  # MQTT port (secure)
username = "TSB_APP"

password = "TheSmoothieBar1"

mqtt_publisher = "/tsb_input"

mqtt_subscriber = "/tsb_feedback"

Replace the values with your MQTT broker settings.
Optional: Configure Other Settings:
You may need to configure other settings in the juice_api_test.py file according to your requirements, such as database connections, file paths, and endpoint URLs.

Run the application:
gunicorn -b 127.0.0.1:8002 -w2 --timeout 10 juice_api_test:app

# Access the API endpoints as needed:-

You can now access the API endpoints using your preferred API client (e.g., curl, Postman). The default endpoint URLs are:
Home Carousel: /homeCarousel

Payment Initiation: /paymentinitiated

Smoothie Status: /smoothieStatus

Feedback Handling: /feedback

Fun Facts: /funFacts

Sweetness Level: /sweetness

Inventory Management: /getInventory

Order Completion: /orderCompleted

Payment Information: /getPaymentInfo

Recipe Listing: /recipes

Promo Code Management: /promoCode

Adding Promo Codes: /addpromoCode

Adding to Inventory: /addToInventory

Static Files (Images): /pics

and more

# License

This project is licensed under the codecodemischief.tech License - see the LICENSE file for details.

# Acknowledgements

Special thanks to the Falcon framework and other libraries used in this project for their valuable contributions.


