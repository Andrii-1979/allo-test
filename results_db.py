import sqlite3
import traceback
import logging


def get_connection_to_db(lock=None):
	'''Функция создания базы данных или подключения к существующей'''
	
	# Подключение к cсуществующей базе данных или создание
	conn = sqlite3.connect('results.db', timeout=5)
	c = conn.cursor()
		
	# Проверяем есть ли в базе таблица для ключей 
	c.execute("SELECT name FROM sqlite_master WHERE type='table' AND \
				name='key'")
	conn.commit()
	a = c.fetchone()

	# Если таблицы для ключей нет - создаем и заполняем все нужные таблицы
	if not a:
		c.execute("CREATE TABLE IF NOT EXISTS hint (value text UNIQUE)")
		c.execute("CREATE INDEX IF NOT EXISTS index_hint ON hint (value)")
		c.execute("CREATE TABLE IF NOT EXISTS key (value text)")
		c.execute("INSERT INTO key VALUES ('а')")
		conn.commit()
	return conn


def get_key(conn):
	'''Функция получения из базы последнего значения ключа'''
	
	c = conn.cursor()
	c.execute("SELECT value FROM key")
	return c.fetchone()[0]


def record_to_db(conn, key, result):
	'''Функция обновления ключа в базе и записи результата'''
	
	# Настройка логгирования
	logging.basicConfig(filename="result_db.log", level=logging.INFO)
	
	try:
		c = conn.cursor()
		print(c)
		# Если подсказки есть
		if result:

			# Проверка есть ли уже такое значение в базе
			c.execute('SELECT value FROM hint WHERE value="' + result + '"')
			conn.commit()

			# Если такое значение есть - только обновляем ключ
			if c.fetchone():
				c.execute("UPDATE key SET value = '"+key+"'")
				conn.commit()
				
		# Если подсказки нет
		else:
			c.execute("UPDATE key SET value = '"+key+"'")
			conn.commit()
			
		# Выполняется после выполнения записей в базу 
		return True
		
	except:
		logging.error(traceback.format_exc())
		return False


def show_result(conn):
	'''Функция показа записей результатов из базы'''
	
	c = conn.cursor()
	
	# Получение значения ключа
	c.execute("SELECT value FROM key")
	conn.commit()
	key = c.fetchone()[0]
	
	# Получение результатов (поисковых подсказок)
	result = []
	c.execute("SELECT value FROM hint")
	conn.commit()
	for i in c.fetchall():
		result.append(i[0])
	print('key='+key)
	print(result)
