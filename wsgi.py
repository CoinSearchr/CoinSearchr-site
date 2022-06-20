from coinsearchr import app

if __name__ == "__main__":
	if app.debug:
		app.run(host='0.0.0.0')
	else:
		app.run()

