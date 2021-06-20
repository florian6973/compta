from data import *
from datetime import date, datetime


file = input("File?\t") or "base.db"
models = BaseModel.__subclasses__()

db.init(file)
db.create_tables(models)


print(f"Reading {file}...")

space = "    "
def gsp(k):
    s = ""
    for i in range(k):
        s += space
    return s

def get_solde(acc, date_max, date_min=None):
    solde = 0
    for line in acc.lines:
        #print("")
        #print((date_min is None and line.operation_line.date_operation <= date_max))
        #print((date_min <= line.operation_line.date_operation <= date_max))
        if (date_min is None and str(line.operation_line.date_operation) <= str(date_max)) or (str(date_min) <= str(line.operation_line.date_operation) <= str(date_max)): # déjà à l'équilibre avant ?
            if line.debit_line == 1:
                solde += line.sum_line
            else:
                solde -= line.sum_line
    return solde

def print_tab(tab):
    for n in sorted(tab.keys()):
        it = tab[n]
        if it != 0:
            print(gsp(2), n.ljust(50, ' '), it)

def sep():    
    print(gsp(2), "".ljust(50, '-'))

def test_start(ch:str, lst):
    for l in lst:
        if ch.startswith(l):
            return True
    return False

def sommer(lst):
    s = 0
    for e in lst.values():
        s += float(e)
    return s

def recap(a, b, dmax, dmin=None):
    charges = {}
    produits = {}
    for acc in Account.select():
        s = get_solde(acc, dmax, dmin)
        n = str(acc.number_account).ljust(5, ' ') + " " + acc.name_account
        if test_start(str(acc.number_account), a):                  
            charges[n] = s
        elif test_start(str(acc.number_account), b):
            produits[n] = -s
        else:
            print(f"{acc.number_account} {acc.name_account} unknown")
        #print(s)
    sep()
    print_tab(charges)
    sep()
    print_tab(produits) # attention erreur colonne bilan si créance client : de l'autre côté
    sep()
    #print(str)
    #print(charges.values())
    #print(produits.values())
    s_p = sommer(produits)
    s_c = sommer(charges)
    print(gsp(2), "Colonnes = ", s_c, s_p)
    print(gsp(2), "Balance =", end = " ")
    print(s_p - s_c)

while True:
    op = input("Operation(a)? q = Quit, a = Add, s = See" + space).strip() or "a"
    if op == "q":
        break
    elif op == "a":
        print("**Add**")
        name = input(gsp(1) + "Name?" + space) or "Default name"        
        date_p = date.today()
        date_p = input(gsp(1) + f"Date({date_p})?" + space) or date_p
        com_p = input(gsp(1) + "Comment?" + space) or ""
        op = Operation.create(name_operation=name, date_operation=date_p, com_operation=com_p)

        sum = "0"
        debit = "1"

        while True:
            newline = input(gsp(1) + "New Line(2)? q = no, 2 = yes" + space).strip() or "2"
            if newline == "q":
                break
            elif newline == "2":
                sum = input(gsp(2) + f"Sum({sum})?" + space) or sum # todo calculer somme restante...
                debit = input(gsp(2) + f"Is debit({debit})?" + space) or debit
                account_nb = input(gsp(2) + f"Account number(512)?" + space) or "512"
                acc, created = Account.get_or_create(number_account=account_nb)
                if created:
                    name_acc = input(gsp(3) + f"Account name?" + space)
                    acc.name_account = name_acc
                    acc.save()
                line = Line.create(sum_line=sum, debit_line=debit, account_line=acc, operation_line=op)
                #link_op = LinkOp.create(op_linkop=op, line_linkop=line)
                
                if debit == "1":
                    debit = "0"
                #else:
                #    debit = "1"
            else:
                print(gsp(1) + "Unknown")

    elif op == "s":
        print("**See**")
        while True:
            #tab_i = "\t\t\t\t\t\t\t"
            #tab_n = "\t\t\t\t"
            newline = input(gsp(1) + "What (j)? q = nothing, j = journal, t = table, r = request, c = compte, b = bilan" + space).strip() or "j"
            if newline == "q":
                break
            elif newline == "j":
                for op in Operation.select().order_by(Operation.date_operation):
                    print(gsp(2), op.date_operation, op.name_operation)
                    for line in op.lines:
                        print(gsp(3), str(line.account_line.number_account).ljust(5, ' '), end="")
                        if line.debit_line == 1:
                            print(line.account_line.name_account.ljust(100, ' '), line.sum_line)
                        else:
                            print("".ljust(50, ' '), line.account_line.name_account.ljust(60, ' '), line.sum_line)
            elif newline == "t":
                for acc in Account.select().order_by(Account.number_account):
                    print(gsp(2) + f"{acc.number_account}\t\t{acc.name_account}")
                nb = input(gsp(2) + "Number(512)?" + space) or "512"
                print(gsp(3) + nb)
                sum_d = 0
                sum_c = 0
                for line in Line.select().join(Account).switch(Line).join(Operation).where(Account.number_account==nb).order_by(Operation.date_operation):
                    print(gsp(3) + f"{line.operation_line.date_operation} - {line.operation_line.name_operation}".ljust(60, ' '), end = "")
                    if line.debit_line == 1:
                        sum_d += line.sum_line
                        print(line.sum_line)
                    else:
                        sum_c += line.sum_line
                        print("".ljust(10, " ") + str(line.sum_line))
                solde = sum_d - sum_c
                print(gsp(3) + "".ljust(60, " ") + str(sum_d).ljust(10, ' ') + str(sum_c))
                print(gsp(3) + "Sum = " + str(solde))
            elif newline == "c":
                dend = str(date.today())
                dend = input(gsp(2) + f"End({dend})?" + space) or dend
                dend_dt = datetime.strptime(dend, "%Y-%m-%d")
                dbeg = str(dend_dt.replace(year = dend_dt.year - 1).date())
                dbeg = input(gsp(2) + f"Begin({dbeg})?" + space) or dbeg
                print(gsp(2), f"Compte de résultat du {dbeg} au {dend}")
                recap(['6'], ['7'], dend, dbeg)
            elif newline == "b":
                dend = date.today()
                dend = input(gsp(2) + f"End({dend})?" + space) or dend
                print(gsp(2), f"Bilan au {dend}")
                recap(['2','3', '41', '42', '5', '48', '49'], ['1', '40', '44'], dend)
            elif newline == "r":                        
                request = input(gsp(1) + "Request?" + space)
                cursor = db.execute_sql(request)
                for row in cursor.fetchall():
                    print(gsp(2) + row)
            else:
                print(gsp(1) + "Unknown")
    else:
        print("Unkwown")

db.close()
print("End")

#bug après entrée et bilan direct, redémarrer l'application