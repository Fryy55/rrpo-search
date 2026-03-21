from typer import Typer
from rich.console import Console
from rich.table import Table
from rrpo_search.utils import download_xml, parse_xml, get_xml_path, get_db_conn
import os

from rapidfuzz import process, fuzz


app = Typer(
	help='[blue bold]Инструмент для поиска по РРПО[/blue bold]',
	add_completion=False,
	context_settings=dict(help_option_names=["-h", "--help"])
)
console = Console()


@app.command()
def search(query: str, raw: bool = False):
	'''[blue bold]Поиск по реестру[/blue bold]'''
	cursor = get_db_conn().cursor()
	cursor.execute('SELECT term FROM reestr_vocab')
	vocab = list[str](map(lambda x: x[0], cursor.fetchall()))

	matches = list[str]()
	for word in query.split():
		match = process.extractOne(word, vocab, scorer=fuzz.token_sort_ratio)
		if match is not None:
			matches.append(match[0])

	cursor.execute('SELECT name FROM reestr WHERE reestr MATCH ? LIMIT 50', (' '.join(matches),))
	print(cursor.fetchall())
	if 1 < len(matches):
		for i in matches:
			cursor.execute('SELECT name FROM reestr WHERE reestr MATCH ? LIMIT 10', (i,))
			print(cursor.fetchall())


@app.command()
def refresh():
	'''[blue bold]Обновление сохраненного реестра[/blue bold]'''
	console.print('[blue bold]Обновление реестра...[/blue bold]')
	#download_xml()
	parse_xml()
	console.print('[blue bold]Удаление временного XML...[/blue bold]')
	#os.remove(get_xml_path())
	console.print('[blue green]Реестр обновлен![/blue green]')


if __name__ == "main":
	app()