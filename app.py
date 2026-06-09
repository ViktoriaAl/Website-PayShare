from flask import Flask, request, redirect, make_response, render_template
from database import User, SessionToken, db_session
from login_user import get_user_by_token
from creating_groups import create_group, add_participant, remove_participant, is_user_in_group, get_user_groups, get_group_by_id, get_group_members

from datetime import datetime
import secrets

app = Flask(__name__)

def get_current_user_from_request():
    token = request.cookies.get('session_token')
    if not token:
        return None
    return get_user_by_token(db_session, token)


@app.route("/")
def index():
    user = get_current_user_from_request()
    if user:
        groups = get_user_groups(db_session, user.user_id)
        return render_template('index.html', user=user, groups=groups)
    # else:
    #     groups = []
        
    # return render_template('index.html', user=user, groups=groups)
    return redirect('/login')
    

@app.route('/register', methods=['GET', 'POST'])
def register_page():
    if request.method == "GET":
        return render_template('register.html', error=None)
    
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']

    from login_user import register as register_user
    success, result = register_user(db_session, name, email, password)
    if success:
        response = make_response(redirect('/'))

        token = result
        response.set_cookie('session_token', token, max_age=86400, httponly=True)
        return response
    else:
        return render_template('register.html', error=result, name=name, email=email)
        
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "GET":
        return render_template('login.html', error=None)
    
    email = request.form['email']
    password = request.form['password']

    from login_user import login as login_user
    success, result = login_user(db_session, email, password)
    if success:
        response = make_response(redirect('/'))

        token = result
        response.set_cookie('session_token', token, max_age=86400, httponly=True)
        return response
    else:
        return render_template('login.html', error=result, email=email)
        
@app.route('/logout')
def logout():
    token = request.cookies.get('session_token')
    if token:
        from login_user import logout as logout_func
        logout_func(db_session, token)
    
    response = make_response(redirect('/'))
    response.set_cookie('session_token', '', max_age=0)
    return response

@app.route('/create_group_by_user', methods=['GET', 'POST'])
def create_group_by_user():
    user = get_current_user_from_request()
    if not user:
        return redirect('/login')
    
    if request.method == 'GET':
        return render_template('create_group.html', error=None, success=None)
    
    group_name = request.form['group_name']
    success, result = create_group(db_session, user.user_id, group_name)
    if success:
        return render_template('create_group.html', error=None, success=f"Группа {group_name} успешно создана")
    return render_template('create_group.html', error=result, success=None)

@app.route('/group/<int:group_id>')
def group_page(group_id):
    user = get_current_user_from_request()
    if not user:
        return redirect('/login')
    
    group = get_group_by_id(db_session, group_id)
    if group is None:
        return "Группа не найдена", 404
    
    if not is_user_in_group(db_session, group_id, user.user_id):
        return "У вас нет доступа к этой группе", 403
    
    members = get_group_members(db_session, group_id)

    
    return render_template('group_detail.html',
                           user=user,
                           group=group,
                           members=members,
                           number_of_members=len(members),
                           add_error=None,
                           add_success=None,
                           remove_error=None,
                           remove_success=None)
    
@app.route('/add_participant', methods=['POST'])
def add_member():
    user = get_current_user_from_request()
    if not user:
        return redirect('/login')
    
    group_id = int(request.form.get('group_id'))
    participant_email = request.form.get('participant_email')
    if not participant_email:
        return redirect(f'/group/{group_id}')
    success, message = add_participant(db_session, user.user_id, participant_email, group_id)

    group = get_group_by_id(db_session, group_id)
    members = get_group_members(db_session, group_id)

    if success:
        return render_template('group_detail.html',
                           user=user,
                           group=group,
                           members=members,
                           number_of_members=len(members),
                           add_error=None,
                           add_success=message,
                           remove_error=None,
                           remove_success=None)
    
    return render_template('group_detail.html',
                           user=user,
                           group=group,
                           members=members,
                           number_of_members=len(members),
                           add_error=message,
                           add_success=None,
                           remove_error=None,
                           remove_success=None)

@app.route('/remove_participant', methods=['POST'])
def remove_member():
    user = get_current_user_from_request()
    if not user:
        return redirect('/login')
    
    group_id = int(request.form.get('group_id'))
    participant_email = request.form.get('participant_email')
    if not participant_email:
        return redirect(f'/group/{group_id}')
    success, message = remove_participant(db_session, user.user_id, participant_email, group_id)

    group = get_group_by_id(db_session, group_id)
    members = get_group_members(db_session, group_id)

    if success:
        return render_template('group_detail.html',
                           user=user,
                           group=group,
                           members=members,
                           add_error=None,
                           add_success=None,
                           remove_error=None,
                           remove_success=message)
    
    return render_template('group_detail.html',
                           user=user,
                           group=group,
                           members=members,
                           add_error=None,
                           add_success=None,
                           remove_error=message,
                           remove_success=None)

if __name__ == '__main__':
    app.run(debug=True, port=5000)




