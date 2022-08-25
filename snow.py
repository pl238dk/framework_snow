import json
import requests
requests.packages.urllib3.disable_warnings()
import time

def timestamp(method):
	def wrapper(*args, **kwargs):
		ts = time.time()
		result = method(*args, **kwargs)
		te = time.time()
		time_result = int((te-ts) * 1000)
		message = (
			f'[I] '
			f'{method.__qualname__}'
			f' took '
			f'{time_result}'
			f'ms to complete, or ~'
			f'{time_result//60000}'
			'm, or ~'
			f'{time_result//1000}'
			f's'
		)
		print(message)
		return result
	return wrapper

class ServiceNow(object):
	def __init__(self, domain):
		self.load_credentials()
		self.session = requests.Session()
		self.base_url = f'https://{domain}.service-now.com'
		self.lookup = {}
		return
	
	def load_credentials(self):
		'''
			keys = ['username','password']
		'''
		try:
			open('configuration.json','r')
		except:
			print('[E] Credentials not found')
		
		with open('configuration.json','r') as f:
			file_raw = f.read()
		credentials = json.loads(file_raw)
		self.un = credentials['credentials']['username']
		self.pw = credentials['credentials']['password']
		return
	
	def get(self, path, params):
		url = f'{self.base_url}/{path}'
		auth = (self.un,self.pw)
		response = self.session.get(
			url,
			params=params,
			auth=auth,
			verify=False,
		)
		output = {
			'success': False,
			'result': response.text,
			'response': response,
		}
		if response.status_code == 200:
			output['success'] = True
			try:
				response_json = json.loads(
					response.text
				)
				output['result'] = response_json['result']
			except:
				pass
		return output
	
	def get_table(self, table, params={}):
		path = '/api/now/table'
		url = f'{path}/{table}'
		output = self.get(url, params=params)
		return output
	
	def get_table_query(self, table, query='', limit=10):
		params = {
			'sysparm_query': query,
			'sysparm_display_value': 'true',
			'sysparm_limit': limit,
		}
		output = self.get_table(
			table,
			params=params,
		)
		return output
	
	def get_assignment_group(self, group_name):
		if group_name in self.lookup:
			return self.lookup[group_name]
		table = 'sys_user_group'
		query = (
			f'name={group_name}'
		)
		output = self.get_table_query(
			table,
			query=query,
			limit=1,
		)
		self.lookup[group_name] = output
		return output
	
	def get_user_by_email(self, email):
		if email in self.lookup:
			return self.lookup[email]
		table = 'sys_user'
		query = (
			f'email={email}'
		)
		output = self.get_table_query(
			table,
			query=query,
			limit=1,
		)
		self.lookup[email] = output
		return output
	
	def get_ticket_group_unassigned(self, table, group_name):
		group = self.get_assignment_group(group_name)
		group_id = group['result'][0]['sys_id']
		query = (
			f'active=true^'
			f'assignment_group={group_id}^'
			f'assigned_toISEMPTY^'
		)
		output = self.get_table_query(
			table,
			query=query,
			limit=30,
		)
		return output
	
	def get_ticket_group_user(self, table, group_name, email):
		#table = self.get_table_of_ticket(ticket_type)
		group = self.get_assignment_group(group_name)
		group_id = group['result'][0]['sys_id']
		user = self.get_user_by_email(email)
		user_id = user['result'][0]['sys_id']
		query = (
			f'active=true^'
			f'assignment_group={group_id}^'
			f'assigned_to={user_id}^'
		)
		output = self.get_table_query(
			table,
			query=query,
			limit=30,
		)
		return output
	
	def get_ticket(self, ticket):
		table = self.get_table_of_ticket(ticket)
		query = (
			f'number={ticket}^'
		)
		output = self.get_table_query(
			table,
			query=query,
			limit=1,
		)
		return output
	
	def put(self, path, body):
		url = f'{self.base_url}{path}'
		auth = (self.un,self.pw)
		header = {
			'Content-type': 'application/json',
		}
		response = self.session.put(
			url,
			headers=header,
			json=body,
			auth=auth,
			verify=False,
		)
		output = {
			'success': False,
			'result': response.text,
			'response': response,
		}
		if response.status_code == 200:
			output['success'] = True
			try:
				response_json = json.loads(
					response.text
				)
				output['result'] = response_json['result']
			except:
				pass
		return output
	
	def get_table_of_ticket(self, ticket):
		if ticket.startswith('INC'):
			table = 'incident'
		elif ticket.startswith('TASK'):
			table = 'sc_task'
		elif ticket.startswith('CHG'):
			table = 'change_request'
		elif ticket.startswith('PRB'):
			table = 'problem'
		elif ticket.startswith('RITM'):
			table = 'sc_req_item'
		elif ticket.startswith('CTASK'):
			table = 'change_task'
		else:
			# why not
			table = 'incident'
		return table
	
	def set_ticket_value(self, ticket, params):
		table = self.get_table_of_ticket(ticket)
		t = self.get_ticket(ticket)
		ticket_id = t['result'][0]['sys_id']
		path = f'/api/now/table/{table}/{ticket_id}'
		output = self.put(path, params)
		return output
	
	def set_ticket_state(self, ticket, state):
		table = self.get_table_of_ticket(ticket)
		t = self.get_ticket(ticket)
		ticket_id = t['result'][0]['sys_id']
		path = f'/api/now/table/{table}/{ticket_id}'
		body = {
			'state': state,
		}
		output = self.put(path, body)
		return output
	
	def set_ticket_assigned_to(self, ticket, email):
		table = self.get_table_of_ticket(ticket)
		user = self.get_user_by_email(email)
		user_id = user['result'][0]['sys_id']
		t = self.get_ticket(ticket)
		ticket_id = t['result'][0]['sys_id']
		path = f'/api/now/table/{table}/{ticket_id}'
		body = {
			'assigned_to': user_id,
		}
		output = self.put(path, body)
		return output
	
	def _():
		return

'''
p = {
	'sysparm_query': (
		f'active=true^'
		f'assignment_group={group_id}^'
		f'assigned_toISEMPTY^'
		f'state!=6^'
	),
	'sysparm_limit':'50',
	'sysparm_display_value' : 'true',
}
'''
if __name__ == '__main__':
	s = ServiceNow()
	#t = s.get_ticket_group_user('incident','Networking','')
	
	
	#sc_item_option_mtom
	#sc_item_option
	print('[I] End')