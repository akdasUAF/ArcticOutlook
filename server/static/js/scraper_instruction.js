// Nested List for more complicated commands
commands = {
    "skip_to_tag":["Parameter"],
    "skip_to_class": ["Parameter"],
    "save_value_as_property": ["Column Name"],
    "save_attribute_as_property": ["Column Name", "Tag"], // param, tag is the actual order the scraper expects!
    "back_to_beginning": [],
    "skip_to_element_with_attribute": ["Tag", "Attribute", "Value"],
    "click_element":[],
    "goto_previous_page":[],
    "scrape_table":["Parameter"],
    "run_function": ["Parameter"],
    "for_each":["Tag", "Attribute", "Value", "Function Name"],
    "create_function": ["Parameter"],
    "end_function": [],
    "special_for_each": ["Pre-Selector", "Iterating Selector", "Post-Selector", "JSON Dataset Name", "Function Name", "Range"],
    "form_send_keys": ["User Input", "Tag", "Attribute", "Value"],
    "form_submit": ["Tag", "Attribute", "Value"],
    "delay": [],
    "save_url": ["Column Name"],
    "check_for_text": ["Text Value", "Column Name"],
    "for_list": ["JSON Dataset Name"]
}
// Can update 'counter' for addInput to just be param / tag / attribute / etc. for backend records
var elements = document.getElementsByClassName("cmdBtn");

function skipToTag()
{
    var div = addInputGroup();
    div.appendChild(addLabel(commands["skip_to_tag"][0]));
    div.appendChild(addInput("skip_to_tag", "parameter", false));
    
    var mainDiv = createMainDiv("skip_to_tag");
    mainDiv.appendChild(div);
    return mainDiv;
}

function skipToClass()
{
    var div = addInputGroup();
    div.appendChild(addLabel(commands["skip_to_class"][0]));
    div.appendChild(addInput("skip_to_class", "parameter", false));
    
    var mainDiv = createMainDiv("skip_to_class");
    mainDiv.appendChild(div);
    return mainDiv;
}

function saveValueAsProperty()
{
    var div = addInputGroup();
    div.appendChild(addLabel(commands["save_value_as_property"][0]));
    div.appendChild(addInput("save_value_as_property", "parameter", false));
    
    var mainDiv = createMainDiv("save_value_as_property");
    mainDiv.appendChild(div);
    return mainDiv;
}

function saveAttributeAsProperty()
{
    var div = addInputGroup();
    div.appendChild(addLabel(commands["save_attribute_as_property"][0]));
    div.appendChild(addInput("save_attribute_as_property", "parameter", false));
    div.appendChild(addLabel(commands["save_attribute_as_property"][1]));
    div.appendChild(addInput("save_attribute_as_property", "tag", false));
    
    var mainDiv = createMainDiv("save_attribute_as_property");
    mainDiv.appendChild(div);
    return mainDiv;
}

function backToBeginning()
{
    var mainDiv = createMainDiv("back_to_beginning");
    return mainDiv;
}

function skipToElementWithAttribute()
{
    var div = addInputGroup();
    div.appendChild(addLabel(commands["skip_to_element_with_attribute"][0]));
    div.appendChild(addInput("skip_to_element_with_attribute", "tag", false));
    div.appendChild(addLabel(commands["skip_to_element_with_attribute"][1]));
    div.appendChild(addInput("skip_to_element_with_attribute", "attribute", false));
    div.appendChild(addLabel(commands["skip_to_element_with_attribute"][2]));
    div.appendChild(addInput("skip_to_element_with_attribute", "value", false));

    var mainDiv = createMainDiv("skip_to_element_with_attribute");
    mainDiv.appendChild(div);
    return mainDiv;
}

function clickElement()
{   
    var mainDiv = createMainDiv("click_element");
    return mainDiv;
}

function gotoPreviousPage()
{   
    var mainDiv = createMainDiv("goto_previous_page");
    return mainDiv;
}

function scrapeTable()
{
    var div = addInputGroup();
    div.appendChild(addLabel(commands["scrape_table"][0]));
    div.appendChild(addInput("scrape_table", "parameter", false));
    
    var mainDiv = createMainDiv("scrape_table");
    mainDiv.appendChild(div);
    return mainDiv;
}

function runFunction()
{
    var div = addInputGroup();
    div.appendChild(addLabel(commands["run_function"][0]));
    div.appendChild(addInput("run_function", "parameter", false));

    var mainDiv = createMainDiv("run_function");
    mainDiv.appendChild(div);
    return mainDiv;
}

function forEach()
{
    var div = addInputGroup();
    div.appendChild(addLabel(commands["for_each"][0]));
    div.appendChild(addInput("for_each", "tag", false));
    div.appendChild(addLabel(commands["for_each"][1]));
    div.appendChild(addInput("for_each", "attribute", false));

    var div2 = addInputGroup();
    div2.appendChild(addLabel(commands["for_each"][2]));
    div2.appendChild(addInput("for_each", "value", false));
    div2.appendChild(addLabel(commands["for_each"][3]));
    div2.appendChild(addInput("for_each", "function_name", false));
    
    var mainDiv = createMainDiv("for_each");
    mainDiv.appendChild(div);
    mainDiv.appendChild(div2);
    return mainDiv;
}

function createFunction()
{
    var div = addInputGroup();
    div.appendChild(addLabel(commands["create_function"][0]));
    div.appendChild(addInput("create_function", "parameter", false));

    var mainDiv = createMainDiv("create_function");
    mainDiv.appendChild(div);
    return mainDiv;
}

function endFunction()
{
    var mainDiv = createMainDiv("end_function");
    return mainDiv;
}

function specialForEach()
{
    var div = addInputGroup();
    div.appendChild(addLabel(commands["special_for_each"][0]));
    div.appendChild(addInput("special_for_each", "parameter", false));
    div.appendChild(addLabel(commands["special_for_each"][1]));
    div.appendChild(addInput("for_each", "tag", false));
    div.appendChild(addLabel(commands["special_for_each"][2]));
    div.appendChild(addInput("special_for_each", "attribute", false));

    var div2 = addInputGroup();
    div2.appendChild(addLabel(commands["special_for_each"][3]));
    div2.appendChild(addInput("special_for_each", "value", false));
    div2.appendChild(addLabel(commands["special_for_each"][4]));
    div2.appendChild(addInput("special_for_each", "function_name", false));
    div2.appendChild(addLabel(commands["special_for_each"][5]));
    div2.appendChild(addInput("special_for_each", "range", false));
    
    var mainDiv = createMainDiv("special_for_each");
    mainDiv.appendChild(div);
    mainDiv.appendChild(div2);
    return mainDiv;
}

function formSendKeys()
{
   var div = addInputGroup();
   div.appendChild(addLabel(commands["form_send_keys"][0]));
   div.appendChild(addInput("form_send_keys", "parameter", false));
   div.appendChild(addLabel(commands["form_send_keys"][1]));
   div.appendChild(addInput("form_send_keys", "tag", false));

   var div2 = addInputGroup();
   div2.appendChild(addLabel(commands["form_send_keys"][2]));
   div2.appendChild(addInput("form_send_keys", "attribute", false));
   div2.appendChild(addLabel(commands["form_send_keys"][3]));
   div2.appendChild(addInput("form_send_keys", "value", false));
   
   var mainDiv = createMainDiv("form_send_keys");
   mainDiv.appendChild(div);
   mainDiv.appendChild(div2);
   return mainDiv;
}

function formSubmit()
{
    var div = addInputGroup();
    div.appendChild(addLabel(commands["form_submit"][0]));
    div.appendChild(addInput("form_submit", "tag", false));
    div.appendChild(addLabel(commands["form_submit"][1]));
    div.appendChild(addInput("form_submit", "attribute", false));
    div.appendChild(addLabel(commands["form_submit"][2]));
    div.appendChild(addInput("form_submit", "value", false));

    var mainDiv = createMainDiv("form_submit");
    mainDiv.appendChild(div);
    return mainDiv;
}

function delay()
{
    var mainDiv = createMainDiv("delay");
    return mainDiv;
}

function saveURL()
{
    var div = addInputGroup();
    div.appendChild(addLabel(commands["save_url"][0]));
    div.appendChild(addInput("save_url", "parameter", false));

    var mainDiv = createMainDiv("save_url");
    mainDiv.appendChild(div);
    return mainDiv;
}

function checkForText()
{
    var div = addInputGroup();
    div.appendChild(addLabel(commands["check_for_text"][0]));
    div.appendChild(addInput("check_for_text", "parameter", false));
    div.appendChild(addLabel(commands["check_for_text"][1]));
    div.appendChild(addInput("check_for_text", "value", false));

    var mainDiv = createMainDiv("check_for_text");
    mainDiv.appendChild(div);
    return mainDiv;
}

function forList()
{
    // ["JSON Dataset Name"]
    var div = addInputGroup();
    div.appendChild(addLabel(commands["for_list"][0]));
    div.appendChild(addInput("for_list", "function_name", false));

    var mainDiv = createMainDiv("for_list");
    mainDiv.appendChild(div);
    return mainDiv;
}

// Function to create user comments input
function addCommentField()
{
    var div = addInputGroup();
    div.appendChild(addLabel("User Notes"));
    var inputText = document.createElement("textarea");
    inputText.setAttribute("class", "form-control");
    inputText.setAttribute("rows", "1");
    inputText.setAttribute("name", "notes");
    div.appendChild(inputText);
    return div;
}

// Function to create name of query step field
function addNameField()
{
    var div = addInputGroup();
    div.appendChild(addLabel("Name"));
    div.appendChild(addInput("name", -1, false));
    
    var btn = document.createElement("button");
    btn.setAttribute("type", "button");
    btn.setAttribute("class", "btn btn-info");
    btn.setAttribute("id", "show-step");
    btn.textContent = "Hide";

    var deleteBtn = document.createElement("button");
    deleteBtn.setAttribute("type", "button");
    deleteBtn.setAttribute("class", "btn btn-danger");
    deleteBtn.setAttribute("id", "delete-step");
    deleteBtn.textContent = "X";
    
    div.appendChild(deleteBtn);
    div.appendChild(btn);
    return div;
}

// Function to create an input group (text field)
function addInputGroup()
{
    var div = document.createElement("div");
    div.setAttribute("class", "input-group mb-3");
    return div;
}

function addLabel(text)
{
    // Function adds a span / label to the input div
    var span = document.createElement("span");
    span.setAttribute("class", "input-group-text");
    span.textContent = text;
    return span;
}

function createMainDiv(id)
{
    var mainDiv = document.createElement("div");
    mainDiv.setAttribute("class", "scraper-contents");
    mainDiv.setAttribute("id", id);
    return mainDiv;
}

function addIcon()
{
    // Function adds a draggable icon to the input div
    var icon = document.createElement("i");
    icon.setAttribute("class", "fa-solid fa-arrows-up-down-left-right handle");
    return icon;
}

function addInput(id, cmd, dropdown)
{
    // Function adds a text input to the input div. The id is set to the <command_inputNumber>
    var input = "";
    if (dropdown === true)
    {
        input = document.createElement("select");
        input.setAttribute("class", "form-select");

        var str = document.createElement("option");
        str.text = "String";
        str.value = "string";

        var dbl = document.createElement("option");
        dbl.text = "Double";
        dbl.value = "double";

        var i = document.createElement("option");
        i.text = "Integer";
        i.value = "integer";
        input.appendChild(str);
        input.appendChild(dbl);
        input.appendChild(i);
    }
    else
    {
        input = document.createElement("input");
        input.setAttribute("class", "form-control user-text");
        input.setAttribute("type", "text");
    }
    var temp = id.concat("_", cmd);

    input.setAttribute("name", temp);
    return input;
}

function addTempUl()
{
    var tempUl = document.createElement("div");
    tempUl.setAttribute("class", "nested-sortable");
    tempUl.setAttribute("data-nest", "2");
    return tempUl;
}

// Function that rotates the color of the list as an item is added/moved
function updateColorIndex()
{
    $('.scraper-step').each(function( index, value ) {
        var step = $(this).children('.scraper-contents')[0].getAttribute('id');
        $(this).attr('data-id', 'step-'+index+'-'+step);
        var color = "";
        if ((($(this).hasClass('final'))===false) && (($(this).hasClass('index'))===false))
        {
            switch(index%4)
            {
                case 0:
                    color="info";
                    break;
                case 1:
                    color="primary";
                    break;
                case 2:
                    color="success";
                    break;
                case 3:
                    color="secondary";
                    break;
            }
            $(this).attr('class', function(i, c){
                return c.replace(/(^|\s)list-group-item-\S+/g, '');
            }).addClass('list-group-item-'+color);
        }
    });
}

function loopSortable(sortables, id)
{
    for (var i = 0; i < sortables.length; i++) {
        new Sortable(sortables[i], {
            group: 'nested',
            animation: 150,
            fallbackOnBody: true,
            swapThreshold: 0.65,
            handle: '.handle',
            filtered: ['.final', '.index'],
            onChoose   : function(e){ $('html').addClass('grabbing'); }, // Dragging started
            onStart    : function(e){ $('html').addClass('grabbing'); }, // Dragging started
            onUnchoose : function(e){ $('html').removeClass('grabbing'); }, // Dragging started
            // https://github.com/SortableJS/Sortable/issues/1739
            onEnd      : function(e){
                // Dragging ended
                $('html').removeClass('grabbing');
                var data_id = 0;
                        
                // check for level change
                var from_lvl = parseInt($(e.from).attr('data-nest'));
                var to_lvl = parseInt($(e.to).attr('data-nest'));
                var diff = to_lvl - from_lvl;
                if (diff !== 0) {
                    // update nested nests
                    $(e.item).find('*').addBack().filter('.nested-sortable').each(function(){
                        var old_lvl = parseInt($(this).attr('data-nest'));
                        var new_lvl = old_lvl + diff;
                        $(this).attr('data-nest', new_lvl);
                    });
                    // update other items
                    $(e.item).find('*').addBack().filter('.scraper-step').each(function(){
                        var old_lvl = parseInt($(this).attr('data-lvl'));
                        var new_lvl = old_lvl + diff;
                        $(this).attr('data-lvl', new_lvl);
                        $(this).attr('class', function(i, c){
                            return c.replace(/(^|\s)nested-\S+/g, '');
                        }).addClass('nested-'+new_lvl);
                    });
                    // update topmost item
                    $(e.item).first().attr('data-lvl', to_lvl);
                }
    
                // serialize
                var order = JSON.stringify( serialize( $(id)[0] ) );
                // pretty output
                var json_out = JSON.stringify(JSON.parse(order),null,2);
                updateColorIndex();

            }
        });}
}

function getActiveList()
{
    // Function to return active tab so the new instruction is added correctly
    var id = $("ul#scraperTabs li button.active").attr('id');
    if (id === "scraper-tab")
    {
        return document.getElementById("instructions");
    }
    else
    {
        return document.getElementById("functions");
    }
}

// Adds a list item to the sortable list
function addLi() {
    var tab = getActiveList();
    var id = this.getAttribute("id");
    var btnName = this.textContent;
    //var counter = 0;
    var newLi = document.createElement("div");

    newLi.setAttribute("class", "scraper-step list-group-item list-group-item-action nested-1");
    newLi.appendChild((addIcon()));

    newLi.setAttribute("data-lvl", "1");
    newLi.appendChild(document.createTextNode(" "+btnName));
    newLi.appendChild(addNameField());

    switch(id) {
        case "skip_to_tag":
            mainDiv = skipToTag();
            break;
        case "skip_to_class":
            mainDiv = skipToClass();
            break;
        case "save_value_as_property":
            mainDiv = saveValueAsProperty();
            break;
        case "save_attribute_as_property":
            mainDiv = saveAttributeAsProperty();
            break;
        case "back_to_beginning":
            mainDiv = backToBeginning();
            break;
        case "skip_to_element_with_attribute":
            mainDiv = skipToElementWithAttribute();
            break;
        case "click_element":
            mainDiv = clickElement();
            break;
        case "goto_previous_page":
            mainDiv = gotoPreviousPage();
            break;
        case "scrape_table":
            mainDiv = scrapeTable();
            break;
        case "run_function":
            mainDiv = runFunction();
            break;
        case "for_each":
            mainDiv = forEach();
            break;
        case "create_function":
            mainDiv = createFunction();
            break;
        case "end_function":
            mainDiv = endFunction();
            break;
        case "special_for_each":
            mainDiv = specialForEach();
            break;
        case "form_send_keys":
            mainDiv = formSendKeys();
            break;
        case "form_submit":
            mainDiv = formSubmit();
            break;
        case "delay":
            mainDiv = delay();
            break;
        case "save_url":
            mainDiv = saveURL();
            break;
        case "check_for_text":
                mainDiv = checkForText();
                break;
        case "for_list":
            mainDiv = forList();
            break;
        default:
            break
    }
    newLi.appendChild(mainDiv);
    newLi.appendChild(addCommentField());

    newLi.appendChild(addTempUl());
    tab.appendChild(newLi);

    // Loop through each nested sortable element
    var scraperSortables = [].slice.call(document.querySelectorAll('#scraper-instruction-list .nested-sortable'));
    console.log(scraperSortables);
    var functionSortables = [].slice.call(document.querySelectorAll('#function-list .nested-sortable'));
    loopSortable(scraperSortables, "#instructions");
    loopSortable(functionSortables, "#functions");
    
    // Call function to update alternating colors
    updateColorIndex();

    // If there is a specific character/character combination located within the input, change the color of the text
    $(document).ready(function(){
        $(".user-text").on("input", function(){
            // If the text contains '@', change color to red
            if ($(this).val().includes('@'))
            {
                $(this).css("color", "red");
            }

            else if ($(this).val().includes('$'))
            {
                $(this).css("color", "green");
            }
            // Else, change color to default (black)
            else
            {
                $(this).css("color", "black");
            }
    })})
    
    
}

// Function that fills the newly created list with saved user input
function fillHTML(div, data)
{
    // Set the current div
    var elem = div.children;
    // Loop through each item in the data array
    for (var x = 0; x < data.length; x++)
    {
        // Select the current step and contents/fields of the step.
        console.log("Loop");
        var cmd = data[x];
        //console.log(cmd);
        console.log(cmd["contents"]);
        var con = cmd["contents"];

        // Select all the input fields
        console.log(x);
        var fields = elem[x].querySelectorAll('input');
        console.log(fields);
        console.log(con.length);

        // Select the textarea representing a query step's notes
        var notes = elem[x].querySelector('textarea');
        
        // Set the name and notes fields of the query
        fields[0].value = cmd["name"];
        //console.log(cmd);
        //notes.value = cmd["notes"];

        // Loop through each input field of the query and fill in previously saved data
        for (var y = 0; y < con.length; y++)
        {
            fields[y+1].value = con[y]["contents"];
        }

        // If this step has nested steps, call this function again.
        if (cmd["subs"].length)
        {
            var e = elem[x].children;
            var nestedList = e[e.length-1];
            fillHTML(nestedList, cmd["subs"]);
        }
    }
}

// Function that repopulates the page with a loaded query
function populateFuncJS(data)
{
    var div = document.getElementById("functions");
    div.textContent = '';
    data[1].pop();
    var mainName = document.getElementById("func_name");
    mainName.value = data[0];
    div.innerHTML = data[2];
    // console.log(data);
    // console.log(data[1]);
    fillHTML(div, data[1]);
}

// Function that repopulates the page with a loaded query
function populateInstrJS(data)
{
    var div = document.getElementById("instructions");
    div.textContent = '';
    data[1].pop(); // Remove instruction list url
    data[1].pop(); // Remove instruction list name
    var mainName = document.getElementById("scraper_name");
    var url = document.getElementById("url");
    mainName.value = data[0];
    url.value = data[3];
    div.innerHTML = data[2];
    fillHTML(div, data[1]);
}

// initialize all cmdBtns to have same event listener
for (var i = 0; i < elements.length; i++) {
    elements[i].addEventListener('click', addLi);
}