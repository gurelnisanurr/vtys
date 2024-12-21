from flask import Flask, render_template, request, redirect, url_for
import pg8000

app = Flask(__name__)

# Veritabanı bağlantısı
def get_db_connection():
    conn = pg8000.connect(
        user="postgres",              
        password="Nisa3578",          
        database="SporSalonuYonetim", 
        host="localhost",             
        port=5432                     
    )
    return conn

# Ana sayfa: Üyeleri listeleme ve arama
@app.route('/', methods=['GET', 'POST'])
def index():
    conn = get_db_connection()
    cur = conn.cursor()

    search_query = request.form.get('search', '')
    if search_query:
        cur.execute("SELECT * FROM Members WHERE name LIKE %s;", ('%' + search_query + '%',))
    else:
        cur.execute("SELECT * FROM Members;")
    
    members = cur.fetchall()
    cur.close()
    conn.close()
    
    return render_template('index.html', members=members)

# Üye ekleme sayfası
@app.route('/add', methods=('GET', 'POST'))
def add_member():
    if request.method == 'POST':
        name = request.form.get('name', '')
        phone = request.form.get('phone', '')
        email = request.form.get('email', '')
        start_date = request.form.get('start_date', '')
        end_date = request.form.get('end_date', '')
        package_id = request.form.get('package_id', '')

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO Members (name, phone, email, start_date, end_date, membership_package_id)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (name, phone, email, start_date, end_date, package_id))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('index'))
    return render_template('add_member.html')

# Üye silme işlemi
@app.route('/delete/<int:id>', methods=['GET', 'POST'])
def delete_member(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT name FROM Members WHERE member_id = %s;", (id,))
    member = cur.fetchone()
    if request.method == 'POST':
        cur.execute("DELETE FROM Members WHERE member_id = %s;", (id,))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('index'))
    cur.close()
    conn.close()
    return render_template('delete_member.html', member_name=member[0], member_id=id)

# Üye güncelleme sayfası
@app.route('/update/<int:id>', methods=('GET', 'POST'))
def update_member(id):
    conn = get_db_connection()
    cur = conn.cursor()
    if request.method == 'POST':
        name = request.form.get('name', '')
        phone = request.form.get('phone', '')
        email = request.form.get('email', '')
        start_date = request.form.get('start_date', '')
        end_date = request.form.get('end_date', '')
        package_id = request.form.get('package_id', '')

        try:
            cur.execute("""
                UPDATE Members
                SET name = %s, phone = %s, email = %s, start_date = %s, end_date = %s, membership_package_id = %s
                WHERE member_id = %s
            """, (name, phone, email, start_date, end_date, package_id, id))
            conn.commit()
            return redirect(url_for('index'))  # Güncelleme sonrası anasayfaya yönlendir
        except Exception as e:
            conn.rollback()  # Hata durumunda rollback yaparak değişiklikleri geri al
            print(f"Hata: {e}")
            return "Bir hata oluştu, lütfen tekrar deneyin."  # Kullanıcıya hata mesajı göster
    cur.execute("SELECT * FROM Members WHERE member_id = %s;", (id,))
    member = cur.fetchone()
    cur.close()
    conn.close()
    return render_template('update_member.html', member=member)

if __name__ == '__main__':
    app.run(debug=True)
