from flask import Flask, flash, render_template, redirect, url_for,request
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm 
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
from flask_sqlalchemy  import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from keras.models import Model,load_model
import pandas as pd
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer,WordNetLemmatizer
import pickle
from keras.preprocessing.sequence import pad_sequences
import tensorflow as tf
import keras
from keras import backend as K


swdf = pd.read_csv("swearwords.csv")



stemmer = PorterStemmer()
lemmatizer=WordNetLemmatizer()
stop_words=stopwords.words('english')
#print(stop_words)
K.clear_session()
model = keras.models.load_model('/home/kunal/Desktop/building_user_login_system-master/finish/promo.h5')
model._make_predict_function()
#graph = tf.get_default_graph()


model1 = keras.models.load_model('/home/kunal/Desktop/play/building_user_login_system-master/finish/aggressive.h5')
model1._make_predict_function()



def process_inputp(i):
    lemma_list=[]
    i=i.lower()
    j=nltk.word_tokenize(i)
    words = [word for word in j if word.isalpha()]
    #token_list.append(words)
    lemmas=[lemmatizer.lemmatize(word) for word in words]
    lemmas=[stemmer.stem(word) for word in words]
        
    lemma_list.append(lemmas)
    with open('/home/kunal/Desktop/building_user_login_system-master/finish/promotoken.pickle', 'rb') as handle:
        tokenizer = pickle.load(handle)
    print(lemma_list)
    list_tokenized_train = tokenizer.texts_to_sequences(lemma_list)
    print(list_tokenized_train)
    X_tr = pad_sequences(list_tokenized_train ,maxlen=500,padding='post', truncating='post')
    return X_tr




def process_inputag(i):
    lemma_list=[]
    i=i.lower()
    j=nltk.word_tokenize(i)
    words = [word for word in j if word.isalpha()]
    #token_list.append(words)
    lemmas=[lemmatizer.lemmatize(word) for word in words]
    lemmas=[stemmer.stem(word) for word in words]
        
    lemma_list.append(lemmas)
    with open('/home/kunal/Desktop/play/building_user_login_system-master/finish/aggressive.pickle', 'rb') as handle:

        tokenizer = pickle.load(handle)
    print(lemma_list)
    list_tokenized_train = tokenizer.texts_to_sequences(lemma_list)
    print(list_tokenized_train)
    X_tr = pad_sequences(list_tokenized_train ,maxlen=100,padding='post', truncating='post')
    return X_tr





#input process function 


app = Flask(__name__)
app.config['SECRET_KEY'] = 'Thisissupposedtobesecret!'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////home/kunal/Desktop/building_user_login_system-master/finish/database.db'
bootstrap = Bootstrap(app)
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class LoginForm(FlaskForm):
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('remember me')

class RegisterForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])

#upar ka chhedna nahi hai

abusive=dict()
abusivefinal=dict()
promotional=dict()
promotionalfinal=dict()
aggressive=dict()
aggressivefinal=dict()
tcounts=dict()
flag=0


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/abu', methods = ['POST', 'GET'])
def abu():

	query=request.form['query']
	username=request.form['user']
	flag=0
	k=query.split(' ')

	if username in tcounts:
		tcounts[username]+=1
	else:
		tcounts[username]=1
	for l in k:
		for m in swdf['SLANGS']:
			if(m.lower()==l.lower()):
				flag=1
				if username in abusive:
					abusive[username]+=1
				else:
					abusive[username]=1


	if(flag==1):
		actual="Abusive"
	else:
		actual="Not Abusive"
	

	for z in tcounts.keys():
	    if z in abusive.keys():
	    
	        flag2 = ((abusive[z]/tcounts[z])*100)
	        abusivefinal[z]=flag2
	    else:
	    	abusivefinal[z]=0

	return render_template('index.html',output=actual)

@app.route('/promo', methods = ['POST', 'GET'])
def promo():

	query=request.form['query']
	username=request.form['user']
	
	if username in tcounts:
	    tcounts[username]+=1
	else:
	    tcounts[username]=1
	
	

	print(query)
	x_tr = process_inputp(query)
	print("Here1")
	print(x_tr)
	
	#print(x_tr.shape())

	y_tr=[[1]]
	#x_tr=x_tr.reshape(500,1,1)
	#global graph
	#with graph.as_default():
	outputs = model.predict(x_tr)
	
	outputs=outputs.reshape(1,1,1)	
	print(outputs)
	print("Here3")
	print(type(x_tr))
	print(type(y_tr))
	#preds = model.evaluate(x_tr,y_tr)
	newpreds=model.predict(x_tr)
	print("Kunal")
	print(newpreds)
	kunal=newpreds[0][0]
	if(kunal>=0.5):
		actual="Promotional"
		flag=1
	else:
		actual="Not Promotional"
		flag=0
	
	if flag==1:
	    if username in promotional:
	        promotional[username]+=1
	    else:
	        promotional[username]=1
	        
	for z in tcounts.keys():
	    if z in promotional.keys():
	    
	        flag2 = ((promotional[z]/tcounts[z])*100)
	        promotionalfinal[z]=flag2
	    else:
	    	promotionalfinal[z]=0  

	return render_template('index.html',output=actual)
	


@app.route('/all', methods = ['POST', 'GET'])
def all():

	query=request.form['query']
	username=request.form['user']
	
	if username in tcounts:
	    tcounts[username]+=1
	else:
	    tcounts[username]=1
	
	

	print(query)
	x_tr = process_inputag(query)
	print("Here1")
	print(x_tr)
	
	#print(x_tr.shape())

	y_tr=[[1]]
	#x_tr=x_tr.reshape(500,1,1)
	#global graph
	#with graph.as_default():
	outputs = model1.predict(x_tr)
	
	outputs=outputs.reshape(1,1,1)	
	print(outputs)
	print("Here3")
	print(type(x_tr))
	print(type(y_tr))
	#preds = model1.evaluate(x_tr,y_tr)
	newpreds=model1.predict(x_tr)
	print("Kunal")
	print(newpreds)
	kunal=newpreds[0][0]
	if(kunal>=0.5):
		actual="Aggressive"
		flag=1
		if username in aggressive:
			aggressive[username]+=1
		else:
			aggressive[username]=1
	else:
		actual="Not aggressive"
		flag=0
	        
	for z in tcounts.keys():
	    if z in aggressive.keys():
	    
	        flag2 = ((aggressive[z]/tcounts[z])*100)
	        aggressivefinal[z]=flag2
	    else:
	    	aggressivefinal[z]=0  

	print(query)
	x_tr = process_inputp(query)
	print("Here1")
	print(x_tr)
	
	#print(x_tr.shape())

	y_tr=[[1]]
	#x_tr=x_tr.reshape(500,1,1)
	#global graph
	#with graph.as_default():
	outputs = model.predict(x_tr)
	
	outputs=outputs.reshape(1,1,1)	
	print(outputs)
	print("Here3")
	print(type(x_tr))
	print(type(y_tr))
	#preds = model.evaluate(x_tr,y_tr)
	newpreds=model.predict(x_tr)
	print("Kunal")
	print(newpreds)
	kunal=newpreds[0][0]
	flag=0
	if(kunal>=0.5):
		actual+="\nPromotional"
		flag=1
	else:
		actual+="\nNon-Promotional"
		flag=0
	
	if flag==1:
	    if username in promotional:
	        promotional[username]+=1
	    else:
	        promotional[username]=1

	for z in tcounts.keys():
	    if z in promotional.keys():
	        flag2 = ((promotional[z]/tcounts[z])*100)
	        promotionalfinal[z]=flag2
	    else:
	    	promotionalfinal[z]=0	          

	flag=0
	k=query.split(' ')

	for l in k:
		for m in swdf['SLANGS']:
			if(m.lower()==l.lower()):
				flag=1


	if(flag==1):
		actual+="\nAbusive"
		if username in abusive:
			abusive[username]+=1
		else:
			abusive[username]=1
	else:
		actual+="\nNot-Abusive"

	for z in tcounts.keys():
	    if z in abusive.keys():
	        flag2 = ((abusive[z]/tcounts[z])*100)
	        abusivefinal[z]=flag2
	    else:
	    	abusivefinal[z]=0

	return render_template('index.html',output=actual)



@app.route('/agg', methods = ['POST', 'GET'])
def agg():

	query=request.form['query']
	username=request.form['user']
	
	if username in tcounts:
	    tcounts[username]+=1
	else:
	    tcounts[username]=1
	
	

	print(query)
	x_tr = process_inputag(query)
	print("Here1")
	print(x_tr)
	
	#print(x_tr.shape())

	y_tr=[[1]]
	#x_tr=x_tr.reshape(500,1,1)
	#global graph
	#with graph.as_default():
	outputs = model1.predict(x_tr)
	
	outputs=outputs.reshape(1,1,1)	
	print(outputs)
	print("Here3")
	print(type(x_tr))
	print(type(y_tr))
	#preds = model1.evaluate(x_tr,y_tr)
	newpreds=model1.predict(x_tr)
	print("Kunal")
	print(newpreds)
	kunal=newpreds[0][0]
	if(kunal>=0.5):
		actual="Aggressive"
		flag=1
		if username in aggressive:
			aggressive[username]+=1
		else:
			aggressive[username]=1
	else:
		actual="Not-Aggressive"
		flag=0
	        
	for z in tcounts.keys():
	    if z in aggressive.keys():
	    
	        flag2 = ((aggressive[z]/tcounts[z])*100)
	        aggressivefinal[z]=flag2 
	    else:
	    	aggressivefinal[z]=0       

	return render_template('index.html',output=actual)
	
		

@app.route('/analytics', methods = ['POST', 'GET'])
def analytics():

	popup=["Promotional : "+str(promotionalfinal),"Abusive :"+ str(abusivefinal),"Aggressive : "+str(aggressivefinal)]
	return render_template('user.html',output=popup)






'''
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                return redirect(url_for('dashboard'))

        return '<h1>Invalid username or password</h1>'
        #return '<h1>' + form.username.data + ' ' + form.password.data + '</h1>'

    return render_template('login.html', form=form)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return '<h1>New user has been created!</h1>'
        #return '<h1>' + form.username.data + ' ' + form.email.data + ' ' + form.password.data + '</h1>'

    return render_template('signup.html', form=form)

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', name=current_user.username)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))
'''


@app.route('/result')
def result():
	return render_template("result.html")


if __name__ == '__main__':
    app.run(debug=True,host="0.0.0.0",port=3590)

