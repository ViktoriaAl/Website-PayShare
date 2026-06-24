from flask import Flask, request, redirect, make_response, render_template
from database import User, SessionToken, db_session
from login_user import get_user_by_token
from creating_groups import (
    create_group, 
    add_participant, 
    remove_participant, 
    is_user_in_group, 
    get_user_groups, 
    get_group_by_id, 
    get_group_members,
    select_payer,
    set_payer_by_name,
    add_payment
)

from login_user import register as register_user
from login_user import creating_verification

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

    success, result = register_user(db_session, name, email, password)
    # if success:
    #     # response = make_response(redirect('/login'))
    #     # # token = result
    #     # # response.set_cookie('session_token', token, max_age=86400, httponly=True)
    #     # return response

    # else:
    return render_template('register.html', success=success, message=result, name=name, email=email)
    
@app.route('/verify/<token>')
def verify(token):
    from login_user import verify_user_email
    success, result = verify_user_email(db_session, token)
    return render_template('verify_result.html', success=success, message=result)

        
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "GET":
        return render_template('login.html', error=None)
    
    email = request.form['email']
    password = request.form['password']

    from login_user import login as login_user
    success, result = login_user(db_session, email, password)
    # if success is None:
    #     return render_template('login.html', error="Ваш email не был подтвержден", email=None)

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


def render_group_page(user, group_id, **extra):
    group = get_group_by_id(db_session, group_id)
    members = get_group_members(db_session, group_id)
    payer_name = group.current_payer.name if group.current_payer else None

    context = dict(
        user=user,
        group=group,
        members=members,
        number_of_members=len(members),
        payer=payer_name,
        add_error=None,
        add_success=None,
        remove_error=None,
        remove_success=None
    )

    context.update(extra)
    return render_template('group_detail.html', **context)


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
    
    return render_group_page(user, group_id)


    
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

    if success:
        return render_group_page(user, group_id, add_success=message)
    return render_group_page(user, group_id, add_error=message)

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
    # group = 

    if success:
        return render_group_page(user, group_id, remove_success=message)
    return render_group_page(user, group_id, remove_error=message)

@app.route('/choose_participant/<int:group_id>', methods=['GET', 'POST'])
def choose_participant(group_id):
    user = get_current_user_from_request()
    if not user:
        return redirect('/login')

    participant_name = request.form.get('participant_name') if request.method == 'POST' else None

    if participant_name:
        set_payer_by_name(db_session, group_id, participant_name)
    else:
        select_payer(db_session, group_id)

    return render_group_page(user, group_id)

@app.route('/add_payment', methods=['POST'])
def add_payment_route():
    user = get_current_user_from_request()
    if not user:
        return redirect('/login')
    
    group_id = int(request.form.get('group_id'))
    payment_raw = request.form.get('payment')

    try:
        amount = float(payment_raw)
    except (TypeError, ValueError):
        amount = None
    
    if amount is not None:
        add_payment(db_session, group_id, amount)
    
        group = get_group_by_id(db_session, group_id)
        group.current_payer = None

        db_session.commit()

    members = get_group_members(db_session, group_id)
    return render_template("group_detail.html", user=user,
            group=group,
            members=members,
            number_of_members=len(members),
            add_error=None,
            add_success=None,
            remove_error=None,
            remove_success=None)
    


if __name__ == '__main__':
    app.run(debug=True, port=5000)




