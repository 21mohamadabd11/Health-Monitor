#nome bot: doctor16bot
#token: 7516687380:AAHItb6UAjK0oZkRLc6v8-Wk8z4yK2CPzjM

import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
import json
import requests
import time
from datetime import datetime, timedelta, timezone
import io
import pytz

mainMenuDoctor = InlineKeyboardMarkup(
    inline_keyboard=[
    	[InlineKeyboardButton(text='add patient', callback_data='addPatient')],
        [InlineKeyboardButton(text='edit patient', callback_data='editPatient'),
        InlineKeyboardButton(text='see statistics', callback_data='statistics')],
        [InlineKeyboardButton(text='settings', callback_data='settings')]
    ]
)

loginMenu = InlineKeyboardMarkup(
    inline_keyboard=[
    	[InlineKeyboardButton(text='log in', callback_data='logIn')],
        [InlineKeyboardButton(text='sign up', callback_data='signUp')]
    ]
)

yes_no_signup = InlineKeyboardMarkup(
    inline_keyboard=[
    	[InlineKeyboardButton(text='yes', callback_data='yes_signup')],
        [InlineKeyboardButton(text='no', callback_data='no_signup')]
    ]
)

yes_no_new_patient = InlineKeyboardMarkup(
    inline_keyboard=[
    	[InlineKeyboardButton(text='yes', callback_data='yes_new_patient')],
        [InlineKeyboardButton(text='no', callback_data='no_new_patient')]
    ]
)

yes_no_del_pat = InlineKeyboardMarkup(
    inline_keyboard=[
    	[InlineKeyboardButton(text='yes', callback_data='yes_del_pat')],
        [InlineKeyboardButton(text='no', callback_data='no_del_pat')]
    ]
)

edit_patient_menu = InlineKeyboardMarkup(
    inline_keyboard=[
    	[InlineKeyboardButton(text='add device', callback_data='add_device')],
        [InlineKeyboardButton(text='remove device', callback_data='remove_device')],
        [InlineKeyboardButton(text='remove patient', callback_data='remove_patient')],
        [InlineKeyboardButton(text='see patient data', callback_data='see_patient_data')]
    ]
)

hr_spo2 = InlineKeyboardMarkup(
    inline_keyboard=[
    	[InlineKeyboardButton(text='heart rate', callback_data='sel_hr')],
        [InlineKeyboardButton(text='Oxygen Saturation (SpO2)', callback_data='sel_spo2')]
    ]
)

time_window = InlineKeyboardMarkup(
    inline_keyboard=[
    	[InlineKeyboardButton(text='last day', callback_data='tw_1d')],
        [InlineKeyboardButton(text='last week', callback_data='tw_1w')],
        [InlineKeyboardButton(text='last month', callback_data='tw_1m')],
        [InlineKeyboardButton(text='last 3 months', callback_data='tw_3m')],
        [InlineKeyboardButton(text='last year', callback_data='tw_1y')],
        [InlineKeyboardButton(text='personalized', callback_data='tw_p')]
    ]
)

settings_1 = InlineKeyboardMarkup(
    inline_keyboard=[
    	[InlineKeyboardButton(text='change password', callback_data='change_password')],
        [InlineKeyboardButton(text='view doctor info', callback_data='view_doctor_info')]
    ]
)

yes_no_new_pw = InlineKeyboardMarkup(
    inline_keyboard=[
    	[InlineKeyboardButton(text='yes', callback_data='yes_new_pw')],
        [InlineKeyboardButton(text='no', callback_data='no_new_pw')]
    ]
)
def geturl(caturl,service2l):
	r=requests.get(f'{caturl}/services')
	r.raise_for_status()  # lanza error si el código no es 2xx
	r=r.json()
	for service in r:
		if service.get('serviceName')==service2l:
			respuesta=service.get('url')
	return respuesta
	
class MyBot:
	def __init__(self,token):
		self.settingss = json.load(open('settings.json','r'))
		self.catalog_url=self.settingss['catalogURL']
		self.statisticProvider_url=geturl(self.catalog_url,'StatisticProvider')
		self.serviceInfo=self.settingss['serviceInfo']
		self.tokenBot=token
		self.tokenBot=self.serviceInfo['dbot_token']
		self.bot=telepot.Bot(self.tokenBot)
		MessageLoop(self.bot, {'chat': self.on_chat_message,'callback_query': self.on_callback_query}).run_as_thread()
		self.info={}
		self.new_patient_info={}
		
	
	def on_chat_message(self,msg):
		content_type, chat_type, chat_ID = telepot.glance(msg)
		message=msg['text']
		if message[0]=='/':
			if message=="/start":
				self.bot.sendMessage(chat_ID, "Choose an option:", reply_markup=loginMenu)

			elif message=="/backtomenu":
				login=True
				try:
					if self.info[chat_ID]["doctor_id"]=="":
						login=False
				except:
					login=False
				if login:
					self.bot.sendMessage(chat_ID, text='Please select an option:',reply_markup=mainMenuDoctor)
				else:
					self.bot.sendMessage(chat_ID, text='Please complete the login')
			else:
				self.bot.sendMessage(chat_ID,text="Command not supported")
		else:
			if self.info[chat_ID]['state']=='0':
				self.bot.sendMessage(chat_ID,text="Error, try again")

			elif self.info[chat_ID]['state']=='login_access_code':
				self.info[chat_ID]['access_code']=message
				self.info[chat_ID]['state']='0'
				self.logIn(chat_ID,1)
			elif self.info[chat_ID]['state']=='login_password':
				self.info[chat_ID]['password']=message
				self.info[chat_ID]['state']='0'
				self.logIn(chat_ID,2)
			elif self.info[chat_ID]['state']=="signup_name":
				self.info[chat_ID]['name']=message
				self.info[chat_ID]['state']='0'
				self.signUp(chat_ID,1)
			elif self.info[chat_ID]['state']=='signup_surname':
				self.info[chat_ID]['surname']=message
				self.info[chat_ID]['state']='0'
				self.signUp(chat_ID,2)
			elif self.info[chat_ID]['state']=="signup_access_code":
				self.info[chat_ID]['access_code']=message
				self.info[chat_ID]['state']='0'
				self.signUp(chat_ID,3)
			elif self.info[chat_ID]['state']=='signup_password':
				self.info[chat_ID]['password']=message
				self.info[chat_ID]['state']='0'
				self.signUp(chat_ID,4)
			elif self.info[chat_ID]['state']=='register_patient_name':
				self.new_patient_info[chat_ID]['data']['name']=message
				self.info[chat_ID]['state']='0'
				self.addPatient(chat_ID,1)
			elif self.info[chat_ID]['state']=='register_patient_surname':
				self.new_patient_info[chat_ID]['data']['surname']=message
				self.info[chat_ID]['state']='0'
				self.addPatient(chat_ID,2)
			elif self.info[chat_ID]['state']=='register_patient_access_code':
				self.new_patient_info[chat_ID]['data']['access_code']=message
				self.info[chat_ID]['state']='0'
				self.addPatient(chat_ID,3)
			elif self.info[chat_ID]['state']=='register_patient_password':
				self.new_patient_info[chat_ID]['data']['password']=message
				self.info[chat_ID]['state']='0'
				self.addPatient(chat_ID,4)
			elif self.info[chat_ID]['state']=='edit_select_patient':
				self.info[chat_ID]['edit_patient_data']={'patient_id':message}
				self.info[chat_ID]['state']='0'
				self.editPatient(chat_ID,1)
			elif self.info[chat_ID]['state'] == 'add_dev_select_device_1':
				self.info[chat_ID]['edit_patient_data']['add_device']={'device_id':message}
				self.info[chat_ID]['state']='0'
				self.editPatient(chat_ID,101)
			elif self.info[chat_ID]['state'] == 'rem_dev_select_device_1':
				self.info[chat_ID]['edit_patient_data']['rem_device']={'device_id':message}
				self.info[chat_ID]['state']='0'
				self.editPatient(chat_ID,201)
			elif self.info[chat_ID]['state']=='edit_select_patient_2':
				self.info[chat_ID]['seeStatistics']={'patient_id':message}
				self.info[chat_ID]['state']='0'
				self.seeStatistics(chat_ID,1)
			elif self.info[chat_ID]['state']=='insert_date_1':
				self.info[chat_ID]['seeStatistics']['pdf_request_data']={'start':message}
				self.info[chat_ID]['state']='0'
				self.seeStatistics(chat_ID,7)
			elif self.info[chat_ID]['state']=='insert_date_2':
				self.info[chat_ID]['seeStatistics']['pdf_request_data']['end']=message
				self.info[chat_ID]['state']='0'
				self.seeStatistics(chat_ID,8)
			elif self.info[chat_ID]['state']=='new_doctor_password':
				self.info[chat_ID]['settings']={'new_password':message}
				self.info[chat_ID]['state']='0'
				self.settings(chat_ID,101)

	def on_callback_query(self,msg):
		query_ID , chat_ID , query_data = telepot.glance(msg,flavor='callback_query')

		login=True
		try:
			if self.info[chat_ID]["doctor_id"]=="":
				login=False
		except:
			login=False

		#action that don't need the login
		if query_data=='logIn':
			self.logIn(chat_ID,0)
			return
		elif query_data=='signUp':
			self.signUp(chat_ID,0)
			return
		if query_data=='yes_signup':
			self.signUp(chat_ID,5)
			return
		elif query_data=='no_signup':
			self.signUp(chat_ID,6)
			return

		#action that need the login
		elif login:
			
			if query_data=='addPatient':
				self.addPatient(chat_ID,0)
				return
			elif query_data=='yes_new_patient':
				self.addPatient(chat_ID,5)
				return
			elif query_data=='no_new_patient':
				self.addPatient(chat_ID,6)
				return
			
			elif query_data=='editPatient':
				self.editPatient(chat_ID,0)
				return
			elif query_data=='yes_del_pat':
				self.editPatient(chat_ID,301)
				return
			elif query_data=='no_del_pat':
				self.editPatient(chat_ID,302)
				return
			elif query_data=='add_device':
				self.editPatient(chat_ID,100)
				return
			elif query_data=='remove_device':
				self.editPatient(chat_ID,200)
				return
			elif query_data=='remove_patient':
				self.editPatient(chat_ID,300)
				return
			elif query_data=='see_patient_data':
				self.editPatient(chat_ID,400)
				return

			elif query_data=='statistics':
				self.seeStatistics(chat_ID,0)
				return
			elif query_data=='sel_hr':
				self.seeStatistics(chat_ID,2)
				return
			elif query_data=='sel_spo2':
				self.seeStatistics(chat_ID,3)
				return
			elif query_data=='tw_1d':
				self.seeStatistics(chat_ID,5,'tw_1d')
				return
			elif query_data=='tw_1w':
				self.seeStatistics(chat_ID,5,'tw_1w')
				return
			elif query_data=='tw_1m':
				self.seeStatistics(chat_ID,5,'tw_1m')
				return
			elif query_data=='tw_3m':
				self.seeStatistics(chat_ID,5,'tw_3m')
				return
			elif query_data=='tw_1y':
				self.seeStatistics(chat_ID,5,'tw_1y')
				return
			elif query_data=='tw_p':
				self.seeStatistics(chat_ID,6,'tw_p')
				return

			elif query_data=='settings':
				self.settings(chat_ID,0)
				return
			elif query_data=='change_password':
				self.settings(chat_ID,100)
				return
			elif query_data=='yes_new_pw':
				self.settings(chat_ID,102)
				return
			elif query_data=='no_new_pw':
				self.settings(chat_ID,103)
				return
			elif query_data=='view_doctor_info':
				self.settings(chat_ID,200)
				return

		else:
			self.bot.sendMessage(chat_ID, text='Please complete the login')
			return

	def settings(self,chat_ID,step):
		
		if (step>=0 and step<100): # initial menu
			if step==0:
				self.bot.sendMessage(chat_ID, "Please select an option", reply_markup=settings_1)
				return

		elif (step>=100 and step<200): # change password
			
			if step==100:
				self.info[chat_ID]['state']='new_doctor_password'
				self.bot.sendMessage(chat_ID, "Please insert the new password")
				return

			elif step==101:
				new_pw = self.info[chat_ID]['settings']['new_password']
				self.bot.sendMessage(chat_ID, "Are you sure to set as new password: "+new_pw, reply_markup=yes_no_new_pw)
				return

			elif step==102:
				self.info[chat_ID]['bot_data'] = self.create_data_file()
				doc_id=self.info[chat_ID]['doctor_id']
				new_pw = self.info[chat_ID]['settings']['new_password']
				self.info[chat_ID]['bot_data']['doctor'][doc_id]['password']=new_pw

				self.update_resource(chat_ID, "doctors", doc_id, "password", new_pw)

				self.bot.sendMessage(chat_ID, "Password updated successfully")
				self.bot.sendMessage(chat_ID,text='Please select an option',reply_markup=mainMenuDoctor)
				return
			
			elif step==103:
				self.bot.sendMessage(chat_ID,text='Ok, please select an option',reply_markup=mainMenuDoctor)
				return

		elif (step>=200 and step<300): # view doctor info
			
			if step==200:

				message='Doctor '+self.info[chat_ID]['doctor_id']+' info: \n'
				message=message+'id: '+ self.info[chat_ID]['doctor_id']
				message=message+'\nname: ' + self.info[chat_ID]['name']
				message=message+'\nsurname: '+ self.info[chat_ID]['surname']
				message=message+'\npatients:'
				
				self.catalog = json.loads(requests.get(self.catalog_url +'/all').text)
				self.info[chat_ID]['bot_data'] = self.create_data_file()

				for pat_id in self.info[chat_ID]['bot_data']['doctor'][self.info[chat_ID]['doctor_id']]['patient_list']:
					message=message+'\n    '+str(pat_id)+' - '+self.catalog['patients'][str(pat_id)]['surname']+' - '+self.catalog['patients'][str(pat_id)]['name']

				message=message+'\naccess code: '+self.info[chat_ID]['bot_data']['doctor'][self.info[chat_ID]['doctor_id']]['access_code']
				message=message+'\npassword: '+self.info[chat_ID]['bot_data']['doctor'][self.info[chat_ID]['doctor_id']]['password']

				self.bot.sendMessage(chat_ID,text=message)
				return

	def seeStatistics(self,chat_ID,step,timeWind=''):

		if step==0: # select patient 1
			self.info[chat_ID]['bot_data'] = self.create_data_file()
			testo='Please instert the id of the patient of your interest:'
			
			doctor_id=self.info[chat_ID]['doctor_id']
			for patient_id in self.info[chat_ID]['bot_data']['doctor'][doctor_id]['patient_list']:
				name=self.info[chat_ID]['bot_data']['patient'][str(patient_id)]['name']
				surname=self.info[chat_ID]['bot_data']['patient'][str(patient_id)]['surname']
				testo=testo+'\n '+str(patient_id)+' - '+surname+' '+name
			self.info[chat_ID]['state']='edit_select_patient_2'
			self.bot.sendMessage(chat_ID, text=testo)
			return
		
		elif step==1: # select patient 2
			try:
				patient_id = int(self.info[chat_ID]['seeStatistics']['patient_id'])
				doctor_id=self.info[chat_ID]['doctor_id']
				if not patient_id in self.info[chat_ID]['bot_data']['doctor'][doctor_id]['patient_list']:
					self.bot.sendMessage(chat_ID, text="The selected id is wrong, try again")
					self.seeStatistics(chat_ID,0)
				else:
					self.bot.sendMessage(chat_ID, "Please select the parameter of your interest:", reply_markup=hr_spo2)
			except:
				self.bot.sendMessage(chat_ID, text="The selected id is wrong, try again")
				self.seeStatistics(chat_ID,0)
			return

		elif step==2: # hr
			self.info[chat_ID]['seeStatistics']['parameter']="hr"
			self.seeStatistics(chat_ID,4)
			return

		elif step==3: # spo2
			self.info[chat_ID]['seeStatistics']['parameter']="spo2"
			self.seeStatistics(chat_ID,4)
			return

		elif step==4: # select time window
			self.bot.sendMessage(chat_ID, "Please select the time window:", reply_markup=time_window)
			return

		elif step==5: # standard time window
			
			if timeWind=='tw_1d':
				self.info[chat_ID]['seeStatistics']['pdf_request_data']={'start':(datetime.now(timezone.utc)-timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")}
				self.info[chat_ID]['seeStatistics']['pdf_request_data']['end']=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
				self.seeStatistics(chat_ID,10)
			elif timeWind=='tw_1w':
				self.info[chat_ID]['seeStatistics']['pdf_request_data']={'start':(datetime.now(timezone.utc)-timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%SZ")}
				self.info[chat_ID]['seeStatistics']['pdf_request_data']['end']=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
				self.seeStatistics(chat_ID,10)
			elif timeWind=='tw_1m':
				self.info[chat_ID]['seeStatistics']['pdf_request_data']={'start':(datetime.now(timezone.utc)-timedelta(days=31)).strftime("%Y-%m-%dT%H:%M:%SZ")}
				self.info[chat_ID]['seeStatistics']['pdf_request_data']['end']=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
				self.seeStatistics(chat_ID,10)
			elif timeWind=='tw_3m':
				self.info[chat_ID]['seeStatistics']['pdf_request_data']={'start':(datetime.now(timezone.utc)-timedelta(days=92)).strftime("%Y-%m-%dT%H:%M:%SZ")}
				self.info[chat_ID]['seeStatistics']['pdf_request_data']['end']=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
				self.seeStatistics(chat_ID,10)
			elif timeWind=='tw_1y':
				self.info[chat_ID]['seeStatistics']['pdf_request_data']={'start':(datetime.now(timezone.utc)-timedelta(days=365)).strftime("%Y-%m-%dT%H:%M:%SZ")}
				self.info[chat_ID]['seeStatistics']['pdf_request_data']['end']=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
				self.seeStatistics(chat_ID,10)
			return

		elif step==6: # personalized time window
			self.bot.sendMessage(chat_ID, text="Please insert the start date in the format YYYY/MM/DD")
			self.info[chat_ID]['state']='insert_date_1'
			return

		elif step==7:
			date=self.info[chat_ID]['seeStatistics']['pdf_request_data']['start']
			
			try:
				[year,month,day]=date.split("/")
				year=int(year)
				month=int(month)
				day=int(day)
			except:
				self.bot.sendMessage(chat_ID,text="Error, try again")
				self.seeStatistics(chat_ID,6)
				return

			if (year > int(datetime.now().year)) or (year < (int(datetime.now().year)-100)) or (month < 1) or (month > 12) or (day<1) or (day>31):
				self.bot.sendMessage(chat_ID,text="Error, try again")
				self.see_statistics(chat_ID,6)
				return

			date_1 = datetime.strptime(date, "%Y/%m/%d")
			date_2 = date_1.replace(tzinfo=pytz.UTC)
			date_3 = date_2.strftime("%Y-%m-%dT%H:%M:%SZ")

			self.info[chat_ID]['seeStatistics']['pdf_request_data']['start']=date_3
			self.bot.sendMessage(chat_ID,text="Well done, now insert the end date in the format YYYY/MM/DD")
			self.state='insert_date_2'
			return

		elif step==8:
			date=self.info[chat_ID]['seeStatistics']['pdf_request_data']['end']
			
			try:
				[year,month,day]=date.split("/")
				year=int(year)
				month=int(month)
				day=int(day)
			except:
				self.bot.sendMessage(chat_ID,text="Error, try again")
				self.seeStatistics(chat_ID,9)
				return

			if (year > int(datetime.now().year)) or (year < (int(datetime.now().year)-100)) or (month < 1) or (month > 12) or (day<1) or (day>31):
				self.bot.sendMessage(chat_ID,text="Error, try again")
				self.see_statistics(chat_ID,9)
				return

			date_1 = datetime.strptime(date, "%Y/%m/%d")
			date_2 = date_1.replace(tzinfo=pytz.UTC)
			date_3 = date_2.strftime("%Y-%m-%dT%H:%M:%SZ")

			self.info[chat_ID]['seeStatistics']['pdf_request_data']['end']=date_3
			self.seeStatistics(chat_ID,10)
			return

		elif step==9:
			self.bot.sendMessage(chat_ID,text="Please insert the end date in the format YYYY/MM/DD")
			self.state='insert_date_2'
			return
			
		elif step==10: # pdf request
			patient_id=self.info[chat_ID]['seeStatistics']['patient_id']
			parameters=self.info[chat_ID]['seeStatistics']['pdf_request_data']
			parameters["field"] = self.info[chat_ID]['seeStatistics']["parameter"]
			#self.statisticProvider_url= self.create_data_file() ['statistic_provider_url']
			#pdf_resp = io.BytesIO(requests.get(self.statisticProvider_url+'/'+self.pdf_request_data['uri'],params=self.pdf_request_data['parameters']).content)
			#print(self.statisticProvider_url+'/'+patient_id)
			#print(parameters)
			pdf_resp = io.BytesIO(requests.get(self.statisticProvider_url+'/'+patient_id,params=parameters).content)
			pdf_resp.name='statistics_'+self.info[chat_ID]['bot_data']['patient'][patient_id]['surname']+'_'+self.info[chat_ID]['bot_data']['patient'][patient_id]['name']+'_'+self.info[chat_ID]['seeStatistics']['parameter']+'.pdf'
			self.bot.sendDocument(chat_ID,pdf_resp)
			return

	def editPatient(self,chat_ID,step):

		if (step>=0 and step<100): # select patient
			
			if step==0:
				self.info[chat_ID]['bot_data'] = self.create_data_file()
				testo='Please instert the id of the patient of your interest:'
				
				doctor_id=self.info[chat_ID]['doctor_id']
				for patient_id in self.info[chat_ID]['bot_data']['doctor'][doctor_id]['patient_list']:
					name=self.info[chat_ID]['bot_data']['patient'][str(patient_id)]['name']
					surname=self.info[chat_ID]['bot_data']['patient'][str(patient_id)]['surname']
					testo=testo+'\n '+str(patient_id)+' - '+surname+' '+name
				self.info[chat_ID]['state']='edit_select_patient'
				self.bot.sendMessage(chat_ID, text=testo)
				return
			
			elif step==1:
				try:
					patient_id = int(self.info[chat_ID]['edit_patient_data']['patient_id'])
					doctor_id=self.info[chat_ID]['doctor_id']
					if not patient_id in self.info[chat_ID]['bot_data']['doctor'][doctor_id]['patient_list']:
						self.bot.sendMessage(chat_ID, text="The selected id is wrong, try again")
						self.editPatient(chat_ID,0)
					else:
						self.bot.sendMessage(chat_ID, "Please select an option:", reply_markup=edit_patient_menu)
				except:
					self.bot.sendMessage(chat_ID, text="The selected id is wrong, try again")
					self.editPatient(chat_ID,0)
				return

		elif (step>=100 and step<200): # add device
			
			if step==100:
				self.catalog = json.loads(requests.get(self.catalog_url +'/all').text)
				message='Please enter the device number to add:'
				for device in self.catalog['devices'].keys():
					if self.catalog['devices'][device]['active'] == 0 or self.catalog['devices'][device]['active'] == '0':
						message=message+'\n'+device+' - '+self.catalog['devices'][device]['IP']+' - '+self.catalog['devices'][device]['location']+' - '+self.catalog['devices'][device]['type']
				self.bot.sendMessage(chat_ID,text=message)
				self.info[chat_ID]['state'] = 'add_dev_select_device_1'
				return
			
			elif step==101:
				self.catalog = json.loads(requests.get(self.catalog_url +'/all').text)
				device_id=str(self.info[chat_ID]['edit_patient_data']['add_device']['device_id'])
				dev_id_correct = False

				if (device_id in self.catalog['devices'].keys()) and (self.catalog['devices'][device_id]['active'] == 0 or self.catalog['devices'][device_id]['active'] == '0'):
					dev_id_correct = True					
				else:
					self.bot.sendMessage(chat_ID, text="The selected id is wrong, try again")
					self.editPatient(chat_ID,100)
				
				if dev_id_correct:
					self.catalog['devices'][device_id]['active'] = 1
					self.catalog['patients'][self.info[chat_ID]['edit_patient_data']['patient_id']]['devices'].append(device_id)
					requests.put(self.catalog_url+'/patients/'+str(self.info[chat_ID]['edit_patient_data']['patient_id']),json=self.catalog['patients'][self.info[chat_ID]['edit_patient_data']['patient_id']])
					requests.put(self.catalog_url+'/devices/'+str(self.info[chat_ID]['edit_patient_data']['add_device']['device_id']),json=self.catalog['devices'][device_id])
					self.bot.sendMessage(chat_ID,text='The device has been added successfully')
					self.bot.sendMessage(chat_ID,text='Please select an option',reply_markup=mainMenuDoctor)
				return

		elif (step>=200 and step<300): # remove device
			
			if step==200:
				self.catalog = json.loads(requests.get(self.catalog_url +'/all').text)
				message='Please enter the device number to remove:'
				for device in self.catalog['patients'][self.info[chat_ID]['edit_patient_data']['patient_id']]['devices']:
					message=message+'\n'+device+' - '+self.catalog['devices'][device]['IP']+' - '+self.catalog['devices'][device]['location']+' - '+self.catalog['devices'][device]['type']
				self.bot.sendMessage(chat_ID,text=message)
				self.info[chat_ID]['state'] = 'rem_dev_select_device_1'
				return
			
			elif step==201:
				self.catalog = json.loads(requests.get(self.catalog_url +'/all').text)
				device_id=str(self.info[chat_ID]['edit_patient_data']['rem_device']['device_id'])
				dev_id_correct = False

				if (device_id in self.catalog['devices'].keys()) and (device_id in self.catalog['patients'][self.info[chat_ID]['edit_patient_data']['patient_id']]['devices']):
					dev_id_correct = True					
				else:
					self.bot.sendMessage(chat_ID, text="The selected id is wrong, try again")
					self.editPatient(chat_ID,100)
				
				if dev_id_correct:
					self.catalog['devices'][device_id]['active'] = 0
					self.catalog['patients'][self.info[chat_ID]['edit_patient_data']['patient_id']]['devices'].remove(device_id)
					requests.put(self.catalog_url+'/patients/'+str(self.info[chat_ID]['edit_patient_data']['patient_id']),json=self.catalog['patients'][self.info[chat_ID]['edit_patient_data']['patient_id']])
					requests.put(self.catalog_url+'/devices/'+str(self.info[chat_ID]['edit_patient_data']['rem_device']['device_id']),json=self.catalog['devices'][device_id])
					self.bot.sendMessage(chat_ID,text='The device has been removed successfully')
					self.bot.sendMessage(chat_ID,text='Please select an option',reply_markup=mainMenuDoctor)
				return

		elif (step>=300 and step<400): # remove patient
			
			if step==300:
				self.bot_data = self.create_data_file()
				self.bot.sendMessage(chat_ID,text='Are you sure of delete all the data related to the patient with id '+self.info[chat_ID]['edit_patient_data']['patient_id']+' ('+self.bot_data['patient'][self.info[chat_ID]['edit_patient_data']['patient_id']]['surname']+' '+self.bot_data['patient'][self.info[chat_ID]['edit_patient_data']['patient_id']]['name']+') ?')
				self.bot.sendMessage(chat_ID, "Choose an option:", reply_markup=yes_no_del_pat)
				return
			
			elif step==301: # yes delete
												
				# deactivate device
				self.catalog = json.loads(requests.get(self.catalog_url +'/all').text)
				device_list = self.catalog['patients'][self.info[chat_ID]['edit_patient_data']['patient_id']]['devices']
				for device_id in device_list:
					self.catalog['devices'][device_id]['active'] = 0
					requests.put(self.catalog_url+'/devices/'+device_id,json=self.catalog['devices'][device_id])

				# delete patient on the catalog
				requests.delete(self.catalog_url+'/patients/'+self.info[chat_ID]['edit_patient_data']['patient_id'])
				self.bot.sendMessage(chat_ID,text='Patient removed successfully')
				self.bot.sendMessage(chat_ID,text='Please select an option',reply_markup=mainMenuDoctor)

				# update doctor info
				patient_list = self.bot_data['doctor'][self.info[chat_ID]['doctor_id']]['patient_list']
				patient_list.remove(int(self.info[chat_ID]['edit_patient_data']['patient_id']))
				self.update_resource(chat_ID, 'doctors', self.info[chat_ID]['doctor_id'], 'patient_list', patient_list)
				
				return
			
			elif step==302: # no delete
				self.bot.sendMessage(chat_ID,text='Ok, Please select an option',reply_markup=mainMenuDoctor)
				return

		elif (step>=400 and step<500): # see patient data
			
			if step==400:

				self.catalog = json.loads(requests.get(self.catalog_url +'/all').text)
				patient_id = self.info[chat_ID]['edit_patient_data']['patient_id']

				message='Patient '+patient_id+' info: \n'
				message=message+'id: '+ self.catalog['patients'][patient_id]['id'] +'\n'
				message=message+'name: ' + self.catalog['patients'][patient_id]['name'] +'\n'
				message=message+'surname: '+ self.catalog['patients'][patient_id]['surname'] +'\n'
				message=message+'devices:'
				for dev_id in list(map(int,self.catalog['patients'][patient_id]['devices'])):
					message=message+'\n    '+str(dev_id)+' - '+self.catalog['devices'][str(dev_id)]['IP']+' - '+self.catalog['devices'][str(dev_id)]['location']+' - '+self.catalog['devices'][str(dev_id)]['type']
				self.bot_data = self.create_data_file()
				message=message+'\naccess code: '+self.bot_data['patient'][patient_id]['access_code']
				message=message+'\npassword: '+self.bot_data['patient'][patient_id]['password']

				self.bot.sendMessage(chat_ID,text=message)
				return

	def addPatient(self,chat_ID,step):
		if step==0:
			self.new_patient_info[chat_ID]={
				"data":{
		            "name": "",
		            "surname": "",
		            "id": "",
		            "TS_params": {
		                "health": {
		                    "ChannelID": "",
		                    "ChannelWriteAPIkey": "",
		                    "ChannelReadAPIKey": "",
		                    "fields": {}
		                },
		                "home": {
		                    "ChannelID": "",
		                    "ChannelWriteAPIkey": "",
		                    "ChannelReadAPIKey": "",
		                    "fields": {}
		                }
		            },
		            "devices": [],
		            "last_update": time.time(),
		            "access_code":"",
		        	"password":""
		        }
		    }
			self.bot.sendMessage(chat_ID, text="Please insert the patient's name")
			self.info[chat_ID]['state']="register_patient_name"
			return

		elif step==1:
			self.bot.sendMessage(chat_ID, text="Please insert the patient's surname")
			self.info[chat_ID]['state']="register_patient_surname"
			return

		elif step==2:
			self.bot.sendMessage(chat_ID, text="Please insert the patient's access code")
			self.info[chat_ID]['state']="register_patient_access_code"
			return

		elif step==3:
			self.bot.sendMessage(chat_ID, text="Please insert the patient's password")
			self.info[chat_ID]['state']="register_patient_password"
			return

		elif step==4:
			message = "A new patient profile with:\n"
			message = message + '  name: '+self.new_patient_info[chat_ID]['data']['name']+'\n'
			message = message + '  surname: '+self.new_patient_info[chat_ID]['data']['surname']+'\n'
			message = message + '  access code: '+self.new_patient_info[chat_ID]['data']['access_code']+'\n'
			message = message + '  password: '+self.new_patient_info[chat_ID]['data']['password']+'\n'
			message = message + 'will be created.\nis everything correct?'
			self.bot.sendMessage(chat_ID, text=message, reply_markup=yes_no_new_patient)
			return

		elif step==5:

			data = self.create_data_file()

			patients_data=data["patient"]
			acc_code_list=list()
			id_list=list()
			indice=0

			for pat in patients_data.keys():
				acc_code_list.append(patients_data[pat]['access_code'])
				id_list.append(int(patients_data[pat]['patient_id']))

			patient_id=1
			while patient_id in id_list:
				patient_id = patient_id+1
			self.new_patient_info[chat_ID]['data']['id']=str(patient_id)

			if self.new_patient_info[chat_ID]['data']['access_code'] in acc_code_list:
				self.bot.sendMessage(chat_ID, text="sorry, but the access code alreay exists.\nThe patient's registration procedure will start again")
				self.addPatient(chat_ID,0)
				return
			else:
				patient_info={
					"patient_id":self.new_patient_info[chat_ID]['data']['id'],
					"name":self.new_patient_info[chat_ID]['data']['name'],
					"surname":self.new_patient_info[chat_ID]['data']['surname'],
					"access_code":self.new_patient_info[chat_ID]['data']['access_code'],
					"password":self.new_patient_info[chat_ID]['data']['password']}
				data['patient'][str(patient_id)]=patient_info
				data['doctor'][str(self.info[chat_ID]['doctor_id'])]['patient_list'].append(int(self.new_patient_info[chat_ID]['data']['id']))
				self.new_patient_info[chat_ID]['data']['last_update']=time.time()
				requests.post(self.catalog_url +'/patients',json=self.new_patient_info[chat_ID]['data'])
				self.update_resource(chat_ID, 'doctors', self.info[chat_ID]['doctor_id'], 'patient_list', data['doctor'][str(self.info[chat_ID]['doctor_id'])]['patient_list'])
				self.bot.sendMessage(chat_ID, text="registration completed successfully")
			return

		elif step==6:
			self.bot.sendMessage(chat_ID, text="The patient's registration procedure will start again")
			self.addPatient(chat_ID,0)
			return

	def signUp(self,chat_ID,step):
		if step==0:
			self.info[chat_ID]={
				"doctor_id": "",
	            "access_code": "",
	            "surname":"",
	            "name":"",
	            "password": "",
	            "state":"0",
	            "patient_list":[],
	            "statistics_info":{
	            	"field":"",
	            	"start":"",
	            	"end":"",
	            }
			}
			self.bot.sendMessage(chat_ID, text='Please insert the name')
			self.info[chat_ID]['state']="signup_name"
			return

		elif step==1:
			self.bot.sendMessage(chat_ID, text='Please insert the surname')
			self.info[chat_ID]['state']="signup_surname"
			return

		elif step==2:
			self.bot.sendMessage(chat_ID, text='Please insert the access code')
			self.info[chat_ID]['state']="signup_access_code"
			return

		elif step==3:
			self.bot.sendMessage(chat_ID, text='Please insert the password')
			self.info[chat_ID]['state']="signup_password"
			return

		elif step==4:
			message = 'A new profile with:\n'
			message = message + 'name: '+self.info[chat_ID]['name']+'\n'
			message = message + 'surname: '+self.info[chat_ID]['surname']+'\n'
			message = message + 'access code: '+self.info[chat_ID]['access_code']+'\n'
			message = message + 'password: '+self.info[chat_ID]['password']+'\n'
			message = message + 'is everything correct?'
			self.bot.sendMessage(chat_ID, text=message, reply_markup=yes_no_signup)
			return

		elif step==5:
			
			data = self.create_data_file()

			acc_code_list=list()
			id_list=list()

			for doctor in data['doctor'].keys():
				acc_code_list.append(data['doctor'][doctor]['access_code'])
				id_list.append(int(data['doctor'][doctor]['doctor_id']))

			doctor_id=1
			while doctor_id in id_list:
				doctor_id = doctor_id+1

			if self.info[chat_ID]['access_code'] in acc_code_list:
				self.bot.sendMessage(chat_ID, text='Sorry, but the access code alreay exists.\nTry with another access code')
				self.signUp(chat_ID,0)
				return

			else:
				doctor_info={
					"id":str(doctor_id),
					"name":self.info[chat_ID]['name'],
					"surname":self.info[chat_ID]['surname'],
					"access_code":self.info[chat_ID]['access_code'],
					"password":self.info[chat_ID]['password'],
					"patient_list":[]}
				data['doctor'][str(doctor_id)]=doctor_info

				requests.post(self.catalog_url+"/doctors", json=doctor_info)
				
				benvenuto="Registration completed successfully.\n"
				benvenuto=benvenuto+"Welcome "+doctor_info["name"]+" "+doctor_info["surname"]+"."
				self.bot.sendMessage(chat_ID, text=benvenuto)
				self.bot.sendMessage(chat_ID, "Choose an option:", reply_markup=mainMenuDoctor)
				self.info[chat_ID]['state']="0"
				self.info[chat_ID]["doctor_id"] = str(doctor_id)
			return

		elif step==6:
			self.bot.sendMessage(chat_ID, text='The signup procedure will start again')
			self.signUp(chat_ID,0)
			return

	def logIn(self, chat_ID, step):
		if step==0:
			self.info[chat_ID]={
						"doctor_id": "",
			            "access_code": "",
			            "surname":"",
			            "name":"",
			            "password": "",
			            "state":"0",
			            "patient_list":[],
			            "statistics_info":{
			            	"field":"",
			            	"start":"",
			            	"end":"",
			            },
			            "found":False
					}
			self.info[chat_ID]['state']="login_access_code"
			self.bot.sendMessage(chat_ID, text='Please insert the access code')
			return

		elif step==1:
			self.bot.sendMessage(chat_ID, text='Please insert the password')
			self.info[chat_ID]['state']='login_password'
			return

		elif step == 2:
			data = self.create_data_file()
			# access code check
			for doctor_id in data['doctor']:
				if data['doctor'][doctor_id]['access_code']==self.info[chat_ID]['access_code']:
					self.info[chat_ID]["found"]=True
					if data['doctor'][doctor_id]['password']==self.info[chat_ID]['password']:
						self.info[chat_ID]['doctor_id']=data['doctor'][doctor_id]['doctor_id']
						self.info[chat_ID]['surname']=data['doctor'][doctor_id]['surname']
						self.info[chat_ID]['name']=data['doctor'][doctor_id]['name']
						self.info[chat_ID]['patient_list']=data['doctor'][doctor_id]['patient_list']
						self.bot.sendMessage(chat_ID, text='Login successful, please select an option:',reply_markup=mainMenuDoctor)
					else:
						self.bot.sendMessage(chat_ID, text='Error, the password is wrong, try again')
						self.logIn(chat_ID,1)

			if self.info[chat_ID]["found"]==False:
				self.bot.sendMessage(chat_ID, text='Error, the access code is wrong, try again')
				self.logIn(chat_ID,0)
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
	token = '7516687380:AAHItb6UAjK0oZkRLc6v8-Wk8z4yK2CPzjM' # token giusto
	#token = '7797116701:AAFc-fChmj2D3SolKZ207Z6wMdvxvDHGqog' # token di prova
	DoctorBot = MyBot(token)	
	try:
		print("\n____________________________________________________________\n")
		print(f"  Doctor's Bot is running with token: {token}\n")
		print("____________________________________________________________\n")
		print("Press Ctrl+C to stop the server. \n")

		while True:
			time.sleep(0.5)
	
	except KeyboardInterrupt:
		print('Bot stopped')









































