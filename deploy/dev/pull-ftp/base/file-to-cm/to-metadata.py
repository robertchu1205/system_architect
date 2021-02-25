import os, sys, time, datetime
from PIL import Image
import mysql.connector

IMAGE_FOLDER_PATH = os.environ['IMAGE_FOLDER_PATH']
database_table = os.environ['database_table']
tree_format = ['OK', 'NG', 'Overkill', 'Leak', 'InversePolarity']
possible_comps = ['AluCap', 'ElecCap', 'acpi', 'Ins', 'SATA', 'L', 'BH', 'Jumper', 'PCI', 'Aud', 'Stud', 'NI', 'DimSoc', 'CONN', 'USB', 'VGA']

mydb = mysql.connector.connect(
  host=os.environ['DB_PATH'].split(':')[0],
  port=os.environ['DB_PATH'].split(':')[1],
  user=os.environ['DB_USER'],
  password=os.environ['DB_PASSWORD'],
)
mycursor = mydb.cursor()
# mycursor.execute(f'select component, count(*) from {database_table} group by component')
# test = mycursor.fetchall()
# print(test)

def get_date(howmanydaysbefore):
    today = datetime.date.today()
    days = datetime.timedelta(days=howmanydaysbefore)
    yesterday = today - days
    return yesterday.strftime('%Y%m%d')

def read_width_height(path):
    try:
        width, height = Image.open(path).size
    except Image.UnidentifiedImageError:
        print(f'unidentified image: {path}')
        width, height = None, None
    # img = tf.io.read_file(path)
    # img = tf.io.decode_image(img, channels=3)
    # width = img.shape[1]
    # height = img.shape[0]
    return width, height

def walk_to_img_list(date):
    img_list = []
    for root, _, files in os.walk(IMAGE_FOLDER_PATH):
        if root.split(os.path.sep)[-2] == date or root.split(os.path.sep)[-3] == date:
            for img_file in files:
                if img_file.endswith('.png') or img_file.endswith('.bmp') or img_file.endswith('.jpg'):
                    img_list.append(os.path.join(root, img_file))
    return img_list

def walk_test_uploading_func(date):
    ori_img_count = len(walk_to_img_list(date))
    time.sleep(5)
    new_img_count = len(walk_to_img_list(date))
    if new_img_count == ori_img_count:
        return True
    else:
        return False

def label_lookup(label):
    table = {
        'OK': 'OK',
        'NG': 'NG',
        'Leak': 'NG',
        'Overkill': 'OK',
        'InversePolarity': 'NG',
    }
    return table.get(label, 'other')

def ontine_test_lookup(label):
    table = {
        'OK': None,
        'NG': 'NG',
        'Leak': 'Leak',
        'Overkill': 'Overkill',
        'InversePolarity': 'Leak-InversePolarity',
    }
    return table.get(label, 'other')

# new version: CN0HMX8DWS20006A03RDA01_355_0AH01_B002_PT4_AluCap_0_270_NA_0
def test_img_list(img_list):
    try:
        for ip in img_list:
            possible_bool = False
            directory, filename = os.path.split(ip)
            directory = directory.split(os.path.sep)
            fn, ext = os.path.splitext(filename)
            ext = ext.split('.')[-1]
            width, height = read_width_height(ip)
            try:
                intdate = int(directory[-2])
                date = directory[-2]
            except:
                date = directory[-3]
            try: 
                if (int(date[4:]) > 1231) or (int(date[4:]) < 101):
                    print('date folder wrong')
                    return ip
                x = int(date)
            except Exception as e:
                print(f'Date wrong; Exception msg: {e}')
                return ip
            if directory[-1] not in tree_format:
                print('label not in [OK/NG/Leak/Overkill/InversePolarity]')
                return ip
            for c in possible_comps:
                if c in fn.split('_'):
                    possible_bool = True
                    splited_filename = fn.split(f'_{c}_')
                    back_filename = splited_filename[-1] # 0_270_NA_0
                    front_filename = splited_filename[0] # CN0HMX8DWS20006A03RDA01_355_0AH01_B002_PT4
                    PanelNo = front_filename.split('_')[0]
                    front_filename = front_filename.replace(f'{PanelNo}_', '') # 355_0AH01_B002_PT4
                    location = front_filename.split('_')[-1]
                    front_filename = front_filename.replace(f'_{location}', '') # 355_0AH01_B002
                    eagle = front_filename.replace('_', '')
                    degree = back_filename.split('_')[0]
                    capacity = back_filename.split('_')[1]
                    voltage = back_filename.split('_')[2]
                    index_count = back_filename.split('_')[3]
            if possible_bool == False:
                print('parsing filename wrong')
                return ip
    except Exception as e:
        print(f'Exception msg: {e}')
        return e
    return True

def new_path_to_symbol(ip):
    # d: IMAGE_FOLDER_PATH/line/date/A4_result
    # f: PanelNo_eagle_location_component_degree_capacity_voltage_index.extension
    # new version: CN0HMX8DWS20006A03RDA01_355_0AH01_B002_PT4_AluCap_0_270_NA_0
    directory, filename = os.path.split(ip)
    directory = directory.split(os.path.sep)
    fn, ext = os.path.splitext(filename)
    ext = ext.split('.')[-1]
    width, height = read_width_height(ip)
    # if len(directory[-2]) != 4:
    #     directory[-2] = '0' + directory[-2]
    for c in possible_comps:
        if c in fn.split('_'):
            possible_bool = True
            splited_filename = fn.split(f'_{c}_')
            back_filename = splited_filename[-1] # 0_270_NA_0
            front_filename = splited_filename[0] # CN0HMX8DWS20006A03RDA01_355_0AH01_B002_PT4
            PanelNo = front_filename.split('_')[0]
            front_filename = front_filename.replace(f'{PanelNo}_', '') # 355_0AH01_B002_PT4
            location = front_filename.split('_')[-1]
            front_filename = front_filename.replace(f'_{location}', '') # 355_0AH01_B002
            eagle = front_filename.replace('_', '')
            degree = back_filename.split('_')[0]
            capacity = back_filename.split('_')[1]
            voltage = back_filename.split('_')[2]
            index_count = back_filename.split('_')[3]
            try:
                intdate = int(directory[-2])
                date = directory[-2]
            except:
                date = directory[-3]
            symbol = (
                        ip, 
                        filename, 
                        date, 
                        label_lookup(directory[-1]), 
                        ontine_test_lookup(directory[-1]), 
                        PanelNo, 
                        location,
                        c,
                        degree,
                        capacity,
                        voltage, 
                        index_count,
                        eagle,
                        width,
                        height,
                        os.environ['file_server_url']+ip, 
            )
            return symbol

if __name__ == '__main__':
    sql = f"""INSERT INTO {database_table} (path, filename, date, label, online_test, SN, location, component, degree, capacity, voltage, index_count, part_name, width, height, file_url) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
    dates = []
    for i in range(int(os.environ['HOW_MANY_DAYS_AGO'])):
        dates.append(get_date(i+1))
    for date in dates:
        # generate failed job but would succeed after try again within backofflimit
        test_uploading = walk_test_uploading_func(date)
        if test_uploading != True: 
            sys.exit(f'labeled images still uploading on {date}, return value {test_uploading}')
        img_list = walk_to_img_list(date)
        if len(img_list)==0:
            continue
        print(f'{date} count:', str(len(img_list)))
        # filename saved from AOI program changed, need to check it by humans
        test_result = test_img_list(img_list)
        if test_result != True:
            sys.exit(f'tree format is not correct on {date}, return value {test_result}')
        # try:
        #     create_new_metadata()
        # except Exception as e:
        #     print(f'new_metadata already exists in {DB_PATH}')
        for ip in img_list:
            # directory, filename = os.path.split(ip)
            # fn, ext = os.path.splitext(filename)
            # splitted_fn = fn.split('_')
            # if len(splitted_fn) == 8:
            #     symbol = path_to_symbol(ip)
            # elif len(splitted_fn) == 7:
            #     symbol = path_to_symbol_wrong(ip)
            symbol = new_path_to_symbol(ip)
            try:
                mycursor.execute(sql, symbol)
                mydb.commit()
            except mysql.connector.IntegrityError as err:
                print(f'Exception msg: {e}')
                print(f'{ip} occured error while inserting to {database_table} with connection of {DB_PATH}')
                # try:
                #     delete_sql = f"DELETE FROM {database_table} WHERE path='{symbol[0]}'"
                #     mycursor.execute(delete_sql)
                #     mycursor.execute(sql, symbol)
                #     mydb.commit()
                # except Exception as e:
                #     print(f'Exception msg: {e}')
                #     print(f'{ip} occured error while deleting & inserting to {database_table} with connection of {DB_PATH}')
            except Exception as e:
                sys.exit(f'Exception msg: {e}, {ip} occured error while inserting to {database_table} with connection of {DB_PATH}')
        print(f'All insertion on {date} succeed!')
    mydb.close()