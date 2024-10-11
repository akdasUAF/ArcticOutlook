##### skip_to_tag = 1
This instruction will skip from the current scraper position to the next located [HTML Element](https://www.w3schools.com/TAGS/default.asp) provided by the user.  

| Input Name | User Input     |
| ---------- | -------------- |
| Parameter  | A HTML element |
|            |                |
###### Example
Say there is a div with a span that contains text we need to save.
```html
<div class="test">
	<span>Hello World</span>
</div>
```

Say I use the instruction with the following input:

| Input Name | User Input |
| ---------- | ---------- |
| Parameter  | span       |
This will move the scraper to the first *span* it finds *after* it's current location.
##### skip_to_class = 2
This instruction will skip from the current scraper position to the next element with the class value specified by the user.

| Input Name | User Input     |
| ---------- | -------------- |
| Parameter  | A HTML element |
###### Example
Say there is a div with a class called *test* located after where my scraper is currently located.
```html
<div class="test">
</div>
```

Say I use the instruction with the following input:

| Input Name | User Input |
| ---------- | ---------- |
| Parameter  | test       |
This will skip the scraper to the first element it finds with this class name *after* it's current location.
##### save_value_as_property = 3
This instruction will tell the scraper to scrape the current item and save it as the name given by the user. This defaults to the [innerText](https://developer.mozilla.org/en-US/docs/Web/API/HTMLElement/innerText), which will save the text inside of the element.

| Input Name | User Input   |
| ---------- | ------------ |
| Parameter  | div, a, etc. |
###### Example
Say the scraper is currently looking at the element below.
```html
<td>AK2123456</td>
```

Say I use the instruction with the following input:

| Input Name | User Input        |
| ---------- | ----------------- |
| Parameter  | WaterSystemNumber |
This will save the value into *WaterSystemNumber*, and I will receive the following json as output:
```json
{
	"WaterSystemNumber": "AK2123456"
}
```

##### save_attribute_as_property = 4
This instruction will tell the scraper to scrape a specific [HTML Attribute](https://www.w3schools.com/html/html_attributes.asp) of the current item and save it as the name given by the user.

| Input Name | Expected User Input         |
| ---------- | --------------------------- |
| Parameter  | The name of the saved value |
| Tag        | An HTML Attribute           |
###### Example
Say the scraper is currently looking at the element below.
```html
<a href="www.google.com">Google.com</a>
```

If I use:

| Input Name | User Input |
| ---------- | ---------- |
| Parameter  | UrlLink    |
| Tag        | href       |
This will save the **href** value into *UrlLink*, and I will receive the following json as output:
```json
{
	"UrlLink": "www.google.com"
}
```

##### back_to_beginning = 5
This instruction will tell the scraper to return to the start of the webpage it is currently looking at.
##### skip_to_element_with_attribute = 6
This instruction will tell the scraper to skip to a [HTML Element](https://www.w3schools.com/TAGS/default.asp) with a specific [HTML Attribute](https://www.w3schools.com/html/html_attributes.asp) value.

| Input Name | Expected User Input                   |
| ---------- | ------------------------------------- |
| Tag        | A HTML Element                        |
| Attribute  | A HTML Attribute                      |
| Value      | The value of the given HTML Attribute |
###### Example
Say there is a webpage that has something like this:
```html
<div id="test-div">
	<table id="test-table">Google.com</a>
</div>
```

If I use skip_to_element_with_attribute with the following input:

| Input Name | User Input |
| ---------- | ---------- |
| Tag        | table      |
| Attribute  | id         |
| Value      | test-table |
This will skip the scraper until it finds an *table* with an id equal to *test-table*.
##### click_element = 7
This instruction will tell the scraper to click the element the scraper is currently looking at.
- If this redirects to a new page (form submit), the scraper will follow to a new page.
- This instruction will always return the scraper to the top of the page!
##### goto_previous_page = 8
This instruction will tell the scraper to return to the previous webpage.
- This will also return the scraper to the top of the previous webpage.
##### scrape_table = 9
This instruction will tell the scraper to scrape a table.
- The instruction expects that the scraper is looking at a table.
- The instruction expects that the table is formatted as a regular table.
	- Columns
		- Column names should be wrapped in the *th* tag.
		- Column names will be recorded as the innerText of the *th* tag.
	- Rows
		- Row values should be wrapped in the *td* tag
		- Row values will be recorded as the innerText of the *td* tag.

| Input Name | Expected User Input              |
| ---------- | -------------------------------- |
| Parameter  | The user given name of the table |
###### Example
Say that there is a table with the following contents. Note that our scraper is currently looking at this table (if it is not, you will need to skip to it first):
```html
<table id = "table-test">
	<tr>
		<th>Name</th>
		<th>Date</th>
	</tr>
	<tr>
		<td>John Doe</td>
		<td>04/20/1999</td>
	</tr>
	<tr>
		<td>Jane Doe</td>
		<td>04/20/2099</td>
	</tr>
</table>
```

And that I call scrape_table with the following input:

| Input Name | User Input |
| ---------- | ---------- |
| Parameter  | TestTable  |
I will receive the following json as the output:
```json
{
	"TestTable":
	[
		{
			"Name": "John Doe",
			"Date": "04/20/1999"
		},
		{
			"Name": "Jane Doe",
			"Date": "04/20/2099"
			
		}
	]
}
```
##### run_function = 10
This instruction will run a user defined function. This function is defined previously in the instruction list and is called by the name specified in the *create_function* instruction.

| Input Name | Expected User Input                 |
| ---------- | ----------------------------------- |
| Parameter  | The name of a user defined function |
##### for_each = 11
This instruction will loop over all items within a group. For each item found on the page that matches a html item with a specific tag value, this instruction will attempt to run a user defined function (see *create_function*).

| Input Name    | Expected User Input                   |
| ------------- | ------------------------------------- |
| Tag           | A HTML Element                        |
| Attribute     | A HTML Attribute                      |
| Value         | The value of the given HTML Attribute |
| Function Name | Name of a user defined function       |
###### Example
Say I have a list of items in a div on a webpage.
```html
<div id="operators">
	<span><a href=".../john-doe" title="operator-name">John Doe</a></span>
	<span><a href=".../jane-doe" title="operator-name">Jane Doe</a></span>
</div>
```

For this example, say that I have defined a function named 'OperatorInfo'. This function will follow the link and pull some information off of the subsequent webpage. If I wanted to use this function on every link within this div, I could use the *for_each* instruction to create a list of each of these items. 

| Input Name    | Expected User Input |
| ------------- | ------------------- |
| Tag           | span                |
| Attribute     | title               |
| Value         | operator-name       |
| Function Name | OperatorInfo        |
This would result in the scraper attempting to use this OperatorInfo function on each a element that has the title "operator-name".
##### create_function = 12
This instruction will start the creation of a user defined function. This should be used primarily if a list of instructions should be repeated multiple times. All instructions given after *create_function* will be assumed as part of the function up until it reaches an *end_function* instruction. This function can be called with *run_function*, or within a loop.

| Input Name | Expected User Input                 |
| ---------- | ----------------------------------- |
| Parameter  | The name of a user defined function |
##### end_function = 13
This instruction will end the creation of a user defined function. All instructions between this instruction and *create_function* will be assumed to be one function under the name specified in *create_function*.
##### special_for_each = 14
This instruction is very similar to *for_each*. This is used when you need to iterate over a list of items (HTML elements) that may have duplicates. (For example: the drinking water watch table provides the same url link and title for the PWSID and water system name links.)

| Input Name    | Expected User Input                                                         |
| ------------- | --------------------------------------------------------------------------- |
| Parameter     | The part of the CSS Selector *before* the iteration.                        |
| Tag           | The HTML Element that is being iterated                                     |
| Attribute     | The part of the CSS Selector *after* the iteration (this can be left blank) |
| Value         | The name of the list of saved values within the json file                   |
| Function Name | Name of a user defined function                                             |
###### Example
Say we have a table that we want to scrape / interact with *only* the first column of each row. We have previously defined a function 'WaterSystems' that will scrape the relevant data. The CSS-Selectors for the first 2 rows are as follows (bolded is the iteration):

.col-md-12 > table:nth-child(3) > tbody:nth-child(1) > **tr:nth-child(2)** > td:nth-child(1) > a:nth-child(1)
.col-md-12 > table:nth-child(3) > tbody:nth-child(1) > **tr:nth-child(3)** > td:nth-child(1) > a:nth-child(1)

We can use this information with this instruction with the following inputs to perform our loop:

| Input Name    | Expected User Input                                  |
| ------------- | ---------------------------------------------------- |
| Parameter     | .col-md-12 > table:nth-child(3) > tbody:nth-child(1) |
| Tag           | tr                                                   |
| Attribute     | td:nth-child(1) > a:nth-child(1)                     |
| Value         | Systems                                              |
| Function Name | WaterSystems                                         |
##### form_send_keys = 15
This instruction allows the user to interact with the webpage by providing user input.
- *select* tags require an option with a valid *value* attribute to ensure they can be selected
- More form options can be implemented as needed.

| Input Name | Expected User Input                   |
| ---------- | ------------------------------------- |
| Parameter  | The user input                        |
| Tag        | A HTML Element                        |
| Attribute  | A HTML Attribute                      |
| Value      | The value of the given HTML Attribute |

###### Select Example
Say I have a webpage that looks something like this:
```html
<div id="form-test">
	<select id="select-test">
		<option value="name">Name</option>
		<option value="date">Date</option>
	</select>
	<input id="input-test" type="text">
	<input id="submit-test" type="submit">
</div>
```
To continue scraping, I need to sort a list by Name. To do this, I would provide the following input to *form_send_keys*:

| Input Name |  User Input |
| ---------- | ----------- |
| Parameter  | name        |
| Tag        | select      |
| Attribute  | id          |
| Value      | select-test |

###### Text Example
Say I have a webpage that looks something like this:
```html
<div id="form-test">
	<select id="select-test">
		<option value="name">Name</option>
		<option value="date">Date</option>
	</select>
	<input id="input-test" type="text">
	<input id="submit-test" type="submit">
</div>
```
To continue scraping, I need to input "Fairbanks" into the search bar *input-test*. To do this, I would provide the following input to *form_send_keys*.

| Input Name |  User Input |
| ---------- | ----------- |
| Parameter  | Fairbanks   |
| Tag        | input       |
| Attribute  | id          |
| Value      | input-test  |

##### form_submit = 16
This instruction will attempt to submit a form by clicking a button. The user can specify which button on the page is the correct button to submit a form. After this instruction, the scraper will return to the top of the webpage as seen in [[#back_to_beginning = 5]]. If submitting the form redirects to a new page, this will result in the scraper looking at the top of the next page.

| Input Name | Expected User Input                   |
| ---------- | ------------------------------------- |
| Tag        | A HTML Element                        |
| Attribute  | A HTML Attribute                      |
| Value      | The value of the given HTML Attribute |
###### Example
Say I have a webpage that looks something like this:
```html
<div id="form-test">
	<select id="select-test">
		<option value="name">Name</option>
		<option value="date">Date</option>
	</select>
	<input id="input-test" type="text">
	<input id="submit-test" type="submit">
</div>
```

| Input Name |  User Input |
| ---------- | ----------- |
| Tag        | input       |
| Attribute  | id          |
| Value      | submit-test |
This will result in the form being submitted.
##### delay = 17
This instruction will tell the scraper to delay for a certain amount of time. This is primarily used to ensure that the webpage has enough time to load before continuing a scrape.