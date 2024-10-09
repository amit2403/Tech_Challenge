from flask_sqlalchemy import SQLAlchemy  
  
db = SQLAlchemy()  
  
class BESSInstallation(db.Model):  
   id = db.Column(db.Integer, primary_key=True)  
   name = db.Column(db.String(100), nullable=False)  
   location = db.Column(db.String(100), nullable=False)  
   status = db.Column(db.String(100), nullable=False)  
  
   def __repr__(self):  
      return f"BESSInstallation('{self.name}', '{self.location}', '{self.status}')"  
  
class BESSStatus(db.Model):  
   id = db.Column(db.Integer, primary_key=True)  
   installation_id = db.Column(db.Integer, db.ForeignKey('bess_installation.id'), nullable=False)  
   installation = db.relationship('BESSInstallation', backref=db.backref('statuses', lazy=True))  
   voltage = db.Column(db.Float, nullable=False)  
   current = db.Column(db.Float, nullable=False)  
   temperature = db.Column(db.Float, nullable=False)  
   state_of_charge = db.Column(db.Float, nullable=False)  
   timestamp = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())  
  
   def __repr__(self):  
      return f"BESSStatus('{self.installation_id}', '{self.voltage}', '{self.current}', '{self.temperature}', '{self.state_of_charge}')"  
  
class BESSAlert(db.Model):  
   id = db.Column(db.Integer, primary_key=True)  
   installation_id = db.Column(db.Integer, db.ForeignKey('bess_installation.id'), nullable=False)  
   installation = db.relationship('BESSInstallation', backref=db.backref('alerts', lazy=True))  
   timestamp = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())  
   message = db.Column(db.String(200), nullable=False)  
  
   def __repr__(self):  
      return f"BESSAlert('{self.installation_id}', '{self.timestamp}', '{self.message}')"
