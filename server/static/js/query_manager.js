// Nested List for more complicated commands
commands = {
    "addFields":["Name", "Value"],
    "lookup": ["From Collection", "Local Field", "Foreign Field", "Output Field"],
    "find": ["Database", "Collection", "Field", "Value"],
    "findOne": ["Database", "Collection", "Field", "Value"],
    "index": ["Database", "Collection", "Key", "Sort Type", "Unique"],
    "coll": ["Database", "Collection Name"],
    "match":["Match"],
    "merge":["Database", "Collection", "on", "let", "If Matched", "If Not Matched"],
    "set":["Set", "as"],
    "setVariable": ["Name", "Type", "Value"],
    "out":["Database", "Collection"],
    "project": ["Field", "[0, 1]"],
    "projectMulti": ["{'Field 1': [0, 1], 'Field 2': [0, 1], etc.}"],
    "unset": ["Field"],
    "unwind": ["Array"],
    "map": ["input", "as", "in"],
    "filter": ["input", "as", "cond", "limit"],
    "concat": ["[ <expression1>, <expression2>, ... ]"],
    "concatArrays": ["[ <array1>, <array2>, ... ]"],
    "range": ["start", "end", "step"],
    "reduce": ["input", "initialValue", "in"],
    "regexMatch": ["input", "regex"],
    "substrCP": ["string", "index", "count"]
}

var list = document.getElementById("sortable");
var elements = document.getElementsByClassName("cmdBtn");

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

function addIcon()
{
    // Function adds a draggable icon to the input div
    var icon = document.createElement("i");
    icon.setAttribute("class", "fa-solid fa-arrows-up-down-left-right handle");
    return icon;
}

function addInput(id, counter, dropdown)
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
    var temp = "";
    if (counter === -1)
    {
        temp = id;
    }
    else
    {
        temp = id.concat("_", counter.toString());
    }
    input.setAttribute("name", temp);
    return input;
}

function deleteButton()
{
    // Function adds the delete / remove step button to the input div.
    var deleteDiv = document.createElement("div");
    deleteDiv.setAttribute("class", "input-group-btn");
    var deleteBtn = document.createElement("button");
    deleteBtn.setAttribute("type", "button");
    deleteBtn.setAttribute("class", "btn btn-danger");
    deleteBtn.setAttribute("id", "delete_step");
    deleteBtn.textContent = "X";
    deleteDiv.appendChild(deleteBtn);
    return deleteDiv;
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
    $('.query_step').each(function( index, value ) {
        var step = $(this).children('.query-contents')[0].getAttribute('id');
        $(this).attr('data-id', 'step_'+index+'_'+step);
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

// Adds a list item to the sortable list
function addLi() {
    var id = this.getAttribute("id");
    var btnName = this.textContent;
    var counter = 0;
    var newLi = document.createElement("div");
    var final = false;

    // Certain commands have unique colors / classes
    if (id === "merge" | id === "out")
    {
        final = true;
        newLi.setAttribute("class", "query_step list-group-item list-group-item-action list-group-item-warning nested-1 final");
    }

    else if (id === "find" | id === "findOne")
    {
        final = true;
        newLi.setAttribute("class", "query_step list-group-item list-group-item-action list-group-item-warning nested-1 final");
    }

    else if (id === "index" | id === "coll")
    {
        newLi.setAttribute("class", "query_step list-group-item list-group-item-action list-group-item-light nested-1 index");
    }

    else 
    {
        newLi.setAttribute("class", "query_step list-group-item list-group-item-action nested-1");
        newLi.appendChild((addIcon()));
    }

    newLi.setAttribute("data-lvl", "1");
    newLi.appendChild(document.createTextNode(" "+btnName));
    newLi.appendChild(addNameField());
    // Make an inner div that stores all content. This div needs to be collapsible and able to have nested li/ul

    // Create div to hold input fields
    const steps = [];
    const divs = [];
    len = commands[id].length;
    for (let i = 0; i < len / 2; i++)
    {
        divs[i] = addInputGroup()
        for (let j = 0; j < 2; j++)
        {
            if (counter >= len)
            {
                break;
            }
            divs[i].appendChild(addLabel(commands[id][counter]));
            var dropdown = false;
            if (commands[id][counter] === 'Type')
            {
                dropdown = true;
            }
            divs[i].appendChild(addInput(id, counter, dropdown));
            counter++;
        }
    }
    var mainDiv = document.createElement("div");
    mainDiv.setAttribute("class", "query-contents");
    mainDiv.setAttribute("id", id);

    divs.slice(-1)[0].appendChild(deleteButton());

    for (let i = 0; i < divs.length; i++)
    {
        mainDiv.appendChild(divs[i]);
    }

    mainDiv.appendChild(addCommentField());
    newLi.appendChild(mainDiv);

    // If there is a 'final' element (out / merge), ensure all commands are inputted before it
    var finalEle = document.getElementsByClassName('final');
    if (finalEle.length > 0)
    {
        if (final === false)
        {
            newLi.appendChild(addTempUl());
        }
        $(newLi).insertBefore('#sortable .query_step:last');
    }
    else
    {
        newLi.appendChild(addTempUl());
        list.appendChild(newLi);
    }

    // Loop through each nested sortable element
    var sortables = [].slice.call(document.querySelectorAll('.nested-sortable'));
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
                    $(e.item).find('*').addBack().filter('.query_step').each(function(){
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
                var order = JSON.stringify( serialize( $('#sortable')[0] ) );
                // pretty output
                var json_out = JSON.stringify(JSON.parse(order),null,2);
                updateColorIndex();

            }
        });}
    
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
        var cmd = data[x];
        var con = cmd["contents"];

        // Select all the input fields
        var fields = elem[x].querySelectorAll('input');

        // Select the textarea representing a query step's notes
        var notes = elem[x].querySelector('textarea');
        
        // Set the name and notes fields of the query
        fields[0].value = cmd["name"];
        notes.value = con[con.length-1]["contents"];

        // Loop through each input field of the query and fill in previously saved data
        for (var y = 0; y < con.length-1; y++)
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
function populateJS(data)
{
    var div = document.getElementById("sortable");
    div.textContent = '';
    data[1].pop();
    var mainName = document.getElementById("main_name");
    mainName.value = data[0];
    div.innerHTML = data[2];
    fillHTML(div, data[1]);
}

// initialize all cmdBtns to have same event listener
for (var i = 0; i < elements.length; i++) {
    elements[i].addEventListener('click', addLi);
}