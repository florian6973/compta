from logging import NullHandler
import peewee as pw
from playhouse.sqlite_ext import SqliteExtDatabase, JSONField

db = SqliteExtDatabase(None)

class BaseModel(pw.Model):
    class Meta:
        database = db

class Account(BaseModel):
    name_account = pw.CharField(default="")
    number_account = pw.IntegerField(unique=True)

class Operation(BaseModel):
    date_operation = pw.DateField()
    name_operation = pw.CharField()
    com_operation = pw.CharField(default="") # ex : amortissement, taux, délai de paiement...

class Line(BaseModel):    
    account_line = pw.ForeignKeyField(Account, backref='lines')
    debit_line = pw.IntegerField()
    sum_line = pw.FloatField()
    operation_line = pw.ForeignKeyField(Operation, backref='lines')

# class LinkOp(BaseModel):
#     op_linkop = pw.ForeignKeyField(Operation, backref='operations')
#     line_linkop = pw.ForeignKeyField(Line, backref='lines')
    

