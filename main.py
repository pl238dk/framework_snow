import json
from snow import ServiceNow
from flask import Flask
from flask import request as r
from flask import render_template as rt
from datetime import datetime

app = Flask(__name__)

email = ''
group = ''
companies = [
	'## REDACTED ##',
]
s = ServiceNow()

def set_unassigned_ticket_to_self():
	global s
	global email
	global group
	global companies
	user = s.get_user_by_email(email)
	user_id = user['result'][0]['sys_id']
	##
	## incident
	tickets = s.get_ticket_group_unassigned('incident', group)
	for ticket in tickets['result']:
		if ticket['company']['display_value'].lower() not in companies:
			print(f'[I] Skipping assignment of {ticket["number"]} for {ticket["company"]["display_value"]}')
			continue
		else:
			print(f'[I] Assigning incident {ticket["number"]} for {ticket["company"]["display_value"]}')
			params = {
				'assigned_to': user_id,
				'state': '-1',
			}
			s.set_ticket_value(ticket['number'], params)
	##
	## sc_task
	tickets = s.get_ticket_group_unassigned('sc_task', group)
	for ticket in tickets['result']:
		if ticket['company']['display_value'].lower() not in companies:
			print(f'[I] Skipping assignment of {ticket["number"]} for {ticket["company"]["display_value"]}')
			continue
		else:
			print(f'[I] Assigning sc_task {ticket["number"]} ({ticket["parent"]["display_value"]}) for {ticket["company"]["display_value"]}')
			params = {
				'assigned_to': user_id,
				'state': '-5',
			}
			s.set_ticket_state(ticket['parent']['display_value'], '-5')
			s.set_ticket_value(ticket['number'], params)
	return

def get_tickets_assigned_to_me(table):
	global s
	global group
	global email
	response = s.get_ticket_group_user(table, group, email)
	output = response['result']
	return output

@app.route('/update_ticket', methods=['POST'])
def update_ticket():
	global s
	d = r.form.to_dict()
	number = d.get('number')
	k = d.get('key')
	v = d.get('value')
	params = {
		k: v,
	}
	s.set_ticket_value(number, params)
	return ''

@app.route('/search', methods=['GET','POST'])
def lookup():
	if r.method == 'GET':
		return rt('search.html',ticket='')
	global s
	d = r.form.to_dict()
	input = d.get('number')
	if not input:
		return rt('search.html',ticket='')
	ticket_raw = s.get_ticket(input.upper())
	ticket = ticket_raw['result'][0]
	return rt(
		'search.html',
		ticket=ticket,
	)

@app.route('/')
def landing():
	set_unassigned_ticket_to_self()
	incidents = get_tickets_assigned_to_me('incident')
	sc_tasks = get_tickets_assigned_to_me('sc_task')
	return rt(
		'landing.html',
		incidents=incidents,
		sc_tasks=sc_tasks,
	)

if __name__ == '__main__':
	app.run(
		host='0.0.0.0',
		port=5000,
		debug=True,
	)