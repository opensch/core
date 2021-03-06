# Replacements (Замены)

## Что это такое?
Замены в openSchool - способ индикации, что на какой-либо день должна произойти замена урока в расписании. В базе данных **НЕ** создаются новые расписания с измененными уроками. Для упрощения хранения в отдельной коллекции создаются отсылки на конкретный день и класс, в которых хранится список новых уроков.


## Где храниться и как использовать?
Замены храняться в коллекции `replacements` в базе данных. Для того, чтобы подключиться к ней, введите:
        ```
        import classes

        connection = classes.createMongo()
        database = connection.replacements
        ```

Но более правильным способом работы с базой данных является класс `Replacement` (см. `classes.py` или документацию класса ниже).


## Структура блока замены в базе данных
	* `date` - число в формате ДД.ММ.ГГГГ
        * `classNumber` -  номер класса
        * `classLetter` - буква класса (если её нету, то `A`)
        * `lessons` - список с обновленными ID уроками

* Заметка 1) Список с ID уроками должен иметь **одинаковую** длину c со списком уроков из расписания на тот же день недели. 
* Заметка 2) В списке с уроками ID могут быть прописаны вместе с префиксами - знаками о том, какой это тип урока (индивидуальный, общий и т.д).
* Заметка 3) Список с уроками прописывается **только** в тех местах, где нужно произвести замену. Остальные же позиции заполняются `-`.


## Префиксы для уроков в расписании 
* `A` - урок для всего класса (все уроки для 1-9 класса, кроме рз. часа, имеют этот префикс)
* `I` - индивидуальный урок. При генерации расписания, будет использоваться `uniqLessons` у `User`. Развивающие часы заполняются с этим префиксом
* `,` - перебор уроков через запятую равносилен `I`
* Если префикса нет, то будет использоваться `A`


## Документация класса `Replacement`
Переменные класса:
	* `date` - дата в виде инстанции Python класса `datetime` 
        * `classNumber` - номер класса
        * `classLetter` - буква класса
        * `lessons` - список со строчками, в которых прописаны ID уроков и префиксы

Методы:
        * `toJSON()`
                * Назначение: перевести данные из текущей инстанции класса в Python словарь
                * Аргументы: ничего 
                * Возращает: Python словарь

        * `fromJSON()`
                * Назначение: создать инстанцию класса `Replacement` из данных, которые находятся в указанном Python словаре.
                * Аргументы:
                        * `json_entry` - Python словарь
                * Возращает: инстанция Python класса `Replacement`
	
	* `create()`
		* Назначение: создать замену одного урока на основе данных, переданных функции
		* Аргументы:
			* `date` - дата в виде инстанции Python класса `datetime`
			* `position` - позиция урока, на которую поставить замену
			* `classNumber` - номер класса
			* `classLetter` - буква класса
			* `oldLesson` - инстанция Python класса `Lesson`, содержащий старый урок. Нужно для сверки позиции, чтобы убедиться, что записываем, куда надо
			* `newLesson` - инстанция Python класса `Lesson`, содержащий новый урок. 
		* Возращает:
			* инстанция Python класса `Replacement`. Это только что созданная замена.
	
	* `edit()`
		* Назначение: отредактировать уже существующую замену на новые данные.
		* Аргументы:
                        * `date` - дата в виде инстанции Python класса `datetime`
                        * `position` - позиция урока, на которую поставить замену
                        * `classNumber` - номер класса
                        * `classLetter` - буква класса
                        * `oldLesson` - инстанция Python класса `Lesson`, содержащий старый урок. Нужно для сверки позиции, чтобы убедиться, что записываем, куда надо   
                        * `newLesson` - инстанция Python класса `Lesson`, содержащий новый урок.
                * Возращает:
                        * инстанция Python класса `Replacement`. Это только что измененная замена.

	* `delete()`
		* Назначение: удалить существующую замену.
		* Аргументы:
			* `date` - дата в виде инстанции Python класса `datetime`
                        * `position` - позиция урока, на которой замена. Можно использовать "*", чтобы удалить весь блок замены из базы данных.
                        * `classNumber` - номер класса
                        * `classLetter` - буква класса
		* Возращает: ничего
		

## Конечные точки для сервера
	* `/privAPI/createReplacement`
		* Назначение: создать замену одного урока
		* Метод: POST
		* Приватный API: да
		* Поддерживает CORS: да
		* Данные:
			* `date` - дата в формате ДД.ММ.ГГГГ
                        * `position` - позиция урока, на которую поставить замену
                        * `classNumber` - номер класса
                        * `classLetter` - буква класса
                        * `oldLesson` - JSON словарь, содержащий старый урок. Нужно для сверки позиции, чтобы убедиться, что записываем, куда надо
                        * `newLesson` - JSON словарь, содержащий новый урок.
		* Возращает при успехе:
			* Код: 200
			* Данные: ничего
		* Возращает при неудаче:
			* Код: 400
			* Данные: ничего

	* `/privAPI/editReplacement`
                * Назначение: отредактировать уже существующую замену
                * Метод: POST
                * Приватный API: да
		* Поддерживает CORS: да
                * Данные:
                        * `date` - дата в формате ДД.ММ.ГГГГ
                        * `position` - позиция урока, на которую поставить замену
                        * `classNumber` - номер класса
                        * `classLetter` - буква класса
                        * `oldLesson` - JSON словарь, содержащий старый урок. Нужно для сверки позиции, чтобы убедиться, что записываем, куда надо
                        * `newLesson` - JSON словарь, содержащий новый урок.
                * Возращает при успехе:
                        * Код: 200
                        * Данные: ничего
                * Возращает при неудаче:
                        * Код: 400
                        * Данные: ничего

	* `/privAPI/deleteReplacement`
		* Назначение: удалить существующую замену
                * Метод: POST
                * Приватный API: да
		* Поддерживает CORS: да
                * Данные:
                        * `date` - дата в формате ДД.ММ.ГГГГ
                        * `position` - позиция урока, на которой замена. Можно использовать "*", чтобы удалить весь блок замены из базы данных.
                        * `classNumber` - номер класса
                        * `classLetter` - буква класса
                * Возращает:
                        * Код: 200
                        * Данные: ничего
