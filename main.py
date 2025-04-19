from showroom import app, db_handler

if __name__ == '__main__':
    with app.app_context():
        db_handler.init()
    app.run(debug=True)
