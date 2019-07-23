#!/usr/bin/python

from flask import Flask, request, jsonify, flash, redirect, render_template, session, abort
import json
import base64
import jsonpatch
import yaml
import logs
import mysql
import os
import forms
import k8s_policy
from dotenv import load_dotenv
import sys



APP_ROOT = os.path.join(os.path.dirname(__file__), '..')
dotenv_path = os.path.join(APP_ROOT, '.env')
load_dotenv(dotenv_path)

app = Flask(__name__)
	


@app.route('/auth', methods=['POST'])
def webhook():
     api_request = json.loads(request.get_data())


     ## Setup logging
     LOG_FILE_ONE = "/app/log/auth-webhook-requests.log"
     LOG_FILE_TWO = "/app/log/auth-denied-requests.log"
     logs.setup_logger('log_one', LOG_FILE_ONE)
     logs.setup_logger('log_two', LOG_FILE_TWO)


     provided = api_request['spec']['token']

     con = mysql.mysql_operation(os.getenv('MYSQL_HOST'), int(os.getenv('MYSQL_PORT')), os.getenv('MYSQL_USER'), os.getenv('MYSQL_PASS'), os.getenv('MYSQL_DB'))     

     record = con.check_password(provided)
     con.close()
     if record is None:
	 response = {
                "apiVersion": "authentication.k8s.io/v1beta1",
                "kind": "TokenReview",
                "status": {
                        "authenticated": False
                }
         }
         logs.logger(request.get_data(), 'warning', 'two')


     else:
	 uid = record[0]
	 user = record[1]
	 group = record[2]
	 response = {
                "apiVersion": "authentication.k8s.io/v1beta1",
                "kind": "TokenReview",
                "status": {
                        "authenticated": True,
                        "user": {
                                "username": "%s",
                                "uid": "%s",
                                "groups" : [ "%s", ]
                        }
                 }
         }
	 response['status']['user']['uid'] = str(uid)
	 response['status']['user']['username'] = user
	 response['status']['user']['groups'] = [ group ]


     return jsonify(response)


@app.route('/')
def app_home():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return render_template('index.html')



@app.route('/login', methods=['POST'])
def login():
    con = mysql.mysql_operation(os.getenv('MYSQL_HOST'), int(os.getenv('MYSQL_PORT')), os.getenv('MYSQL_USER'), os.getenv('MYSQL_PASS'), os.getenv('MYSQL_DB'))

    passwd = request.form['password']
    user = request.form['username'] 
    record = con.check_webpassword(passwd)
    con.close()
    if passwd == record[2] and user == record[1]:
        session['logged_in'] = True
        return render_template('index.html')
    else:
        flash("Wrong username or password..")
        return app_home()


@app.route('/user_create', methods=['GET', 'POST'])
def create_k8s_user():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        form = forms.user_reg(request.form)
        #print form.errors
        if request.method == 'POST':
            name=request.form['username']
            password=request.form['password']
            groups=request.form['groups']
    
	    con = mysql.mysql_operation(os.getenv('MYSQL_HOST'), int(os.getenv('MYSQL_PORT')), os.getenv('MYSQL_USER'), os.getenv('MYSQL_PASS'), os.getenv('MYSQL_DB'))
	    con.insert_record(name, password, groups)            
	    con.close()    	    

        if form.validate():
            # Save the comment here.
            flash('Thanks for registration ' + name)
	    return render_template('index.html')
        else:
            flash('Error: All the form fields are required. ')
    
        return render_template('register_k8s.html', form=form)




@app.route('/user_delete', methods=['GET', 'POST'])
def delete_k8s_user():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        form = forms.user_del(request.form)

        con = mysql.mysql_operation(os.getenv('MYSQL_HOST'), int(os.getenv('MYSQL_PORT')), os.getenv('MYSQL_USER'), os.getenv('MYSQL_PASS'), os.getenv('MYSQL_DB'))
	#print form.errors
        if request.method == 'POST':
            name=request.form['username']
            password=request.form['password']

            con.delete_record(name, password)

        if form.validate():
            # Save the comment here.
            flash('Deleted')
            return render_template('index.html')
        else:
            flash('Error: All the form fields are required. ')

        all_users = con.list_all_k8s()
        con.close()

        return render_template('delete_k8s.html', form=form, data=all_users)


@app.route('/roles_create', methods=['GET', 'POST'])
def create_k8s_roles():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        form = forms.role_create(request.form)
        #print form.errors
        if request.method == 'POST':
            role_file=request.form['role_file']
            cluster = k8s_policy.cluster(os.getenv('K8S_CA_CRT_PATH'), os.getenv('K8S_API_ADDRESS'), os.getenv('K8S_ADMIN_TOKEN'))
	    cluster.role_create(role_file)

        if form.validate():
            # Save the comment here.
            flash('Created')
            return render_template('index.html')
        else:
            flash('Error: All the form fields are required. ')
    return render_template('create_role.html', form=form)


@app.route('/roles_delete', methods=['GET', 'POST'])
def delete_k8s_roles():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        form = forms.role_delete(request.form)
        #print form.errors
        if request.method == 'POST':
            role_name=request.form['role_name']
	    cluster = k8s_policy.cluster(os.getenv('K8S_CA_CRT_PATH'), os.getenv('K8S_API_ADDRESS'), os.getenv('K8S_ADMIN_TOKEN'))
            cluster.role_delete(role_name)

        if form.validate():
            # Save the comment here.
            flash('Created')
            return render_template('index.html')
        else:
            flash('Error: All the form fields are required. ')

    cluster = k8s_policy.cluster(os.getenv('K8S_CA_CRT_PATH'), os.getenv('K8S_API_ADDRESS'), os.getenv('K8S_ADMIN_TOKEN'))
    roles = cluster.get_clusterroles()

    return render_template('delete_role.html', form=form, data=roles)



@app.route('/rolebind_create', methods=['GET', 'POST'])
def create_k8s_rolebind():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        form = forms.rolebind_create(request.form)
        #print form.errors
        if request.method == 'POST':
            rolebind_name=request.form['rolebind_name']
	    cluster = k8s_policy.cluster(os.getenv('K8S_CA_CRT_PATH'), os.getenv('K8S_API_ADDRESS'), os.getenv('K8S_ADMIN_TOKEN'))
            cluster.role_binding_create(rolebind_name)

        if form.validate():
            # Save the comment here.
            flash('Created')
            return render_template('index.html')
        else:
            flash('Error: All the form fields are required. ')
    return render_template('create_rolebind.html', form=form)


@app.route('/rolebind_delete', methods=['GET', 'POST'])
def delete_k8s_rolebind():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        form = forms.rolebind_delete(request.form)
        #print form.errors
        if request.method == 'POST':
            rolebind_name=request.form['rolebind_name']
	    cluster = k8s_policy.cluster(os.getenv('K8S_CA_CRT_PATH'), os.getenv('K8S_API_ADDRESS'), os.getenv('K8S_ADMIN_TOKEN'))
            cluster.rolebind_delete(rolebind_name)

        if form.validate():
            # Save the comment here.
            flash('Created')
            return render_template('index.html')
        else:
            flash('Error: All the form fields are required. ')

    cluster = k8s_policy.cluster(os.getenv('K8S_CA_CRT_PATH'), os.getenv('K8S_API_ADDRESS'), os.getenv('K8S_ADMIN_TOKEN'))
    binds = cluster.get_crbindings()

    return render_template('delete_rolebind.html', form=form, data=binds)




try:
    if sys.argv[1] == 'db-init':
        con = mysql.mysql_operation(os.getenv('MYSQL_HOST'), int(os.getenv('MYSQL_PORT')), os.getenv('MYSQL_USER'), os.getenv('MYSQL_PASS'), os.getenv('MYSQL_DB'))
        con.create_tables()
        con.insert_record('auth-admin', os.getenv('K8S_ADMIN_TOKEN'), 'system:masters')
except IndexError:
    ## Start the admission webhook app
    app.secret_key = os.urandom(12)
    app.run(host='0.0.0.0', port=8443, ssl_context=('/app/ssl/tls.crt', '/app/ssl/tls.key'))
