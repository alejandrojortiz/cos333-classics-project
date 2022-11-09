'''
functions responsible for all query interactions with the logion database

authors: Eugene Liu

'''
from sqlalchemy import create_engine
from sqlalchemy import Column, String, Integer, Identity, MetaData
from sqlalchemy.orm import declarative_base
from sqlalchemy import insert, select
from sqlalchemy.sql import text

db_string = "postgres://gsbouuzayqpjre:d5fd5fcaa4eeed8266d6a411cc9104962045870cffa23ba8118cb9f4cb487bf1@ec2-54-85-56-210.compute-1.amazonaws.com:5432/d6giaa1c28o2lu"
engine = create_engine(db_string, echo=True)

base = declarative_base()

# declaring users table
class User(base):
    __tablename__ = "users"
    
    user_id = Column(Integer, primary_key=True)
    name = Column(String(500))
    email = Column(String(500))
    institution = Column(String(500))
    position = Column(String(500))
    ip_address = Column(String(500))
    
    def __init__(self, user_id, name, email, institution, position, ip_address):
        self.user_id = user_id
        self.name = name
        self.email = email
        self.time = institution
        self.position = position
        self.ip_address = ip_address
        
# declaring texts table
class Text(base):
    __tablename__ = "texts"
    
    text_id = Column(Integer, Identity(start = 1, cycle=True), primary_key=True)
    user_id = Column(Integer)
    text_name = Column(String(8000))
    uploaded = Column(String(8000))
    time = Column(String(500))
    
    def __init__(self, text_id, user_id, text_name, uploaded, time):
        self.text_id = text_id
        self.user_id = user_id
        self.text_name = text_name
        self.uploaded = uploaded
        self.time = time

# declaring predictions table
class Prediction(base):
    
    __tablename__ = "predictions"
    
    prediction_id = Column(Integer, Identity(start = 1, cycle=True), primary_key=True)
    token_number = Column(Integer)
    text_id = Column(Integer)
    prediction_name = Column(String(8000))
    prediction_output = Column(String(8000))
    
    def __init__(self, prediction_id, token_number, text_id, prediction_name, prediction_output):
        self.prediction_id = prediction_id
        self.text_id = text_id
        self.token_number = token_number
        self.prediction_name = prediction_name
        self.prediction_output = prediction_output

base.metadata.create_all(engine)   

def confirm_user(userID:str):
    '''Function that checks if user is in the database'''
    conn = engine.connect()
    
    stmt = select(User).where(User.user_id == userID)
    result = conn.execute(stmt)
    
    print("we are getting a result")
    if result is None:
        return False
    else:
        return True

def add_account(parameter_dict: dict):
    '''Function for updating account information'''
    
    # unpacking dictionary items
    ID = parameter_dict.get("id")
    name = parameter_dict.get("name")
    email = parameter_dict.get("email")
    institution = parameter_dict.get("institution")
    position = parameter_dict.get("position")
    

    # adding it to the users table
    stmt = insert(User).values(user_id=ID, name=name, 
                                email=email, 
                                institution=institution, 
                                position=position)

    # execution of stmt
    conn = engine.connect()
    result = conn.execute(stmt)

def update_account(parameter_to_update: dict, userID: int):
    
    # getting all parameters to be updated
    parameters = parameter_to_update.keys
    
    # defining base case SQL statement
    SQL_str = "UPDATE users SET "
    
    # adding addition expressions to update
    for i, parameter in enumerate(parameters):
        
        # first case does not need to add comma in the beginning
        if i == 0:
            SQL_str += parameter + "=" + str(parameter_to_update.get(parameter))
        
        else:
            SQL_str += ", " + parameter + "=" + str(parameter_to_update.get(parameter))
    
    with engine.connect() as con:
        rs = con.execute(SQL_str)
    
def get_text(userid:str):
    '''
    Function that returns arrays of dicts where each dict is a row of a text query. Each
    row/dict will have the following keys: "textid", "userid", "textname", "uploaded" (text). 
    '''
    conn = engine.connect()
    
    # creating SQL statement
    stmt = select(Text).where(Text.user_id == userid)
    result = conn.execute(stmt)
    
    
    if result is None:
        return None
    
    text_array = []
    for text in result:
        text = list(text)
        text_dict = {}
        
        text_dict["textid"] = text[0]
        text_dict["userid"] = text[1]
        text_dict["textname"] = text[2]
        text_dict["uploaded"] = text[3]
        
        text_array.append(text_dict)

    return text_array

def get_predictions(textID: int):
    ''''
    Function that returns arrays of dicts where each dict is a row of prediction query. Each
    row/dict will have the following keys: "textid", "prediction_name", "token_number", 
    "prediction" (text). 
    '''
    
    conn = engine.connect()
    
    # creating SQL statement
    stmt = select(Prediction).where(Prediction.text_id == textID)
    result = conn.execute(stmt)
    
    
    if result is None:
        return None
    
    prediction_array = []
    for prediction in result:
        prediction = list(prediction)
        prediction_dict = {}
        
        prediction_dict["prediction_id"] = prediction[0]
        prediction_dict["token_number"] = prediction[1]
        prediction_dict["text_id"] = prediction[2]
        prediction_dict["prediction_name"] = prediction[3]
        prediction_dict["prediction_output"] = prediction[4]       
        prediction_array.append(prediction_dict)

    return prediction_array

def upload_text(text: str, text_name: str, userid: str):
    '''uploads text'''

    stmt = insert(Text).values(user_id=userid, text_name=text_name,
                                uploaded=text)

    # execution of stmt
    conn = engine.connect()
    result = conn.execute(stmt)
        

def upload_prediction(prediction: str, textid: int, token_number: int, prediction_name: str):
    '''Function that uploads prediction to database'''
    
    stmt = insert(Prediction).values(token_number=token_number, text_id=textid,
                                      prediction_name=prediction_name,
                                      prediction_output=prediction)

    # execution of stmt
    conn = engine.connect()
    result = conn.execute(stmt)


def update_text(update_dict: dict, textid):
    
    columns = update_dict.keys
    for i, col in enumerate(columns):
        if i == 0:
            SQL_str += col + "=" + update_dict[col]
        else:
            SQL_str += ", " + col + "=" + update_dict[col]
    
    SQL_str += "WHERE textid=" + str(textid)

    with engine.connect() as con:
        rs = con.execute(SQL_str)

def update_prediction(update_dict: dict, predictionid: int):
    SQL_str = "UPDATE predictions SET "
    
    columns = update_dict.keys
    for i, col in enumerate(columns):
        
        if i == 0:
            SQL_str += col + "=" + update_dict[col]
        else:
            SQL_str += ", " + col + "=" + update_dict[col]
    
    SQL_str += "WHERE predictionid=" + str(predictionid)

    with engine.connect() as con:
        rs = con.execute(SQL_str)

    
    



