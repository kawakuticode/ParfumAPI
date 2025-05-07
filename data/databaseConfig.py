
import urllib.parse
import time
import requests
import socket
from urllib.parse import quote_plus
from sqlalchemy.ext.asyncio import create_async_engine
import pyodbc




class DatabaseConfig:
 def __init__(self, driver, server, port, database, username, password):
    self.driver = driver 
    self.server = server
    self.port = port
    self.database = database
    self.username = username
    self.password = password
 
 """Raises :class:`HTTPError  ."""
 def get_my_ip(self) -> str:
   print ("getting my IP ***** ") 
   try:
    response = requests.get('https://api.ipify.org?format=json')
    response.raise_for_status()
    ip_data = response.json()
    return ip_data['ip']
   except requests.RequestException as e:
    print(f"Error fetching IP: {e}")
    return None

 def check_ip (self) -> str:  
   
   print(f"Checking ip modification ... .... ... ")
   
   try : 
           
      with open("ip_stock.txt", "r+") as f :
         
         old_ip = f.readline().strip() 
         new_ip = self.get_my_ip()
         
         if old_ip == new_ip : 
            print(f"Same IP ... : {old_ip}. No need to update database firewall rule ")
            return old_ip
         else : 
            print(f"ip changed!! Add the new ip to Azure database firewall rule : {new_ip}")
            f.seek(0)
            f.write(new_ip)
            f.truncate ()
            return new_ip
         
   except FileNotFoundError as fe : 
      print("File not find : ",  fe) 
      return False   
   finally : 
      f.close()
    
 def can_connect(self) -> bool:  
   
   timeout = 60
   
   print(f"testing if reachable  my ip : {self.check_ip()}  host: {self.server} and port : {self.port} with time-out :{timeout} seconds --> Good Lucky!!")
   retries = 5 
   for attempt in range ( retries) : 
      try:          
         with socket.create_connection((self.server, self.port)): 
            return True
      except socket.gaierror as e : 
         print(f"Attempt {attempt + 1} DNS lookup failed {e}:")
         time.sleep(5)# Wait before retrying
      except socket.timeout: 
         print(f"Attempt {attempt + 1} Connection time - out" ) 
         time.sleep(5) # Wait before retrying             
      except OSError as os : 
         print(f"Attempt {attempt + 1} Connection failed:{os}") 
         time.sleep(5) # Wait before retrying   
         return False 
   print("All attempts to connect to Azure SQL Database failed")    
   

    
 def get_engine(self):
   
   odbc_string = (
      f"DRIVER={self.driver};"
      f"SERVER=tcp:{self.server},{self.port};"
      f"DATABASE={self.database};"
      f"UID={self.username};"
      f"PWD={self.password};"
   )
   
   connection_url = f"mssql+aioodbc:///?odbc_connect={urllib.parse.quote_plus(odbc_string)}"
   return create_async_engine( connection_url, future = True,  echo = True)
 