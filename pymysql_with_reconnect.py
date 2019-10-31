import pymysql
import numpy as np
import pickle, json
import pyDes
import traceback
import time
from binascii import a2b_hex

use_pyDes = 0
DES_KEY="01123456"
k=pyDes.des(DES_KEY, pyDes.ECB, "\0\0\0\0\0\0\0\0", pad=None, padmode=pyDes.PAD_PKCS5)
class Mysql_Query:
	def __init__(self,host,user,password,port):
		self.host = host
		self.user = user
		self.password = password
		self.port = int(port)
		self.charset = 'utf8'
		self.conn   = None
		self._conn()

	def _conn (self):
		try:
			self.conn = pymysql.connect(host=self.host,user=self.user,password=self.password,port=self.port, charset=self.charset)
			return True
		except :
			return False
		
	def _reConn (self, num=28800, stime=3): #重试连接总次数为1天,这里根据实际情况自己设置,如果服务器宕机1天都没发现就......
		_number = 0
		_status = True
		while _status and _number <= num:
			try:
				self.conn.ping()       #cping 校验连接是否异常
				_status = False
			except:
				if self._conn()==True: #重新连接,成功退出
					_status = False
					break
				_number +=1
				time.sleep(stime)      #连接不成功,休眠3秒钟,继续循环，知道成功或重试次数结束

	def query_sql(self, sql_operation):
		self._reConn()
		self.cursor = self.conn.cursor()
		self.cursor.execute(sql_operation)
		results = self.cursor.fetchall()
		self.cursor.close()
		return results

	def uid_query(self, uids):
		res = []
		uids_str = "'"+"','".join(uids)+"'"
		sql_operation = "select user_id, unit_id, building_name, room_name, name, id_type, id_code, telephone, user_image, face_id from db_unitpropertybase.house_user where user_id in ({}) or face_id in ({})".format(uids_str, uids_str)
		print("==", sql_operation)
		try:
			results = self.query_sql(sql_operation)
			for item in results:
				if item[9] in uids:
					res.append({
						"uid":item[9],
						"unit_id":item[1],
						"building_name":item[2],
						"room_name":item[3],
						"name":item[4],
						"id_type":item[5],
						"id_code":k.decrypt(a2b_hex(item[6])) if use_pyDes else item[6],
						"telephone":k.decrypt(a2b_hex(item[7])) if use_pyDes else item[7],
						"face_image":item[8]})
				else:
					res.append({
					"uid":item[0],
					"unit_id":item[1],
					"building_name":item[2],
					"room_name":item[3],
					"name":item[4],
					"id_type":item[5],
					"id_code":k.decrypt(a2b_hex(item[6])) if use_pyDes else item[6],
					"telephone":k.decrypt(a2b_hex(item[7])) if use_pyDes else item[7],
					"face_image":item[8]})
			return res
		except Exception as e:
			print ("mysql error: {}".format(traceback.format_exc()))


	def unit_query(self,unit_ids):
		res = []
		unit_str = "'"+"','".join(map(lambda x: str(x),unit_ids))+"'"
		sql_operation = "select id, name, province_name, city_name, town_name from db_unitpropertybase.t_pb_unit where id in ({})".format(unit_str)
		print("==", sql_operation)
		try:
			results = self.query_sql(sql_operation)
			for item in results:
				res.append({
					"id":item[0],
					"name":item[1],
					"province_name":item[2],
					"city_name":item[3],
					"town_name":item[4]})
			return res	
		except Exception as e:
			print ("mysql error: {}".format(traceback.format_exc()))

		cursor.close()
		self.conn.close()

	def blacklist_query(self):
		res = []
		sql_operation = "select item_id, user_id, image_id from db_securitycenter.peopleblacklist"
		try:
			results = self.query_sql(sql_operation)
			for item in results:
				res.append({"item_id": item[0], 'user_id': item[1], 'image_id': item[2]})
			return res
		except Exception as e:
			print ("mysql error: {}".format(traceback.format_exc()))


	def get_face_feature(self):
		white_uids = []
		white_md5s = []
		white_features = []
		white_city_code = []
		white_town_code = []
		black_uids = []
		black_md5s = []
		black_features = []
		black_city_code = []
		black_town_code = []

		sql_operation = "select u.uid, u.pic_md5, f.feature, f.city_code, f.town_code from feature_new_model.feature_model_0330 f, feature_new_model.user " \
						"u where f.user_id=u.id"
		try:
			results = self.query_sql(sql_operation)
			for item in results:
				uid = item[0]
				if item[1]==None:
					continue
				uid_md5s = pickle.loads(item[1])
				# uid_features = eval(bytearray.decode(item[2], encoding='utf-8'))
				uid_features = eval(item[2])
				if item[3]==None:
					uid_city_code = [-1 for i in range(20)]
				else:
					uid_city_code = [item[3] for i in range(20)]
				if item[4]==None:
					uid_town_code = [-1 for i in range(20)]
				else:
					uid_town_code = [item[4] for i in range(20)]
					#print item[4]
				if uid.startswith('black'):
					for md5, feature, city_code, town_code in zip(uid_md5s, uid_features['emb_2'], uid_city_code, uid_town_code):
						black_uids.append(uid)
						black_md5s.append(md5)
						black_features.append(np.array(feature, dtype=np.float32))
						black_city_code.append(city_code)
						black_town_code.append(town_code)
				else:
					for md5, feature, city_code, town_code in zip(uid_md5s, uid_features['emb_2'], uid_city_code, uid_town_code):
						white_uids.append(uid)
						white_md5s.append(md5)
						white_features.append(np.array(feature, dtype=np.float32))
						white_city_code.append(city_code)
						white_town_code.append(town_code)
			return np.array(white_uids), np.array(white_md5s), np.array(white_features), np.array(white_city_code), np.array(white_town_code), np.array(black_uids), np.array(black_md5s), np.array(black_features), np.array(black_city_code), np.array(black_town_code)

		except Exception as e:
			print ("mysql error: {}".format(traceback.format_exc()))




if __name__ == "__main__":
	host = '192.168.0.246'
	user = "syncdb"
	password = "syncdb_oeasy"
	port = 3306
	mysql_query = Mysql_Query(host,user,password,port)
	# face_white_uids, face_white_md5s, face_white_features, face_white_city_code, face_white_town_code, face_black_uids, face_black_md5s, face_black_features, face_black_city_code, face_black_town_code = mysql_query.get_face_feature()
	uids = ['971988_eed5682ca3754769858eae8fb6d0a4a7','971988_fd21e9a3c57a42df8321121b374376bb','22d862426a18418a8899a9132a37ee6d','971988_2c0a7950dc6349f59c83bfa923780c83','971988_3726d163cf7e49f1aa5646272c425092','971988_42f19dd0f73a4756a6311c6399d4ace0','971988_2e60d204a56847e49ed561c2781bf1b6','972317_6080825422844c4181529d2bc76e3b48','971988_b86fabcae1b840aebe58879cd9dc3cc5','971048_0cf0fc764c034895ab0c2c7c49c60318','4a2367cf2c3940e7b7c90088fedad242','971988_29d0594042714171a67a5200b4c39919','971988_5e038238a6b243ad8ccef1d5ad855cb9','971988_12d1dbe91a294d4aa55f2f0722a172d1','6fbdccffc72347a8b9f49f6f2e43bd0b','FK_19dd997451af4d7d954947617679ae17']
	time.sleep(28800)
	t = mysql_query.uid_query(uids)
	print(t)