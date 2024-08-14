# This file is a WIP of utilizing the simple query manager front end. All pymongo queries should be maintained in this file.
import pymongo, json

class QueryManager():
    """This class handles running the query manager, displaying query information to the user, and submitting queries to the db."""
    def __init__(self, db="TestGui", col="Dump"):
        self.uri = "mongodb+srv://relewis:JAP8ES9I6dLD0i9r@practice.cv4a2wt.mongodb.net/?retryWrites=true&w=majority"
        self.db = db
        self.col = col
        self.response = ""
        self.pipeline = []
        self.queries = {
            "addFields": """Adds new fields to documents. $addFields outputs documents that contain all existing fields 
                            from the input documents and newly added fields.""",
            "lookup": """Performs a left outer join to a collection in the same database to filter in documents from 
                        the "joined" collection for processing. The $lookup stage adds a new array field to each input document. 
                        The new array field contains the matching documents from the "joined" collection. 
                        The $lookup stage passes these reshaped documents to the next stage.""",
            "find": """Selects documents in a collection or view and returns a cursor to the selected documents.""",
            "findOne": """Returns one document that satisfies the specified query criteria on the collection or view.
                        If multiple documents satisfy the query, this method returns the first document according to the natural order which reflects the 
                        order of documents on the disk. In capped collections, natural order is the same as insertion order. If no document satisfies the query, 
                        the method returns null.""",
            "match": """Filters the documents to pass only the documents that match the specified condition(s) to the next pipeline stage.""",
            "merge": """Writes the results of the aggregation pipeline to a specified collection. Only 'into' sThe $merge operator must be the last stage in the pipeline.""",
            "out": """Takes the documents returned by the aggregation pipeline and writes them to a specified collection. You can specify the output database.""",
            "project": """Passes along the documents with the requested fields to the next stage in the pipeline. 
                        The specified fields can be existing fields from the input documents or newly computed fields.""",
            "set": """Adds new fields to documents. $set outputs documents that contain all existing fields from the input documents and newly added fields.""",
            "unset": """Removes/excludes fields from documents.""",
            "unwind": """Deconstructs an array field from the input documents to output a document for each element. 
                        Each output document is the input document with the value of the array field replaced by the element.""",
            "setVariable": """This enables the user to create a temporary variable inside of a function.""",
            "index": """This enables the user to create an index for a specified table/collection. This will fail if the index already exists.""",
            "coll": """This enables the user to create a specific collection to be used with this query. This will fail if the collection
                        already exists.""",
            "concat": """Concatenate the string values into one string.""",
            "concatArrays": """Concatenates multiple arrays.""",
            "filter": """Selects a subset of an array to return based on the specified condition. Returns an array with only those elements that 
                        match the condition. The returned elements are in the original order.""",
            "map": """Applies an expression to each item in an array and returns an array with the applied results.""",
            "range": """Returns an array whose elements are a generated sequence of numbers.""",
            "reduce": """Applies an expression to each element in an array and combines them into a single value.""",
            "regexMatch": """Performs a regular expression (regex) pattern matching and returns: true if a match exists, false if a match does not exist.""",
            "substrCP": """Returns the substring of a string. The substring starts with the character at the specified index (zero-based) 
            in the string for the number of code points specified."""
        }
        self.syntaxes = {
            "addFields": "Name: <FieldName>, Value: <FieldValue>",
            "find": "db.collection.find( <query>, <projection>, <options> )",
            "findOne": "db.collection.findOne( <query>, <projection>, <options> )",
            "lookup": """
            from: <collection to join>,
            localField: <field from the input documents>,
            foreignField: <field from the documents of the "from" collection>,
            as: <output array field>""",
            "match": "{ $match: { <query> } }",
            "merge": """
            into: <collection> -or- { db: <db>, coll: <collection> },
            on: <identifier field> -or- [ <identifier field1>, ...],  
            let: <variables>,                                         
            whenMatched: <replace|keepExisting|merge|fail|pipeline>,                  
            whenNotMatched: <insert|discard|fail>""",
            "out": """Database (Optional): <Database-Name>, Collection: <Output-Collection>""",
            "project": """{ "<FieldName>": 0 or 1, "<FieldName2>": 0 or 1, ... }""",
            "set": """Set: <FieldName>, As: <FieldValue>""",
            "unset": """Field: <FieldName> """,
            "unwind": """{ $unwind: <field path> }""",
            "setVariable": """{<Variable Name>: <Variable Value>}""",
            "index": """
            Database: <Database Name>,
            Collection: <Collection Name>,
            Key: <Name of the field used as the index>,
            Sort: ASCENDING or DESCENDING,
            Unique: True or False""",
            "coll": """Database: <Database Name>, Collection Name: <Collection-Name>""",
            "concat": """["<Value 1>", "<Value 2>", "<Value 3>", etc.]""",
            "concatArrays": """{"<field>": [<Array 1>, <Array 2>, "<Array 3>", etc.]}""",
            "filter": """
            input: <array>,
            as (optional): <string>,
            cond: <expression>,
            limit (optional): <number expression>""",
            "map": """input: <expression>, as (optional): <string>, in: <expression>""",
            "range": """Start: <start-index>, End: <end-index>, Step (optional): <non-zero step>""",
            "reduce": """
            input: <array>,
            initialValue: <expression>,
            in: <expression> """,
            "regexMatch": """input: <expression> , regex: <expression>, options (optional): <expression>""",
            "substrCP": """string: <string expression>, index: <code point index>, count: <code point count>"""
        }
        self.cmd = {
            "addFields": "$addFields",
            "set": "$set",
            "project": "$project",
            "projectMulti": "$project",
            "match": "$match",
            "merge": "$merge",
            "concat": "$concat",
            "out": "$out",
            "filter": "$filter",
            "regexMatch": "$regexMatch",
            "map": "$map",
            "range": "$range",
            "substrCP": "$substrCP",
            "reduce": "$reduce",
            "index": "index",
            "coll": "coll",
            "unset": "$unset",
            "concatArrays": "$concatArrays"
        }
        self.instructions = []

    def set_mongodb(self, db="", col="", uri=""):
        if uri != "":
            self.uri = uri
        self.db = db
        self.col = col

    def accept_json(self, str):
        """Function that controls generating a pipeline. This will turn the user input dictionary into a pymongo pipeline."""
        self.response = json.loads(str)
        query_name = self.response.pop(-1)
        name = query_name["query_name"]
        pipeline = self.generate_gui_pipeline(self.response)
        pipeline = self.remove_query_name(pipeline)
        self.pipeline = self.clean_pipeline(pipeline)
        return self.pipeline, name

    def remove_query_name(self, pipeline):
        for p in pipeline:
            if "query_name" in p:
                del p["query_name"]
        return pipeline
    
    def clean_pipeline(self, pipeline):
        query = []
        if pipeline:
            for p in pipeline:
                query.append(p["query"])
            return query
    
    def aggre_pipeline(self, pipeline):
        """Function that submits the aggregation to mongodb."""
        client = pymongo.MongoClient(self.uri)
        db = client[self.db]
        col = db[self.col]
        results = col.aggregate(pipeline)
        # for r in results:
        #     print(r)
        # print(results)

    def check_name(self, name):
        """Future function that will check user input for specific commands."""
        # if $: mongodb val
        # if @$: temp variable somewhere in pipeline
        # if @.: function
        # if @: function
        # if @@: subfunction?
        pass

    def generate_gui_pipeline(self, lst):
        """Function that generates a query pipeline."""
        pipeline = []
        if lst == []:
            return
        
        # Loop through the list of dictionaries.
        for i in lst:
            index = i["id"]
            name = i["name"]
            contents = i["contents"]
            subs = i["subs"]

            # Determine command of current item
            cmd = self.determine_cmd(index)

            # Determine if there are any substeps. If there are, generate those steps first
            sub_steps = self.generate_gui_pipeline(subs)

            # Determine current step
            step = ""
            match cmd:
                case "$addFields":
                    step = self.cmd_addFields(contents, name)
                case "$concat":
                    step = self.cmd_concat(contents, name)
                case "$concatArrays":
                    step = self.cmd_concatArrays(contents, name)
                case "$filter":
                    step = self.cmd_filter(contents, name)
                case "$match":
                    step = self.cmd_match(contents, name)
                case "$map":
                    step = self.cmd_map(contents, name)
                case "$merge":
                    step = self.cmd_merge(contents, name)
                case "$out":
                    step = self.cmd_out(contents, name)
                case "$project":
                    step = self.cmd_project(contents, name)
                case "$unset":
                    step = self.cmd_unset(contents, name)
                case "$range":
                    step = self.cmd_range(contents, name)
                case "$reduce":
                    step = self.cmd_reduce(contents, name)
                case "$regexMatch":
                    step = self.cmd_regexMatch(contents, name)
                case "$set":
                    step = self.cmd_set(contents, name)
                case "$substrCP":
                    step = self.cmd_substrCP(contents, name)
                case "index":
                    self.create_index(contents)
                case "coll":
                    self.create_coll(contents)
            
            # Append any substeps into the current command.
            if cmd != 'index' and cmd != 'coll':
                if sub_steps:
                    query = step["query"]
                    q = query[list(query.keys())[0]]
                    for s in sub_steps:
                        for k in list(q.keys()):
                            if ("@"+s["query_name"]) == q[k]:
                                q[k] = s["query"]
                                break
                    sub_steps = self.remove_query_name(sub_steps)
                pipeline.append(step)
        return pipeline
    
    def create_index(self, contents):
        """Function that enables the user to create an index for a specified collection."""
        database = contents[0]["contents"]
        collection = contents[1]["contents"]
        key = contents[2]["contents"]
        sort = contents[3]["contents"]
        unique = contents[4]["contents"]

        client = pymongo.MongoClient(self.uri)
        db = client[database]
        col = db[collection]

        sort_type = ""

        if not unique:
            unique = False
        else:
            unique = True

        if sort:
            sort = sort.lower()[0]
            match sort:
                case 'a':
                    sort_type = pymongo.ASCENDING
                case 'd':
                    sort_type = pymongo.DESCENDING
        else:
            sort_type = pymongo.ASCENDING

        col.create_index([(key, sort_type)], unique=unique)

    def create_coll(self, contents):
        """Function that enables the user to create a specific collection for a query."""
        database = contents[0]["contents"]
        name = contents[1]["contents"]

        client = pymongo.MongoClient(self.uri)
        db = client[database]
        db.create_collection(name)

    def determine_cmd(self, index):
        s = index.split('_')
        return self.cmd[s[2]]
    
    def cmd_unset(self, contents, name):
        """Function that generates the mongodb unset command."""
        arr = contents[0]["contents"]
        step = {
            "$unset": arr
            }
        q = {"query_name": name, "query": step}
        return q

    def cmd_addFields(self, contents, name):
        """Function that generates the mongodb addFields command."""
        q_name = contents[0]["contents"]
        q_value = contents[1]["contents"]
        step = {
            "$addFields": {
                q_name: q_value
            }
        }
        q = {"query_name": name, "query": step}
        return q

    def cmd_reduce(self, contents, name):
        """Function that generates the mongodb reduce command."""
        arr = contents[0]["contents"]
        init = contents[1]["contents"]
        exp = contents[2]["contents"]
        step = {
                "$reduce": {
                    "input": arr,
                    "initialValue": init,
                    "in": exp
                }
            }
        q = {"query_name": name, "query": step}
        return q

    def cmd_filter(self, contents, name):
        """Function that generates the mongodb filter command."""
        arr = contents[0]["contents"]
        s = contents[1]["contents"]
        cond = contents[2]["contents"]
        limit = contents[3]["contents"]
        step = {
            "$filter": {
                    "input": arr,
                    "cond": cond,
                }
            }
        
        # Limit and as are optional
        if limit:
            step["$filter"]["limit"] = int(limit)
        if s:
            step["$filter"]["as"] = s
        q = {"query_name": name, "query": step}
        return q

    def cmd_map(self, contents, name):
        """Function that generates the mongodb map command."""
        in_put = contents[0]["contents"]
        as_input = contents[1]["contents"]
        inn = contents[2]["contents"]
        # "as" is optional
        if as_input:
            step = {
                    "$map": {
                        "input": in_put,
                        "as": as_input,
                        "in": inn,
                    }
                }
        else:
            step = {
                    "$map": {
                        "input": in_put,
                        "in": inn,
                    }
                }
        q = {"query_name": name, "query": step}
        return q

    def cmd_range(self, contents, name):
        """Function that generates the mongodb range command."""
        start = int(contents[0]["contents"])
        stop = int(contents[1]["contents"])
        count = contents[2]["contents"]
        if count:
            step = {
                "$range": [start, stop, int(count)]
            }
        else:
            step = {
                "$range": [start, stop]
            }
        q = {"query_name": name, "query": step}
        return q

    def cmd_substrCP(self, contents, name):
        """Function that generates the mongodb substrCP command."""
        string = contents[0]["contents"]
        index = contents[1]["contents"]
        count = int(contents[2]["contents"])
        step = {
                "$substrCP": [string, index, int(count)]
            }
        q = {"query_name": name, "query": step}
        return q

    def cmd_regexMatch(self, contents, name):
        """Function that generates the mongodb regexMatch command."""
        str_input = contents[0]["contents"]
        regex = contents[1]["contents"]
        step = {
                "$regexMatch": {
                    "input": str_input,
                    "regex": regex
                }
            }
        q = {"query_name": name, "query": step}
        return q

    def cmd_set(self, contents, name):
        """Function that generates the mongodb set command."""
        q_name = contents[0]["contents"]
        q_value = contents[1]["contents"]
        if '[' in q_value and ']':
            q_value = json.loads(q_value)
        step = {
            "$set": {
                q_name: q_value
            }
        }
        q = {"query_name": name, "query": step}
        return q

    def cmd_match(self, contents, name):
        """Function that generates the mongodb match command."""
        query = contents[0]["contents"]
        qry = {}
        qry["Contact Identifier"] = json.loads(query)
        if qry["Contact Identifier"]["$ne"] == 'None':
            qry["Contact Identifier"]["$ne"] = None
        # try:
        #     qry = json.loads(query)

        #     print("Qry", qry)
        # except:
        #     # Temp fix until we implement $ne
        #     qry["Contact Identifier"] = json.loads(query)
            
        step = {
            "$match": qry
        }
        q = {"query_name": name, "query": step}
        return q

    def cmd_merge(self, contents, name):
        """Function that generates the mongodb merge command."""
        db = contents[0]["contents"]
        col = contents[1]["contents"]
        on = contents[2]["contents"]
        let = contents[3]["contents"]
        when_matched = contents[4]["contents"]
        when_not_matched = contents[5]["contents"]
        if db == "":
            into = col
        else:
            into = {"db": db, "coll": col}
        
        step = {
            "$merge":
            {
                "into": into,
                "on": on,
            }
        }
        if let:
            step["$merge"]["let"] = let
        if when_matched:
            step["$merge"]["whenMatched"] = when_matched
        if when_not_matched:
            step["$merge"]["whenNotMatched"] = when_not_matched
        q = {"query_name": name, "query": step}
        return q
    
    def cmd_out(self, contents, name):
        """Function that generates the mongodb out command."""
        db = contents[0]["contents"]
        col = contents[1]["contents"]
        if db == "":
            into = col
        else:
            into = {"db": db, "coll": col}
        
        step = {
            "$out": into
        }
        q = {"query_name": name, "query": step}
        return q
    
    def cmd_project(self, contents, name):
        """Function that generates the mongodb project command."""
        query = contents[0]["contents"]
        step = {}
        try:
            proj = json.loads(query)
            step["$project"] = proj
        except:
            step["query"] = query
        q = {"query_name": name, "query": step}
        return q
    
    def cmd_concatArrays(self, contents, name):
        """Function that generates the mongodb concatArrays command."""
        pass

    def cmd_concat(self, contents, name):
        """Function that generates the mongodb unset command."""
        query = contents[0]["contents"]
        step = {
            "$concat": json.loads(query)
        }
        q = {"query_name": name, "query": step}
        return q