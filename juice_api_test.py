import random
import traceback
import falcon
import sqlite3
import json
import os
import os
import mimetypes
import uuid
import time
import logging
import threading
import paho.mqtt.client as paho
import ssl
import re
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
site_url = os.getenv('site_url')

class StaticMiddleware:
    def __init__(self, app, static_folder):
        self.app = app
        self.static_folder = static_folder

    def __call__(self, env, start_response):
        path = env.get('PATH_INFO', '')
        filepath = self.static_folder +  path[7:]
        print(f'sending image <{filepath}>',flush=True)
        if os.path.isfile(filepath):
            with open(filepath, 'rb') as file:
                content = file.read()
                status = '200 OK'
                mime_type, _ = mimetypes.guess_type(filepath)
                response_headers = [('Content-type', mime_type)]
                start_response(status, response_headers)
                return [content]
        #else:
        #    start_response('404 NOT FOUND', [('Content-type', 'text/plain')])
        #    return [b'File Not Found']
        return self.app(env, start_response)
    

class StaticMiddlewareForStartup:
    def __init__(self, app, static_folder, endpoint_path):
        self.app = app
        self.static_folder = static_folder
        self.endpoint_path = endpoint_path

    def __call__(self, env, start_response):
        path = env.get('PATH_INFO', '')
        filepath = os.path.join(self.static_folder, path[len(self.endpoint_path):].lstrip("/"))

        if os.path.isfile(filepath):
            with open(filepath, 'rb') as file:
                content = file.read()
                status = '200 OK'
                mime_type, _ = mimetypes.guess_type(filepath)
                response_headers = [('Content-type', mime_type)]
                start_response(status, response_headers)
                return [content]

        return self.app(env, start_response)

try:
    conn = sqlite3.connect('juice_vending_api.db')
    cursor = conn.cursor()

   
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS ingridients_prices (
        Id INTEGER PRIMARY KEY,
        Type TEXT,
        Name TEXT,
        Custom_grams INTEGER,
        Toppings_grams INTEGER,
        Price_gram REAL,
        img_url TEXT,
        Weight INTEGER  -- Corrected column definition
    )
''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS paymentinitiated (
        sr_no INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id TEXT,
        recipe_string TEXT,
        user_name TEXT,
        user_phone TEXT,
        amount REAL,
        selected_base TEXT,
        sweetness_level TEXT,
        smoothie_status INTEGER DEFAULT 1,
        ingredient_A_quantity INTEGER,
        ingredient_B_quantity INTEGER,
        ingredient_C_quantity INTEGER
    )
''')





    cursor.execute('''
    CREATE TABLE IF NOT EXISTS recipes (
        name TEXT PRIMARY KEY,
        recipe TEXT,
        price INTEGER,
        discount INTEGER,
        toppings TEXT,
        nutrition_info TEXT,
        about TEXT
    )
''')

    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS received_payments (
            phone_number TEXT,
            amount INTEGER,
            order_id INTEGER
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS promo_codes (
            serial_number TEXT PRIMARY KEY,
            promo_code TEXT,
            status TEXT
        )
    ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS smoothie_combinations (
        combination_id INTEGER PRIMARY KEY,
        picking_up_fruits TEXT,
        blending TEXT,
        toppings TEXT,
        final_stage TEXT
    )
''')
    smoothie_combinations_data = [
    (1, "Hello [Customer's Name]! We're gathering the freshest fruits for your custom smoothie. Please hold tight, it'll just be another moment.",
     "Great choices, Your selected fruits are now being blended into a delicious smoothie. The aroma is amazing!",
     "We're almost there, [Customer's Name]! Toppings are being added to your smoothie for that perfect finishing touch.",
     "Choosing our smoothie is a step toward a healthier you. Enjoy the taste and we look forward to welcoming you back again. 🍹 #SmartSips #SmoothieAdventures"),
    (2, "Hey [User's Name]! Your fresh, healthy smoothie is in the works! 🍓🍌 We're gathering the best ingredients to kickstart your day right!",
     "Our blenders are working their magic Your unique blend is getting perfectly crafted. 🌀",
     'Adding the finishing touch, [User\'s Name]! Toppings for a burst of flavor, You\'ve crafted a smart choice!"',
     "Your personalized smoothie is a subtle win for your well-being. Enjoy this moment, and we'll be here waiting for you again 🥤 #SmartChoices #SmoothieMagic"),
    (3, "Hey [User's Name]! We're picking the freshest fruits for your super-smooth smoothie! Your choice for health today is a win – great start!",
     "Your blend is in progress. We're turning your healthy choice into a tasty reality. Pat yourself on the back!",
     'Adding the finishing touch, [User\'s Name]! Toppings for an extra flavor kick and a boost of goodness',
     "Your smoothie choice whispers health and pride. Enjoy every sip, and we're excited to have you back for more subtle victories. 🌟 #SmartSips #SmoothieWhispers")
]
    

    inventory_data = [
        (1, 'Powder', 'Coco Powder', 10, 5, 1,'static/images/1.jpg',669),
        (2, 'Powder', 'Whey Protein', 5, 5, 2.4,'static/images/2.jpg',735),
        (3, 'Powder', 'Dry Fruits', 5, 5, 1.75,'static/images/3.jpg',750),
        (4, 'Powder', 'Cinnamon', 5, 5, 1.8,'static/images/4.jpg',561),
        (5, 'Powder', 'Pumpkin Seeds', 8, 5, 1.1,'static/images/5.jpg',750),
        (6, 'Powder', 'Sunflower Seeds', 8, 5, 0.5,'static/images/6.jpg',750),
        (7, 'Powder', 'Chia Seeds', 8, 5, 0.5,'static/images/7.jpg',690),
        (8, 'Solid', 'Apple', 30, 5, 0.1,'static/images/8.jpg',3847),
        (9, 'Solid', 'Banana', 30, 5, 0.048,'static/images/9.jpg',3770),
        (10, 'Solid', 'Papaya', 30, 5, 0.071,'static/images/10.jpg',3928),
        (11, 'Solid', 'Strawberry', 30, 5, 0.5,'static/images/11.jpg',4000),
        (12, 'Solid', 'Muskmelon', 30, 5, 0.04,'static/images/12.jpg',3991),
        (13, 'Solid', 'Pineapple', 30, 5, 0.07,'static/images/13.jpg',3800),
        (14, 'Solid', 'Dates', 30, 5, 0.18,'static/images/14.jpg',4000),
        (15, 'Solid', 'Oats', 30, 5, 0.13,'static/images/15.jpg',3729),
        (16, 'Liquid', 'Milk', 30, 5, 0.054,'static/images/16.jpg',5000),
        (17, 'Liquid', 'Milk', 30, 5, 0.054,'static/images/17.jpg',5000),
        (18, 'Liquid', 'Water', 30, 5, 0.02,'static/images/18.jpg',5000),
        (19, 'Liquid', 'Water', 30, 5, 0.02,'static/images/19.jpg',5000),
        (20,  'Liquid', 'Honey', 30, 5, 0.2,'static/images/20.jpg',4990),
        (21, 'Liquid', 'Coconut Milk', 30, 5, 0.1,'static/images/21.jpg',4760)
    ]

    recipes_data = [
    (
        'Tropical Delight',
        '13:100-9:100-21:120-20:5',
        150,
        25,
        '1,2,3,4,5,6',
        'calories-80Kcal;carbs-319g;proteins-71g;sodium-6mg;Fiber-55mg;calcium-3mg;totalfat-7g;potassium-1.2mg',
        'Immerse your taste buds in a refreshing blend of tropical fruits, including succulent pineapple, juicy mango, and creamy coconut. A delightful sip of paradise to brighten your day.'
    ),
    (
        'Berry Blast',
        '11:50-13:50-16:150-20:5',
        220,
        25,
        '1,2,3,4,5,20',
        'calories-90Kcal;carbs-119g;proteins-81g;sodium-9mg;Fiber-58mg;calcium-5mg;totalfat-4g;potassium-1.4mg',
        'Indulge in a burst of flavors with our Berry Blast Salad. A medley of sweet strawberries, plump blueberries, and tart raspberries tossed with crisp greens, creating a vibrant and nutritious sensation.'
    )
]



    # Change this line to use INSERT instead of INSERT OR REPLACE
    cursor.executemany('INSERT OR REPLACE INTO ingridients_prices (Id, Type, Name, Custom_grams, Toppings_grams, Price_gram, img_url,Weight) VALUES (?, ?, ?, ?, ?, ?, ?,?)', inventory_data)
    cursor.executemany('''
    INSERT OR REPLACE INTO recipes (name, recipe, price, discount, toppings, nutrition_info, about)
    VALUES (?, ?, ?, ?, ?, ?, ?)
''', recipes_data)

    cursor.executemany('INSERT OR REPLACE INTO smoothie_combinations (combination_id, picking_up_fruits, blending, toppings, final_stage) VALUES (?, ?, ?, ?, ?)', smoothie_combinations_data)
    
    conn.commit()

    conn.commit()
    conn.close()

except sqlite3.Error as e:
    print(f"SQLite Error: {e}")
finally:
    conn.close()


class GetInventory:
    def on_get(self, req, resp):
        try:
            logging.info('Handling GET request for inventory')
            conn = sqlite3.connect('juice_vending_api.db')
            cursor = conn.cursor()

            inventory = []
            cursor.execute('SELECT * FROM ingridients_prices')
            rows = cursor.fetchall()

            for row in rows:
                img_file_name = row[6]
                img_url = f'{site_url}/{img_file_name}'
                inventory.append({
                    'id': str(row[0]),
                    'type': row[1],
                    'name': row[2],
                    'custom_grams': row[3],
                    'toppings_grams': row[4],
                    'price_gram': str(row[5]),
                    'img_url': img_url,
                    'weights': row[7]
                })

            conn.close()

            response_data = {
                'status_code': "0",
                'status_desc': "Getting successfully Inventory",
                'data': inventory
            }

            resp.body = json.dumps(response_data)
            resp.status = falcon.HTTP_200

            # Log the response payload
            logging.info(f"GET response payload: {response_data}")

        except Exception as e:
            logging.error(f"Error in GetInventory: {e}")
            response_data = {
                'status_code': "1",
                'status_desc': f"Error: {str(e)}",
                'data': []
            }
            resp.body = json.dumps(response_data)
            resp.status = falcon.HTTP_500

            logging.error(f"Error in GetInventory: {e}")
            traceback.print_exc()

class AddToInventory:
    def on_post(self, req, resp):
        try:
            # Parse JSON data from the request body
            data = json.loads(req.stream.read().decode('utf-8'))
            logging.info(f'Handling POST request to add item to inventory: {data}')
            
            # Extract data from the JSON payload
            item_type = data.get('type', '')
            item_name = data.get('name', '')
            custom_grams = data.get('custom_grams', 0)
            toppings_grams = data.get('toppings_grams', 0)
            price_gram = data.get('price_gram', 0)
            img_url = data.get('img_url', '')
            weight = data.get('weight', None)  # Assuming weight field exists in the JSON payload

            # Insert data into the database
            conn = sqlite3.connect('juice_vending_api.db')
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO ingridients_prices (Type, Name, Custom_grams, Toppings_grams, Price_gram, img_url, Weight)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (item_type, item_name, int(custom_grams), int(toppings_grams), float(price_gram), img_url, weight))

            # Get the ID of the last inserted row
            item_id = cursor.lastrowid

            conn.commit()
            conn.close()

            # Prepare response data
            response_data = {
                'status_code': "0",
                'status_desc': 'Item added to inventory successfully!',
                'data': {
                    'id': str(item_id),
                    'type': item_type,
                    'name': item_name,
                    'custom_grams': int(custom_grams),
                    'toppings_grams': int(toppings_grams),
                    'price_gram': str(price_gram),
                    'img_url': img_url,
                    'weight': weight
                }
            }

            resp.body = json.dumps(response_data)
            resp.status = falcon.HTTP_200

        except Exception as e:
            logging.error(f'Error handling POST request to add item to inventory: {str(e)}')
            # Handle exceptions and return appropriate response
            response_data = {
                'status_code': "1",
                'status_desc': f"Error: {str(e)}",
                'data': {}
            }
            resp.body = json.dumps(response_data)
            resp.status = falcon.HTTP_500

            print(f"Error in AddToInventory: {e}")
            traceback.print_exc()

class OrderCompleted:
    def on_post(self, req, resp):
        data = json.load(req.bounded_stream)

        resp.status = falcon.HTTP_200

class GetRecipes:
    def on_get(self, req, resp):
        try:
            conn = sqlite3.connect('juice_vending_api.db')
            cursor = conn.cursor()

            recipes = []
            cursor.execute('SELECT name, recipe, price, discount, toppings, nutrition_info, about FROM recipes')
            rows = cursor.fetchall()

            for row in rows:
                recipes.append({
                    'name': row[0],
                    'recipe': row[1],
                    'price': row[2],
                    'discount': row[3],
                    'toppings': [int(topping) for topping in row[4].split(',')],
                    'nutrition_info': row[5],
                    'about': row[6]
                })

            conn.close()

            response_data = {
                'status_code': "0",
                'status_desc': "recipes",
                'data': recipes
            }

            # Log the full payload
            logging.info(f"GET response payload: {response_data}")

            resp.body = json.dumps(response_data)
            resp.status = falcon.HTTP_200
        except Exception as e:
            response_data = {
                'status_code': "1",
                'status_desc': "Recipes data is not Found",
                'message': f"Error: {str(e)}",
                'data': []
            }

            # Log the full payload
            logging.error(f"Error in GetRecipes: {response_data}")

            resp.body = json.dumps(response_data)
            resp.status = falcon.HTTP_500
class AddRecipe:
    def on_post(self, req, resp):
        try:
            data = json.loads(req.stream.read().decode('utf-8'))
            logging.info(f'Handling POST request for adding a recipe: {data}')

            conn = sqlite3.connect('juice_vending_api.db')
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO recipes (name, recipe, price, discount, toppings, nutrition_info, about)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                data.get('name', ''),
                data.get('recipe', ''),
                data.get('price', 0),
                data.get('discount', 0),  # Assuming discount is provided in the request
                data.get('toppings', ''),
                data.get('nutrition_info', ''),
                data.get('about', '')
            ))

            conn.commit()
            conn.close()

            # Prepare response data for success
            response_data = {
                'status_code': "0",
                'status_desc': 'Recipe added successfully',
                'data': {
                    'name': data.get('name', ''),
                    'recipe': data.get('recipe', ''),
                    'price': data.get('price', 0),
                    'discount': data.get('discount', 0),
                    'toppings': [int(topping) for topping in data.get('toppings', '').split(',')],
                    'nutrition_info': data.get('nutrition_info', ''),
                    'about': data.get('about', '')
                }
            }

            resp.body = json.dumps(response_data)
            resp.status = falcon.HTTP_200

            logging.info('POST request for adding a recipe successful')

        except Exception as e:
            # Handle exceptions and return appropriate response
            response_data = {
                'status_code': "1",
                'status_desc': f"Error: {str(e)}",
                'data': {}
            }
            resp.body = json.dumps(response_data)
            resp.status = falcon.HTTP_500

            # Log the error for debugging
            logging.error(f"Error in AddRecipe POST request: {e}")


class PromoCodeResource:
    def on_get(self, req, resp):
        try:
            logging.info('Handling GET request for promocode ')
            
            with sqlite3.connect('juice_vending_api.db') as conn:
                cursor = conn.cursor()

                promo_codes = []
                cursor.execute('SELECT * FROM promo_codes')
                rows = cursor.fetchall()

                for row in rows:
                    promo_codes.append({
                        'serial_number': row[0],
                        'promo_code': row[1],
                        'status': row[2]
                    })

                # Prepare response data
                response_data = {
                    'status_code': "0",
                    'status_desc': 'promocode getting successfully',
                    'data': promo_codes
                }

                # Log the full payload
                logging.info(f"GET response payload: {response_data}")

                resp.body = json.dumps(response_data)
                resp.status = falcon.HTTP_200
        except Exception as e:
            # Handle exceptions and return appropriate response
            response_data = {
                'status_code': "1",
                'status_desc': f"Error: {str(e)}",
                'data': []
            }

            # Log the full payload
            logging.error(f"Error in PromoCodeResource GET request: {response_data}")

            resp.body = json.dumps(response_data)
            resp.status = falcon.HTTP_500

class AddPromoCodeResource:
    def on_post(self, req, resp):
        try:
            
            data = json.loads(req.stream.read().decode('utf-8'))
            logging.info(f'Handling POST request of Add promo{data}')
            with sqlite3.connect('juice_vending_api.db') as conn:
                cursor = conn.cursor()

                cursor.execute('''
                    INSERT INTO promo_codes (serial_number, promo_code, status)
                    VALUES (?, ?, ?)
                ''', (data.get('serial_number', ''), data.get('promo_code', ''), data.get('status', '')))

            # Prepare response data
            response_data = {
                'status_code': "0",
                'status_desc': 'Added promocode sucussfully!',
                'data': {
                    'serial_number': data.get('serial_number', ''),
                    'promo_code': data.get('promo_code', ''),
                    'status': data.get('status', '')
                }
            }

            resp.body = json.dumps(response_data)
            resp.status = falcon.HTTP_200
        except Exception as e:
            logging.error(f"Error in addpromo POST: {e}")
            # Handle exceptions and return appropriate response
            response_data = {
                'status_code': "1",
                'status_desc': f"Error: {str(e)}",
                'data': {}
            }
            resp.body = json.dumps(response_data)
            resp.status = falcon.HTTP_500

            # Log the error for debugging
            print(f"Error in AddPromoCodeResource: {e}")
            traceback.print_exc()  # Add this line for detailed traceback

class SweetnessResource:
    def __init__(self):
        self.sweetness_levels = [
            {"sweetness_level": "low", "grams": 6},
            {"sweetness_level": "medium", "grams": 10},
            {"sweetness_level": "high", "grams": 12},
        ]

    def on_get(self, req, resp):
        try:
            logging.info('Handling GET request for sweetness levels')
            
            response_data = {
                'status_code': "0",
                'status_desc': 'success',
                'data': self.sweetness_levels
            }

            resp.body = json.dumps(response_data)
            resp.status = falcon.HTTP_200
            
            # Log the response payload
            logging.info(f'GET response for sweetness levels: {response_data}')

        except Exception as e:
            response_data = {
                'status_code': "1",
                'status_desc': f"Error: {str(e)}",
                'data': {}
            }
            resp.body = json.dumps(response_data)
            resp.status = falcon.HTTP_500

            # Log the error for debugging
            logging.error(f"Error in SweetnessResource GET request: {e}")

class FunFactsResource:
    def on_get(self, req, resp):
        try:
            fun_facts = [
                "Smoothies were popularized in the 1930s as a health food, and today, they're not just a trend but a tasty tradition!",
                "The word 'smoothie' was officially added to the Oxford English Dictionary in 2003, marking its status as a delightful language addition!",
                "The world's largest smoothie was made in 2017, weighing over 44,000 pounds. Imagine the blend of flavors in that colossal concoction!",
                "Banana-based smoothies are known for their natural ability to replenish electrolytes, making them a tasty choice after a workout.",
                "Smoothies became an international sensation after surfers in Hawaii added fresh fruit to their blended drinks in the 1970s. A wave of flavor innovation was born!",
                "Smoothies are not just for humans! Some zoos serve 'animal smoothies' made from fruits and vegetables for their residents – a refreshing treat for all!",
                "The inventor of the first blender, Stephen J. Poplawski, likely never imagined his creation would lead to the global phenomenon of delicious, nutritious smoothies!"
            ]

            random_fact = random.choice(fun_facts)

            response_data = {
                'status_code': "0",
                'status_desc': 'funfacts successfully getting',
                'data': {'fun_fact': random_fact}
            }

            resp.body = json.dumps(response_data)
            resp.status = falcon.HTTP_200

            # Log the response payload
            logging.info(f'GET response for FunFactsResource: {response_data}')

        except Exception as e:
            response_data = {
                'status_code': "1",
                'status_desc': f"Error: {str(e)}",
                'data': {}
            }
            resp.body = json.dumps(response_data)
            resp.status = falcon.HTTP_500

            # Log the error for debugging
            logging.error(f"Error in FunFactsResource GET request: {e}")


class SmoothieCombinationResource:
    def on_get(self, req, resp, combination_id):
        try:
            conn = sqlite3.connect('juice_vending_api.db')
            cursor = conn.cursor()

            cursor.execute('SELECT * FROM smoothie_combinations WHERE combination_id = ?', (combination_id,))
            row = cursor.fetchone()

            if row:
                combination_data = {
                    'combination_id': row[0],
                    'picking_up_fruits': row[1],
                    'blending': row[2],
                    'toppings': row[3],
                    'final_stage': row[4]
                }

                response_data = {
                    'status_code': "0",
                    'status_desc': 'smoothie combination successful',
                    'data': combination_data
                }

                resp.body = json.dumps(response_data)
                resp.status = falcon.HTTP_200

                # Log the response payload
                logging.info(f'GET response for SmoothieCombinationResource: {response_data}')
            else:
                response_data = {
                    'status_code': "1",
                    'status_desc': 'Combination not found',
                    'data': {}
                }

                resp.body = json.dumps(response_data)
                resp.status = falcon.HTTP_404

                # Log the response payload
                logging.info(f'GET response for SmoothieCombinationResource: {response_data}')

        except Exception as e:
            response_data = {
                'status_code': "1",
                'message': f"Error: {str(e)}",
                'data': {}
            }
            resp.body = json.dumps(response_data)
            resp.status = falcon.HTTP_500
            logging.error(f"Error handling GET request for SmoothieCombinationResource: {str(e)}")
        finally:
            conn.close()
class PaymentInitiate:
    def __init__(self, mqtt_client):
        self.mqtt_client = mqtt_client

    def parse_recipe_string(self, recipe_string):
        ingredients_pattern = re.compile(r'([A-Za-z]+):(\d+)')

        try:
            # Parse ingredients
            ingredients = dict(ingredients_pattern.findall(recipe_string))

            return {
                'ingredients': ingredients,
            }

        except ValueError:
            # Handle the case when there are no ingredients (e.g., "A:XXX-B:XXX-C:XXX")
            ingredients = dict(ingredients_pattern.findall(recipe_string))
            return {
                'ingredients': ingredients,
            }

    def on_post(self, req, resp):
        try:
            # Parse JSON data from the request body
            data = json.loads(req.stream.read().decode('utf-8'))

            logging.info(f'Handling POST request to initiate payment {data}')

            # Extract data from the JSON payload
            recipe_string = data.get('recipe_string', '')
            user_name = data.get('user_name', '')
            user_phone = data.get('user_phone', '')
            amount = data.get('amount', 0)
            selected_base = data.get('selected_base', '')
            sweetness_level = data.get('sweetness_level', '')

            # Parse recipe string
            parsed_recipe = self.parse_recipe_string(recipe_string)

            # Generate a unique order_id using uuid
            order_id = str(uuid.uuid4())

            # Extract ingredient quantities from the parsed recipe
            ingredient_a_quantity = parsed_recipe['ingredients'].get('A', 0)
            ingredient_b_quantity = parsed_recipe['ingredients'].get('B', 0)
            ingredient_c_quantity = parsed_recipe['ingredients'].get('C', 0)

            # Insert data into the database
            conn = sqlite3.connect('juice_vending_api.db')
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO paymentinitiated (
                    order_id, recipe_string, user_name, user_phone, amount,
                    ingredient_A_quantity, ingredient_B_quantity, ingredient_C_quantity,
                    selected_base, sweetness_level
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                order_id, recipe_string, user_name, user_phone, float(amount),
                int(ingredient_a_quantity), int(ingredient_b_quantity), int(ingredient_c_quantity),
                selected_base, sweetness_level
            ))

            conn.commit()
            conn.close()

            # Publish the recipe string to the MQTT client
            self.mqtt_client.publish_data(recipe_string)

            response_data = {
                'status_code': "0",
                'status_desc': "Recipe order saved successfully!",
                'data': {
                    'order_id': order_id,
                    'recipe_string': recipe_string,
                    'parsed_recipe': parsed_recipe,
                    'user_name': user_name,
                    'user_phone': user_phone,
                    'amount': amount,
                    'selected_base': selected_base,
                    'sweetness_level': sweetness_level
                }
            }

            resp.body = json.dumps(response_data)
            resp.status = falcon.HTTP_200

            logging.info(f'Payment initiation successful. Order ID: {order_id}')

        except Exception as e:
            response_data = {
                'status_code': "1",
                'status_desc': f"Error: {str(e)}",
                'data': {}
            }
            resp.body = json.dumps(response_data)
            resp.status = falcon.HTTP_500

            # Log the error for debugging
            logging.error(f"Error in PaymentInitiate: {e}")
            traceback.print_exc()
            
class GetPaymentInfo:
    def on_get(self, req, resp):
        try:
            conn = sqlite3.connect('juice_vending_api.db')
            cursor = conn.cursor()

            cursor.execute("SELECT order_id FROM paymentinitiated ORDER BY sr_no DESC LIMIT 1")
            

            order_data = cursor.fetchone()

            conn.close()

            if order_data:
                response_data = {
                    'status_code': "0",
                    'status_desc': "order retrieved successfully!",
                    'data': {
                        'order_id': order_data[0]
                    }
                }
                resp.body = json.dumps(response_data)
                resp.status = falcon.HTTP_200
            else:
                response_data = {
                    'status_code': "0",
                    'status_desc': "order not found!",
                    
                    'data': {}
                }
                resp.body = json.dumps(response_data)
                resp.status = falcon.HTTP_404

        except Exception as e:
            response_data = {
                'status': False,
                'error': True,
                'message': f"Error: {str(e)}",
                'data': {}
            }
            resp.body = json.dumps(response_data)
            resp.status = falcon.HTTP_500

            # Log the error for debugging
  


class SmoothieFeedbackResource:
    def create_table(self):
        # Connect to the database
        conn = sqlite3.connect('juice_vending_api.db')
        cursor = conn.cursor()

        # Create the smoothie_feedback table if it does not exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS smoothie_feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id TEXT NOT NULL,
                rating INTEGER NOT NULL
            )
        ''')

        # Commit the changes and close the connection
        conn.commit()
        conn.close()

    def on_post(self, req, resp):
        try:
            # Parse the JSON request body
            req_data = json.loads(req.stream.read().decode('utf-8'))

            # Extract smoothie rating and order_id from the request data
            rating = req_data.get('rating')
            order_id = req_data.get('order_id')

            # Validate input (rating should be between 0 and 5)
            if not isinstance(rating, int) or not 0 <= rating <= 5:
                raise ValueError("Invalid rating")

            # Validate order_id
            if not order_id or not isinstance(order_id, str):
                raise ValueError("Invalid order_id")

            # Connect to the database and create the table
            self.create_table()

            # Connect to the database for inserting feedback
            conn = sqlite3.connect('juice_vending_api.db')
            cursor = conn.cursor()

            # Store the feedback in the database
            cursor.execute("INSERT INTO smoothie_feedback (order_id, rating) VALUES (?, ?)", (order_id, rating))
            conn.commit()
            conn.close()

            # Prepare the response payload
            response_data = {
                'status_code': "0",
                'status_desc': 'smoothieFeedback',
                'data': {
                    'order_id': order_id,
                    'rating': rating
                }
            }

            # Log the response payload
            logging.info(f'Smoothie Feedback Response Payload: {json.dumps(response_data)}')

            # Store the response in the request context
            resp.body = json.dumps(response_data)
            resp.status = falcon.HTTP_200

        except ValueError as ve:
            logging.error(f'Error in SmoothieFeedbackResource POST request: {str(ve)}', exc_info=True)
            resp.status = falcon.HTTP_400
            resp.body = json.dumps({'error': 'Bad Request - Invalid Input'})

        except Exception as e:
            logging.error(f'Error in SmoothieFeedbackResource POST request: {str(e)}', exc_info=True)
            resp.status = falcon.HTTP_500
            resp.body = json.dumps({'error': 'Internal Server Error'})

    def on_get(self, req, resp):
        try:
            # Extract order_id from the query string parameters
            order_id = req.params.get('order_id')

            # If order_id is not provided, fetch the latest order_id from smoothie_feedback
            if not order_id:
                # Connect to the database
                conn = sqlite3.connect('juice_vending_api.db')
                cursor = conn.cursor()

                # Fetch the latest order_id from the 'smoothie_feedback' table
                cursor.execute("SELECT order_id FROM smoothie_feedback ORDER BY id DESC LIMIT 1")
                latest_order_id = cursor.fetchone()

                if latest_order_id:
                    order_id = latest_order_id[0]
                else:
                    conn.close()
                    logging.error("No orders available.")
                    resp.body = json.dumps({'error': 'No orders available.'})
                    resp.status = falcon.HTTP_404
                    return

                conn.close()

            # Validate order_id
            if not order_id or not isinstance(order_id, str):
                raise ValueError("Invalid order_id")

            # Connect to the database
            conn = sqlite3.connect('juice_vending_api.db')
            cursor = conn.cursor()

            # Fetch the feedback for the specified order_id
            cursor.execute("SELECT rating FROM smoothie_feedback WHERE order_id = ? ORDER BY id DESC LIMIT 1", (order_id,))
            feedback = cursor.fetchone()

            # Close the database connection
            conn.close()

            if feedback:
                feedback = feedback[0]
            else:
                feedback = "No feedback available for the specified order."

            # Prepare the response payload
            response_data = {
                'status_code': "0",
                'status_desc': 'smoothieFeedback',
                'data': {
                    'order_id': order_id,
                    'feedback': feedback
                }
            }

            # Log the response payload
            logging.info(f'Smoothie Feedback GET Response Payload: {json.dumps(response_data)}')

            # Store the response in the request context
            resp.body = json.dumps(response_data)
            resp.status = falcon.HTTP_200

        except ValueError as ve:
            logging.error(f'Error in SmoothieFeedbackResource GET request: {str(ve)}', exc_info=True)
            resp.status = falcon.HTTP_400
            resp.body = json.dumps({'error': 'Bad Request - Invalid Input'})

        except Exception as e:
            logging.error(f'Error in SmoothieFeedbackResource GET request: {str(e)}', exc_info=True)
            resp.status = falcon.HTTP_500
            resp.body = json.dumps({'error': 'Internal Server Error'})

class MQTTClient:
    def __init__(self, broker_address, port, username, password, mqtt_publisher, mqtt_subscriber):
        self.client = paho.Client()
        self.client.tls_set(cert_reqs=ssl.CERT_NONE, tls_version=ssl.PROTOCOL_TLS)
        self.client.username_pw_set(username, password)
        self.client.connect(broker_address, port, keepalive=60)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.loop_start()
        self.mqtt_publisher = mqtt_publisher
        self.mqtt_subscriber = mqtt_subscriber
        self.next_order = False
        self.last_received_messages = []
        self.recipe_resource = None  # Reference to RecipeResource instance
        self.lock = threading.Lock()

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker")
            client.subscribe(self.mqtt_subscriber)
        else:
            print("Connection failed")

    def on_message(self, client, userdata, msg):
        with self.lock:
            message_data = {
                "000": "Cup placed",
                "001": "Ingredients dispensed",
                "010": "Blending completed",
                "011": "Going for toppings",
                "100": "Your smoothie is ready",
                "101": "Cup removed",
                "110": "Process done",
                "incorrect_input": "Incorrect Input"
            }

            message_code = msg.payload.decode()
            print("Received: {} - {}".format(message_code, message_data.get(message_code, "Unknown")))
            self.last_received_messages.append({"code": message_code, "message": message_data.get(message_code, "Unknown")})

            if message_code == "110" or message_code == "incorrect_input":
                self.next_order = True

                # Update live updates in the RecipeResource instance
                if self.recipe_resource is not None:
                    with self.recipe_resource.lock:
                        self.recipe_resource.live_updates = list(self.last_received_messages)

    def publish_data(self, data):
        self.client.publish(self.mqtt_publisher, data)

    def set_recipe_resource(self, recipe_resource):
        self.recipe_resource = recipe_resource

class RecipeResource:
    def __init__(self, mqtt_client):
        self.mqtt_client = mqtt_client
        self.last_received_message = 'No new messages'
        self.live_updates = []
        self.lock = threading.Lock()

        # Set the RecipeResource instance in the MQTTClient
        self.mqtt_client.set_recipe_resource(self)

    def on_post(self, req, resp):
        try:
            recipe_data = json.loads(req.stream.read().decode('utf-8'))
            recipe_string = recipe_data['recipe']
            print("Received recipe string:", recipe_string)

            # Process the recipe string and publish data
            self.mqtt_client.publish_data(recipe_string)

            # Wait for the next order
            while not self.mqtt_client.next_order:
                pass
            self.mqtt_client.next_order = False

            # Update the last received message
            with self.lock:
                self.last_received_message = 'Next order'
                self.live_updates = self.mqtt_client.last_received_messages

            # Return the response
            response_data = {
                'code': 200,
                'message': self.last_received_message,
                'live_updates': self.live_updates
            }
            resp.media = response_data
            resp.status = falcon.HTTP_200
            print("Response Payload:", json.dumps(response_data))
        except Exception as e:
            print("Error processing recipe:", str(e))
            resp.status = falcon.HTTP_400
            resp.media = {'code': 400, 'message': 'Bad Request'}

    def on_get(self, req, resp):
        # Return the response with the last received message and live updates
        with self.lock:
            if self.mqtt_client.last_received_messages:
                last_update = self.mqtt_client.last_received_messages[-1]

                # Check if the message is "Process done" with code "110"
                if last_update['code'] == "110":
                    # Increment the hit count
                    RecipeResource.hit_count += 1

                    # Check if it's the second hit
                    if RecipeResource.hit_count == 1:
                        # Return an empty response and reset the hit count
                        resp.media = {'code': 200, 'message': 'No new messages', 'live_updates': []}
                        RecipeResource.hit_count = 0
                        # Clear live updates after sending the last one in the response
                        self.mqtt_client.last_received_messages.clear()
                        self.live_updates.clear()
                    else:
                        # Return the standard response
                        response_data = {
                            'status_code': "0",
                            'status_desc': "soomthie status",
                            'message': last_update['message'],
                            'live_updates': [last_update]
                        }
                        resp.media = response_data
                else:
                    # Reset the hit count if the message is not "110"
                    RecipeResource.hit_count = 0
                    # Return the standard response
                    response_data = {
                        'status_code': "0",
                        'status_desc': "soomthie status",
                        'message': last_update['message'],
                        'live_updates': [last_update]
                    }
                    resp.media = response_data
            else:
                # Return the standard empty response
                resp.media = {'code': 200, 'message': 'No new messages', 'live_updates': []}

            resp.status = falcon.HTTP_200

    def receive_live_updates(self):
        def on_message(client, userdata, msg):
            with self.lock:
                print("Received live update:", msg.payload.decode())
                self.live_updates.append(msg.payload.decode())

        while True:
            try:
                if self.mqtt_client.client is not None:
                    self.mqtt_client.client.on_message = on_message
                    self.mqtt_client.client.subscribe("/tsb_feedback")
                    self.mqtt_client.client.loop_start()  # Use loop_start instead of loop_forever

                    # Sleep for a while to allow the loop to run in the background
                    time.sleep(60)
                else:
                    print("MQTT client is None. Reconnecting...")
                    self.mqtt_client.client = paho.Client()
                    self.mqtt_client.client.tls_set(cert_reqs=ssl.CERT_NONE, tls_version=ssl.PROTOCOL_TLS)
                    self.mqtt_client.client.username_pw_set(self.mqtt_client.username, self.mqtt_client.password)
                    self.mqtt_client.client.on_connect = self.mqtt_client.on_connect
                    self.mqtt_client.client.connect(self.mqtt_client.broker_address, self.mqtt_client.port, keepalive=60)

            except Exception as e:
                print("Error in receive_live_updates:", str(e))
                logging.exception("Error in receive_live_updates")
                time.sleep(1)

def start_live_updates():
    live_updates_thread = threading.Thread(target=recipe_resource.receive_live_updates)
    live_updates_thread.start()

# MQTT broker settings
broker_address = "bc7ad181ea014fedb722198e18386a65.s2.eu.hivemq.cloud"
port = 8883  # MQTT port (secure)
username = "TSB_APP"
password = "TheSmoothieBar1"
mqtt_publisher = "/tsb_input"
mqtt_subscriber = "/tsb_feedback"

# Create MQTT client instance
mqtt_client = MQTTClient(
    broker_address=broker_address,
    port=port,
    username=username,
    password=password,
    mqtt_publisher=mqtt_publisher,
    mqtt_subscriber=mqtt_subscriber
)


class PicsResource:
    def on_get(self, req, resp):
        # Define the list of file names or URLs
        file_names = ['bottomCurve.svg', 'carousel1.png', 'carousel2.png', 'carousel3.png', 'circle.svg',
                      'create_menu_icon.png', 'cupAnimation.mp4', 'exotic.svg', 'fitness.svg', 'fullMeals.svg',
                      'glassLevel1.png', 'glassLevel2.png', 'glassLevel3.png', 'glassLevel4.png', 'glassLevel5.png',
                      'main_menu_bg.png', 'menu_icon.png', 'menu_icon.png', 'plus.svg', 'product_img.png',
                      'selection_bg.png', 'smoothieLoadingAnimation1.gif', 'smoothieLoadingAnimation2.gif',
                      'smoothieLoadingAnimation3.mp4', 'smoothieWithStraw.png', 'star.svg', 'tastyDelights.svg', 
                      '1.jpg','2.jpg','3.jpg','4.jpg','5.jpg','6.jpg','7.jpg','8.jpg','9.jpg','10.jpg','11.jpg','12.jpg',
                      '13.jpg','14.jpg','15.jpg','16.jpg','17.jpg','18.jpg','19.jpg','20.jpg','21.jpg']

        # Create the response data
        response_data = {
            "status_code": "0",
            "status_desc": "pics",
            "data": [{"Pic_url": f"/startup/{file_name}"} for file_name in file_names]
        }

        resp.body = json.dumps(response_data)
        resp.status = falcon.HTTP_200

class HomeCarouselResource:
    def __init__(self):
        # Create a SQLite database connection
        self.conn = sqlite3.connect('juice_vending_api.db')
        self.cursor = self.conn.cursor()

        # Create the home_carousel_data table if not exists
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS home_carousel_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                recipe TEXT,
                price INTEGER,
                discount INTEGER,
                toppings TEXT,
                nutrition_info TEXT,
                about TEXT
            )
        ''')
        self.conn.commit()

    def on_post(self, req, resp):
        try:
            # Parse the JSON request body
            req_data = json.loads(req.stream.read().decode('utf-8'))

            name = req_data.get('name')
            recipe = req_data.get('recipe')
            price = req_data.get('price')
            discount = req_data.get('discount')
            toppings = json.dumps(req_data.get('toppings'))
            nutrition_info = req_data.get('nutrition_info')
            about = req_data.get('about')

            # Validate input
            if not name or not recipe or not price or not discount or not toppings or not nutrition_info or not about:
                raise ValueError("All fields are required")

            # Insert or update home carousel data in the database
            self.insert_or_update_home_carousel_data(name, recipe, price, discount, toppings, nutrition_info, about)

            # Fetch all data from the database after the update
            carousel_data = self.fetch_all_home_carousel_data()

            # Respond with success message
            response_data = {
                "status_code": "0",
                "status_desc": "homeCarousel",
                "data": carousel_data
            }
            resp.text = json.dumps(response_data)
            resp.status = falcon.HTTP_201  # 201 Created

        except ValueError as ve:
            # Respond with error message
            response_data = {
                "status_code": "1",
                "status_desc": "homeCarousel",
                "message": str(ve)
            }
            resp.status = falcon.HTTP_400  # 400 Bad Request
            resp.text = json.dumps(response_data)

        except Exception as e:
            print(f"Error: {e}")
            # Respond with error message
            response_data = {
                "status_code": "1",
                "status_desc": "homeCarousel",
                "message": "Internal Server Error"
            }
            resp.status = falcon.HTTP_500
            resp.text = json.dumps(response_data)

    def on_get(self, req, resp):
        try:
            # Fetch all data from the database
            carousel_data = self.fetch_all_home_carousel_data()

            # Check if any recipe has items with weight over
            for data in carousel_data:
                recipe_items = data['recipe'].split('-')
                for item in recipe_items:
                    item_id, weight = item.split(':')
                    if not self.item_exists_in_inventory(item_id):
                        data['availability'] = 'Item over'
                        break  # No need to check other items in the recipe
                else:
                    data['availability'] = 'Available'

            response_data = {
                "status_code": "0",
                "status_desc": "homeCarousel",
                "data": carousel_data
            }

            resp.text = json.dumps(response_data)
            resp.status = falcon.HTTP_200

        except Exception as e:
            print(f"Error in GET request: {e}")
            # Respond with error message
            response_data = {
                "status_code": "1",
                "status_desc": "homeCarousel",
                "message": "Internal Server Error"
            }
            resp.status = falcon.HTTP_500
            resp.text = json.dumps(response_data)

    def fetch_all_home_carousel_data(self):
        try:
            # Fetch all data from the database
            self.cursor.execute('SELECT * FROM home_carousel_data')
            results = self.cursor.fetchall()

            # Convert results to a list of dictionaries
            carousel_data = [{
                "name": result[1],
                "recipe": result[2],
                "price": result[3],
                "discount": result[4],
                "toppings": json.loads(result[5]),
                "nutrition_info": result[6],
                "about": result[7]
            } for result in results]

        except Exception as e:
            print(f"Error fetching data: {e}")
            # Respond with error message
            carousel_data = [{
                "status_code": "1",
                "status_desc": "homeCarousel",
                "message": "Internal Server Error"
            }]

        return carousel_data

    def item_exists_in_inventory(self, item_id):
        try:
            # Check if the item ID exists in inventory and its weight is not finished
            self.cursor.execute("SELECT Weight FROM ingridients_prices WHERE Id = ?", (item_id,))
            weight = self.cursor.fetchone()[0]

            return weight > 0

        except Exception as e:
            print(f"Error checking item in inventory: {e}")
            return False

    def insert_or_update_home_carousel_data(self, name, recipe, price, discount, toppings, nutrition_info, about):
        try:
            # Insert or update home carousel data in the database
            self.cursor.execute('''
                INSERT OR REPLACE INTO home_carousel_data 
                (name, recipe, price, discount, toppings, nutrition_info, about) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (name, recipe, price, discount, toppings, nutrition_info, about))
            self.conn.commit()
        except Exception as e:
            print(f"Error inserting/updating data: {e}")
            raise



class RootResource:
    def on_get(self, req, resp):
        # Response data including the "texts" array
        response_data = {
            "status_code": "0",
            "status_desc": "startupAPI",
            "texts": ["tastyDelights", "fitness", "exotic", "fullMeals"]
        }
        
        resp.body = json.dumps(response_data)
        resp.status = falcon.HTTP_200
app = falcon.App()
root_resource = RootResource()
app.add_route('/startup', root_resource)
payment_initiate_instance = PaymentInitiate(mqtt_client)
recipe_resource = RecipeResource(mqtt_client)
home_carousel_resource = HomeCarouselResource()
app.add_route('/homeCarousel', home_carousel_resource)
app.add_route('/paymentinitiated', payment_initiate_instance)
app.add_route('/smoothieStatus', recipe_resource)
app.add_route('/feedback', SmoothieFeedbackResource()) #
app.add_route('/smoothieCombination/{combination_id}', SmoothieCombinationResource()) ##
app.add_route('/funFacts', FunFactsResource()) 
app.add_route('/sweetness', SweetnessResource()) 
app.add_route('/getInventory', GetInventory()) 

app.add_route('/orderCompleted', OrderCompleted())
app.add_route('/getPaymentInfo', GetPaymentInfo()) 
app.add_route('/recipes', GetRecipes())
app.add_route('/addrecipes', AddRecipe()) 
app.add_route('/promoCode', PromoCodeResource()) 
app.add_route('/addpromoCode', AddPromoCodeResource()) ##
app.add_route('/addToInventory', AddToInventory())  ##
pics_resource = PicsResource()
app.add_route('/pics', pics_resource)

static_folder = '/home/epicure/epicure-backend/static'  
app = StaticMiddleware(app, static_folder)

static_folder_startup = '/home/epicure/epicure-backend/static/assets'
app_middleware_startup = StaticMiddlewareForStartup(app, static_folder_startup, '/pics')
app = app_middleware_startup



# gunicorn -b 127.0.0.1:8002 -w2 --timeout 10 juice_api_test:app
