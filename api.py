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

try:
    conn = sqlite3.connect('juice_vending_api.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ingridients_weights (
            Dispenser INTEGER PRIMARY KEY,
            Weight INTEGER
        )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS ingridients_prices (
        Id INTEGER PRIMARY KEY,
        Type TEXT,
        Name TEXT,
        Custom_grams INTEGER,
        Toppings_grams INTEGER,
        Price_gram REAL,
        img_url TEXT
    )
''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS paymentinitiated (
    order_id INTEGER PRIMARY KEY,
    recipe_string TEXT,
    user_name TEXT,
    user_phone TEXT,
    amount INTEGER,
    toppings TEXT
    )
''')                   

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS recipes (
        name TEXT PRIMARY KEY,
        recipe TEXT,
        price INTEGER,
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
    
    ingredients_weights_data = [
        (1, 669), (2, 735), (3, 750), (4, 561), (5, 750),
        (6, 750), (7, 690), (8, 3847), (9, 3770), (10, 3928),
        (11, 4000), (12, 3991), (13, 3800), (14, 4000), (15, 3729),
        (16, 5000), (17, 5000), (18, 5000), (19, 5000), (20, 4990),
        (21, 4760)
    ]

    inventory_data = [
        (1, 'Powder', 'Coco Powder', 10, 5, 1,'static/images/1.jpg'),
        (2, 'Powder', 'Whey Protein', 5, 5, 2.4,'static/images/2.jpg'),
        (3, 'Powder', 'Dry Fruits', 5, 5, 1.75,'static/images/3.jpg'),
        (4, 'Powder', 'Cinnamon', 5, 5, 1.8,'static/images/4.jpg'),
        (5, 'Powder', 'Pumpkin Seeds', 8, 5, 1.1,'static/images/5.jpg'),
        (6, 'Powder', 'Sunflower Seeds', 8, 5, 0.5,'static/images/6.jpg'),
        (7, 'Powder', 'Chia Seeds', 8, 5, 0.5,'static/images/7.jpg'),
        (8, 'Solid', 'Apple', 30, 5, 0.1,'static/images/8.jpg'),
        (9, 'Solid', 'Banana', 30, 5, 0.048,'static/images/9.jpg'),
        (10, 'Solid', 'Papaya', 30, 5, 0.071,'static/images/10.jpg'),
        (11, 'Solid', 'Strawberry', 30, 5, 0.5,'static/images/11.jpg'),
        (12, 'Solid', 'Muskmelon', 30, 5, 0.04,'static/images/12.jpg'),
        (13, 'Solid', 'Pineapple', 30, 5, 0.07,'static/images/13.jpg'),
        (14, 'Solid', 'Dates', 30, 5, 0.18,'static/images/14.jpg'),
        (15, 'Solid', 'Oats', 30, 5, 0.13,'static/images/15.jpg'),
        (16, 'Liquid', 'Milk', 30, 5, 0.054,'static/images/16.jpg'),
        (17, 'Liquid', 'Milk', 30, 5, 0.054,'static/images/17.jpg'),
        (18, 'Liquid', 'Water', 30, 5, 0.02,'static/images/18.jpg'),
        (19, 'Liquid', 'Water', 30, 5, 0.02,'static/images/19.jpg'),
        (20, 'Liquid', 'Honey', 30, 5, 0.2,'static/images/20.jpg'),
        (21, 'Liquid', 'Coconut Milk', 30, 5, 0.1,'static/images/21.jpg')
    ]

    recipes_data = [
    (
        'Tropical Delight',
        '13:100-9:100-21:120-20:5',
        150,
        '1,2,3,4,5,6',
        'calories-80Kcal;carbs-319g;proteins-71g;sodium-6mg;Fiber-55mg;calcium-3mg;totalfat-7g;potassium-1.2mg',
        'Immerse your taste buds in a refreshing blend of tropical fruits, including succulent pineapple, juicy mango, and creamy coconut. A delightful sip of paradise to brighten your day.'
    ),
    (
        'Berry Blast',
        '11:50-13:50-16:150-20:5',
        220,
        '1,2,3,4,5,20',
        'calories-90Kcal;carbs-119g;proteins-81g;sodium-9mg;Fiber-58mg;calcium-5mg;totalfat-4g;potassium-1.4mg',
        'Indulge in a burst of flavors with our Berry Blast Salad. A medley of sweet strawberries, plump blueberries, and tart raspberries tossed with crisp greens, creating a vibrant and nutritious sensation.'
    )
]



    # Change this line to use INSERT instead of INSERT OR REPLACE
    cursor.executemany('INSERT OR REPLACE INTO ingridients_prices (Id, Type, Name, Custom_grams, Toppings_grams, Price_gram, img_url) VALUES (?, ?, ?, ?, ?, ?, ?)', inventory_data)
    cursor.executemany('INSERT OR REPLACE INTO ingridients_weights (Dispenser, Weight) VALUES (?, ?)', ingredients_weights_data)
    cursor.executemany('INSERT OR REPLACE INTO recipes (name, recipe, price, toppings, nutrition_info, about) VALUES (?, ?, ?, ?, ?, ?)', recipes_data)
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
                    'weights': None  
                })

            
            cursor.execute('SELECT * FROM ingridients_weights')
            weights_rows = cursor.fetchall()

           
            for weight_row in weights_rows:
                dispenser_id = str(weight_row[0])
                matching_item = next((item for item in inventory if item['id'] == dispenser_id), None)
                if matching_item:
                    matching_item['weights'] = weight_row[1]

            conn.close()

            response_data = {
                'status': True,
                'error': False,
                'message': 'success',
                'data': inventory
            }

            resp.body = json.dumps(response_data)
            resp.status = falcon.HTTP_200
        except Exception as e:
            response_data = {
                'status': False,
                'error': True,
                'message': f"Error: {str(e)}",
                'data': []
            }
            resp.body = json.dumps(response_data)
            resp.status = falcon.HTTP_500

            # Log the error for debugging
            print(f"Error in GetInventory: {e}")
            traceback.print_exc()  # Add this line for detailed traceback


class RegisterPayment:
    def on_post(self, req, resp):
        try:
            data = json.loads(req.stream.read().decode('utf-8'))
            conn = sqlite3.connect('juice_vending_api.db')
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO received_payments (phone_number, amount, order_id)
                VALUES (?, ?, ?)
            ''', (data.get('phone_number', ''), data.get('amount', 0), data.get('order_id', 0)))
            conn.commit()
            conn.close()
            resp.body = 'Payment registered successfully!'
            resp.status = falcon.HTTP_200
        except Exception as e:
            resp.body = f"Error: {str(e)}"
            resp.status = falcon.HTTP_500


class GetPaymentInfo:
    def on_get(self, req, resp):
        try:
            conn = sqlite3.connect('juice_vending_api.db')
            cursor = conn.cursor()

            cursor.execute('''
                SELECT * FROM paymentinitiated ORDER BY order_id DESC LIMIT 1
            ''')

            order_data = cursor.fetchone()

            conn.close()

            if order_data:
                response_data = {
                    'status': True,
                    'error': False,
                    'message': 'order retrieved successfully!',
                    'data': {
                        'order_id': order_data[0]
                    }
                }
                resp.body = json.dumps(response_data)
                resp.status = falcon.HTTP_200
            else:
                response_data = {
                    'status': False,
                    'error': True,
                    'message': ' order not found!',
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
            cursor.execute('SELECT name, recipe, price, toppings, nutrition_info, about FROM recipes')
            rows = cursor.fetchall()

            for row in rows:
                recipes.append({
                    'name': row[0],
                    'recipe': row[1],
                    'price': row[2],
                    'toppings': [int(topping) for topping in row[3].split(',')],
                    'nutrition_info': row[4],
                    'about': row[5]
                })

            conn.close()

            response_data = {
                'status': True,
                'error': False,
                'message': 'success',
                'data': recipes
            }

            resp.body = json.dumps(response_data)
            resp.status = falcon.HTTP_200
        except Exception as e:
            response_data = {
                'status': False,
                'error': True,
                'message': f"Error: {str(e)}",
                'data': []
            }
            resp.body = json.dumps(response_data)
            resp.status = falcon.HTTP_500


class AddRecipe:
    def on_post(self, req, resp):
        try:
            data = json.loads(req.stream.read().decode('utf-8'))

            conn = sqlite3.connect('juice_vending_api.db')
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO recipes (name, recipe, price, toppings, nutrition_info, about)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                data.get('name', ''),
                data.get('recipe', ''),
                data.get('price', 0),
                data.get('toppings', ''),
                data.get('nutrition_info', ''),
                data.get('about', '')
            ))

            conn.commit()
            conn.close()

            resp.body = 'Recipe added successfully!'
            resp.status = falcon.HTTP_200
        except Exception as e:
            resp.body = f"Error: {str(e)}"
            resp.status = falcon.HTTP_500


class PaymentCB:
    def on_post(self, req, resp):
        try:
            data = json.loads(req.stream.read().decode('utf-8'))
            print(f'GOT from PP <{data}>')
            resp.status = falcon.HTTP_200
        except Exception as e:
            resp.body = f"PaymentCB: Error: {str(e)}"
            resp.status = falcon.HTTP_500


class PromoCodeResource:
    def on_get(self, req, resp):
        try:
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

                resp.body = json.dumps(promo_codes)
                resp.status = falcon.HTTP_200
        except Exception as e:
            resp.body = f"Error: {str(e)}"
            resp.status = falcon.HTTP_500

    def on_post(self, req, resp):
        try:
            data = json.loads(req.stream.read().decode('utf-8'))

            with sqlite3.connect('juice_vending_api.db') as conn:
                cursor = conn.cursor()

                cursor.execute('''
                    INSERT INTO promo_codes (serial_number, promo_code, status)
                    VALUES (?, ?, ?)
                ''', (data.get('serial_number', ''), data.get('promo_code', ''), data.get('status', '')))

            resp.body = 'Promo code added successfully!'
            resp.status = falcon.HTTP_200
        except Exception as e:
            resp.body = f"Error: {str(e)}"
            resp.status = falcon.HTTP_500

class SweetnessResource:
    def __init__(self):
        self.sweetness_levels = [
            {"sweetness_level": "low", "grams": 6},
            {"sweetness_level": "medium", "grams": 10},
            {"sweetness_level": "high", "grams": 12},
        ]

    def on_get(self, req, resp):
        response_data = {
            'status': True,
            'error': False,
            'message': 'success',
            'data': self.sweetness_levels
        }

        resp.body = json.dumps(response_data)
        resp.status = falcon.HTTP_200
sweetness_resource = SweetnessResource()



class FunFactsResource:
    def on_get(self, req, resp):
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
            'status': True,
            'error': False,
            'message': 'success',
            'data': {'fun_fact': random_fact}
        }

        resp.body = json.dumps(response_data)
        resp.status = falcon.HTTP_200

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
                    'status': True,
                    'error': False,
                    'message': 'success',
                    'data': combination_data
                }

                resp.body = json.dumps(response_data)
                resp.status = falcon.HTTP_200
            else:
                response_data = {
                    'status': False,
                    'error': True,
                    'message': 'Combination not found',
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
        finally:
            conn.close()

class paymentinitiated:
    def on_post(self, req, resp):
        try:
            # Parse JSON data from the request body
            data = json.loads(req.stream.read().decode('utf-8'))

            # Extract data from the JSON payload
            recipe_string = data.get('recipe_string', '')
            user_name = data.get('user_name', '')
            user_phone = data.get('user_phone', '')
            amount = data.get('amount', 0)
            toppings = data.get('toppings', '')

            # Generate a unique order_id using uuid
            order_id = str(uuid.uuid4())

            # Insert data into the database
            conn = sqlite3.connect('juice_vending_api.db')
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO paymentinitiated (order_id, recipe_string, user_name, user_phone, amount, toppings)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (order_id, recipe_string, user_name, user_phone, int(amount), toppings))

            conn.commit()
            conn.close()

            response_data = {
                'status': True,
                'error': False,
                'message': 'Recipe order saved successfully!',
                'data': {
                    'order_id': order_id,
                    'recipe_string': recipe_string,
                    'user_name': user_name,
                    'user_phone': user_phone,
                    'amount': amount,
                    'toppings': toppings
                }
            }

            resp.body = json.dumps(response_data)
            resp.status = falcon.HTTP_200

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
            print(f"Error in SaveRecipeOrder: {e}")
            traceback.print_exc()  # Add this line for detailed traceback

class paymentinitiate:
    def on_post(self, req, resp):
        try:
            # Parse JSON data from the request body
            data = json.loads(req.stream.read().decode('utf-8'))

            # Extract data from the JSON payload
            recipe_string = data.get('recipe_string', '')
            user_name = data.get('user_name', '')
            user_phone = data.get('user_phone', '')
            amount = data.get('amount', 0)
            toppings=data.get('toppings','')
            # Generate a unique order_id using uuid
            order_id = str(uuid.uuid4())

            # Insert data into the database
            conn = sqlite3.connect('juice_vending_api.db')
            cursor = conn.cursor()

            cursor.execute('''
    INSERT INTO paymentinitiated (recipe_string, user_name, user_phone, amount,toppings)
    VALUES (?, ?, ?, ?, ?)
''', (recipe_string, user_name, user_phone, int(amount),toppings))


            conn.commit()
            conn.close()

            response_data = {
                'status': True,
                'error': False,
                'message': 'Recipe order saved successfully!',
                'data': {
                    'order_id': order_id,
                    'recipe_string': recipe_string,
                    'user_name': user_name,
                    'user_phone': user_phone,
                    'amount': amount,
                    'toppings': toppings
                }
            }

            resp.body = json.dumps(response_data)
            resp.status = falcon.HTTP_200

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
            print(f"Error in SaveRecipeOrder: {e}")
            traceback.print_exc()  # Add this line for detailed traceback

            
class SmoothieStatusResource:
    def __init__(self):
        self.status_code = 1  # Initial status code
        self.status_messages = {
            1: "Smoothie ingredient is collected",
            2: "Smoothie is blending",
            3: "Smoothie is dispensing",
            4: "Toppings are added",
            5: "Smoothie is ready"
        }

    def on_get(self, req, resp, order_id=None):
        try:
            # Simulate a delay before updating the status
            time.sleep(3)

            # Update the status code
            self.status_code = 2  # This can be updated based on your logic

            # Generate a unique order_id using uuid
            order_id = str(uuid.uuid4())

            # Insert data into the database (example)
            conn = sqlite3.connect('juice_vending_api.db')
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO smoothie_status (order_id, status_code)
                VALUES (?, ?)
            ''', (order_id, self.status_code))

            conn.commit()
            conn.close()

            response_data = {
                'status': True,
                'error': False,
                'message': 'success',
                'data': {
                    'order_id': order_id,
                    'smoothie_status': {
                        'code': self.status_code,
                        'message': self.status_messages.get(self.status_code, "Unknown Status")
                    }
                }
            }

            resp.body = json.dumps(response_data)
            resp.status = falcon.HTTP_200

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
            print(f"Error in SmoothieStatusResource: {e}")
            traceback.print_exc()  # Add this line for detailed traceback


class SmoothieStatusResource:
    def __init__(self):
        self.status_code = 1  # Initial status code
        self.status_messages = {
            1: "Smoothie ingredient is Collected",
            2: "Smoothie is Blending",
            3: "Smoothie is Dispensed",
            4: "Toppings are Added",
            5: "Smoothie is Ready"
        }

    def on_get(self, req, resp):
        try:
            # Connect to the database
            conn = sqlite3.connect('juice_vending_api.db')
            cursor = conn.cursor()

            # Fetch the latest order_id from the paymentinitiated table
            cursor.execute("SELECT MAX(order_id) FROM paymentinitiated")
            latest_order_id = cursor.fetchone()[0]

            # Close the database connection
            conn.close()

            response_data = {
                'status': True,
                'error': False,
                'message': 'success',
                'data': {
                    'order_id': latest_order_id,
                    'smoothie_status': {
                        'code': self.status_code,
                        'message': self.status_messages.get(self.status_code, "Unknown Status")
                    }
                }
            }

            resp.body = json.dumps(response_data)
            resp.status = falcon.HTTP_200

            # Simulate a delay before updating the status
            time.sleep(3)

            # Update the status code
            self.status_code += 1

            if self.status_code > 5:
                self.status_code = 1  # Reset to the initial status

        except Exception as e:
            response_data = {
                'status': False,
                'error': True,
                'message': f"Error: {str(e)}",
                'data': {}
            }
            resp.body = json.dumps(response_data)
            resp.status = falcon.HTTP_500


app = falcon.App()
smoothie_status_resource = SmoothieStatusResource()
app.add_route('/smoothieStatus', smoothie_status_resource)
app.add_route('/smoothieCombination/{combination_id}', SmoothieCombinationResource())
app.add_route('/funFacts', FunFactsResource())
app.add_route('/sweetness', sweetness_resource)
app.add_route('/getInventory', GetInventory())
app.add_route('/registerPayment', RegisterPayment())
app.add_route('/orderCompleted', OrderCompleted())
app.add_route('/getPaymentInfo', GetPaymentInfo())
app.add_route('/recipes', GetRecipes())
app.add_route('/addrecipes', AddRecipe())
app.add_route('/paymentCB', PaymentCB())
app.add_route('/promoCode', PromoCodeResource())
app.add_route('/paymentinitiated', paymentinitiate())


static_folder = '/home/epicure/epicure-backend/static'  # Path to your static files
app = StaticMiddleware(app, static_folder)

# gunicorn -b 127.0.0.1:8002 -w2 --timeout 10 juice_api_test:app
