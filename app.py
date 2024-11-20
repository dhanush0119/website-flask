from flask import Flask, render_template,redirect,url_for,request,flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta

app =Flask(__name__)
app.secret_key='pottyshop'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shop.db'
db=SQLAlchemy(app)

class Company(db.Model):
    cmpy_id=db.Column(db.Integer, primary_key=True)
    cmpy_name=db.Column(db.String(150),  nullable=False, default ="Namma Kadai")
    cash_bal=db.Column(db.Integer, default=1000.00)

class Items(db.Model):
    item_id=db.Column(db.Integer, primary_key=True)
    item_name=db.Column(db.String(150),nullable=False, unique=True)
    item_qty=db.Column(db.Integer, default=0)

class Purchase(db.Model):
    pur_id=db.Column(db.Integer, primary_key=True)
    pur_time = db.Column(db.DateTime, default=lambda: datetime.utcnow() + timedelta(hours=5, minutes=30))
    pitem_id=db.Column(db.Integer, db.ForeignKey('items.item_id'),nullable=False)
    qty=db.Column(db.Integer,nullable=False)
    rate=db.Column(db.Float, nullable=False)
    amount=db.Column(db.Float)

class Sales(db.Model):
    sale_id=db.Column(db.Integer, primary_key=True)
    sale_time=db.Column(db.DateTime, default=lambda: datetime.utcnow() + timedelta(hours=5, minutes=30))
    s_item_id=db.Column(db.Integer, db.ForeignKey('items.item_id'),nullable=False)
    s_qty=db.Column(db.Integer, db.ForeignKey('purchase.qty'),nullable=False)
    s_rate=db.Column(db.Float, db.ForeignKey('purchase.rate'),nullable=False)
    s_amount=db.Column(db.Float,db.ForeignKey('purchase.amount'),nullable=False)


def add_cmpy():
     def_cmpy=Company.query.filter_by(cmpy_name="Namma Kadai").first()

     if not def_cmpy:
          new_cmpy=Company(cmpy_name="Namma Kadai", cash_bal=1000.00)
          db.session.add(new_cmpy)
          db.session.commit()


with app.app_context():
    db.create_all()
    add_cmpy()


@app.route('/')
def home():
    company=Company.query.first()
    items=Items.query.all()
    return render_template('index.html',company=company,items=items)

@app.route('/add_items',methods=['POST','GET'])
def add_items():
    if request.method=='POST':
        item_name=request.form['item_name'].strip().upper()

        exist=Items.query.filter_by(item_name=item_name).first()
        if exist :
            flash('item already exist','error')
        else:
            new_item=Items(item_name=item_name)
            db.session.add(new_item)
            db.session.commit()
            flash('item added successfully','success')
            return redirect(url_for("add_items"))
    
    return render_template('add_items.html')

        
@app.route('/view_items',methods=['POST','GET'])
def view_items():
        items=Items.query.all()
        return render_template('view_items.html',items=items)

@app.route('/view_company',methods=['POST','GET'])
def view_company():
        company=Company.query.all()
        return render_template('view_company.html',company=company)



@app.route('/purchase', methods=['GET', 'POST'])
def purchase():
    company = Company.query.first() 
    items = Items.query.all() 
    if request.method == 'POST':
        selected_item_id = request.form.get('item_id')
        qty = int(request.form.get('qty', 0))
        rate = float(request.form.get('rate', 0.0))
        amount = qty * rate

       
        if company.cash_bal >= amount:
            
            item = Items.query.get(selected_item_id)

            if item:
               
                new_purchase = Purchase(pitem_id=selected_item_id, qty=qty, rate=rate, amount=amount)
                db.session.add(new_purchase)

                
                item.item_qty += qty 

                
                company.cash_bal -= amount
                db.session.commit()
                
                flash('Purchase successful!', 'success')
            else:
                flash('Item does not exist!', 'error')
        else:
            flash('Insufficient cash balance!', 'error')
        
        return redirect(url_for('purchase'))

    return render_template('purchase.html', company=company, items=items)

@app.route('/sales',methods=['POST','GET'])
def sale():
    company = Company.query.first()
    items = Items.query.all()
    if request.method == 'POST':
        selected_item_id = request.form.get('item_id')
        qty = int(request.form.get('qty', 0))
        rate = float(request.form.get('rate', 0.0))
        amount = qty * rate

        item=Items.query.filter_by(item_id=selected_item_id).first()

        if item and item.item_qty >=qty:
            item.item_qty-=qty
            company.cash_bal+=amount
            new_sale=Sales(s_item_id=selected_item_id,s_qty=qty,s_rate=rate,s_amount=amount)
            db.session.add(new_sale)
            db.session.commit()
            flash('Sale successfully','success')
        else:
            flash('Insufficient quantity','error')

    return render_template('sales.html',company=company,items=items)     

@app.route('/purchase_history')
def purchase_history():
    new_his=Purchase.query.all()
    return render_template('purchase_history.html',new_his=new_his)

@app.route('/sales_history')
def sale_history():
    new_his=Sales.query.all()
    return render_template('sales_history.html',new_his=new_his)


@app.route('/edit_item/<int:id>',methods=['POST','GET'])
def edit_item(id):
    item=Items.query.get_or_404(id)
    if request.method=='POST':
        item_name=request.form['item_name'].strip().upper()
        item_qty=int(request.form['item_qty'])

        item.item_name=item_name
        item.item_qty=item_qty
        db.session.commit()
        flash('item updated successfully','success')
        return redirect(url_for("home"))
    
    return render_template('edit_item.html')



app.run(debug=True)