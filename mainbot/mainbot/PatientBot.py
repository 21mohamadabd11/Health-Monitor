#This bot will be able to communicate with the catalog 

#token: 8012715662:AAHaSa2-8gordFNA-GL9xERkx-swsvC_5j4

import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
import json
import requests
import time
from datetime import datetime, timedelta, timezone
import io
import pytz

start_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
    	[InlineKeyboardButton(text='log in', callback_data='logIn')]
    ]
)

main_menu_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
    	[InlineKeyboardButton(text='add new room', callback_data='add_room')],
        [InlineKeyboardButton(text="edit room's temperature", callback_data='edit_temperature')],
        [InlineKeyboardButton(text="edit room's humidity", callback_data='edit_humidity')],
        [InlineKeyboardButton(text="see statistics", callback_data='see_statistics')],
        [InlineKeyboardButton(text="settings", callback_data='settings')]
    ]
)

hr_spo2_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
    	[InlineKeyboardButton(text='heart rate', callback_data='sel_hr')],
        [InlineKeyboardButton(text='Oxygen Saturation (SpO2)', callback_data='sel_spo2')]
    ]
)

time_window_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
    	[InlineKeyboardButton(text='last day', callback_data='tw_1d')],
        [InlineKeyboardButton(text='last week', callback_data='tw_1w')],
        [InlineKeyboardButton(text='last month', callback_data='tw_1m')],
        [InlineKeyboardButton(text='last 3 months', callback_data='tw_3m')],
        [InlineKeyboardButton(text='last year', callback_data='tw_1y')],
        [InlineKeyboardButton(text='personalized', callback_data='tw_p')]
    ]

)

select_setting = InlineKeyboardMarkup(
    inline_keyboard=[
    	[InlineKeyboardButton(text='see account information', callback_data='acc_info')],
        [InlineKeyboardButton(text='change password', callback_data='change_pw')]
    ]
)

confirm_password= InlineKeyboardMarkup(
    inline_keyboard=[
    	[InlineKeyboardButton(text='yes', callback_data='yes_pw')],
        [InlineKeyboardButton(text='no', callback_data='no_pw')]
    ]
)

def geturl(caturl,service2l):
	r=requests.get(f'{caturl}/services')
	r.raise_for_status()  # lanza error si el código no es 2xx
	r=r.json()
	for service in r:
		if service['serviceName']==service2l:
			respuesta=service['url']
	return respuesta

class MyBot:
	def __init__(self,token):
		self.settingss = json.load(open('settings.json','r'))
		self.catalog_url=self.settingss['catalogURL']
		self.statisticProvider_url=geturl(self.catalog_url,'StatisticProvider')
		self.serviceInfo=self.settingss['serviceInfo']
		self.tokenBot=token
		self.tokenBot=self.serviceInfo['pbot_token']
		self.bot=telepot.Bot(self.tokenBot)
		MessageLoop(self.bot, {'chat': self.on_chat_message,'callback_query': self.on_callback_query}).run_as_thread()
		self.info={}
	
	def on_chat_message(self,msg):
		content_type, chat_type, chat_ID = telepot.glance(msg)
		message=msg['text']
		if message[0]=='/':
			if message=="/start":
				self.bot.sendMessage(chat_ID, "Welcome, please proceed with the login:", reply_markup=start_keyboard)
			elif message=="/backtomenu":
				login=True
				try:
					if self.info[chat_ID]["patient_id"]=="":
						login=False
				except:
					login=False
				if login:
					self.bot.sendMessage(chat_ID, text='Please select an option:',reply_markup=main_menu_keyboard)
				else:
					self.bot.sendMessage(chat_ID, text='Please complete the login')
			else:
				self.bot.sendMessage(chat_ID,text="Command not supported")
		else:
			if self.info[chat_ID]['state']=='0':
				self.bot.sendMessage(chat_ID,text="Error, try again")

			elif self.info[chat_ID]['state']=='insert_access_code':
				self.info[chat_ID]['access_code']=message
				self.info[chat_ID]['state']='0'
				self.logIn(chat_ID,1)
			
			elif self.info[chat_ID]['state']=='insert_password':
				self.info[chat_ID]['password']=message
				self.info[chat_ID]['state']='0'
				self.logIn(chat_ID,2)

			elif self.info[chat_ID]['state']=='insert_date_1':
				self.info[chat_ID]['statistics_info']['start']=message
				self.see_statistics(chat_ID,4)

			elif self.info[chat_ID]['state']=='insert_date_2':
				self.info[chat_ID]['statistics_info']['end']=message
				self.see_statistics(chat_ID,5)

			elif self.info[chat_ID]['state']=='add_room_0':
				self.info[chat_ID]['state']='0'
				self.add_room(chat_ID,1,message)

			elif self.info[chat_ID]['state']=='edit_temp_0':
				self.info[chat_ID]['state']='0'
				self.edit_temperature(chat_ID,1,id_room=message)

			elif self.info[chat_ID]['state']=='edit_temp_1':
				self.info[chat_ID]['state']='0'
				self.edit_temperature(chat_ID,2,temperature=message)

			elif self.info[chat_ID]['state']=='edit_temp_2':
				self.info[chat_ID]['state']='0'
				self.edit_temperature(chat_ID,3,temperature=message)

			elif self.info[chat_ID]['state']=='edit_hum_0':
				self.info[chat_ID]['state']='0'
				self.edit_humidity(chat_ID,1,id_room=message)

			elif self.info[chat_ID]['state']=='edit_hum_1':
				self.info[chat_ID]['state']='0'
				self.edit_humidity(chat_ID,2,humidity=message)

			elif self.info[chat_ID]['state']=='edit_hum_2':
				self.info[chat_ID]['state']='0'
				self.edit_humidity(chat_ID,3,humidity=message)

			elif self.info[chat_ID]['state']=='change_pw_0':
				self.info[chat_ID]['state']='0'
				self.settings(chat_ID,3,new_password=message)

	def on_callback_query(self,msg):
		query_ID , chat_ID , query_data = telepot.glance(msg,flavor='callback_query')

		login=True
		try:
			if self.info[chat_ID]["patient_id"]=="":
				login=False
		except:
			login=False

		#action that don't need the login
		if query_data=='logIn':
			self.logIn(chat_ID,0)
			return

		#action that need the login
		elif login:
			
			if query_data=='add_room':
				self.add_room(chat_ID,0)
				return
			elif query_data=='edit_temperature':
				self.edit_temperature(chat_ID,0)
				return
			elif query_data=='edit_humidity':
				self.edit_humidity(chat_ID,0)
				return
			elif query_data=='see_statistics':
				self.see_statistics(chat_ID,0)
				return
			elif query_data=='settings':
				self.settings(chat_ID,0)
				return
			elif query_data=='sel_hr':
				self.info[chat_ID]['statistics_info']['field']='hr'
				self.see_statistics(chat_ID,1)
				return
			elif query_data=='sel_spo2':
				self.info[chat_ID]['statistics_info']['field']='spo2'
				self.see_statistics(chat_ID,1)
				return
			elif query_data=='tw_1d':
				self.info[chat_ID]['statistics_info']['start']=(datetime.now(timezone.utc)-timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
				self.info[chat_ID]['statistics_info']['end']=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
				self.see_statistics(chat_ID,2)
				return
			elif query_data=='tw_1w':
				self.info[chat_ID]['statistics_info']['start']=(datetime.now(timezone.utc)-timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%SZ")
				self.info[chat_ID]['statistics_info']['end']=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
				self.see_statistics(chat_ID,2)
				return
			elif query_data=='tw_1m':
				self.info[chat_ID]['statistics_info']['start']=(datetime.now(timezone.utc)-timedelta(days=31)).strftime("%Y-%m-%dT%H:%M:%SZ")
				self.info[chat_ID]['statistics_info']['end']=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
				self.see_statistics(chat_ID,2)
				return
			elif query_data=='tw_3m':
				self.info[chat_ID]['statistics_info']['start']=(datetime.now(timezone.utc)-timedelta(days=92)).strftime("%Y-%m-%dT%H:%M:%SZ")
				self.info[chat_ID]['statistics_info']['end']=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
				self.see_statistics(chat_ID,2)
				return
			elif query_data=='tw_1y':
				self.info[chat_ID]['statistics_info']['start']=(datetime.now(timezone.utc)-timedelta(days=365)).strftime("%Y-%m-%dT%H:%M:%SZ")
				self.info[chat_ID]['statistics_info']['end']=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
				self.see_statistics(chat_ID,2)
				return
			elif query_data=='tw_p':
				self.see_statistics(chat_ID,3)
				return
			elif query_data=='acc_info':
				self.settings(chat_ID,1)
				return
			elif query_data=='change_pw':
				self.settings(chat_ID,2)
				return
			elif query_data=='yes_pw':
				self.settings(chat_ID,4)
				return
			elif query_data=='no_pw':
				self.settings(chat_ID,5)
				return
		else:
			self.bot.sendMessage(chat_ID, text='Please complete the login')
			return

	def settings(self,chat_ID,step,new_password=''):
		
		if step==0:
			self.bot.sendMessage(chat_ID, text='Please select an option:',reply_markup=select_setting)
			return
		
		elif step==1:
			catalog_data=requests.get(self.catalog_url+'/all').json()
			patient_data=catalog_data['patients'][self.info[chat_ID]['patient_id']]

			list_room_dev=list()
			list_health_dev=list()
			for device_id in catalog_data['patients'][self.info[chat_ID]['patient_id']]['devices']:
				if catalog_data['devices'][device_id]['type']=='home':
					list_room_dev.append(device_id)
				else:
					list_health_dev.append(device_id)

			message="Patient's info:\n"
			message=message+'  Name:         '+patient_data['name']+'\n'
			message=message+'  Surname:      '+patient_data['surname']+'\n'
			message=message+'  Id number:    '+patient_data['id']+'\n\n'
			message=message+"Room's devices:"

			for device_id in list_room_dev:
				message=message+"\n\n  Device's id number:             "+catalog_data['devices'][device_id]['id']
				message=message+"\n    Device's IP:                  "+catalog_data['devices'][device_id]['IP']
				message=message+"\n    Device's port:                "+str(catalog_data['devices'][device_id]['port'])
				message=message+"\n    Device's location:            "+catalog_data['devices'][device_id]['location']
				message=message+"\n    Device's state:               "+str(catalog_data['devices'][device_id]['active'])
				message=message+"\n    Device's services: "+str(catalog_data['devices'][device_id]['available'])
				if 'temperature' in catalog_data['devices'][device_id]['available']:
					message=message+"\n    Device's minimum temperature: "+str(catalog_data['devices'][device_id]['home_parameters']['temperature']['min'])
					message=message+"\n    Device's maximum temperature: "+str(catalog_data['devices'][device_id]['home_parameters']['temperature']['max'])
				if 'humidity' in catalog_data['devices'][device_id]['available']:
					message=message+"\n    Device's minimum humidity:    "+str(catalog_data['devices'][device_id]['home_parameters']['humidity']['min'])
					message=message+"\n    Device's maximum humidity:    "+str(catalog_data['devices'][device_id]['home_parameters']['humidity']['max'])
				message=message+"\n    Device's last update:         "+datetime.fromtimestamp(catalog_data['devices'][device_id]['last_update']).strftime("%y/%m/%d")
			message=message+'\n\n'
			message=message+"Health's devices:"

			for device_id in list_health_dev:
				message=message+"\n\n  Device's id number:     "+catalog_data['devices'][device_id]['id']
				message=message+"\n    Device's IP:          "+catalog_data['devices'][device_id]['IP']
				message=message+"\n    Device's port:        "+str(catalog_data['devices'][device_id]['port'])
				message=message+"\n    Device's location:    "+catalog_data['devices'][device_id]['location']
				message=message+"\n    Device's state:       "+str(catalog_data['devices'][device_id]['active'])
				message=message+"\n    Device's services:    "+str(catalog_data['devices'][device_id]['available'])
				message=message+"\n    Device's last update: "+datetime.fromtimestamp(catalog_data['devices'][device_id]['last_update']).strftime("%y/%m/%d")
			self.bot.sendMessage(chat_ID, text=message)
			return

		elif step==2:
			self.bot.sendMessage(chat_ID, text='Please insert the new password')
			self.info[chat_ID]['state']='change_pw_0'
			return

		elif step==3:
			self.info[chat_ID]['new_password']=new_password
			self.bot.sendMessage(chat_ID, text=new_password+' will be used as new password, do you agree?',reply_markup=confirm_password)
			return

		elif step==4:
			patient_id = self.info[chat_ID]['patient_id']
			self.update_resource(chat_ID, 'patients', patient_id, 'password', self.info[chat_ID]['new_password'])
			self.bot.sendMessage(chat_ID, text='Password updated successfully')
			return

		elif step==5:
			self.bot.sendMessage(chat_ID, text='Password change has been cancelled')
			self.bot.sendMessage(chat_ID, text='Please select an option:',reply_markup=main_menu_keyboard)
			return

	def edit_humidity(self,chat_ID,step,id_room='',humidity=''):
	
		if step==0:
			catalog_data=requests.get(self.catalog_url+'/all').json()
			self.info[chat_ID]['home_devices']=list()
			message='Please, insert the number of the room of your interest:'
			for room_id in self.info[chat_ID]['catalog_data']['devices']:
				if catalog_data['devices'][room_id]['type']=='home':
					message=message+'\n   '+catalog_data['devices'][room_id]['id']+" - "+catalog_data['devices'][room_id]['IP']+" - "+catalog_data['devices'][room_id]['location']
					self.info[chat_ID]['home_devices'].append(int(catalog_data['devices'][room_id]['id']))
			self.info[chat_ID]['state']='edit_hum_0'
			self.bot.sendMessage(chat_ID, text=message)
			return

		elif step==1:
			try:
				id_room = int(id_room)
			except:
				self.bot.sendMessage(chat_ID, text='Error, please insert an integer number present in the list')
				self.edit_temperature(chat_ID,0)
				return
			if not( id_room in self.info[chat_ID]['home_devices'] ):
				self.bot.sendMessage(chat_ID, text='Error, try again')
				self.edit_temperature(chat_ID,0)
				return
			else:
				self.info[chat_ID]['prov_room']={
					"id":id_room,
					"min_hum":"",
					"max_hum":"",
				}
				self.info[chat_ID]['state']='edit_hum_1'
				self.bot.sendMessage(chat_ID, text='Please enter the minimum room humidity value')
			return

		elif step==2:
			try:
				humidity = float(humidity)
			except:
				self.bot.sendMessage(chat_ID, text='Error, try again')
				self.edit_humidity(chat_ID,1,id_room=self.info[chat_ID]['prov_room']['id'])
				return
			self.info[chat_ID]['prov_room']['min_hum']=humidity
			self.info[chat_ID]['state']='edit_hum_2'
			self.bot.sendMessage(chat_ID, text='Please enter the maximum room humidity value')
			return

		elif step==3:
			try:
				humidity = float(humidity)
			except:
				self.bot.sendMessage(chat_ID, text='Error, try again')
				self.edit_humidity(chat_ID,1,id_room=self.info[chat_ID]['prov_room']['id'])
				return
			self.info[chat_ID]['prov_room']['max_hum']=humidity
			if self.info[chat_ID]['prov_room']['min_hum']>self.info[chat_ID]['prov_room']['max_hum']:
				self.bot.sendMessage(chat_ID, text='Error, the maximum humidity value must be lower than the minimum humidity value, try again')
				self.edit_temperature(chat_ID,0)
				return
			else:
				new_room=requests.get(self.catalog_url+'/all').json()['devices'][str(self.info[chat_ID]['prov_room']['id'])]
				new_room['home_parameters']['humidity']['min']=self.info[chat_ID]['prov_room']['min_hum']
				new_room['home_parameters']['humidity']['max']=self.info[chat_ID]['prov_room']['max_hum']
				requests.put(self.catalog_url+'/devices/'+str(self.info[chat_ID]['prov_room']['id']), json=new_room)
				self.bot.sendMessage(chat_ID, text="Room's humidity values updated successfully")
			return

	def edit_temperature(self,chat_ID,step,id_room='',temperature=''):
		
		if step==0:
			catalog_data=requests.get(self.catalog_url+'/all').json()
			self.info[chat_ID]['home_devices']=list()
			message='Please, insert the number of the room of your interest:'
			for room_id in self.info[chat_ID]['catalog_data']['devices']:
				if catalog_data['devices'][room_id]['type']=='home':
					message=message+'\n   '+catalog_data['devices'][room_id]['id']+" - "+catalog_data['devices'][room_id]['IP']+" - "+catalog_data['devices'][room_id]['location']
					self.info[chat_ID]['home_devices'].append(int(catalog_data['devices'][room_id]['id']))
			self.info[chat_ID]['state']='edit_temp_0'
			self.bot.sendMessage(chat_ID, text=message)
			return

		elif step==1:
			try:
				id_room = int(id_room)
			except:
				self.bot.sendMessage(chat_ID, text='Error, please insert an integer number present in the list')
				self.edit_temperature(chat_ID,0)
				return
			if not( id_room in self.info[chat_ID]['home_devices'] ):
				self.bot.sendMessage(chat_ID, text='Error, try again')
				self.edit_temperature(chat_ID,0)
				return
			else:
				self.info[chat_ID]['prov_room']={
					"id":id_room,
					"min_temp":"",
					"max_temp":"",
				}
				self.info[chat_ID]['state']='edit_temp_1'
				self.bot.sendMessage(chat_ID, text='Please enter the minimum room temperature value')
			return

		elif step==2:
			try:
				temperature = float(temperature)
			except:
				self.bot.sendMessage(chat_ID, text='Error, try again')
				self.edit_temperature(chat_ID,1,id_room=self.info[chat_ID]['prov_room']['id'])
				return
			self.info[chat_ID]['prov_room']['min_temp']=temperature
			self.info[chat_ID]['state']='edit_temp_2'
			self.bot.sendMessage(chat_ID, text='Please enter the maximum room temperature value')
			return

		elif step==3:
			try:
				temperature = float(temperature)
			except:
				self.bot.sendMessage(chat_ID, text='Error, try again')
				self.edit_temperature(chat_ID,1,id_room=self.info[chat_ID]['prov_room']['id'])
				return
			self.info[chat_ID]['prov_room']['max_temp']=temperature
			if self.info[chat_ID]['prov_room']['min_temp']>self.info[chat_ID]['prov_room']['max_temp']:
				self.bot.sendMessage(chat_ID, text='Error, the maximum temperature must be lower than the minimum temperature, try again')
				self.edit_temperature(chat_ID,0)
				return
			else:
				new_room=requests.get(self.catalog_url+'/all').json()['devices'][str(self.info[chat_ID]['prov_room']['id'])]
				new_room['home_parameters']['temperature']['min']=self.info[chat_ID]['prov_room']['min_temp']
				new_room['home_parameters']['temperature']['max']=self.info[chat_ID]['prov_room']['max_temp']
				print(f'\nPUT REQUEST {new_room}\n')
				requests.put(self.catalog_url+'/devices/'+str(self.info[chat_ID]['prov_room']['id']), json=new_room)
				self.bot.sendMessage(chat_ID, text='Room temperature updated successfully')
			return

	def add_room(self,chat_ID,step,id_room=''):
		
		if step==0:
			catalog_data=requests.get(self.catalog_url+'/all').json()['devices']
			list_id_room=list()
			message='Please insert the id number of your room:'
			for device in catalog_data.keys():
				if (catalog_data[device]['active']==0 or catalog_data[device]['active']=='0') and (catalog_data[device]['type']=='home'):
					list_id_room.append(int(catalog_data[device]['id']))
					message=message+'\n   '+catalog_data[device]['id']+" - "+catalog_data[device]['IP']+" - "+catalog_data[device]['location']
			self.info[chat_ID]['list_id_room']=list_id_room
			self.info[chat_ID]['state']='add_room_0'
			self.bot.sendMessage(chat_ID, text=message)
			return

		elif step==1:
			try:
				id_room = int(id_room)
			except:
				self.bot.sendMessage(chat_ID, text='Error, please insert an integer number present in the list')
				self.add_room(chat_ID,0)
				return
			if not( id_room in self.info[chat_ID]['list_id_room'] ):
				self.bot.sendMessage(chat_ID, text='Error, please insert an id present in the list')
				self.add_room(chat_ID,0)
				return
			else:
				self.info[chat_ID]['catalog_data']['devices'].append(str(id_room))
				requests.put(self.catalog_url+'/patients/'+self.info[chat_ID]['catalog_data']['id'], json=self.info[chat_ID]['catalog_data'])
				new_room=requests.get(self.catalog_url+'/all').json()['devices'][str(id_room)]
				new_room['active']=1
				new_room['home_parameters']['temperature']['min']=19
				new_room['home_parameters']['temperature']['max']=25
				new_room['home_parameters']['humidity']['min']=30
				new_room['home_parameters']['humidity']['max']=70
				requests.put(self.catalog_url+'/devices/'+str(id_room), json=new_room)
				self.bot.sendMessage(chat_ID, text='Room added successfully')
			return

	def see_statistics(self,chat_ID,step):
		
		if step==0:
			self.bot.sendMessage(chat_ID, "Please select the parameter of your interest:", reply_markup=hr_spo2_keyboard)
			return

		elif step==1:
			self.bot.sendMessage(chat_ID, "Please select the time window:", reply_markup=time_window_keyboard)
			return

		elif step==2:
			#self.statisticProvider_url = self.create_data_file()['statistic_provider_url']
			pdf_resp = io.BytesIO(requests.get(self.statisticProvider_url+'/'+self.info[chat_ID]['patient_id'],params=self.info[chat_ID]['statistics_info']).content)
			pdf_resp.name='statistics_'+self.info[chat_ID]['surname']+'_'+self.info[chat_ID]['name']+'_'+self.info[chat_ID]['statistics_info']['field']+'.pdf'
			self.info[chat_ID]['state']='0'
			self.bot.sendDocument(chat_ID,pdf_resp)
			return

		elif step==3:
			self.bot.sendMessage(chat_ID, text="Please insert the start date in the format YYYY/MM/DD")
			self.info[chat_ID]['state']='insert_date_1'
			return

		elif step==4:
			date=self.info[chat_ID]['statistics_info']['start']
			try:
				[year,month,day]=date.split("/")
				year=int(year)
				month=int(month)
				day=int(day)
			except:
				self.bot.sendMessage(chat_ID,text="Error, try again")
				self.see_statistics(chat_ID,3)
				return
			if (year > int(datetime.now().year)) or (year < (int(datetime.now().year)-100)) or (month < 1) or (month > 12) or (day<1) or (day>31):
				self.bot.sendMessage(chat_ID,text="Error, try again")
				self.see_statistics(chat_ID,3)
				return
			date_1 = datetime.strptime(date, "%Y/%m/%d")
			date_2 = date_1.replace(tzinfo=pytz.UTC)
			date_3 = date_2.strftime("%Y-%m-%dT%H:%M:%SZ")
			self.info[chat_ID]['statistics_info']['start']=date_3
			self.bot.sendMessage(chat_ID, text="Please insert the end date in the format YYYY/MM/DD")
			self.info[chat_ID]['state']='insert_date_2'
			return

		elif step==5:
			date=self.info[chat_ID]['statistics_info']['end']
			try:
				[year,month,day]=date.split("/")
				year=int(year)
				month=int(month)
				day=int(day)
			except:
				self.bot.sendMessage(chat_ID,text="Error, try again")
				self.see_statistics(chat_ID,4)
				return
			if (year > int(datetime.now().year)) or (year < (int(datetime.now().year)-100)) or (month < 1) or (month > 12) or (day<1) or (day>31):
				self.bot.sendMessage(chat_ID,text="Error, try again")
				self.see_statistics(chat_ID,4)
				return
			date_1 = datetime.strptime(date, "%Y/%m/%d")
			date_2 = date_1.replace(tzinfo=pytz.UTC)
			date_3 = date_2.strftime("%Y-%m-%dT%H:%M:%SZ")
			self.info[chat_ID]['statistics_info']['end']=date_3
			self.see_statistics(chat_ID,2)
			return

	def create_data_file(self):
		catalog = json.loads(requests.get(self.catalog_url +'/all').text)
		data={
		    "catalog_url": self.catalog_url,
		    "statistic_provider_url": self.statisticProvider_url,
		    "doctor":{},
		    "patient": {}
		}
		'''
		for service in catalog["services"]:
			if service["serviceName"]=="StatisticProvider":
				data["statistic_provider_url"] = service["url"]
		'''
		data["doctor"] = catalog["doctors"]
		
		for patient_id, patient in catalog["patients"].items():
		    data["patient"][patient_id] = {
		        'patient_id': patient["id"],
		        'name': patient["name"],
		        'surname': patient["surname"],
		        'access_code': patient["access_code"],
		        'password': patient["password"]
		    }
		
		for doctor_id, doctor in catalog["doctors"].items():
		    data["doctor"][doctor_id] = {
		        'doctor_id': doctor["id"],
		        'name': doctor["name"],
		        'surname': doctor["surname"],
		        'access_code': doctor["access_code"],
		        'password': doctor["password"],
		        'patient_list': doctor["patient_list"]
		    }

		return data

	def logIn(self,chat_ID,step):
		
		if step == 0:
			self.info[chat_ID]={
						"patient_id": "",
			            "name": "",
			            "surname": "",
			            "access_code": "",
			            "password": "",
			            "state":"0",
			            "catalog_data":{},
			            "list_id_room":[],
			            "statistics_info":{
			            	"field":"",
			            	"start":"",
			            	"end":""
						},
			            "found":False
					}
			self.bot.sendMessage(chat_ID, text='Please insert the access code')
			self.info[chat_ID]['state']='insert_access_code'
			return

		elif step == 1:
			self.bot.sendMessage(chat_ID, text='Please insert the password')
			self.info[chat_ID]['state']='insert_password'
			return

		elif step == 2:
			data = self.create_data_file()
			# access code check
			for patient_id in data['patient']:
				if data['patient'][patient_id]['access_code']==self.info[chat_ID]['access_code']:
					self.info[chat_ID]["found"] = True
					if data['patient'][patient_id]['password']==self.info[chat_ID]['password']:
						self.info[chat_ID]['patient_id']=data['patient'][patient_id]['patient_id']
						self.info[chat_ID]['surname']=data['patient'][patient_id]['surname']
						self.info[chat_ID]['name']=data['patient'][patient_id]['name']
						self.info[chat_ID]['catalog_data']=requests.get(self.catalog_url+'/all').json()['patients'][patient_id]
						self.bot.sendMessage(chat_ID, text='Login successful, please select an option:',reply_markup=main_menu_keyboard)
					else:
						self.bot.sendMessage(chat_ID, text='Error, the password is wrong, try again')
						self.logIn(chat_ID,1)
				
			if not self.info[chat_ID]["found"]:
				self.bot.sendMessage(chat_ID, text='Error, the access code is wrong, try again')
				self.logIn(chat_ID,0)
			return

	def update_resource(self, chat_ID, uri_0, uri_1, name, value):
		#  uri_0 --> tipo della risorsa da aggiornare
		#  uri_1 --> id della risorsa da aggiornare
		#  name --> nome del campo (es: name, surname, password, ...)
		#  value --> nuovo valore
		catalog = json.loads(requests.get(self.catalog_url +'/all').text)
		new_object = catalog[uri_0][uri_1]
		new_object[name] = value
		requests.put(self.catalog_url +'/'+uri_0+'/'+uri_1, json=new_object)

if __name__=='__main__':
	time.sleep(10)
	token='8012715662:AAHaSa2-8gordFNA-GL9xERkx-swsvC_5j4'
	AndreaVolaBot = MyBot(token)	
	try:
		print("\n____________________________________________________________\n")
		print(f"  Patient's Bot is running with token: {token}\n")
		print("____________________________________________________________\n")
		print("Press Ctrl+C to stop the server. \n")

		while True:
			time.sleep(0.5)
	
	except KeyboardInterrupt:
		print('Bot stopped')























