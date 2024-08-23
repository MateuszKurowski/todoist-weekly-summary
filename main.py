import gettext
import locale
import os
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
import requests

load_dotenv()
api_token = os.getenv('TODOIST_API_KEY')

with open('config.json', 'r') as config_file:
    config = json.load(config_file)

if config['language'] == 'pl':
    locale.setlocale(locale.LC_ALL, 'pl_PL.UTF-8')
    language = 'pl'
elif config['language'] == 'en':
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    language = 'en'
else:
    raise ValueError("Unsupported language in config.json")

locale_dir = os.path.join(os.path.dirname(__file__), 'locales')

lang = gettext.translation('messages', localedir=locale_dir, languages=[language])
lang.install()
_ = lang.gettext

today = datetime.now()
start_date = (today - timedelta(days=7)).replace(hour=0, minute=0, second=0, microsecond=0)
end_date = (today - timedelta(days=1)).replace(hour=23, minute=59, second=59, microsecond=999999)

formatted_start_date = start_date.strftime('%Y-%m-%dT%H:%M')
formatted_end_date = end_date.strftime('%Y-%m-%dT%H:%M')

print(formatted_start_date)

url = 'https://api.todoist.com/sync/v9/completed/get_all'
params = {
    'since': formatted_start_date,
    'until': formatted_end_date
}
headers = {
    "Authorization": "Bearer " + api_token
}

response = requests.get(url, params=params, headers=headers)

output_file = _('Completed tasks') + '.md'
title = _("Completed Tasks from {start_date} to {end_date}").format(
    start_date=start_date.strftime('%d %B'),
    end_date=end_date.strftime('%d %B')
)

if response.status_code == 200:
    tasks = response.json()['items']
    if tasks:
        with open(output_file, 'w', encoding='utf-8') as file:
            file.write(f"# {title}\n\n")
            for task in tasks:
                completed_at = datetime.fromisoformat(task['completed_at']).strftime('%A, %d %B %H:%M')
                file.write(f"- **{task['content']}** ({_('Completed at')}: {completed_at})\n")
        print(_("Tasks have been saved to {output_file}").format(output_file=output_file))
    else:
        print(_("No completed tasks in the specified period."))
else:
    print(_("Error: {status_code} - {response_text}").format(
        status_code=response.status_code, response_text=response.text))
