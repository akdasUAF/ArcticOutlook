import xlsxwriter, json, os

def retrieve_instructions(instr_name):
    file = os.path.join("./files", "instruction_lists.json")
    with open(file, 'r') as f:
        instr_json = json.load(f)

    user_list = instr_name
    instruction_list = instr_json[user_list]
    instructions = instruction_list["Instructions"]
    instructions.pop()
    instructions.pop()

    functions = instruction_list["Functions"]

    return instructions, functions

def retrieve_functions(func_name):
    file = os.path.join("./files", "functions.json")
    with open(file, 'r') as f:
        instr_json = json.load(f)

    user_list = func_name
    function_list = instr_json[user_list]
    functions = function_list["Instructions"]
    functions.pop()
    functions.pop()

    return functions

def create_instr_list(instructions):
    instr_list = []
    name, instr_type, parameter, attribute, value, tag, function_name, r, notes = "", "", "", "", "", "", "", "", ""

    for instr in instructions:
        name = instr['name']
        names = instr['id'].split('-')
        instr_type = names[2]
        for con in instr['contents']:
            inner_name = con['name']
            tags = inner_name.split("_")
            match tags[-1]:
                case 'parameter':
                    parameter = con['contents']
                case 'attribute':
                    attribute = con['contents']
                case 'value':
                    value = con['contents']
                case 'tag':
                    tag = con['contents']
                case 'function_name':
                    function_name = con['contents']
                case 'range':
                    r = con['contents']
                case 'notes':
                    notes = con['contents']
        instr_list.append([name, instr_type, parameter, attribute, tag, value, function_name, r, notes])
    return instr_list

def create_func_excel_sheet(name, excel_name):
    if name and name != 'Select Function':
        func = retrieve_functions(name)
        funcs = create_instr_list(func)

        files = "./files"
        name = f"{excel_name}.xlsx"
        path = os.path.join(files, name)
        workbook = xlsxwriter.Workbook(path)
        worksheet = workbook.add_worksheet(name)

        bold = workbook.add_format({'bold': True})
        worksheet.write('A1', 'Instruction Name', bold)
        worksheet.write('B1', 'Instruction Type', bold)
        worksheet.write('C1', 'Parameter', bold)
        worksheet.write('D1', 'Attribute', bold)
        worksheet.write('E1', 'Tag', bold)
        worksheet.write('F1', 'Value', bold)
        worksheet.write('G1', 'Function Name', bold)
        worksheet.write('H1', 'Range', bold)
        worksheet.write('I1', 'Notes', bold)

        row, col = 1,0

        for name, instr_type, parameter, attribute, tag, value, function_name, r, notes in (funcs):
            worksheet.write(row, col,     name)
            worksheet.write(row, col + 1, instr_type)
            worksheet.write(row, col + 2, parameter)
            worksheet.write(row, col + 3, attribute)
            worksheet.write(row, col + 4, tag)
            worksheet.write(row, col + 5, value)
            worksheet.write(row, col + 6, function_name)
            worksheet.write(row, col + 7, r)
            worksheet.write(row, col + 8, notes)
            row += 1

        workbook.close()

def create_excel_sheet(name, excel_name):
    instructions, functions = retrieve_instructions(name)
    instr_list = create_instr_list(instructions)

    funcs = []
    if functions and functions != 'Select Function':
        func = retrieve_functions(functions[0])
        funcs = create_instr_list(func)
    
    files = "./files"
    name = f"{excel_name}.xlsx"
    path = os.path.join(files, name)
    workbook = xlsxwriter.Workbook(path)
    worksheet = workbook.add_worksheet('Instructions')

    bold = workbook.add_format({'bold': True})
    worksheet.write('A1', 'Instruction Name', bold)
    worksheet.write('B1', 'Instruction Type', bold)
    worksheet.write('C1', 'Parameter', bold)
    worksheet.write('D1', 'Attribute', bold)
    worksheet.write('E1', 'Tag', bold)
    worksheet.write('F1', 'Value', bold)
    worksheet.write('G1', 'Function Name', bold)
    worksheet.write('H1', 'Range', bold)
    worksheet.write('I1', 'Notes', bold)

    row, col = 1,0

    for name, instr_type, parameter, attribute, tag, value, function_name, r, notes in (instr_list):
        worksheet.write(row, col,     name)
        worksheet.write(row, col + 1, instr_type)
        worksheet.write(row, col + 2, parameter)
        worksheet.write(row, col + 3, attribute)
        worksheet.write(row, col + 4, tag)
        worksheet.write(row, col + 5, value)
        worksheet.write(row, col + 6, function_name)
        worksheet.write(row, col + 7, r)
        worksheet.write(row, col + 8, notes)
        row += 1

    if funcs:
        worksheet2 = workbook.add_worksheet(functions[0])
        worksheet2.write('A1', 'Instruction Name', bold)
        worksheet2.write('B1', 'Instruction Type', bold)
        worksheet2.write('C1', 'Parameter', bold)
        worksheet2.write('D1', 'Attribute', bold)
        worksheet2.write('E1', 'Tag', bold)
        worksheet2.write('F1', 'Value', bold)
        worksheet2.write('G1', 'Function Name', bold)
        worksheet2.write('H1', 'Range', bold)
        worksheet2.write('I1', 'Notes', bold)

        row, col = 1,0

        for name, instr_type, parameter, attribute, tag, value, function_name, r, notes in (funcs):
            worksheet2.write(row, col,     name)
            worksheet2.write(row, col + 1, instr_type)
            worksheet2.write(row, col + 2, parameter)
            worksheet2.write(row, col + 3, attribute)
            worksheet2.write(row, col + 4, tag)
            worksheet2.write(row, col + 5, value)
            worksheet2.write(row, col + 6, function_name)
            worksheet2.write(row, col + 7, r)
            worksheet2.write(row, col + 8, notes)
            row += 1

    workbook.close()