import libxslt, libxml2

import time

class Xslt:

    def __init__(self, template_file):
        self.template_file = template_file
        self.template_doc = libxml2.parseFile(template_file)
        self.template = libxslt.parseStylesheetDoc(self.template_doc) 

    def apply_to_doc(self, doc):
        output = self.template.applyStylesheet(doc, None)
        return output

    def __del__(self):
        self.template.freeStylesheet()
#        self.template_doc.freeDoc()

    def __str__(self):
        return self.template_file
