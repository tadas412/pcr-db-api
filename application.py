#!flask/bin/python
from flask import Flask, jsonify, request
from flaskext.mysql import MySQL

# AWS RDS pcr-db
db_params = {
	'user' : USER
	'passwd' : PWD
	'host' : HOST
	'db' : DB
}


application = Flask(__name__)
mysql = MySQL()
application.config['MYSQL_DATABASE_USER'] = db_params['user']
application.config['MYSQL_DATABASE_PASSWORD'] = db_params['passwd']
application.config['MYSQL_DATABASE_DB'] = db_params['db']
application.config['MYSQL_DATABASE_HOST'] = db_params['host']
mysql.init_app(application)

@application.route('/')
def index():
    return 'Root page of PCR API.'

'''
	/get
			[pennkey=]
			([limit=])
		-->
			{ 'status' : 'success',
			  'courses' : trie of courses
			}
			OR
			{ 'status' : 'failure',
			  'msg' : [error message]	
			}
'''
@application.route('/register_courses/courses/get', methods=['GET'])
def pull_classes():
	if not 'pennkey' in request.args:
		return jsonify({"status" : "failure", "msg" : "No pennkey found"})
	if ('limit' in request.args and len(request.args) != 2) or len(request.args) != 1:
		return jsonify({"status" : "failure", "msg" : "Expected pennkey param + optional limit param"})

	pennkey = request.args['pennkey']
	limit = -1
	if 'limit' in request.args:
		limit = request.args['limit']

	cnx = mysql.connect()
	cursor = cnx.cursor()
	query = ("SELECT subject_code, course_code, section_code FROM register_courses "
	    	 "WHERE pennkey = %s")
	if limit != -1:
		query = query + " LIMIT " + str(limit)
	cursor.execute(query, (pennkey,))

	try:
		classes = dict()
		for (subject_code, course_code, section_code) in cursor:
			if subject_code not in classes:
				classes[subject_code] = dict()
			if course_code not in classes[subject_code]:
				classes[subject_code][course_code] = []
			classes[subject_code][course_code].append(section_code)
	except:
		return jsonify({"status" : "failure", "msg" : "Error pulling"})
	cursor.close()
	cnx.close()

	return jsonify({"status" : "success", "classes" : classes})

'''
	/put
			[pennkey=]
			[subject_code=]
			[course_code=]
			[section_code=]
		-->
			{ 'status' : 'success'}
			OR
			{ 'status' : 'failure',
			  'msg' : [error message]	
			}
'''
@application.route('/register_courses/courses/put', methods=['GET'])
def put_class():
	if not all (key in request.args for key in ('pennkey', 'subject_code', 'course_code', 'section_code')):
		return jsonify({"status" : "failure", "msg" : "Expected exactly: pennkey, subject_code, course_code, section_code"})

	cnx = mysql.connect()
	cursor = cnx.cursor()
	query = ("INSERT INTO register_courses (pennkey, subject_code, course_code, section_code) "
			 "VALUE(%s, %s, %s, %s)")
	cursor.execute(query, (request.args['pennkey'],request.args['subject_code'],request.args['course_code'],
					request.args['section_code']))
	# TODO should probably add error checking
	cnx.commit()
	cursor.close()
	cnx.close()

	return jsonify({"status" : "success"})

''' TODO whole thing
	/remove - note: if item didn't exist, returns success
			[pennkey=]
			[subject_code=]
			[course_code=]
			[section_code=]
			{ 'status' : 'success'}
			OR
			{ 'status' : 'failure',
			  'msg' : [error message]	
			}
'''
@application.route('/register_courses/courses/remove', methods=['GET'])
def remove_class():
	if not all (key in request.args for key in ('pennkey', 'subject_code', 'course_code', 'section_code')):
		return jsonify({"status" : "failure", "msg" : "Expected exactly: pennkey, subject_code, course_code, section_code"})

	cnx = mysql.connect()
	cursor = cnx.cursor()
	query = ("DELETE FROM register_courses WHERE "
			 "pennkey=%s AND "
			 "subject_code=%s AND "
			 "course_code=%s AND "
			 "section_code=%s")
	cursor.execute(query, (request.args['pennkey'],request.args['subject_code'],request.args['course_code'],
					request.args['section_code']))
	# TODO should probably add error checking
	cnx.commit()
	cursor.close()
	cnx.close()

	return jsonify({"status" : "success"})

if __name__ == '__main__':
    application.run(debug=True)