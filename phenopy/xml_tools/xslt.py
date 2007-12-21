import libxslt, libxml2

import time

class Xslt:

    def __init__(self, template_file):
        self.template_file = template_file
        self.template = libxslt.parseStylesheetFile(template_file)

    def apply_to_doc(self, doc):
        output = self.template.applyStylesheet(doc, None)
        return output

    def __del__(self):
        self.template.freeStylesheet()

    def __str__(self):
        return self.template_file
