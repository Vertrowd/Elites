from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
from datetime import datetime

app = Flask(__name__)

# Database connection
def connect_to_database():
    try:
        con = mysql.connector.connect(
            host='localhost',
            user='root',
            password='Aadhi@2006123',
            database='DBMS'
        )
        return con
    except mysql.connector.Error as err:
        print(f"❌ Error: {err}")
        return None

# Create tables if they don't exist
def create_tables(con):
    cursor = con.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Product (
            ProdId INT PRIMARY KEY,
            name VARCHAR(20) NOT NULL,
            Quantity INT NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Delivered (
            DeliveryId INT AUTO_INCREMENT PRIMARY KEY,
            product VARCHAR(255) NOT NULL,
            ProdId INT NOT NULL,
            Quantity INT NOT NULL,
            DOD DATE NOT NULL,
            FOREIGN KEY (ProdId) REFERENCES Product(ProdId) ON DELETE CASCADE
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Records (
            R_ID INT AUTO_INCREMENT PRIMARY KEY,
            product VARCHAR(255) NOT NULL,
            DOR DATE NOT NULL,
            ProdId INT NOT NULL,
            Quantity INT NOT NULL,
            Status TEXT NOT NULL,
            FOREIGN KEY (ProdId) REFERENCES Product(ProdId) ON DELETE CASCADE
        )
    """)
    con.commit()
    cursor.close()

# Initialize database
def initialize_database():
    con = connect_to_database()
    if con:
        create_tables(con)
    return con

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/manage_products', methods=['GET', 'POST'])
def manage_products():
    if request.method == 'POST':
        choice = request.form['choice']
        if choice == '1':
            return redirect(url_for('add_product'))
        elif choice == '2':
            return redirect(url_for('view_products'))
        elif choice == '3':
            return redirect(url_for('mark_delivered'))
        elif choice == '4':
            return redirect(url_for('index'))
    return render_template('manage_products.html')

@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        prod_id = int(request.form['prod_id'])
        name = request.form['name']
        quantity = int(request.form['quantity'])

        cursor = con.cursor()
        cursor.execute("SELECT Quantity FROM Product WHERE ProdId = %s", (prod_id,))
        existing_product = cursor.fetchone()

        if existing_product:
            new_quantity = existing_product[0] + quantity
            cursor.execute("UPDATE Product SET Quantity = %s WHERE ProdId = %s", (new_quantity, prod_id))
        else:
            cursor.execute("INSERT INTO Product (ProdId, name, Quantity) VALUES (%s, %s, %s)", (prod_id, name, quantity))

        con.commit()

        current_date = datetime.now().strftime("%Y-%m-%d")
        cursor.execute(
            "INSERT INTO Records (product, DOR, ProdId, Quantity, Status) VALUES (%s, %s, %s, %s, %s)", 
            (name, current_date, prod_id, quantity, 'IN')
        )
        con.commit()
        cursor.close()

        return redirect(url_for('manage_products'))
    return render_template('add_products.html')

@app.route('/view_products')
def view_products():
    cursor = con.cursor()
    cursor.execute("SELECT * FROM Product")
    products = cursor.fetchall()
    cursor.close()
    return render_template('view_products.html', products=products)

@app.route('/mark_delivered', methods=['GET', 'POST'])
def mark_delivered():
    if request.method == 'POST':
        prod_id = int(request.form['prod_id'])
        quantity = int(request.form['quantity'])

        cursor = con.cursor()
        cursor.execute("SELECT name, Quantity FROM Product WHERE ProdId = %s", (prod_id,))
        product = cursor.fetchone()

        if not product:
            return "Product not found in inventory!"

        product_name, available_quantity = product

        if quantity > available_quantity:
            return "Not enough stock available!"

        current_date = datetime.now().strftime("%Y-%m-%d")

        cursor.execute(
            "INSERT INTO Delivered (product, ProdId, Quantity, DOD) VALUES (%s, %s, %s, %s)", 
            (product_name, prod_id, quantity, current_date)
        )
        con.commit()

        cursor.execute(
            "INSERT INTO Records (product, DOR, ProdId, Quantity, Status) VALUES (%s, %s, %s, %s, %s)", 
            (product_name, current_date, prod_id, quantity, 'OUT')
        )
        con.commit()

        new_quantity = available_quantity - quantity
        cursor.execute("UPDATE Product SET Quantity = %s WHERE ProdId = %s", (new_quantity, prod_id))
        con.commit()
        cursor.close()

        return redirect(url_for('manage_products'))
    return render_template('mark_delivered.html')

@app.route('/about_us')
def about_us():
    return render_template('about_us.html')

@app.route('/view_records', methods=['GET', 'POST'])
def view_records():
    if request.method == 'POST':
        choice = request.form['choice']
        if choice == '1':
            return redirect(url_for('view_all_records'))
        elif choice == '2':
            return redirect(url_for('view_in_records'))
        elif choice == '3':
            return redirect(url_for('view_out_records'))
        elif choice == '4':
            return redirect(url_for('index'))
    app.logger.info("Rendering view_records_menu.html")
    return render_template('view_records_menu.html')

@app.route('/view_all_records')
def view_all_records():
    cursor = con.cursor()
    cursor.execute("SELECT * FROM Records")
    records = cursor.fetchall()
    cursor.close()
    return render_template('view_records.html', records=records)

@app.route('/view_in_records')
def view_in_records():
    cursor = con.cursor()
    cursor.execute("SELECT * FROM Records WHERE Status = 'IN'")
    records = cursor.fetchall()
    cursor.close()
    return render_template('view_records.html', records=records)

@app.route('/view_out_records')
def view_out_records():
    cursor = con.cursor()
    cursor.execute("SELECT * FROM Records WHERE Status = 'OUT'")
    records = cursor.fetchall()
    cursor.close()
    return render_template('view_records.html', records=records)

# Main function to initialize and run the application
def main():
    global con
    con = initialize_database()
    if con:
        # Run the Flask app on port 5008
        app.run(debug=True, port=5008)
    else:
        print("❌ Failed to connect to the database. Exiting...")

if __name__ == '__main__':
    main()
