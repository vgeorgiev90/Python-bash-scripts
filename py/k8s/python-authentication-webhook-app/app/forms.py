from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField

class user_reg(Form):
    username = TextField('Username:', validators=[validators.required()])
    password = TextField('Password:', validators=[validators.required(), validators.Length(min=6, max=35)])
    groups = TextField('Groups:', validators=[validators.required(), validators.Length(min=3, max=35)])

class user_del(Form):
    username = TextField('Username:', validators=[validators.required()])
    password = TextField('Password:', validators=[validators.required(), validators.Length(min=6, max=35)])

class role_create(Form):
    role_file = TextField('Your Kubernetes Role Here...', validators=[validators.required(), validators.Length(min=6, max=10000)])

class rolebind_create(Form):
    rolebind_file = TextField('Your Kubernetes Role Here...', validators=[validators.required(), validators.Length(min=6, max=10000)])

class role_delete(Form):
    role_name = TextField('Your Kubernetes Role Here...', validators=[validators.required(), validators.Length(min=6, max=20)])

class rolebind_delete(Form):
    rolebind_name = TextField('Your Kubernetes RoleBind Here...', validators=[validators.required(), validators.Length(min=6, max=20)])


