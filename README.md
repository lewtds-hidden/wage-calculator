# Wage Calculator

Written as a Python Flask web app. It's recommended to use a Python 3 [virtual environment](https://docs.python.org/3/library/venv.html). All commands below must be run inside this folder.

Install dependencies:

```
pip install -r requirements.txt
```

Running on your dev machine:

```
make run-dev
```

Testing:

```
make test
```

To deploy on a production server, copy `settings_prod.cfg.example` to `settings_prod.cfg`, make neccessary changes and run this:

```
make run-prod
```

## License

HourList201403.csv is copyrighted by Solinor. All external libaries are copyrighted by their respective authors. Everything else is given to the public domain.

```
CC0

To the extent possible under law, the person who associated CC0 with this work has waived all copyright and related or neighboring rights to this work.
```