# -*- encoding: utf-8 -*-
"""
License: MIT
Copyright (c) 2019 - present AppSeed.us
"""

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
app.config['MYSQL_HOST'] = '192.168.3.250'
app.config['MYSQL_USER'] = 'employee'
app.config['MYSQL_PASSWORD'] = 'Syabian247#'
app.config['MYSQL_DB'] = 'employee'
mysqlX = MySQL(app) 
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

        # print(username, flush=True)
        # print(password, flush=True)

        # Locate user
        user = User.query.filter_by(username=username).first()
        print(user, flush=True)
        parpar = {'username' : user, 'desc' : 'login'}
        authpar = {'username' : username, 'password' : password}
        userlog = requests.post('http://'+BACKEND+'/api/karyawan/userlog', params = parpar)

        crestatus = requests.post('http://'+BACKEND+'/api/auth/rlogin', params = authpar)
        crestatus = crestatus.json()

        # print('crestatus', flush = True)
        # print(crestatus['message'], flush = True)
        # Check the password
        # if user and verify_pass( password, user.password):
        if crestatus['message'] == 'Success':
            login_user(user)
            return redirect(url_for('base_blueprint.route_default'))

        # Something (user or pass) is not ok
        return render_template( 'login/login.html', msg='Wrong user or password', form=login_form)

    if not current_user.is_authenticated:
        return render_template( 'login/login.html',form=login_form)
        
    if current_user.role == 2 or current_user.role == 6 or current_user.role == 11:
        # return redirect(url_for('home_blueprint.pmo.index'))

        r = requests.get('http://'+BACKEND+'/api/pmo/ressum')
        a = []
        b = []
        for i in range(len(r.json()['Resource'])):
            #print(len(r.json()['Resource']),flush=True)
            #print(r.json()['Resource'][i]['posisi'], flush=True)
            a.append(r.json()['Resource'][i]['posisi'])
            b.append(r.json()['Resource'][i]['jumlah'])
            i = i+1

        legend = 'Monthly Data'
        labels = a
        values = b
        # labels = ["January", "February", "March", "April", "May", "June", "July", "August"]
        # values = [10, 9, 8, 7, 6, 4, 7, 8]

        r = requests.get('http://'+BACKEND+'/api/pmo/summary?user_role='+str(current_user.role))
        s = requests.get('http://'+BACKEND+'/api/trello/getlastten?user_role='+str(current_user.role))
        #return render_template('/pmo/index.html', lastten=s.json()['LastTen'],summary = r.json()['Summary'], values=values, labels=labels, legend=legend)
        #return render_template('/pmo/index.html', lastten=s.json()['LastTen'], values=values, labels=labels, legend=legend)
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
        # requests.post('http://'+BACKEND+'/api/karyawan/add', params=pars)


        if 'register' in request.form:
            sampleStr = ''.join((random.choice(string.ascii_letters) for i in range(5)))
            sampleStr += ''.join((random.choice(string.digits) for i in range(3)))
                    # Convert string to list and shuffle it to mix letters and digits
            sampleList = list(sampleStr)
            random.shuffle(sampleList)
            finalString = ''.join(sampleList)

            user = User(username=userid,email=email,password=finalString,role=role)
            #print(finalString,flush=True)
            db.session.add(user)
            db.session.commit()

            addkaryawan = requests.post('http://'+BACKEND+'/api/karyawan/add', params=pars)
            #print(addkaryawan.url, flush=True)

            #parmail = { 'user_id': userid, 'password': finalString, 'fullname': fullname, 'email': email}
            #addkaryawan = requests.post('http://'+BACKEND+'/api/karyawan/mailreg', params=parmail)


        return redirect(url_for('base_blueprint.karyawan'))

@blueprint.route('/addclientpmo', methods=['GET', 'POST'])
def addclientpmo():
    login_form = LoginForm(request.form)
    if not current_user.is_authenticated or current_user.role == 5 or current_user.role == 3  or current_user.role == 4 :
        return redirect(url_for('base_blueprint.login'))

    if request.method == 'GET':
        return render_template('/addclientpmo.html')
    else:
        createdby = current_user.username
        nama = request.form['nama']
        alamat = request.form['alamat']

        pars = { 'createdby': createdby, \
            'nama': nama, \
            'alamat': alamat \
            }
        # requests.post('http://'+BACKEND+'/api/karyawan/add', params=pars)


        if 'register' in request.form:
            
            addclient = requests.post('http://'+BACKEND+'/api/pmo/addclient', params=pars)

        return redirect(url_for('base_blueprint.pmoclient'))


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

        # else we can create the user
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

@blueprint.route('/shutdown')
def shutdown():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
    return 'Server shutting down...'

## Errors

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

@blueprint.route('/kresign',methods=['GET','POST'])
def kresign():

    login_form = LoginForm(request.form)
    if not current_user.is_authenticated or current_user.role == 5 or current_user.role == 3 :
        return redirect(url_for('base_blueprint.login'))

    pars = { 'user_role', current_user.role }
    r = requests.get('http://'+BACKEND+'/api/karyawanresign/list?user_role='+str(current_user.role))
    
    return render_template('/karyawanresign.html', karyawan=r.json()['karyawan'])



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
        print('KESINI NIH', flush=True)

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

@blueprint.route('/project_m_detail/<project_id>',methods=['GET','POST'])
def project_m_detail(project_id):

    login_form = LoginForm(request.form)
    if not current_user.is_authenticated or current_user.role == 5 or current_user.role == 3 :
        return redirect(url_for('base_blueprint.login'))

    if request.method == 'GET':
        
        pars = { 'project_id' : project_id }
        r = requests.get('http://'+BACKEND+'/api/trello/projectmdetail',params=pars)

        return render_template('/pmo/project_m_detail.html', proj=r.json()['Project'])

    else:
        print('KESINI NIH', flush=True)
        board = request.form['board']

        if 'update' in request.form:
            board = request.form['board']
            startd = request.form['startd']
            endd = request.form['endd']
            mandays = request.form['mandays']
            nilai = request.form['nilai']
            noproject = request.form['noproject']
            namaproject = request.form['namaproject']
            no_po = request.form['no_po']
            nama_po = request.form['nama_po']
            invoice1 = request.form['invoice1']
            invoice2 = request.form['invoice2']
            project_type = request.form['project_type']
            status = request.form['status']
            
            pars = { 'board': board, 'startd':startd, 'endd': endd, 'mandays': mandays, 'nilai': nilai, 'status':status,'no_po' : no_po, 'nama_po' : nama_po, 'project_type' : project_type, 'noproject':noproject,'namaproject':namaproject,'invoice1':invoice1,'invoice2':invoice2 }

            print(pars, flush=True)

            #print(pars, flush=True)
            v = requests.post('http://'+BACKEND+'/api/trello/pmndaysupdate',params=pars)

        # if 'resign' in request.form:
        #     username = request.form['username']
        #     pars = { 'username' : username }

        #     v = requests.post('http://'+BACKEND+'/api/karyawan/resign',params=pars)



        pars = { 'project_id' : board }
        r = requests.get('http://'+BACKEND+'/api/trello/projectmdetail',params=pars)

        return render_template('/pmo/project_m_detail.html', proj=r.json()['Project'])


@blueprint.route('/pmoclient',methods=['GET'])
def pmoclient():
    login_form = LoginForm(request.form)
    if not current_user.is_authenticated or current_user.role != 2:
        return redirect(url_for('base_blueprint.login'))


    r = requests.get('http://'+BACKEND+'/api/pmo/client')
    # print(r.json()['Assignment'],flush=True)

    # return {'OK' : 'Robot'}
    return render_template('/pmoclient.html', client=r.json()['Client'])



        
@blueprint.route('/dailyactivitybyselected',methods=['GET','POST'])
def dailyactivitybyselected():

    login_form = LoginForm(request.form)
    if not current_user.is_authenticated  or current_user.role == 3  or current_user.role == 1 :
        return redirect(url_for('base_blueprint.login'))

    hariini = str(datetime.today().strftime('%Y-%m-%d-%H:%M:%S'))
    # form = MyForm()
    if request.method == 'GET':
       
        userid = { 'user_id' : current_user.username }

        # print(current_user,flush=True)
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
            #print('KESINI ',flush=True)
            bulan = request.form['bulan']
            #print(bulan, flush=True)

            bul = datetime.strptime(bulan,'%Y-%m')
            bulanB = bul.strftime('%B')
            bulanb = bul.strftime('%b')
            tahun  = bulan[0:4]

            pars = { 'tanggal': bulan,'user_role' : current_user.role }
            r = requests.get('http://'+BACKEND+'/api/trello/reporttimesheet',params=pars)
         

            return render_template('/pmo/timesheet.html', proj=r.json()['Report'],bulanB=bulanB, tahunB=tahun)
        if 'idownload' in request.form:

            bulan = request.form['bulan']
            #print(bulan, flush=True)

            bul = datetime.strptime(bulan,'%Y-%m')
            bulanB = bul.strftime('%B')
            bulanb = bul.strftime('%b')
            tahun  = bulan[0:4]
            return redirect(url_for('base_blueprint.download',bulan=bulanb,tahun=tahun))

        if 'tohrd' in request.form:

            bulan = request.form['bulan']
            #print(bulan, flush=True)

            bul = datetime.strptime(bulan,'%Y-%m')
            bulanB = bul.strftime('%B')
            bulanb = bul.strftime('%b')
            tahun  = bulan[0:4]
            return redirect(url_for('base_blueprint.downloadhrd',bulan=bulanb,tahun=tahun))


@blueprint.route('/board_detail/<boardid>', methods=['GET','POST'])
def board_detail(boardid):
    

    login_form = LoginForm(request.form)
    if not current_user.is_authenticated or current_user.role == 5 or current_user.role == 3 :

        return redirect(url_for('base_blueprint.login'))

    if request.method == 'GET':
        tanggal = datetime.today().strftime('%Y-%m-%d')

        pars = { 'boardid' : boardid, 'tanggal' : tanggal }
        bd = { 'boardid' : boardid }
        r = requests.get('http://'+BACKEND+'/api/trello/boarddetail', params=pars)
        s = requests.get('http://'+BACKEND+'/api/trello/boardmembersmandays', params=pars)
        b = requests.get('http://'+BACKEND+'/api/trello/boardname', params=bd)


        return render_template('/board_detail.html', boardname=b.json()['boardname'], boards=r.json()['Boards'], members=s.json()['Members'])
        
    else:
        if 'sdownload' in request.form:
            #print('Masuk Pak Eko', flush=True)
            tanggal = request.form['tanggal']


            pars = { 'boardid' : boardid, 'tanggal' : tanggal }
            bd = { 'boardid' : boardid }
            r = requests.get('http://'+BACKEND+'/api/trello/boarddetail', params=pars)
            s = requests.get('http://'+BACKEND+'/api/trello/boardmembersmandays',params=pars)
            b = requests.get('http://'+BACKEND+'/api/trello/boardname', params=bd)
            return render_template('/board_detail.html', boardname=b.json()['boardname'], boards=r.json()['Boards'], members=s.json()['Members'])

        if 'ddownload' in request.form:
            #print('Masuk Pak Eko', flush=True)
            tanggal = request.form['tanggal']

            pars = { 'boardid' : boardid, 'tanggal' : tanggal }
            path = '/home/dolants/baback/DailyDetail_'+boardid+'_'+tanggal+'.xlsx'
            r = requests.get('http://'+BACKEND+'/api/trello/boarddetaildaily', params=pars)
            
            return send_file(path, as_attachment=True)

        if 'mdownload' in request.form:
            #print('Masuk Pak Eko', flush=True)
            tanggalx = request.form['tanggal']
            tanggal = tanggalx[0:7]

            pars = { 'boardid' : boardid, 'tanggal' : tanggal }
            path = '/home/dolants/baback/MonthlyDetail_'+boardid+'_'+tanggal+'.xlsx'
            r = requests.get('http://'+BACKEND+'/api/trello/boarddetailmonthly', params=pars)
            
            return send_file(path, as_attachment=True)

@blueprint.route('/resourceactive',methods=['GET','POST'])
def resourceactive():
    login_form = LoginForm(request.form)
    if not (current_user.is_authenticated or current_user.role != 2 or current_user.role != 6):
        return redirect(url_for('base_blueprint.login'))


    if request.method == 'GET':
        tanggal = datetime.today().strftime('%Y-%m-%d')
        # d = datetime.today() - timedelta(days=1)
        # tanggal = d.strftime('%Y-%m-%d')
        bulanB = datetime.today().strftime('%B')
        # bulan = request.form['bulan']
        # if request.form['bulan']:
        #     pars = { 'tanggal':bulan }
        # else:
        pars = { 'tanggal': tanggal, 'role' : current_user.role }

        r = requests.get('http://'+BACKEND+'/api/trello/dailyactivity',params=pars)
        # print(r.json()['Assignment'],flush=True)

        # return {'OK' : 'Robot'}
        return render_template('/pmo/resourceactive.html', tanggal=tanggal,proj=r.json()['Activity'],bulanB=bulanB)
    else:
        if 'show' in request.form:
            tanggal = request.form['tanggal']
            bulanB = datetime.today().strftime('%B')

            pars = { 'tanggal': tanggal, 'role' : current_user.role  }
            r = requests.get('http://'+BACKEND+'/api/trello/dailyactivity',params=pars)
         

            return render_template('/pmo/resourceactive.html', tanggal=tanggal, proj=r.json()['Activity'],bulanB=bulanB)

        if 'ddownload' in request.form:
            tanggal = request.form['tanggal']

            pars = { 'tanggal' : tanggal }
            path = '/home/dolants/baback/DailyAct_'+tanggal+'.xlsx'
            r = requests.get('http://'+BACKEND+'/api/trello/actdetaildaily', params=pars)
            
            return send_file(path, as_attachment=True)

        if 'mdownload' in request.form:
            tanggalx = request.form['tanggal']
            tanggal = tanggalx[0:7]

            pars = { 'tanggal' : tanggal }
            path = '/home/dolants/baback/MonthlyAct_'+tanggal+'.xlsx'
            r = requests.get('http://'+BACKEND+'/api/trello/actdetailmonthly', params=pars)

@blueprint.route('/monthlyactivity',methods=['GET','POST'])
def monthlyactivity():
    login_form = LoginForm(request.form)
    if not (current_user.is_authenticated or current_user.role != 2 or current_user.role != 6):
        return redirect(url_for('base_blueprint.login'))


    if request.method == 'GET':
        tahun = datetime.today().strftime('%Y')
        # d = datetime.today() - timedelta(days=1)
        # tanggal = d.strftime('%Y-%m-%d')
        bulanB = datetime.today().strftime('%B')
        # bulan = request.form['bulan']
        # if request.form['bulan']:
        #     pars = { 'tanggal':bulan }
        # else:
        pars = { 'tahun': tahun,'user_role' : current_user.role }

        r = requests.get('http://'+BACKEND+'/api/trello/monthlyactkaryawanlist',params=pars)
        # print(r.json()['Assignment'],flush=True)

        # return {'OK' : 'Robot'}
        return render_template('/pmo/monthlyactkaryawanlist.html', bulanB=bulanB, proj=r.json()['karyawanlist'])
    else:
        if 'show' in request.form:
            tanggal = request.form['tanggal']
            bulanB = datetime.today().strftime('%B')

            pars = { 'tanggal': tanggal }
            r = requests.get('http://'+BACKEND+'/api/trello/dailyactivity',params=pars)
         

            return render_template('/pmo/resourceactive.html', tanggal=tanggal, proj=r.json()['Activity'],bulanB=bulanB)

        if 'ddownload' in request.form:
            tanggal = request.form['tanggal']

            pars = { 'tanggal' : tanggal }
            path = '/home/dolants/baback/DailyAct_'+tanggal+'.xlsx'
            r = requests.get('http://'+BACKEND+'/api/trello/actdetaildaily', params=pars)
            
            return send_file(path, as_attachment=True)

        if 'mdownload' in request.form:
            tanggalx = request.form['tanggal']
            tanggal = tanggalx[0:7]

            pars = { 'tanggal' : tanggal }
            path = '/home/dolants/baback/MonthlyAct_'+tanggal+'.xlsx'
            r = requests.get('http://'+BACKEND+'/api/trello/actdetailmonthly', params=pars)

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

@blueprint.route('/pmoprojecthist',methods=['GET','POST'])
def pmoprojecthist():
    login_form = LoginForm(request.form)
    if not (current_user.is_authenticated or current_user.role != 2 or current_user.role != 6):
        return redirect(url_for('base_blueprint.login'))


    if request.method == 'GET':
        r = requests.get('http://'+BACKEND+'/api/pmo/projectshist')
        # print(r.json()['Assignment'],flush=True)

        # return {'OK' : 'Robot'}
        return render_template('/pmo/pmoprojecthist.html', proj=r.json()['Project'])
    

@blueprint.route('/addproject', methods=['GET', 'POST'])
def addproject():

    login_form = LoginForm(request.form)
    if not current_user.is_authenticated or current_user.role == 5 or current_user.role == 3 or current_user.role == 4 :
        return redirect(url_for('base_blueprint.login'))

    if request.method == 'GET':
        r = requests.get('http://'+BACKEND+'/api/pmo/client')
        pm = requests.get('http://'+BACKEND+'/api/pmo/listpm')
        sa = requests.get('http://'+BACKEND+'/api/pmo/listsa')
        dev = requests.get('http://'+BACKEND+'/api/pmo/listdev')
        qc = requests.get('http://'+BACKEND+'/api/pmo/listqc')
        tw = requests.get('http://'+BACKEND+'/api/pmo/listtw')
        pa = requests.get('http://'+BACKEND+'/api/pmo/listpa')
        return render_template('/addproject.html', client=r.json()['Client'], pm=pm.json()['PM'],sa=sa.json()['SA'],dev=dev.json()['Dev'],qc=qc.json()['QC'],tw=tw.json()['TW'],pa=pa.json()['PA'])

    else:


        createdby = current_user.username
        dev = request.form.getlist('dev')
        project = request.form['project']
        client = request.form['client']
        po = request.form['po']
        cr = request.form['cr']
        jenispekerjaan = request.form['jenispekerjaan']
        mulai = request.form['mulai']
        selesai = request.form['selesai']
        pm = request.form['pm']
        sa = request.form['sa']
        qc = request.form.getlist('qc')
        tw = request.form.getlist('tw')
        pa = request.form.getlist('pa')

        print(qc, flush=True)
        
        
        # requests.post('http://'+BACKEND+'/api/karyawan/add', params=pars)


        if 'register' in request.form:
            ############ For Developer
            #print(len(dev),flush=True)
            i=0

            while i<len(dev):
                #print(dev[i], flush=True)
                getdev = dev[i],
                pars = { 'createdby': createdby, \
                    'project': project, \
                    'client': client, \
                    'po': po, \
                    'cr': cr, \
                    'jenispekerjaan': jenispekerjaan, \
                    'mulai': mulai, \
                    'selesai': selesai, \
                    'posisi': 'Developer', \
                    'resource_name': getdev[0] \
                    }
                
                #print(pars, flush=True)
                requests.post('http://'+BACKEND+'/api/pmo/project/add', params=pars)
                i += 1
            ###################For QC
            i=0
            while i<len(qc):
                getqc = qc[i],
                pars = { 'createdby': createdby, \
                    'project': project, \
                    'client': client, \
                    'po': po, \
                    'cr': cr, \
                    'jenispekerjaan': jenispekerjaan, \
                    'mulai': mulai, \
                    'selesai': selesai, \
                    'posisi': 'Quality Control', \
                    'resource_name': getqc[0] \
                    }
                
                #print(pars, flush=True)
                requests.post('http://'+BACKEND+'/api/pmo/project/add', params=pars)
                i += 1

            ###################For TW
            i=0
            while i<len(tw):
                gettw = tw[i],
                pars = { 'createdby': createdby, \
                    'project': project, \
                    'client': client, \
                    'po': po, \
                    'cr': cr, \
                    'jenispekerjaan': jenispekerjaan, \
                    'mulai': mulai, \
                    'selesai': selesai, \
                    'posisi': 'Technical Writer', \
                    'resource_name': gettw[0] \
                    }
                
                #print(pars, flush=True)
                requests.post('http://'+BACKEND+'/api/pmo/project/add', params=pars)
                i += 1

            ###################For PM
            pars = { 'createdby': createdby, \
                'project': project, \
                'client': client, \
                'po': po, \
                'cr': cr, \
                'jenispekerjaan': jenispekerjaan, \
                'mulai': mulai, \
                'selesai': selesai, \
                'posisi': 'Project Manager', \
                'resource_name': pm \
                }
            
            #print(pars, flush=True)
            requests.post('http://'+BACKEND+'/api/pmo/project/add', params=pars)

            ###################For SA
            pars = { 'createdby': createdby, \
                'project': project, \
                'client': client, \
                'po': po, \
                'cr': cr, \
                'jenispekerjaan': jenispekerjaan, \
                'mulai': mulai, \
                'selesai': selesai, \
                'posisi': 'System Analyst', \
                'resource_name': sa \
                }
            
            #print(pars, flush=True)
            requests.post('http://'+BACKEND+'/api/pmo/project/add', params=pars)

            ###################For PA
            pars = { 'createdby': createdby, \
                'project': project, \
                'client': client, \
                'po': po, \
                'cr': cr, \
                'jenispekerjaan': jenispekerjaan, \
                'mulai': mulai, \
                'selesai': selesai, \
                'posisi': 'Project Admin', \
                'resource_name': pa \
                }
            
            #print(pars, flush=True)
            requests.post('http://'+BACKEND+'/api/pmo/project/add', params=pars)

        return redirect(url_for('base_blueprint.addproject'))

@blueprint.route('/karyawancuti', methods=['GET', 'POST'])
def karyawancuti():

    login_form = LoginForm(request.form)
    if not current_user.is_authenticated or current_user.role == 5 or current_user.role == 3 or current_user.role == 4 :
        return redirect(url_for('base_blueprint.login'))

    if request.method == 'GET':
        # r = requests.get('http://'+BACKEND+'/api/pmo/client')
        # pm = requests.get('http://'+BACKEND+'/api/pmo/listpm')
        # sa = requests.get('http://'+BACKEND+'/api/pmo/listsa')
        # if(current_user.role!=6):
        #     dev = requests.get('http://'+BACKEND+'/api/karyawan/list')
        # else:
        dev = requests.get('http://'+BACKEND+'/api/karyawan/list?user_role='+str(current_user.role))
            
        cuti = requests.get('http://'+BACKEND+'/api/karyawan/listcuti')
        # qc = requests.get('http://'+BACKEND+'/api/pmo/listqc')
        # tw = requests.get('http://'+BACKEND+'/api/pmo/listtw')
        # pa = requests.get('http://'+BACKEND+'/api/pmo/listpa')
        return render_template('/karyawancuti.html', dev=dev.json()['karyawan'], cuti=cuti.json()['Cuti'])

    else:
        

        createdby = current_user.username

        # dev = requests.get('http://'+BACKEND+'/api/karyawan/list')
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
            
        # cuti = requests.get('http://'+BACKEND+'/api/karyawan/listcuti')
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


@blueprint.route('/karyawanmutasi', methods=['GET', 'POST'])
def karyawanmutasi():

    login_form = LoginForm(request.form)
    if not current_user.is_authenticated or current_user.role == 5 or current_user.role == 3 or current_user.role == 4 :
        return redirect(url_for('base_blueprint.login'))

    if request.method == 'GET':
        # r = requests.get('http://'+BACKEND+'/api/pmo/client')
        # pm = requests.get('http://'+BACKEND+'/api/pmo/listpm')
        # sa = requests.get('http://'+BACKEND+'/api/pmo/listsa')
        # if(current_user.role!=6):
        #     dev = requests.get('http://'+BACKEND+'/api/karyawan/list')
        # else:
        dev = requests.get('http://'+BACKEND+'/api/karyawan/listall')
            
        cuti = requests.get('http://'+BACKEND+'/api/karyawan/listcuti')
        return render_template('/karyawanmutasi.html', dev=dev.json()['karyawan'], cuti=cuti.json()['Cuti'])

    else:

        createdby = current_user.username
        karyawan = request.form['karyawan']
        divisi = request.form['divisi']
        tanggalmutasi = request.form['tanggalmutasi']
        ket = request.form['ket']
        # mutasi = requests.get('http://'+BACKEND+'/api/karyawan/listcuti')

        if 'submit' in request.form:
            pars = { 'karyawan': karyawan, 'divisi' : divisi, 'createdby' : createdby, 'tanggalmutasi':tanggalmutasi, 'ket': ket }

            requests.post('http://'+BACKEND+'/api/karyawan/mutasi', params=pars)

        return redirect(url_for('base_blueprint.daftarkaryawanmutasi'))      

@blueprint.route('/daftarkaryawanmutasi', methods=['GET', 'POST'])
def daftarkaryawanmutasi():

    login_form = LoginForm(request.form)
    if not current_user.is_authenticated or current_user.role == 5 or current_user.role == 3 or current_user.role == 4 :
        return redirect(url_for('base_blueprint.login'))

    
    if request.method == 'GET':
        # r = requests.get('http://'+BACKEND+'/api/pmo/client')
        # pm = requests.get('http://'+BACKEND+'/api/pmo/listpm')
        # sa = requests.get('http://'+BACKEND+'/api/pmo/listsa')
        dev = requests.get('http://'+BACKEND+'/api/karyawan/list')
        if(current_user.role!=6):
            mutasi = requests.get('http://'+BACKEND+'/api/karyawan/listmutasi')
        else:
            mutasi = requests.get('http://'+BACKEND+'/api/karyawan/listmutasi')
        # qc = requests.get('http://'+BACKEND+'/api/pmo/listqc')
        # tw = requests.get('http://'+BACKEND+'/api/pmo/listtw')
        # pa = requests.get('http://'+BACKEND+'/api/pmo/listpa')
        return render_template('/daftarkaryawanmutasi.html', dev=dev.json()['karyawan'], mutasi=mutasi.json()['Mutasi'])

@blueprint.route('/challengelist', methods=['GET', 'POST'])
def challengelist():
    login_form = LoginForm(request.form)
    if not current_user.is_authenticated or current_user.role == 5 or current_user.role == 3 or current_user.role == 4 :
        return redirect(url_for('base_blueprint.login'))

    
    if request.method == 'GET':
        # r = requests.get('http://'+BACKEND+'/api/pmo/client')
        # pm = requests.get('http://'+BACKEND+'/api/pmo/listpm')
        # sa = requests.get('http://'+BACKEND+'/api/pmo/listsa')
        dev = requests.get('http://'+BACKEND+'/api/karyawan/list')
        if(current_user.role!=6):
            challenge = requests.get('http://'+BACKEND+'/api/karyawan/listchallenge')
        else:
            challenge = requests.get('http://'+BACKEND+'/api/karyawan/listchallenge')
        # qc = requests.get('http://'+BACKEND+'/api/pmo/listqc')
        # tw = requests.get('http://'+BACKEND+'/api/pmo/listtw')
        # pa = requests.get('http://'+BACKEND+'/api/pmo/listpa')
        return render_template('/daftarkaryawanchallenge.html', dev=dev.json()['karyawan'], challenge=challenge.json()['Challenge'])

@blueprint.route('/addchallenge', methods=['GET', 'POST'])
def addchallenge():

    login_form = LoginForm(request.form)
    if not current_user.is_authenticated or current_user.role == 5 or current_user.role == 3 or current_user.role == 4 :
        return redirect(url_for('base_blueprint.login'))

    if request.method == 'GET':
        # r = requests.get('http://'+BACKEND+'/api/pmo/client')
        # pm = requests.get('http://'+BACKEND+'/api/pmo/listpm')
        # sa = requests.get('http://'+BACKEND+'/api/pmo/listsa')
        # if(current_user.role!=6):
        #     dev = requests.get('http://'+BACKEND+'/api/karyawan/list')
        # else:
        dev = requests.get('http://'+BACKEND+'/api/karyawan/list?user_role='+str(current_user.role))
            
        # cuti = requests.get('http://'+BACKEND+'/api/karyawan/listcuti')
        return render_template('/addchallenge.html', dev=dev.json()['karyawan'])

    else:

        createdby = current_user.username
        karyawan = request.form['karyawan']
        posisi = request.form['posisi']
        start = request.form['start']
        end = request.form['end']
        # mutasi = requests.get('http://'+BACKEND+'/api/karyawan/listcuti')

        if 'submit' in request.form:
            pars = { 'karyawan': karyawan, 'posisi' : posisi, 'start': start, 'end': end,'createdby' : createdby }

            #print(pars, flush=True)
            requests.post('http://'+BACKEND+'/api/karyawan/addchallenge', params=pars)

        return redirect(url_for('base_blueprint.challengelist'))


@blueprint.route('/karyawancovid', methods=['GET', 'POST'])
def karyawancovid():

    login_form = LoginForm(request.form)
    if not current_user.is_authenticated or current_user.role == 5 or current_user.role == 3 or current_user.role == 4 :
        return redirect(url_for('base_blueprint.login'))

    if request.method == 'GET':
        # r = requests.get('http://'+BACKEND+'/api/pmo/client')
        # pm = requests.get('http://'+BACKEND+'/api/pmo/listpm')
        # sa = requests.get('http://'+BACKEND+'/api/pmo/listsa')
        dev = requests.get('http://'+BACKEND+'/api/karyawan/listucovid')
        # cuti = requests.get('http://'+BACKEND+'/api/karyawan/listcuti')
        # qc = requests.get('http://'+BACKEND+'/api/pmo/listqc')
        # tw = requests.get('http://'+BACKEND+'/api/pmo/listtw')
        # pa = requests.get('http://'+BACKEND+'/api/pmo/listpa')
        return render_template('/karyawancovid.html', dev=dev.json()['karyawan'])

    else:
        

        createdby = current_user.username

        # dev = requests.get('http://'+BACKEND+'/api/karyawan/list')
        dev = request.form.getlist('dev')
        cuti = requests.get('http://'+BACKEND+'/api/karyawan/listcovid')

        # print(qc, flush=True)
        
        
        # requests.post('http://'+BACKEND+'/api/karyawan/add', params=pars)


        if 'register' in request.form:
            ############ For Developer
            # print(len(dev),flush=True)
            # i=0

            # while i<len(dev):
                # print(dev[i], flush=True)
                # getdev = dev[i],
            tanggal = request.form['tanggal']
            keterangan = request.form['ket']
            status = request.form['status']
            pars = { 'resource_name': dev[0], 'tanggal' : tanggal, 'keterangan' : keterangan, 'status': status }
                # print(pars, flush=True)

            requests.post('http://'+BACKEND+'/api/karyawan/covid', params=pars)
                # i += 1
            ###################For QC
            
        # devl = requests.get('http://'+BACKEND+'/api/karyawan/list')

        # return render_template('/daftarkaryawancuti.html', dev=devl.json()['karyawan'], cuti=cuti.json()['Cuti'])  
        return redirect(url_for('base_blueprint.daftarkaryawancovid'))      


@blueprint.route('/daftarkaryawancovid', methods=['GET', 'POST'])
def daftarkaryawancovid():

    login_form = LoginForm(request.form)
    if not current_user.is_authenticated or current_user.role == 5 or current_user.role == 3 or current_user.role == 4 :
        return redirect(url_for('base_blueprint.login'))

    if request.method == 'GET':
        # r = requests.get('http://'+BACKEND+'/api/pmo/client')
        # pm = requests.get('http://'+BACKEND+'/api/pmo/listpm')
        # sa = requests.get('http://'+BACKEND+'/api/pmo/listsa')
        # dev = requests.get('http://'+BACKEND+'/api/karyawan/covid')
        cuti = requests.get('http://'+BACKEND+'/api/karyawan/listcovid')
        # qc = requests.get('http://'+BACKEND+'/api/pmo/listqc')
        # tw = requests.get('http://'+BACKEND+'/api/pmo/listtw')
        # pa = requests.get('http://'+BACKEND+'/api/pmo/listpa')
        return render_template('/daftarkaryawancovid.html', cuti=cuti.json()['Covid'])




@blueprint.route('/project_detail/<id_project>', methods=['GET','POST'])
def project_detail(id_project):
    

    login_form = LoginForm(request.form)
    if not current_user.is_authenticated or current_user.role == 5 or current_user.role == 3 :
        return redirect(url_for('base_blueprint.login'))

    if request.method == 'GET':
        sa = requests.get('http://'+BACKEND+'/api/pmo/listsa')
        dev = requests.get('http://'+BACKEND+'/api/pmo/listdev')
        qc = requests.get('http://'+BACKEND+'/api/pmo/listqc')
        tw = requests.get('http://'+BACKEND+'/api/pmo/listtw')
        pa = requests.get('http://'+BACKEND+'/api/pmo/listpa')

        pars = { 'id_project' : id_project }
        r = requests.get('http://'+BACKEND+'/api/pmo/project',params=pars)
        s = requests.get('http://'+BACKEND+'/api/pmo/project/pm',params=pars)
        t = requests.get('http://'+BACKEND+'/api/pmo/project/sa',params=pars)
        u = requests.get('http://'+BACKEND+'/api/pmo/project/dev',params=pars)
        v = requests.get('http://'+BACKEND+'/api/pmo/project/pa',params=pars)
        w = requests.get('http://'+BACKEND+'/api/pmo/project/qc',params=pars)
        x = requests.get('http://'+BACKEND+'/api/pmo/project/tw',params=pars)

        return render_template('/project_detail.html',pid=id_project, project=r.json()['Project'],pm=s.json()['Project'],sa=t.json()['Project'],dev=u.json()['Project'], \
            pa=v.json()['Project'],qc=w.json()['Project'],tw=x.json()['Project'], \
            sas=sa.json()['SA'],devs=dev.json()['Dev'],qcs=qc.json()['QC'],tws=tw.json()['TW'],pas=pa.json()['PA'])
    else:
        id_project = request.form['id_project']
        createdby = current_user.username
        project = request.form['project']
        client = request.form['client']
        po = request.form['po_name']
        cr = request.form['cr_name']
        jenispekerjaan = request.form['jenis']
        mulai = request.form['mulai']
        selesai = request.form['selesai']
        # pm = request.form['pm']
        
        if 'updateselesai' in request.form:
            selesaix = request.form['upds']

            pars = { 'id_project': id_project, \
                        'selesai': selesaix
                        }
                    
            #print(pars, flush=True)
            requests.post('http://'+BACKEND+'/api/pmo/project/updtgl', params=pars)


        if 'deleteresource' in request.form:
            resource = request.form['deleteresource']

            pars = { 'id_project': id_project, \
                        'resource_name': resource
                        }
                    
            #print(pars, flush=True)
            requests.post('http://'+BACKEND+'/api/pmo/project/delres', params=pars)




        if 'register' in request.form:
            sa = request.form['sa']
            dev = request.form.getlist('dev')
            qc = request.form.getlist('qc')
            tw = request.form.getlist('tw')
            pa = request.form.getlist('pa')
            ############ For Developer
            #print('Jumlah Dev',flush=True)
            #print(len(dev),flush=True)
            #print(dev[0], flush=True)
            #print('Jumlah SA',flush=True)
            #print(len(sa),flush=True)
            #print(sa, flush=True)
            #print('Jumlah QC',flush=True)
            #print(len(qc),flush=True)
            #print(qc, flush=True)
            #print('Jumlah TW',flush=True)
            #print(len(tw),flush=True)
            #print(tw, flush=True)
            i=0
            if len(dev) >= 1 and dev[0] != '':
                while i<len(dev):
                    #print(dev[i], flush=True)
                    getdev = dev[i],
                    pars = { 'createdby': createdby, \
                        'project': project, \
                        'client': client, \
                        'po': po, \
                        'cr': cr, \
                        'jenispekerjaan': jenispekerjaan, \
                        'mulai': mulai, \
                        'selesai': selesai, \
                        'posisi': 'Developer', \
                        'resource_name': getdev[0] \
                        }
                    
                    #print(pars, flush=True)
                    requests.post('http://'+BACKEND+'/api/pmo/project/add', params=pars)
                    i += 1
            ###################For QC
            if len(qc) >= 1 and qc[0] != '':
                i=0
                while i<len(qc):
                    getqc = qc[i],
                    pars = { 'createdby': createdby, \
                        'project': project, \
                        'client': client, \
                        'po': po, \
                        'cr': cr, \
                        'jenispekerjaan': jenispekerjaan, \
                        'mulai': mulai, \
                        'selesai': selesai, \
                        'posisi': 'Quality Control', \
                        'resource_name': getqc[0] \
                        }
                    
                    #print(pars, flush=True)
                    requests.post('http://'+BACKEND+'/api/pmo/project/add', params=pars)
                    i += 1

            ###################For TW
            if len(tw) >= 1 and tw[0] != '':
                i=0
                while i<len(tw):
                    gettw = tw[i],
                    pars = { 'createdby': createdby, \
                        'project': project, \
                        'client': client, \
                        'po': po, \
                        'cr': cr, \
                        'jenispekerjaan': jenispekerjaan, \
                        'mulai': mulai, \
                        'selesai': selesai, \
                        'posisi': 'Technical Writer', \
                        'resource_name': gettw[0] \
                        }
                    
                    #print(pars, flush=True)
                    requests.post('http://'+BACKEND+'/api/pmo/project/add', params=pars)
                    i += 1

            ###################For SA
            if len(sa) > 1 and sa != '':
                pars = { 'createdby': createdby, \
                    'project': project, \
                    'client': client, \
                    'po': po, \
                    'cr': cr, \
                    'jenispekerjaan': jenispekerjaan, \
                    'mulai': mulai, \
                    'selesai': selesai, \
                    'posisi': 'System Analyst', \
                    'resource_name': sa \
                    }
                
                #print(pars, flush=True)
                requests.post('http://'+BACKEND+'/api/pmo/project/add', params=pars)


        sa = requests.get('http://'+BACKEND+'/api/pmo/listsa')
        dev = requests.get('http://'+BACKEND+'/api/pmo/listdev')
        qc = requests.get('http://'+BACKEND+'/api/pmo/listqc')
        tw = requests.get('http://'+BACKEND+'/api/pmo/listtw')
        pa = requests.get('http://'+BACKEND+'/api/pmo/listpa')

        pars = { 'id_project' : id_project }
        r = requests.get('http://'+BACKEND+'/api/pmo/project',params=pars)
        s = requests.get('http://'+BACKEND+'/api/pmo/project/pm',params=pars)
        t = requests.get('http://'+BACKEND+'/api/pmo/project/sa',params=pars)
        u = requests.get('http://'+BACKEND+'/api/pmo/project/dev',params=pars)
        v = requests.get('http://'+BACKEND+'/api/pmo/project/pa',params=pars)
        w = requests.get('http://'+BACKEND+'/api/pmo/project/qc',params=pars)
        x = requests.get('http://'+BACKEND+'/api/pmo/project/tw',params=pars)

        return render_template('/project_detail.html', project=r.json()['Project'],pm=s.json()['Project'],sa=t.json()['Project'],dev=u.json()['Project'], \
            pa=v.json()['Project'],qc=w.json()['Project'],tw=x.json()['Project'], \
            sas=sa.json()['SA'],devs=dev.json()['Dev'],qcs=qc.json()['QC'],tws=tw.json()['TW'],pas=pa.json()['PA'])


####DINAS

@blueprint.route('/adddinas', methods=['GET', 'POST'])
def adddinas():

    login_form = LoginForm(request.form)
    if not current_user.is_authenticated or current_user.role == 5 or current_user.role == 3  or current_user.role == 4 :
        return redirect(url_for('base_blueprint.login'))

    if request.method == 'GET':

        karyawanpmo = requests.get('http://'+BACKEND+'/api/pmo/karyawan')

        return render_template('/adddinas.html',karyawanpmo = karyawanpmo.json()['Karyawan'])
    else:
        createdby = current_user.username
        nama = request.form['nama']
        alamat = request.form['alamat']

        pars = { 'createdby': createdby, \
            'nama': nama, \
            'alamat': alamat \
            }
        # requests.post('http://'+BACKEND+'/api/karyawan/add', params=pars)


        if 'register' in request.form:
            
            addclient = requests.post('http://'+BACKEND+'/api/pmo/addclient', params=pars)

        return redirect(url_for('base_blueprint.pmoclient'))


#### Report
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

#### Report
@blueprint.route('/download',methods=['GET'])
def download():
    login_form = LoginForm(request.form)
    if not (current_user.is_authenticated or current_user.role != 2 or current_user.role != 6):
        return redirect(url_for('base_blueprint.login'))

    if request.method == 'GET':
        bulan = request.args['bulan']
        tahun = request.args['tahun']

        # from dateutil.relativedelta import relativedelta
        # last_month = datetime.now() - relativedelta(months=1)
        # bulan = format(last_month, '%b')
        # tahun = format(last_month, '%Y')
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

        # from dateutil.relativedelta import relativedelta
        # last_month = datetime.now() - relativedelta(months=1)
        # bulan = format(last_month, '%b')
        # tahun = format(last_month, '%Y')
        path = '/home/dolants/baback/Timesheet_HRD_Karyawan_'+bulan+'_'+tahun+'.xlsx'
        return send_file(path, as_attachment=True)

@blueprint.route('/reportbyproject',methods=['GET'])
def reportbyproject():
    login_form = LoginForm(request.form)
    if not (current_user.is_authenticated or current_user.role != 2 or current_user.role != 6):
        return redirect(url_for('base_blueprint.login'))

    if request.method == 'GET':
        bulan = datetime.today().strftime('%b')
        tahun = datetime.today().strftime('%Y')
        path = '/home/dolants/baback/Board_Report_PerProject_'+bulan+'_'+tahun+'.xlsx'
        print(path,flush=True)
        return send_file(path, as_attachment=True)


@blueprint.route('/boarddaily',methods=['GET'])
def boarddaily():
    login_form = LoginForm(request.form)
    if not (current_user.is_authenticated or current_user.role != 2 or current_user.role != 6):
        return redirect(url_for('base_blueprint.login'))

    if request.method == 'GET':
        prii = request.form['dateDefault']
        bulan = datetime.today().strftime('%b')
        tahun = datetime.today().strftime('%Y')
        path = '/home/dolants/baback/Vang_2020.xlsx'
        pas = requests.get('http://'+BACKEND+'/api/trello/boarddaily')
        print('HYIIIIIIIIII , ', flush=True)
        print(prii,flush=True)
        return send_file(path, as_attachment=True)
    
@blueprint.route('/monthly_detail/<trelloid>', methods=['GET','POST'])
def monthly_detail(trelloid):

    login_form = LoginForm(request.form)
    if not current_user.is_authenticated:
        return redirect(url_for('base_blueprint.login'))

    if request.method == 'GET':
        bulanB = datetime.today().strftime('%B')
        bulan = datetime.today().strftime('%Y-%m')
        print(bulan, flush=True)
        pars = { 'trelloid' : trelloid, 'bulan': bulan }
        r = requests.get('http://'+BACKEND+'/api/trello/monthlyact',params=pars)

        return render_template('/pmo/monthly_detail.html', bulanB = bulanB, detail=r.json()['detail'])
    else:
        
        if 'show' in request.form:
            #print('KESINI ',flush=True)
            bulan = request.form['bulan']
            #print(bulan, flush=True)

            bul = datetime.strptime(bulan,'%Y-%m')
            bulanB = bul.strftime('%B')
            bulanb = bul.strftime('%b')
            tahun  = bulan[0:4]

            pars = { 'bulan': bulan, 'trelloid': trelloid }
            r = requests.get('http://'+BACKEND+'/api/trello/monthlyact',params=pars)
         
            return render_template('/pmo/monthly_detail.html', bulanB = bulanB, detail=r.json()['detail'])
        
        if 'idownload' in request.form:

            bulan = request.form['bulan']
            # trelloid = request.form['trelloid']
            #print(bulan, flush=True)
            #print(bulan, flush=True)
            #print(trelloid, flush=True)

            bul = datetime.strptime(bulan,'%Y-%m')
            bulanB = bul.strftime('%B')
            bulanb = bul.strftime('%b')
            tahun  = bulan[0:4]
            pars = { 'bulan': bulan, 'trelloid': trelloid }
            path = '/home/dolants/baback/Monthly_'+trelloid+'_'+bulan+'.xlsx'
            pas = requests.get('http://'+BACKEND+'/api/trello/monthlyact', params=pars)
            #print('HYIIIIIIIIII SUKSES , ', flush=True)
            
            # print('Masuk Pak Eko', flush=True)
            # tanggalx = request.form['tanggal']
            # tanggal = tanggalx[0:7]
            # pars = { 'boardid' : boardid, 'tanggal' : tanggal }
            # path = '/home/dolants/baback/MonthlyDetail_'+boardid+'_'+tanggal+'.xlsx'
            # r = requests.get('http://'+BACKEND+'/api/trello/boarddetailmonthly', params=pars)
            # return render_template('/pmo/monthly_detail.html', bulanB = bulanB, detail=pas.json()['detail'])
            return send_file(path, as_attachment=True)
        
            # 


@blueprint.route('fetchrecords', methods=['GET','POST'])
def fetchrecords():
    # cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method == 'POST':
        querytahun = request.form['querytahun']
        querybulan = request.form['querybulan']
        if querybulan == '':
            # cur.execute("SELECT * FROM karyawan ORDER BY fullname DESC")
            # employeelist = cur.fetchall()
            print('Hell, yeah!', flush=True)
        else:
            search_text = request.form['querybulan']
            #print(search_text, flush=True)
            
            tahun = datetime.today().strftime('%Y')
            user_role = str(current_user.role)
            pars2 = { '2022',  '2021', '2014' }
            return pars2
            # cur.execute("SELECT * FROM karyawan WHERE posisi IN (%s) ORDER BY fullname DESC", [search_text])
            # employeelist = cur.fetchall()  
        return 'OK'
    # return jsonify({'htmlresponse': render_template('response.html', employeelist=employeelist)})
    
@blueprint.route('/assignment_detail/<assignment_id>',methods=['GET','POST'])
def assignment_detail(assignment_id):

    login_form = LoginForm(request.form)
    if not current_user.is_authenticated or current_user.role == 5 or current_user.role == 3 :
        return redirect(url_for('base_blueprint.login'))
    #
    if request.method == 'GET':
        
        pars = { 'assignment_id' : assignment_id }
        r = requests.get('http://'+BACKEND+'/api/karyawan/detailassignment',params=pars)

        return render_template('/pmo/assignment_detail.html', proj=r.json()['Assignment'])

    else:
        print('KESINI NIH', flush=True)
        board = request.form['board']

        if 'update' in request.form:
            assignmentid = request.form['assignmentid']
            startd = request.form['startd']
            endd = request.form['endd']
            typex = request.form['typex']
            status = request.form['status']
            extendd = request.form['extendd']
            crname = request.form['crname']
            
            pars = { 'assignmentid': assignmentid, 'startd':startd, 'endd': endd, 'typex': typex, 'status': status, 'extendd':extendd, 'crname': crname }

            # print(pars, flush=True)

            #print(pars, flush=True)
            v = requests.post('http://'+BACKEND+'/api/karyawan/assignmentupdate',params=pars)

        # if 'resign' in request.form:
        #     username = request.form['username']
        #     pars = { 'username' : username }

        #     v = requests.post('http://'+BACKEND+'/api/karyawan/resign',params=pars)



        pars = { 'assignment_id' : assignment_id }
        r = requests.get('http://'+BACKEND+'/api/karyawan/detailassignment',params=pars)

        return render_template('/pmo/assignment_detail.html', proj=r.json()['Assignment'])

@blueprint.route('/assignment_delete/<assignment_id>',methods=['GET','POST'])
def assignment_delete(assignment_id):

    login_form = LoginForm(request.form)
    if not current_user.is_authenticated or current_user.role == 5 or current_user.role == 3 :
        return redirect(url_for('base_blueprint.login'))

    if request.method == 'GET':
        
        pars = { 'assignment_id' : assignment_id }
        r = requests.get('http://'+BACKEND+'/api/karyawan/assignment_delete',params=pars)

    r = requests.get('http://'+BACKEND+'/api/karyawan/listassignment')
    return render_template('/reportassignment.html', karyawan=r.json()['Assignment'])
    

@blueprint.route('/skills', methods=['GET', 'POST'])
def skills():

    login_form = LoginForm(request.form)
    if not current_user.is_authenticated or current_user.role == 5 or current_user.role == 3 or current_user.role == 4 :
        return redirect(url_for('base_blueprint.login'))

    if request.method == 'GET':
        dev = requests.get('http://'+BACKEND+'/api/karyawan/skills')
            
        return render_template('/skills.html', karyawan=dev.json()['Skills'])

    else:
        

        createdby = current_user.username


        if 'submit' in request.form:
            karyawan = request.form['karyawan']
            skills = request.form['skills']
            createdby = createdby
            pars = { 'karyawan': karyawan, 'skills' : skills, 'createdby': createdby }

            requests.post('http://'+BACKEND+'/api/karyawan/addskills', params=pars)

        return redirect(url_for('base_blueprint.addskill'))


@blueprint.route('/addskill', methods=['GET', 'POST'])
def addskill():

    login_form = LoginForm(request.form)
    if not current_user.is_authenticated or current_user.role == 5 or current_user.role == 3 or current_user.role == 4 :
        return redirect(url_for('base_blueprint.login'))

    if request.method == 'GET':
        dev = requests.get('http://'+BACKEND+'/api/karyawan/list?user_role='+str(current_user.role))
            
        return render_template('/addskills.html', dev=dev.json()['karyawan'])

    else:
        

        createdby = current_user.username

        # dev = requests.get('http://'+BACKEND+'/api/karyawan/list')
        # karyawan = request.form['karyawan']
        # skills = request.form['skills']
        # cuti = requests.get('http://'+BACKEND+'/api/karyawan/listcuti')
        # dev = requests.get('http://'+BACKEND+'/api/karyawan/list?user_role='+str(current_user.role))


        if 'submit' in request.form:
            karyawan = request.form['karyawan']
            skills = request.form['skills']
            createdby = createdby
            pars = { 'karyawan': karyawan, 'skills' : skills, 'createdby': createdby }

            requests.post('http://'+BACKEND+'/api/karyawan/addskills', params=pars)

        return redirect(url_for('base_blueprint.skills'))      

@blueprint.route('/appraisalteam',methods=['GET'])
def appraisalteam():
    login_form = LoginForm(request.form)
    if not current_user.is_authenticated:
        return redirect(url_for('base_blueprint.login'))


    user_id = current_user.username
    
    pars = { 'userid' : user_id }
    r = requests.get('http://'+BACKEND+'/api/pmo/appraisalteam',params=pars)

    return render_template('/pmo/appraisalteam.html', karyawan=r.json()['appraisalteam'])


@blueprint.route('/appraisaldetail/<appraisalid>',methods=['GET','POST'])
def appraisaldetail(appraisalid):

    login_form = LoginForm(request.form)
    if not current_user.is_authenticated or current_user.role == 5 or current_user.role == 3 :
        return redirect(url_for('base_blueprint.login'))



    if request.method == 'GET':
        pars = { 'appraisalid' : appraisalid }
        r = requests.get('http://'+BACKEND+'/api/karyawan/appraisaldetail',params=pars)

        return render_template('/appraisaldetail.html', karyawan=r.json()['Appraisal'])

    else:
        if 'delete' in request.form:
            pars = { 'appraisalid' : appraisalid }

            v = requests.post('http://'+BACKEND+'/api/karyawan/deleteappraisal',params=pars)


        user_id = current_user.username
        pars = { 'userid' : user_id }
        
        r = requests.get('http://'+BACKEND+'/api/pmo/appraisalteam',params=pars)
        
        return render_template('/pmo/appraisalteam.html', karyawan=r.json()['appraisalteam'])

@blueprint.route('/addappraisal/<user_id>',methods=['GET','POST'])
def addappraisal(user_id):

    login_form = LoginForm(request.form)
    if not current_user.is_authenticated or current_user.role == 5 or current_user.role == 3 :
        return redirect(url_for('base_blueprint.login'))

    periode = 'Semester 1 - 2022'

    if request.method == 'GET':
        pars = { 'user_id' : user_id }
        # r = requests.get('http://'+BACKEND+'/api/karyawan',params=pars)

        return render_template('/addappraisal.html', userid = user_id)

    else:
        pm = current_user.username
        userid = user_id
        performance = request.form['performance']
        potential = request.form['potential']
        attitude = request.form['attitude']

        pars = { 'user_id': userid, \
            'performance': performance, \
            'potential': potential, \
            'attitude': attitude, \
            'pm': pm, \
            'periode': periode
            }
        # requests.post('http://'+BACKEND+'/api/karyawan/add', params=pars)


        if 'register' in request.form:
            addkaryawan = requests.post('http://'+BACKEND+'/api/karyawan/addappraisal', params=pars)
            # print('BISA NIH CUY '+performance, flush=True)
            # print('BISA NIH CUY '+potential, flush=True)
            # print('BISA NIH CUY '+attitude, flush=True)
            # print('BISA NIH CUY '+pm, flush=True)
            # print('BISA NIH CUY '+userid, flush=True)
            
        return redirect(url_for('base_blueprint.appraisalteam'))

@blueprint.route('/jadwalappraisal', methods=['GET', 'POST'])
def jadwalappraisal():
    login_form = LoginForm(request.form)
    if not current_user.is_authenticated or current_user.role == 5 or current_user.role == 3  or current_user.role == 4 :
        return redirect(url_for('base_blueprint.login'))

    if request.method == 'GET':
        tahun = '2022'
        return render_template('/jadwalappraisal.html', tahun=tahun)
    else:
        createdby = current_user.username
        nama = request.form['nama']
        alamat = request.form['alamat']

        pars = { 'createdby': createdby, \
            'nama': nama, \
            'alamat': alamat \
            }
        # requests.post('http://'+BACKEND+'/api/karyawan/add', params=pars)


        if 'register' in request.form:
            
            addclient = requests.post('http://'+BACKEND+'/api/pmo/addclient', params=pars)

        return redirect(url_for('base_blueprint.pmoclient'))
