from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime, timedelta
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Job categories
JOB_CATEGORIES = [
    'خیاط', 'کارگر ساده', 'راننده', 'پرستار', 'معلم',
    'برقکار', 'لوله کش', 'نقاش', 'نجار', 'آشپز',
    'منشی', 'حسابدار', 'برنامه نویس', 'طراح', 'باغبان',
    'تعمیرکار موبایل', 'مکانیک', 'آرایشگر', 'خرده فروش', 'تحویلدار'
]

# Database simulation
ads_db = []
notifications_db = {}
global_message = ""

# Check for do.html message
if os.path.exists('templates/do.html'):
    with open('templates/do.html', 'r', encoding='utf-8') as f:
        global_message = f.read().strip()
    try:
        os.remove('templates/do.html')
    except:
        pass

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'search' in request.form:
            search_term = request.form.get('search_term', '').lower()
            filtered_ads = [ad for ad in ads_db if (
                search_term in ad['description'].lower() or 
                search_term in ad['category'].lower() or
                search_term in ad['ad_type'].lower()
            )]
            return render_template('index.html', 
                               ads=filtered_ads, 
                               categories=JOB_CATEGORIES,
                               global_message=global_message,
                               notifications=notifications_db.get(request.remote_addr, []))
        
    return render_template('index.html', 
                         ads=ads_db, 
                         categories=JOB_CATEGORIES,
                         global_message=global_message,
                         notifications=notifications_db.get(request.remote_addr, []))

@app.route('/submit_ad', methods=['POST'])
def submit_ad():
    ad_type = request.form.get('ad_type')
    category = request.form.get('category')
    description = request.form.get('description')
    phone = request.form.get('phone')
    
    if not all([ad_type, category, description, phone]):
        flash('لطفا تمام فیلدها را پر کنید', 'error')
        return redirect(url_for('index'))
    
    # Add new ad
    new_ad = {
        'id': len(ads_db) + 1,
        'ad_type': ad_type,
        'category': category,
        'description': description,
        'phone': phone,
        'timestamp': datetime.now(),
        'ip': request.remote_addr
    }
    ads_db.append(new_ad)
    
    # Create notifications for matching ads
    for ad in ads_db:
        if ad['ad_type'] != ad_type and ad['category'] == category:
            notification_msg = ""
            if ad_type == 'جویای کار':
                notification_msg = f"یک کارفرما در دسته {category} به دنبال نیرو است"
            else:
                notification_msg = f"یک جویای کار در دسته {category} آماده به کار است"
            
            if ad['ip'] not in notifications_db:
                notifications_db[ad['ip']] = []
            notifications_db[ad['ip']].append({
                'message': notification_msg,
                'category': category,
                'description': description,
                'phone': phone,
                'timestamp': datetime.now()
            })
    
    flash('آگهی با موفقیت ثبت شد', 'success')
    return redirect(url_for('index'))

@app.route('/clear_notifications', methods=['POST'])
def clear_notifications():
    if request.remote_addr in notifications_db:
        notifications_db[request.remote_addr] = []
    return redirect(url_for('index'))

@app.route('/clear_global_message', methods=['POST'])
def clear_global_message():
    global global_message
    global_message = ""
    return redirect(url_for('index'))

def cleanup_old_ads():
    global ads_db
    one_week_ago = datetime.now() - timedelta(days=7)
    ads_db = [ad for ad in ads_db if ad['timestamp'] > one_week_ago]

# Initial cleanup
cleanup_old_ads()

if __name__ == '__main__':
    app.run(debug=True)
