import os

basedir = os.path.abspath(os.path.dirname(__file__))


class CONFIG(object):
	# app启动设置
	HOST = '127.0.0.1'
	PORT = 5000
	DEBUG = True
	SECRET_KEY = 'hard to guess'
	FLASK_ENV = 'Development'
	# FLASK日志配置
	LOG_PATH = os.path.join(basedir, "logs", "catch.log")
	LOG_FORMATTER = (
		"%(asctime)s [%(name)s] [%(thread)d:%(threadName)s] "
		"%(filename)s:%(module)s:%(funcName)s "
		"in %(lineno)d] "
		"[%(levelname)s]: %(message)s"
	)
	LOG_MAX_BYTES = 50 * 1024 * 1024  # 日志文件大小
	LOG_BACKUP_COUNT = 10  # 备份文件数量
	LOG_INTERVAL = 1
	LOG_WHEN = "S"

	# 设置邮件发送相关参数
	EMAIL_HOST = "smtp.163.com"
	EMAIL_USER = "15884473327@163.com"
	EMAIL_PORT = "25"
	# 邮箱授权码
	EMAIL_PASSWORD = "*****"
	EMAIL_SENDER = "*****"
	CREDENTIALS = (EMAIL_SENDER, EMAIL_PASSWORD)
	SUBJECT = '测试日志'
	# 收件人
	EMAIL_RECEIVER = "15884473327@163.com"
	LOG_LEVEL = "WARN"


class Development(CONFIG):
	HOST = '127.0.0.2'
	PORT = 5000
	DEBUG = True
	LOG_LEVEL = "INFO"


class Test(CONFIG):
	pass


class Production(CONFIG):
	pass


config = {
	'development': Development,
	'testing': Test,
	'production': Production,
	'default': CONFIG
}

print(config['development'])