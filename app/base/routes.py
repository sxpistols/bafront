# -*- encoding: utf-8 -*-

from flask import Flask,jsonify, render_template, redirect, request, url_for,flash
from flask_login import current_user,login_required, login_user, logout_user
import requests
from datetime import datetime, timedelta
from app import db, login_manager
from app.base import blueprint
from app.base.forms import LoginForm, CreateAccountForm
from app.base.models import User
import random
import string
from app.base.util import verify_pass
from flask import send_file
import os
from flask_mysqldb import MySQL,MySQLdb
import os.path

app = Flask(__name__)
BACKEND='localhost:9966'
@blueprint.route('/')
def route_default():
    return redirect(url_for('base_blueprint.login'))

@blueprint.route('/page_<error>')
def route_errors(error):
    return render_template('errors/page_{}.html'.format(error))

## Login & Registration
@blueprint.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm(request.form)
    if 'login' in request.form:
        
        # read form data
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        print(user, flush=True)
        parpar = {'username' : user, 'desc' : 'login'}
        authpar = {'username' : username, 'password' : password}
        userlog = requests.post('http://'+BACKEND+'/api/karyawan/userlog', params = parpar)

        crestatus = requests.post('http://'+BACKEND+'/api/auth/rlogin', params = authpar)
        crestatus = crestatus.json()

        if crestatus['message'] == 'Success':
            login_user(user)
            return redirect(url_for('base_blueprint.route_default'))

        # Something (user or pass) is not ok
        return render_template( 'login/login.html', msg='Wrong user or password', form=login_form)

    if not current_user.is_authenticated:
        return render_template( 'login/login.html',form=login_form)
        
    if current_user.role == 2 or current_user.role == 6 or current_user.role == 11:
        r = requests.get('http://'+BACKEND+'/api/pmo/ressum')
        a = []
        b = []
        for i in range(len(r.json()['Resource'])):
            a.append(r.json()['Resource'][i]['posisi'])
            b.append(r.json()['Resource'][i]['jumlah'])
            i = i+1

        legend = 'Monthly Data'
        labels = a
        values = b

        r = requests.get('http://'+BACKEND+'/api/pmo/summary?user_role='+str(current_user.role))
        s = requests.get('http://'+BACKEND+'/api/trello/getlastten?user_role='+str(current_user.role))
        pars = { 'user_role', current_user.role }
        r = requests.get('http://'+BACKEND+'/api/karyawan/list?user_role='+str(current_user.role))
        return render_template('/karyawan.html', karyawan=r.json()['karyawan'])

    elif current_user.role != 2 and current_user.role != 5:
        return redirect(url_for('home_blueprint.index'))
    else:
        return redirect(url_for('base_blueprint.emp',user_id=current_user.username))
    
@blueprint.route('/addemp', methods=['GET', 'POST'])
def addemp():
    login_form = LoginForm(request.form)
    if not current_user.is_authenticated or current_user.role == 5 or current_user.role == 3 :
        return redirect(url_for('base_blueprint.login'))
    if request.method == 'GET':
        r = requests.get('http://'+BACKEND+'/api/role')
        return render_template('/addemp.html', role=r.json()['Role'])
    else:
        createdby = current_user.username
        userid = request.form['userid']
        fullname = request.form['fullname']
        email = request.form['email']
        phone = request.form['phone']
        telegram = request.form['telegram']
        nik = request.form['nik']
        identitas = request.form['identitas']
        statuspernikahan = request.form['statuspernikahan']
        divisi = request.form['divisi']
        posisi = request.form['posisi']
        statuskaryawan = request.form['statuskaryawan']
        site = request.form['site']
        tanggalmasuk = request.form['tanggalmasuk']
        alamat = request.form['alamat']
        role = request.form['role']
        tempatlahir = request.form['tempatlahir']
        tanggallahir = request.form['tanggallahir']
        pendidikan = request.form['pendidikan']
        institusi = request.form['institusi']
        nikkaryawan = request.form['nikkaryawan']
        jurusan = request.form['jurusan']
        
        pars = { 'user_id': userid, \
            'fullname': fullname, \
            'statuspernikahan': statuspernikahan, \
            'nik': nik, \
            'identitas': identitas, \
            'divisi': divisi, \
            'tanggalmasuk': tanggalmasuk, \
            'statuskaryawan': statuskaryawan, \
            'email': email, \
            'phone': phone, \
            'alamat': alamat, \
            'posisi': posisi, \
            'site': site, \
            'telegram': telegram, \
            'tempatlahir': tempatlahir, \
            'tanggallahir': tanggallahir, \
            'pendidikan': pendidikan, \
            'institusi': institusi, \
            'nikkaryawan': nikkaryawan, \
            'jurusan': jurusan, \
            'createdby': createdby \
            }

        if 'register' in request.form:
            sampleStr = ''.join((random.choice(string.ascii_letters) for i in range(5)))
            sampleStr += ''.join((random.choice(string.digits) for i in range(3)))
            sampleList = list(sampleStr)
            random.shuffle(sampleList)
            finalString = ''.join(sampleList)
            user = User(username=userid,email=email,password=finalString,role=role)
            db.session.add(user)
            db.session.commit()
            addkaryawan = requests.post('http://'+BACKEND+'/api/karyawan/add', params=pars)

        return redirect(url_for('base_blueprint.karyawan'))

@blueprint.route('/daftarproject', methods=['GET'])
def coba():
    login_form = LoginForm(request.form)
    if not current_user.is_authenticated or current_user.role == 5 or current_user.role == 3  or current_user.role == 4 :
        return redirect(url_for('base_blueprint.login'))
    if request.method == 'GET':
        r = requests.get('http://'+BACKEND+'/api/trello/allboards')
        return render_template('/daftarproject.html', boards=r.json()['Boards'])

@blueprint.route('/create_user', methods=['GET', 'POST'])
def create_user():
    login_form = LoginForm(request.form)
    create_account_form = CreateAccountForm(request.form)
    if 'register' in request.form:
        username  = request.form['username']
        email     = request.form['email'   ]
        user = User.query.filter_by(username=username).first()
        if user:
            return render_template( 'login/register.html', msg='Username already registered', form=create_account_form)
        user = User.query.filter_by(email=email).first()
        if user:
            return render_template( 'login/register.html', msg='Email already registered', form=create_account_form)
        user = User(**request.form)
        db.session.add(user)
        db.session.commit()
        return render_template( 'login/register.html', success='User created please <a href="/login">login</a>', form=create_account_form)
    else:
        return render_template( 'login/register.html', form=create_account_form)

@blueprint.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('base_blueprint.login'))

@login_manager.unauthorized_handler
def unauthorized_handler():
    return render_template('errors/page_403.html'), 403

@blueprint.errorhandler(403)
def access_forbidden(error):
    return render_template('errors/page_403.html'), 403

@blueprint.errorhandler(404)
def not_found_error(error):
    return render_template('errors/page_404.html'), 404

@blueprint.errorhandler(405)
def method_forbidden(error):
    return render_template('errors/page_405.html'), 403

@blueprint.errorhandler(500)
def internal_error(error):
    return render_template('errors/page_500.html'), 500

@blueprint.route('/karyawan',methods=['GET','POST'])
def karyawan():
    login_form = LoginForm(request.form)
    if not current_user.is_authenticated or current_user.role == 5 or current_user.role == 3 :
        return redirect(url_for('base_blueprint.login'))
    pars = { 'user_role', current_user.role }
    r = requests.get('http://'+BACKEND+'/api/karyawan/list?user_role='+str(current_user.role))
    return render_template('/karyawan.html', karyawan=r.json()['karyawan'])

@blueprint.route('/emp/<user_id>')
def emp(user_id):
    login_form = LoginForm(request.form)
    if not current_user.is_authenticated:
        return redirect(url_for('base_blueprint.login'))

    pars = { 'user_id' : user_id }
    r = requests.get('http://'+BACKEND+'/api/karyawan',params=pars)
    return render_template('/emp.html', karyawan=r.json()['karyawan'])

@blueprint.route('/user_detail/<user_id>',methods=['GET','POST'])
def user_detail(user_id):
    login_form = LoginForm(request.form)
    if not current_user.is_authenticated or current_user.role == 5 or current_user.role == 3 :
        return redirect(url_for('base_blueprint.login'))

    if request.method == 'GET':
        pars = { 'user_id' : user_id }
        r = requests.get('http://'+BACKEND+'/api/karyawan',params=pars)
        return render_template('/user_detail.html', karyawan=r.json()['karyawan'])
    else:
        if 'update' in request.form:
            username = request.form['username']
            email = request.form['email']
            fullname = request.form['fullname']
            telegram = request.form['telegram']
            divisi = request.form['divisi']
            posisi = request.form['posisi']
            alamat = request.form['alamat']
            telepon = request.form['telepon']
            tanggalmasuk = request.form['tanggalmasuk']
            statuskaryawan = request.form['statuskaryawan']
            identitas = request.form['identitas']
            statuspernikahan = request.form['statuspernikahan']
            pendidikan = request.form['pendidikan']
            trelloid = request.form['trelloid']
            institusi = request.form['institusi']
            nikkaryawan = request.form['nikkaryawan']
            jurusan = request.form['jurusan']
            resource = request.form['resource']

            pars = { 'username' : username,'email': email,'fullname' : fullname , 'telegram': telegram,'divisi': divisi,'posisi': posisi,'alamat': alamat,'telepon': telepon,'tanggalmasuk': tanggalmasuk, 'statuskaryawan': statuskaryawan, 'identitas': identitas,'statuspernikahan': statuspernikahan, 'pendidikan': pendidikan, 'institusi' : institusi, 'nikkaryawan' : nikkaryawan , 'trelloid': trelloid, 'jurusan': jurusan, 'resource': resource}
            v = requests.post('http://'+BACKEND+'/api/karyawan/update',params=pars)
        if 'resign' in request.form:
            username = request.form['username']
            pars = { 'username' : username }
            v = requests.post('http://'+BACKEND+'/api/karyawan/resign',params=pars)

        pars = { 'user_id' : user_id }
        r = requests.get('http://'+BACKEND+'/api/karyawan',params=pars)
        return render_template('/user_detail.html', karyawan=r.json()['karyawan'])

@blueprint.route('/cuti_delete/<cutiid>',methods=['GET','POST'])
def cuti_delete(cutiid):
    login_form = LoginForm(request.form)
    if not current_user.is_authenticated or current_user.role == 5 or current_user.role == 3 :
        return redirect(url_for('base_blueprint.login'))
    if request.method == 'GET':
        pars = { 'cutiid' : cutiid }
        r = requests.get('http://'+BACKEND+'/api/karyawan/cutidelete',params=pars)
        dev = requests.get('http://'+BACKEND+'/api/karyawan/list')
        if(current_user.role!=6):
            cuti = requests.get('http://'+BACKEND+'/api/karyawan/listcuti')
        else:
            cuti = requests.get('http://'+BACKEND+'/api/karyawan/sdolistcuti')
        return render_template('/daftarkaryawancuti.html', dev=dev.json()['karyawan'], cuti=cuti.json()['Cuti'])
        
@blueprint.route('/dailyactivitybyselected',methods=['GET','POST'])
def dailyactivitybyselected():
    login_form = LoginForm(request.form)
    if not current_user.is_authenticated  or current_user.role == 3  or current_user.role == 1 :
        return redirect(url_for('base_blueprint.login'))
    hariini = str(datetime.today().strftime('%Y-%m-%d-%H:%M:%S'))
    # form = MyForm()
    if request.method == 'GET':
        userid = { 'user_id' : current_user.username }
        pars = { 'user_role' : current_user.role }
        namek = requests.get('http://'+BACKEND+'/api/karyawan/list', params=pars)
        tahun = datetime.today().strftime('%Y')
        bulan = datetime.today().strftime('%b')
        tanggal = datetime.today().strftime('%Y-%m')
        user_role = str(current_user.role)
        return render_template('/pmo/dailyactivitybyselected.html', namak=namek.json()['karyawan'],  valharini=hariini)
    else:
        userid = { 'user_id' : current_user.username }
        karyawan = request.form['karyawan']
        dateassignment = request.form['dateassignment']
        endassignment = request.form['endassignment']
        pars = { 'user_role' : current_user.role }
        namek = requests.get('http://'+BACKEND+'/api/karyawan/list', params=pars)
        pars = { 'karyawan' : karyawan, 'dateassignment' : dateassignment , 'endassignment': endassignment}
        state = requests.get('http://'+BACKEND+'/api/pmo/activityByDate', params=pars)
        return render_template('/pmo/dailyactivitybyselected.html', project=state.json()['Project'],namak=namek.json()['karyawan'])

@blueprint.route('/timesheet',methods=['GET','POST'])
def timesheet():
    login_form = LoginForm(request.form)
    if not (current_user.is_authenticated or current_user.role != 2 or current_user.role != 6):
        return redirect(url_for('base_blueprint.login'))
    if request.method == 'GET':
        tanggal = datetime.today().strftime('%Y-%m')
        bulanB = datetime.today().strftime('%B')
        tahun  = tanggal[0:4]
        pars = { 'tanggal': tanggal, 'user_role' : current_user.role }
        r = requests.get('http://'+BACKEND+'/api/trello/reporttimesheet',params=pars)
        return render_template('/pmo/timesheet.html', proj=r.json()['Report'],bulanB=bulanB, tahunB=tahun)
    else:
        if 'download' in request.form:
            bulan = request.form['bulan']
            bul = datetime.strptime(bulan,'%Y-%m')
            bulanB = bul.strftime('%B')
            bulanb = bul.strftime('%b')
            tahun  = bulan[0:4]
            pars = { 'tanggal': bulan,'user_role' : current_user.role }
            r = requests.get('http://'+BACKEND+'/api/trello/reporttimesheet',params=pars)
            return render_template('/pmo/timesheet.html', proj=r.json()['Report'],bulanB=bulanB, tahunB=tahun)
        if 'idownload' in request.form:
            bulan = request.form['bulan']
            bul = datetime.strptime(bulan,'%Y-%m')
            bulanB = bul.strftime('%B')
            bulanb = bul.strftime('%b')
            tahun  = bulan[0:4]
            return redirect(url_for('base_blueprint.download',bulan=bulanb,tahun=tahun))

        if 'tohrd' in request.form:
            bulan = request.form['bulan']
            bul = datetime.strptime(bulan,'%Y-%m')
            bulanB = bul.strftime('%B')
            bulanb = bul.strftime('%b')
            tahun  = bulan[0:4]
            return redirect(url_for('base_blueprint.downloadhrd',bulan=bulanb,tahun=tahun))

@blueprint.route('/resourceidle',methods=['GET','POST'])
def resourceidle():
    login_form = LoginForm(request.form)
    if not (current_user.is_authenticated or current_user.role != 2 or current_user.role != 6):
        return redirect(url_for('base_blueprint.login'))
    if request.method == 'GET':
        user_role = current_user.role
        r = requests.get('http://'+BACKEND+'/api/pmo/resourceidle')
        return render_template('/pmo/resourceidle.html', proj=r.json()['Resource'])
    else:
        user_role = current_user.role
        if 'show' in request.form:
            tanggal = request.form['tanggal']
            bulanB = datetime.today().strftime('%B')
            pars = { 'tanggal': tanggal }
            r = requests.get('http://'+BACKEND+'/api/pmo/resourceidledaily',params=pars)
            return render_template('/pmo/resourceidle.html', proj=r.json()['Resource'])
        if 'mdownload' in request.form:
            tanggal = request.form['tanggal']
            pars = { 'tanggal': tanggal }
            path = '/home/dolants/baback/ResIdle_'+tanggal+'.xlsx'
            r = requests.get('http://'+BACKEND+'/api/pmo/resourceidledailyD',params=pars)
            return send_file(path, as_attachment=True)

@blueprint.route('/karyawancuti', methods=['GET', 'POST'])
def karyawancuti():
    login_form = LoginForm(request.form)
    if not current_user.is_authenticated or current_user.role == 5 or current_user.role == 3 or current_user.role == 4 :
        return redirect(url_for('base_blueprint.login'))
    if request.method == 'GET':
        dev = requests.get('http://'+BACKEND+'/api/karyawan/list?user_role='+str(current_user.role))
        cuti = requests.get('http://'+BACKEND+'/api/karyawan/listcuti')
        return render_template('/karyawancuti.html', dev=dev.json()['karyawan'], cuti=cuti.json()['Cuti'])
    else:
        createdby = current_user.username
        dev = request.form['dev']
        cuti = requests.get('http://'+BACKEND+'/api/karyawan/listcuti')
        if 'register' in request.form:
            tanggal = request.form['tanggal']
            keterangan = request.form['ket']
            pars = { 'resource_name': dev, 'tanggal' : tanggal, 'keterangan' : keterangan }
            requests.post('http://'+BACKEND+'/api/karyawan/cuti', params=pars)
        return redirect(url_for('base_blueprint.daftarkaryawancuti'))  

@blueprint.route('/addkaryawanresign', methods=['GET', 'POST'])
def addkaryawanresign():
    login_form = LoginForm(request.form)
    if not current_user.is_authenticated or current_user.role == 5 or current_user.role == 3 or current_user.role == 4 :
        return redirect(url_for('base_blueprint.login'))
    if request.method == 'GET':
        dev = requests.get('http://'+BACKEND+'/api/karyawan/list?user_role='+str(current_user.role))
        return render_template('/addkaryawanresign.html', dev=dev.json()['karyawan'])
    else:
        if 'register' in request.form:
            createdby = current_user.username
            karyawan = request.form['karyawan']
            tanggal = request.form['tanggal']
            handover = request.form['handover']
            ket = request.form['ket']
            ket2 = request.form['ket2']
            pars = { 'createdby': createdby, 'karyawan' : karyawan, 'tanggal' : tanggal,'handover': handover,'ket':ket,'ket2':ket2 }
            requests.post('http://'+BACKEND+'/api/karyawan/addresign', params=pars)
        pars = { 'user_role', current_user.role }
        r = requests.get('http://'+BACKEND+'/api/karyawanresign/list?user_role='+str(current_user.role))
        return render_template('/karyawanresign.html', karyawan=r.json()['karyawan'])     

@blueprint.route('/daftarkaryawancuti', methods=['GET', 'POST'])
def daftarkaryawancuti():
    login_form = LoginForm(request.form)
    if not current_user.is_authenticated or current_user.role == 5 or current_user.role == 3 or current_user.role == 4 :
        return redirect(url_for('base_blueprint.login'))
    if request.method == 'GET':
        dev = requests.get('http://'+BACKEND+'/api/karyawan/list')
        cuti = requests.get('http://'+BACKEND+'/api/karyawan/listcuti')
        return render_template('/daftarkaryawancuti.html', dev=dev.json()['karyawan'], cuti=cuti.json()['Cuti'])

@blueprint.route('/downloadl',methods=['GET'])
def downloadl():
    login_form = LoginForm(request.form)
    if not (current_user.is_authenticated or current_user.role != 2 or current_user.role != 6):
        return redirect(url_for('base_blueprint.login'))
    if request.method == 'GET':
        bulan = datetime.today().strftime('%b')
        tahun = datetime.today().strftime('%Y')
        path = '/home/dolants/baback/Timesheet_Karyawan_'+bulan+'_'+tahun+'.xlsx'
        return send_file(path, as_attachment=True)

@blueprint.route('/download',methods=['GET'])
def download():
    login_form = LoginForm(request.form)
    if not (current_user.is_authenticated or current_user.role != 2 or current_user.role != 6):
        return redirect(url_for('base_blueprint.login'))

    if request.method == 'GET':
        bulan = request.args['bulan']
        tahun = request.args['tahun']
        path = '/home/dolants/baback/Timesheet_Karyawan_'+bulan+'_'+tahun+'.xlsx'
        return send_file(path, as_attachment=True)

@blueprint.route('/downloadhrd',methods=['GET'])
def downloadhrd():
    login_form = LoginForm(request.form)
    if not (current_user.is_authenticated or current_user.role != 2 or current_user.role != 6):
        return redirect(url_for('base_blueprint.login'))

    if request.method == 'GET':
        bulan = request.args['bulan']
        tahun = request.args['tahun']
        path = '/home/dolants/baback/Timesheet_HRD_Karyawan_'+bulan+'_'+tahun+'.xlsx'
        return send_file(path, as_attachment=True)