

from handler.handler import Handler
from google.appengine.api import users
from google.appengine.api import mail
import hmac
import hashlib
import datetime

from database.user import User, Menu
from logic.Logic import Authenticate
import logging
import json
import urllib, urllib2
from google.appengine.api import memcache
import random
import traceback

debug=True

bot_id = "310096364:AAFRH7mN7SE15wSF11Do55Mlpvcjh9DzLgw"

#### EMOJI
screaming_face = '\xF0\x9F\x98\xB1'
grinning_face = '\xF0\x9F\x98\x81'
hatching_chick = '\xF0\x9F\x90\xA3'
smirking_face = '\xF0\x9F\x98\x8F'
delicious_face = '\xF0\x9F\x98\x8B'
smiley_eye_close = '\xF0\x9F\x98\x86'
white_smiley = '\xE2\x98\xBA'

#### Default menu
default_menu = ["Char Kway Teow", "Chicken Rice", "Hor fun", "Tom Yum", "Mee Pok", "Prata", "Fried Carrot Cake", "Bak Kut Teh", "Yong Tau Foo", "Mee Siam", "Mee Soto", "Chicken Chop", "Curry Rice"]
default_drink = ["Ice Coffee","Ice Lemon Tea", "Barley", "Teh"]
cuisine = ["JAPANESE", "WESTERN", "THAI", "INDIAN", "MALAY", "VIETNAMESE", "CHINESE"]
"""
Pending function
/endless random
/stop
/surprise
/remove
/cuisine
"""


"""
Commands:
create - Create a menu
order - Add food item to menu
pick - Help you pick a food from the list you have created
remove - Remove food item from existing menu
delete - Delete existing menu
surprise - (food, drink, cuisine)
"""

class Login(Handler):

    def post(self):
        action=self.request.get("action")
        email = self.request.get("email")
        password = self.request.get("password")

        if action=='sign_in':
            user = User.login(email,password)
            if user:
                data={
                "status":"ok",
                "user_id":user.key.id()
                }
                
            else:
                data={
                "status":"fail",
                }
            logging.info("User logged in!: email-"+email)
            self.write(json.dumps(data))
        elif action=='sign_up':
            phone = self.request.get('phone')
            if len(phone)==8:
                user=User.register(password,email,phone)
                if user:
                        # for sending email
                        # sender_address='ZaibikeTeam <sbikeweb-964@appspot.gserviceaccount.com>'
                        # user_address=email
                        # body="Zai Bike Sign up"
                        # subject="test"
                        # mail.send_mail(sender_address, user_address, subject, body)
                       
                    data={"status":"ok","user_id":user.key.id()}
                else:                   
                    data={"status":"fail"}
                logging.info("New User Signed up!: email-"+email)
                self.write(json.dumps(data))
                                            

        elif action=="user_changepw":
            user=User.by_email(email)
            if user:
                user.password=password
                data={
                "status":"ok",
                }
            else:
                data={
                "status":"fail",
                }
            self.write(json.dumps(data))

class Chatter(Handler):

    def post(self):

        """
        {"update_id":82180126,
        "message":{"message_id":5,"from":{"id":296314122,"first_name":"Pornthip","last_name":"Sae-Chong","username":"Yellowducky"},"chat":{"id":296314122,"first_name":"Pornthip","last_name":"Sae-Chong","username":"Yellowducky","type":"private"},"date":1485182182,"text":"hi"}}
        """

        """
        {u'message': {u'from': {u'username': u'Yellowducky', u'first_name': u'Pornthip', u'last_name': u'Sae-Chong', u'id': 296314122}, u'text': u'/create', u'entities': [{u'length': 7, u'type': u'bot_command', u'offset': 0}], u'chat': {u'all_members_are_administrators': True, u'type': u'group', u'id': -150503855, u'title': u'Test my bot'}, u'date': 1485700387, u'message_id': 46}, u'update_id': 24681082}
        """

        """
        {u'message': {u'from': {u'username': u'Yellowducky', u'first_name': u'Pornthip', u'last_name': u'Sae-Chong', u'id': 296314122}, u'left_chat_participant': {u'username': u'PickAFooodBot', u'first_name': u'pickafood', u'id': 310096364}, u'left_chat_member': {u'username': u'PickAFooodBot', u'first_name': u'pickafood', u'id': 310096364}, u'chat': {u'all_members_are_administrators': True, u'type': u'group', u'id': -150503855, u'title': u'Test my bot'}, u'date': 1485703426, u'message_id': 58}, u'update_id': 24681090}
        """

        """
        {u'message': {u'from': {u'username': u'Yellowducky', u'first_name': u'Pornthip', u'last_name': u'Sae-Chong', u'id': 296314122}, u'new_chat_participant': {u'username': u'PickAFooodBot', u'first_name': u'pickafood', u'id': 310096364}, u'chat': {u'all_members_are_administrators': True, u'type': u'group', u'id': -150503855, u'title': u'Test my bot'}, u'date': 1485703716, u'message_id': 59, u'new_chat_member': {u'username': u'PickAFooodBot', u'first_name': u'pickafood', u'id': 310096364}}, u'update_id': 24681091}
        """

        """
        create - Create a menu
        order - Add the food you feel like eating to the list of other food you feel like eating e.g. /order mee siam
        pick - I'll help you pick a food from the list you have created
        """

        try:
            request = json.loads(self.request.body)
            logging.info(request)
            message = request["message"]
            chat_id = message["chat"]["id"]
            if message["chat"]["type"] == "group":             
                firstname = message["from"]["first_name"]
                lastname = message["from"]["last_name"]
            else:
                firstname = message["chat"]["first_name"]
                lastname = message["chat"]["last_name"]

            if "left_chat_member" in message and message["left_chat_member"]["username"]=="PickAFooodBot":
                text = "Thanks for using PickAFoood. BB have a good day!"
            elif (message["chat"]["type"] == "group" and "new_chat_member" in message and message["new_chat_member"]["username"]=="PickAFooodBot") or (message["text"]=="/start"):
                text = """HELLOOO Thank you for adding PickAFoood bot. 
I'm designed to solve the biggest 1st world problem i.e.
<b>What to eat today?</b> {}{}{}
You can use me within a group or privately to decide your next meal!

There are 3 simple commands that you should remember:
/create Create a menu
/order Add food item to menu created e.g. /order mee siam
/pick I'll help you pick a food from the list you have created

Other helpful commands:
/remove Remove food item from existing menu
/delete Delete existing menu and move on

<i>IF YOU COMPLETELY HAVE NO IDEA OF WHAT TO EAT ...</i>
I can surprise you with delicious food you don't even know you want to eat {}
/surprise (food, drink, cuisine) 3 options available:

No more time wasting, No more undecided moments, No more conflicting thoughts BUT MORE FOOOOOD ENJOYYY {} """.format(screaming_face,screaming_face,screaming_face,delicious_face,grinning_face)
            else:

                text_msg = message["text"]
                text = None

                if text_msg=="/create":
                    ### create menu
                    if memcache.get("menu{}".format(chat_id)):
                        text = "This chat has an existing menu. Continue to /order or /delete before creating new one!"
                    else:
                        menu = Menu.create(firstname)
                        text = "{} has created a menu".format(firstname)
                        memcache.set("menu{}".format(chat_id), menu)

                elif "/order" in text_msg:
                    menu = memcache.get("menu{}".format(chat_id))
                    if not menu:
                        text = "Please create a menu using /create"
                    else:    
                        food = text_msg.replace("/order","")
                        food = food.strip()
                        if not food:
                            text = "Order something! type /order <b>{{food}}</b>"
                        else:
                            menu.add_to_menu(food)
                            menu.put()
                            memcache.set("menu{}".format(chat_id), menu) # update menu
                            text = "{} want to eat <b>{}</b>".format(firstname,food)
                            text += "\nCurrent choices:"
                            count = 1
                            for food in menu.food_list:
                                text+="\n{}. {}".format(count,food)
                                count+=1
                            text += "\n\nReady to /pick?"

                elif "/pick" in text_msg:
                    menu = memcache.get("menu{}".format(chat_id))
                    if not menu:
                        text = "Please create a menu using /create"
                    else:
                        if not menu.food_list:
                            text = "No food to choose from"
                        else:
                            choice = random.choice(menu.food_list)
                            text = "Today let's eat <b>{}</b> !!! YAYYYYY. \nNot happy? You can /pick again until you /delete the menu".format(choice)

                elif "/delete" in text_msg:
                    menu = memcache.get("menu{}".format(chat_id))
                    if not menu:
                        text = "Please create a menu using /create"
                    else:
                        menu.key.delete()
                        memcache.delete("menu{}".format(chat_id))
                        text = "Deleting menu. Enjoy your meal and have a good day! {}".format(white_smiley)

                elif "/remove" in text_msg:
                    menu = memcache.get("menu{}".format(chat_id))
                    if not menu:
                        text = "Please create a menu using /create"
                    else:
                        count = text_msg.replace("/remove","")
                        if not count:
                                text = "Excuse me, what do you want to remove?????"
                        else:
                            try:
                                count = int(count)
                                if (count > len(menu.food_list)) or (count < 1):
                                    text = "Order specified not in menu range"
                                else:
                                    food_removed = menu.food_list[count-1]
                                    menu.food_list.pop(count-1)
                                    menu.put()
                                    memcache.set("menu{}".format(chat_id), menu) # update menu
                                    text = "{} doesn't want to eat <b>{}</b> anymore :(".format(firstname,food_removed)
                                    text += "\nCurrent choices:"
                                    count = 1
                                    for food in menu.food_list:
                                        text+="\n{}. {}".format(count,food)
                                        count+=1
                                    text += "\n\nReady to /pick?"
                            except:
                                text = "Please specify the number of the food you want to remove according to the order in the menu."                        


                elif "/surprise" in text_msg:
                    food_type = text_msg.replace("/surprise","")
                    food_type = food_type.strip()
                    if not food_type:
                        text = "Please indicate a type => food, drink, cuisine"
                    elif food_type=="food":
                        text = "Surprise!!! I think today you should eat <b>{}</b> {}".format(random.choice(default_menu),delicious_face)
                    elif food_type=="drink":
                        text = "Hmm nothing to drink better than <b>{}</b> {}".format(random.choice(default_drink),smiley_eye_close)
                    elif food_type=="cuisine":
                        text = "I know you are secretly craving for <b>{}</b> food {}".format(random.choice(cuisine),smirking_face)
                    else:
                        text = "Sorry we can't surprise you with that ..."                           


            if text:
                reply = {"chat_id":chat_id,"text":text, "parse_mode":"HTML"}
                reply = urllib.urlencode(reply)

                url = "https://api.telegram.org/bot{}/sendMessage?{}".format(bot_id,reply)
                response = urllib2.urlopen(url).read()
                response = json.loads(response)
                if response.get("ok") == True:
                    chat_id = response["result"]["chat"]["id"]
                    logging.info(chat_id)
                    logging.info("ok")
                else:
                    logging.info("fail")

            return
        except Exception,e:
            traceback.print_exc()
            logging.error(e)

    def get(self):

        self.response.out.write("HIHIHIHI")
        return



class CreateMenu(Handler):
    def post(self):
        try:
            request = json.loads(self.request.body)
            logging.info(request)
            message = request["message"]

            chat_id = message["chat"]["id"]

            firstname = message["chat"]["first_name"]
            lastname = message["chat"]["last_name"]

            reply = {"chat_id":chat_id,"text":"{} has created a menu".format(firstname)}
            reply = urllib.urlencode(reply)
            logging.info(reply)

            url = "https://api.telegram.org/bot{}/sendMessage?{}".format(bot_id,reply)
            logging.info(url)
            response = urllib2.urlopen(url).read()
            response = json.loads(response)
            logging.info(response)
            if response.get("ok") == True:
                chat_id = response["result"]["chat"]["id"]
                logging.info(chat_id)
                logging.info("ok")
            else:
                logging.info("fail")

            return
        except Exception,e:
            logging.error(e)
        