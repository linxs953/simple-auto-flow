from time import sleep
from creat_app import creat_app
import logging

def setup():
	sleep(300)


def stop_schedule():
	sleep(90)

def main():
	app = creat_app('development')
	maps=app.url_map
	print(str(maps))
	app.run(port=app.config['PORT'], debug=app.config['DEBUG'])

if __name__ == '__main__':
	main()