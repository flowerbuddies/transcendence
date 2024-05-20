## Add a new language

1. Add a new entry in transcendence/settings.py

```py
LANGUAGES = [
    ("en", "English"),
    ("fr", "French"),
    ("fi", "Finnish"),
    # here
]
```

2. Run the command

`django-admin makemessages -e django -l <locale code>`

## After adding a new `{% trans %}`

`django-admin makemessages -a -e django -e py`

## After translating the new string

`django-admin compilemessages`
