class FileUpload():
    def __init__(self):
        self.df = None
        self.og_df = ""
        self.template = ""
        self.df1 = ""
        self.df2 = ""
        self.compare_cols = []
        self.cols1 = []
        self.cols2 = []
        self.indexes = ""
        self.header2 = ""
        self.mongo_db = ""
        self.mongo_col = ""
        self.mongo_uri = ""
        self.compared = False
        self.form_dict = ""
    
    def clear(self):
        self.df = None
        self.og_df = ""
        self.template = ""
        self.template = ""
        self.df1 = ""
        self.df2 = ""
        self.compare_cols = []
        self.cols1 = []
        self.cols2 = []
        self.indexes = ""
        self.mongo_db = ""
        self.mongo_col = ""
        self.mongo_uri = ""
        self.compared = False
        self.form_dict = ""