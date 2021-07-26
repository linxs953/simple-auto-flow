from flask import Flask, current_app
from config import config, CONFIG
import logging
from logging import handlers


def creat_app(env):
	if env is None:
		env = CONFIG.FLASK_ENV
	app = Flask('_app_', static_folder='./test_case_app/static')
	app.config.from_object(config[env])

	register_logging(app)
	register_blueprints(app)

	return app


def register_logging(app):
	app.config.setdefault("LOG_PATH", "application.log")

	log_formatter = "%(asctime)s [%(thread)d:%(threadName)s] %(filename)s:%(module)s:%(funcName)s in %(lineno)d] [%(levelname)s]: %(message)s"
	app.config.setdefault("LOG_FORMATTER", log_formatter)
	app.config.setdefault("LOG_MAX_BYTES", 50 * 1024 * 1024)
	app.config.setdefault("LOG_BACKUP_COUNT", 10)
	app.config.setdefault("LOG_INTERVAL", 1)
	app.config.setdefault("LOG_WHEN", "D")
	app.config.setdefault("LOG_LEVEL", "INFO")

	formatter = logging.Formatter(app.config["LOG_FORMATTER"])
	# 将日志输出到文件
	# 指定间隔时间自动生成文件的处理器
	# 实例化TimedRotatingFileHandler
	# interval是时间间隔，
	# backupCount是备份文件的个数，如果超过这个个数，就会自动删除
	# when是间隔的时间单位，单位有以下几种：
	# S 秒
	# M 分
	# H 小时、
	# D 天、
	# W 每星期（interval==0时代表星期一）
	# midnight 每天凌晨
	timed_rotating_file_handler = handlers.TimedRotatingFileHandler(
		filename=app.config["LOG_PATH"],
		interval=app.config["LOG_INTERVAL"],
		when=app.config["LOG_WHEN"],
		backupCount=app.config["LOG_BACKUP_COUNT"],
		encoding="utf-8",
	)

	timed_rotating_file_handler.setFormatter(formatter)  # 设置文件里写入的格式
	timed_rotating_file_handler.setLevel(app.config["LOG_LEVEL"])

	# StreamHandler
	stream_handler = logging.StreamHandler()
	stream_handler.setFormatter(formatter)
	stream_handler.setLevel(app.config["LOG_LEVEL"])

	# SMTPHandler
	mail_handler = handlers.SMTPHandler(
		mailhost=app.config["EMAIL_HOST"],
		credentials=app.config["CREDENTIALS"],
		fromaddr=app.config["EMAIL_SENDER"],
		toaddrs=app.config["EMAIL_RECEIVER"],
		subject=app.config["SUBJECT"],
	)
	mail_handler.setLevel(logging.ERROR)
	mail_handler.setFormatter(formatter)


def register_blueprints(app):
	from test_case_app.test_case_app import test
	app.register_blueprint(test, url_prefix='/test')
