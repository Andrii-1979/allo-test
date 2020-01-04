import asyncio
import logging
import threading
import urllib.parse
from arsenic import get_session, browsers, services
from arsenic.actions import Mouse, chain

from results_db import get_connection_to_db, get_key, record_to_db, show_result 
from key_generator import key_generator


async def search_hints():
	
	global global_key, result
	
	# Локальная переменная блокировки
	this_thread = threading.local()
	
	# Блокировка
	lock = threading.Lock()
	
	# Получение соединение к базе данных
	while not lock.acquire(False):
		pass
	try:
		conn = get_connection_to_db()
	except:
		logging.error(traceback.format_exc())
	finally:
		lock.release()


	# Инициализируем сессию с браузером
	service = services.Chromedriver()
	browser = browsers.Chrome(chromeOptions=
				{'args': ['--headless', '--disable-gpu']})
	
	async with get_session(service, browser) as session:
				
		# Переходим к сайту Алло
		await session.get('https://allo.ua/')
		
		# Получаем объект строки поиска
		search_box = await session.wait_for_element(2, '#search')

		# Жмем мышью на строку поиска
		mouse = Mouse()
		actions = chain(mouse.move_to(search_box), mouse.down(), mouse.up())
		await session.perform_actions(actions)
	
		while True:
			try:		
				# Изменение ключей
				print('global_key - '+global_key)
				while not lock.acquire(False):	
					pass
					
				# Если все варианты просмотрены
				if global_key == 'аааа':
					lock.release()
					return
					
				# Если варианты еще есть
				try:
					this_thread.key = global_key
					global_key = next(key_generator(global_key))
				except StopAsyncIteration:
					if global_key == 'яяя':
						this_thread.key = 'яяя'
						global_key = 'аааа'
				except:
					logging.error(traceback.format_exc())
				finally:
					lock.release()
					
				# Вводим текст в поле поиска
				await search_box.send_keys(this_thread.key)
				
				# Получение подсказок
				selector = 'ul#search-suggest-query a'	
				await asyncio.sleep(2)
				hints_list = await session.get_elements(selector)
				
				# Если подсказки были
				if hints_list:
					print('Запись подсказок для ключа - '+this_thread.key)
					for hint in hints_list:
						string = await hint.get_attribute('href')
						string_converted = urllib.parse.unquote(string.split('/?q=')[1])
						
						# Запись результата в базу данных
						print('Попытка записи в базу данных '+this_thread.key)
						while not lock.acquire(False):
							pass						
						if not record_to_db(conn, this_thread.key, string_converted):
							logging.error('Не получилось записать в базу ключ '+this_thread.key+' со значением '+string_converted)
						lock.release()		
									
				# Если подсказок не было
				else:
					print('Подсказок не было для ключа - ' + this_thread.key)
					# Запись результата в базу данных - обновление ключа
					while not lock.acquire(False):						
						pass
					if not record_to_db(conn, this_thread.key, ''):
						logging.error('Не получилось записать в базу ключ '+this_thread.key)
					lock.release()							
				
				# Очистка строки поиска
				await search_box.clear()	
			
			except:
				# Если все комбинации закончились
				if get_key(conn) == 'яяя':
					conn.close()
					return True


# Запуск асинхронной функции (в потоке)
def main():
	asyncio.run(search_hints())


# Старт скрипта
if __name__ == '__main__':
	
	# Настройка логгирования
	logging.basicConfig(filename="main.log", level=logging.INFO)
	
	# Получение последнего значения ключа
	conn = get_connection_to_db()
	global_key = get_key(conn)
	#global_key = 'яях'
	if global_key != 'яяя':		
		a = input('Последний ключ - '+global_key+\
		'. Нажмите ENTER для запуска скрипта или Ctrl+C для выхода')
		conn.close()		

		# Запуск потоков
		threads = []
		for i in range(10):
			t = threading.Thread(target=main)
			threads.append(t)
			t.start()
	else:
		print('Задача выполнена')
