from . import main
from .. import login_manager, db
from flask_login import login_user, logout_user, login_required, current_user, fresh_login_required
from flask import redirect, flash, render_template, url_for, request
from .models import User, Role, Room, Type, Use, Request, State, Permission
from .forms import LoginForm, CreateAccountForm, EditAccountForm, CreateRoomForm, EditRoomForm, CreateUseForm, CreateRequestForm
from .decorators import root_required, permission_required
from datetime import date, timedelta
from sqlalchemy import not_

@main.route('/')
def index():
    #[ 1 if x in a else 0 for x in range(1, 7)]
    return redirect(url_for('main.index2', offset=10000))

@main.route('/<int:offset>')
def index2(offset):
    today = date.today()
    today += timedelta(days=offset-10000)
    rooms = Room.query.order_by(Room.name.desc()).all()
    for room in rooms:
        uses = Use.query.filter_by(room=room, date=today).all()
        room.seg = [0]*6
        for use in uses:
            room.seg[use.seg-1] = 1
    return render_template('index.html', left=offset-1, right=offset+1, today=today.isoformat(), Type=Type, rooms=rooms)

@main.route('/approve', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.APPROVE)
def approve():
    requests = Request.query.filter(Request.state==0, Request.date>date.today()).order_by(Request.date).all()
    #use = Use.query.filter_by(room=room, seg=form.select.data, date=form.date.data).first()
    return render_template('approve.html', requests=requests, State=State)

@main.route('/approve_disagree/<int:id>', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.APPROVE)
def approve_disagree(id):
    request = Request.query.get_or_404(id)
    request.state = 2
    request.approval_id = current_user.id
    db.session.add(request)
    db.session.commit()
    flash('You have disagreed with an application.')
    return redirect(url_for('main.approve'))

@main.route('/approve_agree/<int:id>', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.APPROVE)
def approve_agree(id):
    request = Request.query.get_or_404(id)
    use = Use.query.filter_by(room=request.room, seg=request.seg, date=request.date).first()
    if use is None:
        request.state = 1
        request.approval_id = current_user.id
        db.session.add(request)
        use = Use(room=request.room, seg=request.seg, date=request.date, reason=request.reason)
        db.session.add(use)
        db.session.commit()
        flash('You have agreed with an application.')
        return redirect(url_for('main.approve'))
    flash('Already In Use.')
    return redirect(url_for('main.approve'))

@main.route('/request', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.REQUEST)
def request():
    requests = Request.query.filter_by(user=current_user).order_by(Request.date.desc()).all()
    return render_template('request.html', requests=requests, State=State)

@main.route('/delete_request/<int:id>', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.REQUEST)
def delete_request(id):
    request = Request.query.get_or_404(id)
    db.session.delete(request)
    db.session.commit()
    flash('A piece of request has been deleted.')
    return redirect(url_for('main.request'))

@main.route('/create_request/<int:id>', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.REQUEST)
def create_request(id):
    room = Room.query.get_or_404(id)
    form = CreateRequestForm()
    form.room.data = room.name
    if form.validate_on_submit():
        use = Use.query.filter_by(room=room, seg=form.select.data, date=form.date.data).first()
        if use is None:
            req = Request(user=current_user, room=room, seg=form.select.data, date=form.date.data, reason=form.reason.data)
            db.session.add(req)
            db.session.commit()
            flash('A piece of request has been added.')
            return redirect(url_for('main.request'))
        flash('Already in use.')
    return render_template('create_request.html', form=form)

@main.route('/account', methods=['GET', 'POST'])
@login_required
@root_required
def account():
    users = User.query.filter(not_(User.acc_num==current_user.acc_num)).all()
    return render_template('account.html', users=users)

@main.route('/edit_account/<int:id>', methods=['GET', 'POST'])
@login_required
@root_required
def edit_account(id):
    user = User.query.get_or_404(id)
    form = EditAccountForm()
    form.acc_num.data = user.acc_num
    form.name.data = user.name
    form.password.data = user.password
    form.select.data = 'User'
    if form.validate_on_submit():
        user.acc_num = form.acc_num.data
        user.name = form.name.data
        user.password = form.password.data
        user.role = Role.query.filter_by(actor=form.select.data).first()
        db.session.add(user)
        db.session.commit()
        flash('Account has been updated.')
        return redirect(url_for('main.account'))
    return render_template('edit_account.html', form=form)

@main.route('/delete_account/<int:id>', methods=['GET', 'POST'])
@login_required
@root_required
def delete_account(id):
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    flash('Account has been deleted.')
    return redirect(url_for('main.account'))

@main.route('/create_account', methods=['GET', 'POST'])
@login_required
@root_required
def create_account():
    form = CreateAccountForm()
    form.select.data = 'User'

    if form.validate_on_submit():
        user = User.query.filter_by(acc_num=form.acc_num.data).first()
        role = Role.query.filter_by(actor=form.select.data).first()
        if user is None and role is not None:
            user = User(acc_num=form.acc_num.data, name=form.name.data, password=form.password.data, role=role)
            db.session.add(user)
            db.session.commit()
            flash('An account has been created.')
            return redirect(url_for('main.create_account'))

    return render_template('create_account.html', form=form)

@main.route('/edit_room/<int:id>', methods=['GET', 'POST'])
@login_required
@root_required
def edit_room(id):
    room = Room.query.get_or_404(id)
    form = EditRoomForm()
    form.name.data = room.name
    form.floor.data = room.floor
    form.select.data = str(room.tpe)
    form.num.data = room.num
    if form.validate_on_submit():
        room.name = form.name.data
        room.floor = int(form.floor.data)
        room.tpe = int(form.select.data)
        room.num = int(form.num.data)
        db.session.add(room)
        db.session.commit()
        flash('Rooom has been updated.')
        return redirect(url_for('main.room'))
    return render_template('edit_room.html', form=form)

@main.route('/room', methods=['GET', 'POST'])
@login_required
@root_required
def room():
    rooms = Room.query.order_by(Room.name.desc()).all()
    return render_template('room.html', rooms=rooms, Type=Type)

@main.route('/create_room', methods=['GET', 'POST'])
@login_required
@root_required
def create_room():
    form = CreateRoomForm()
    form.select.data = '1'
    if form.validate_on_submit():
        room = Room.query.filter_by(name=form.name.data).first()
        if room is None:
            room = Room(name=form.name.data, floor=int(form.floor.data), tpe=int(form.select.data), num=int(form.num.data))
            db.session.add(room)
            db.session.commit()
            flash('A room has been created.')
            return redirect(url_for('main.create_room'))
    return render_template('create_room.html', form=form)

@main.route('/delete_room/<int:id>', methods=['GET', 'POST'])
@login_required
@root_required
def delete_room(id):
    room = Room.query.get_or_404(id)
    db.session.delete(room)
    db.session.commit()
    flash('Room has been deleted.')
    return redirect(url_for('main.room'))

@main.route('/delete_use/<int:id>', methods=['GET', 'POST'])
@login_required
@root_required
def delete_use(id):
    use = Use.query.get_or_404(id)
    db.session.delete(use)
    db.session.commit()
    flash('Use has been deleted.')
    return redirect(url_for('main.use'))

@main.route('/use', methods=['GET', 'POST'])
@login_required
@root_required
def use():
    uses = Use.query.order_by(Use.date.desc()).all()
    return render_template('use.html', uses=uses, Type=Type)

@main.route('/create_use/<int:id>', methods=['GET', 'POST'])
@login_required
@root_required
def create_use(id):
    room = Room.query.get_or_404(id)
    form = CreateUseForm()
    form.room.data = room.name
    if form.validate_on_submit():
        use = Use(room=room, seg=form.select.data, date=form.date.data, reason=form.reason.data)
        db.session.add(use)
        db.session.commit()
        flash('A piece of useage of room has been added.')
        return redirect(url_for('main.room'))
    return render_template('create_use.html', form=form)

@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(acc_num=form.acc_num.data).first()
        if user is not None and user.password == form.password.data:
            login_user(user)
            flash('Login Succeed.')
            return redirect(url_for('main.index'))
        flash('Invalid user account or password.')
    return render_template('login.html', form=form)

@main.route('/logout')
def logout():
    logout_user()
    flash('You have logged out.')
    return redirect(url_for('main.index'))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def to_date(s):
    s = s.split('-')
    return date(int(s[0]), int(s[1]), int(s[2]))